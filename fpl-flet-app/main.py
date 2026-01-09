"""FPL Analytics - Flet Mobile/Desktop App."""

import flet as ft
import logging
import asyncio
import os # Added for path manipulation
import sys # Added for sys.path manipulation
from datetime import datetime # Added for timestamping logs

# Ensure the current directory is in sys.path for local module imports
sys.path.insert(0, os.path.dirname(__file__))

from config.app_config import AppConfig
from utils.theme import PLTheme, Typography, Spacing
from services.fpl_api_service import FPLDataService
from services.player_recommendation_service import PlayerRecommendationService
from services.data_utilities_service import DataUtilitiesService
from views.dashboard_view import build_dashboard
from views.my_team_view import build_my_team
from views.fixtures_view import build_fixtures
from views.ai_tips_view import build_ai_tips
from views.player_comparison_view import build_player_comparison
from components.views import create_error_view
from components.skeleton import create_skeleton_list

# --- NEW Logging Configuration ---
# Function to get a writable path on the device and configure file logging
def configure_file_logging(log_file_name: str, page_obj: ft.Page):
    log_dir = None
    try:
        # Try Flet's API for app data directory
        if hasattr(page_obj, 'get_app_data_dir') and callable(page_obj.get_app_data_dir):
            log_dir = page_obj.get_app_data_dir()
    except Exception:
        # Catch any exceptions during get_app_data_dir() call
        pass
    
    if log_dir is None or not os.path.exists(log_dir):
        # Fallback to environment variable or current directory
        log_dir = os.getenv("FLET_APP_STORAGE_DATA", ".")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True) # Ensure directory exists

    log_file_path = os.path.join(log_dir, log_file_name)

    # Remove previous handlers to avoid duplicate logs if this is called multiple times
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, mode='a'), # Append to log file
            logging.StreamHandler() # Also log to console for development/debug builds
        ]
    )
    logger_instance = logging.getLogger(__name__) # Use a local logger instance
    logger_instance.info(f"Logging to file: {log_file_path}")
    return logger_instance, log_file_path # Return the configured logger instance and path

# Global logger instance (will be configured in FPLApp __init__)
logger = logging.getLogger(__name__)


class FPLApp:
    def __init__(self, page: ft.Page, logger_instance: logging.Logger, log_file_path: str):
        self.page = page
        self.logger = logger_instance
        self.log_path = log_file_path
        
        self.data_service = FPLDataService()
        self.rec_service = PlayerRecommendationService()
        self.util_service = DataUtilitiesService()
        self.current_view = "dashboard"
        self.team_id = None
        self.is_loading = False
        # self.loading_indicator = None # Loading indicator will be part of views
        self.team_id_input = None
        self.import_status_text = None
        
        # Configure page with Premier League theme
        self.page.title = f"FPL Analytics v{AppConfig.VERSION}"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = PLTheme.BACKGROUND
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=PLTheme.PRIMARY,
                on_primary=PLTheme.ON_SURFACE,
                secondary=PLTheme.ACCENT,
                on_secondary=PLTheme.PRIMARY,
                surface=PLTheme.SURFACE,
                on_surface=PLTheme.ON_SURFACE,
            ),
            use_material3=True,
        )
        self.page.padding = 0

        # Setup Flet routing
        self.page.on_route_change = self.route_change_sync
        self.page.on_view_pop = self.view_pop
        self.page.on_error = self.on_page_error
        # Pre-cache player data for quick access on other tabs - now async
        asyncio.create_task(self.data_service.get_players())

    def start(self):
        self.logger.info("FPLApp starting...")
        # Trigger initial route directly
        asyncio.create_task(self._initial_route())
    
    async def _initial_route(self):
        """Load initial route after app is ready"""
        # Small delay to ensure page is ready
        await asyncio.sleep(0.1)
        self.logger.info("Loading initial route")
        # Manually trigger route change for "/"
        await self.route_change(type('obj', (object,), {'route': '/'})())

    def _build_tab_bar(self, current_route):
        tabs = []
        
        def make_click_handler(route_path):
            def handler(e):
                asyncio.create_task(self._navigate_to(route_path))
            return handler
        
        for route, icon, label in [
            ("/", "📊", "Dashboard"),
            ("/my_team", "👥", "My Team"),
            ("/fixtures", "📅", "Fixtures"),
            ("/ai_tips", "💡", "AI Tips"),
            ("/player_comparison", "👥", "Compare"),
        ]:
            is_active = current_route == route
            tab = ft.Container(
                content=ft.Text(f"{icon} {label}", size=14, color=PLTheme.ON_SURFACE),
                padding=Spacing.MD,
                on_click=make_click_handler(route),
                ink=True,
                border=ft.Border(bottom=ft.BorderSide(2, PLTheme.ACCENT)) if is_active else ft.Border(),
            )
            tabs.append(tab)
        
        return ft.Container(
            content=ft.Row(
                tabs,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            bgcolor=PLTheme.PRIMARY,
            height=48,
        )
    
    async def _navigate_to(self, route_path):
        """Navigate to a route"""
        await self.route_change(type('obj', (object,), {'route': route_path})())

    async def _build_view_content(self, route):
        content = create_skeleton_list() # Default placeholder
        if route == "/":
            content = await build_dashboard(self.data_service, self.rec_service, self.util_service)
        elif route == "/my_team":
            # Create controls and store references
            self.team_id_input = ft.TextField(
                label="Enter your FPL Team ID",
                hint_text="e.g., 1437667",
                width=300,
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor="#2d2d2d",
                border_color="#00ff00",
                color="#FFFFFF",
            )
            self.import_status_text = ft.Text("", size=14, color="#BDBDBD")
            content = await build_my_team(self.data_service, self.team_id_input, self.import_status_text, self._import_team_callback)
        elif route == "/fixtures":
            content = await build_fixtures(self.data_service)
        elif route == "/ai_tips":
            content = await build_ai_tips(self.data_service)
        elif route == "/player_comparison":
            content = await build_player_comparison(self.data_service, self.page.session)
        
        return content
    

    
    def route_change_sync(self, route):
        """Synchronous wrapper for async route_change"""
        asyncio.create_task(self.route_change(route))
    
    async def route_change(self, route):
        self.logger.info(f"Route changed to: {route.route}")
        
        # Immediately show loading state
        self.page.controls.clear()
        
        self.page.controls.append(
            ft.AppBar(
                title=ft.Text("⚽ FPL Analytics", weight=ft.FontWeight.BOLD, size=Typography.HEADING_3),
                center_title=False,
                bgcolor=PLTheme.PRIMARY,
                toolbar_height=56,
            )
        )
        
        self.page.controls.append(self._build_tab_bar(route.route))
        
        # Show loading indicator
        loading_container = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Loading...", size=16, color=PLTheme.ON_SURFACE_VARIANT),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            padding=Spacing.MD,
        )
        
        self.page.controls.append(loading_container)
        self.page.update()
        
        # Now load content asynchronously
        try:
            view_content = await self._build_view_content(route.route)
            self.logger.info(f"View content type: {type(view_content)}")
            self.logger.info(f"View content: {view_content.__class__.__name__ if hasattr(view_content, '__class__') else 'Unknown'}")
        except Exception as e:
            self.logger.error(f"Error building view content: {e}", exc_info=True)
            view_content = ft.Column([
                ft.Text(f"Error loading view: {str(e)}", color="#FF0000"),
                ft.ElevatedButton("Reload", on_click=lambda _: asyncio.create_task(self.route_change(route)))
            ])
        
        # Replace loading indicator with actual content
        self.page.controls[-1] = ft.Container(
            content=view_content,
            expand=True,
            padding=Spacing.MD,
        )
        
        self.page.update()
        self.logger.info(f"Page updated with {len(self.page.controls)} controls")

    def view_pop(self, view):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.push_route(top_view.route)

    def _import_team_callback(self, e):
        """Callback to import team data based on user input, now part of the FPLApp instance."""
        asyncio.create_task(self._import_team_async(e))
    
    async def _import_team_async(self, e):
        """Async implementation of team import"""
        team_id_str = self.team_id_input.value
        
        if not team_id_str or not team_id_str.strip():
            self.import_status_text.value = "❌ Please enter a Team ID"
            self.import_status_text.color = "#ff0000"
            self.import_status_text.update()
            return
        
        try:
            team_id = int(team_id_str.strip())
            
            # Show loading state
            self.import_status_text.value = "⏳ Loading team data..."
            self.import_status_text.color = "#ffd700"
            self.import_status_text.update()
            
            # Fetch team data
            team_data = await self.data_service.get_my_team(team_id, force_refresh=True)
            
            if team_data is None:
                self.import_status_text.value = "❌ Failed to load team. Check the Team ID and try again."
                self.import_status_text.color = "#ff0000"
                self.import_status_text.update()
                return
            
            # Success - store team ID and reload view
            self.team_id = team_id
            team_name = team_data['team_info'].get('name', 'Your Team')
            self.import_status_text.value = f"✅ Successfully loaded {team_name}!"
            self.import_status_text.color = "#00ff00"
            self.import_status_text.update()
            
            # Reload the view to show team data
            self.logger.info(f"Successfully imported team {team_id}")
            await self._navigate_to("/my_team")
            
        except ValueError:
            self.import_status_text.value = "❌ Invalid Team ID. Please enter numbers only."
            self.import_status_text.color = "#ff0000"
            self.import_status_text.update()
        except Exception as ex:
            self.logger.error(f"Error importing team: {ex}")
            self.import_status_text.value = f"❌ Error: {str(ex)}"
            self.import_status_text.color = "#ff0000"
            self.import_status_text.update()

    def on_page_error(self, e: ft.ControlEvent):
        import traceback
        self.logger.error(f"Unhandled UI exception caught: {e.data}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        # Simplified error handling - just log, don't try to rebuild view
        # to avoid error loops

    def show_log_path_snackbar(self, e):
        """Displays the log file path in a SnackBar."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(f"Log file: {self.log_path}", color=PLTheme.ON_SURFACE),
            open=True,
        )
        self.page.update()


async def main(page: ft.Page):
    # Ensure the page is configured for async before anything else
    
    # Configure logging globally first
    global logger
    app_logger, log_path = configure_file_logging(AppConfig.LOG_FILE_NAME, page)
    logger = app_logger # Update the global logger instance
    logger.info("Flet app started.")

    app = FPLApp(page, app_logger, log_path)
    
    # Register cleanup handler
    async def on_page_close(e):
        logger.info("Page closing, cleaning up resources...")
        await app.data_service.close()
    
    page.on_close = on_page_close
    
    # Use asyncio.create_task to ensure the start logic 
    # runs inside the correct event loop
    app.start()


if __name__ == "__main__":
    ft.app(target=main)