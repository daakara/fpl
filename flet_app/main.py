"""
FPL Analytics - Flet Mobile App
Main entry point for iOS/Android native application
"""

import flet as ft
import logging
import sys
import traceback

# Handle imports for both direct execution and module execution
try:
    # Try relative imports first (when run as module)
    from .pages.dashboard_page import DashboardPage
    from .pages.player_analysis_page import PlayerAnalysisPage
    from .pages.team_builder_page import TeamBuilderPage
    from .pages.learning_resources_page import LearningResourcesPage
    from .utils.theme import get_app_theme
    from .utils.data_service import FPLDataService
except ImportError:
    # Fall back to absolute imports (when run directly)
    from pages.dashboard_page import DashboardPage
    from pages.player_analysis_page import PlayerAnalysisPage
    from pages.team_builder_page import TeamBuilderPage
    from pages.learning_resources_page import LearningResourcesPage
    from utils.theme import get_app_theme
    from utils.data_service import FPLDataService


class FPLAnalyticsApp:
    """Main FPL Analytics mobile application"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.data_service = FPLDataService()
        
        # Theme state
        self.dark_mode = True
        
        # Configure page
        self.page.title = "FPL Analytics"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = get_app_theme(dark=True)
        self.page.padding = 0
        
        # Initialize pages
        self.dashboard = DashboardPage(self, self.data_service)
        self.player_analysis = PlayerAnalysisPage(self.data_service)
        self.team_builder = TeamBuilderPage(self.data_service)
        self.learning = LearningResourcesPage()
        
        # Navigation state
        self.current_page = "dashboard"
        
        # Build UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI with navigation"""
        self.page.appbar = ft.AppBar(
            title=ft.Text("FPL Analytics", weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor="surfacevariant",
            actions=[],
        )
        
        # Content area
        self.content_area = ft.Container(
            content=self.dashboard.build(),
            expand=True,
        )
        
        # Bottom navigation
        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon="dashboard_outlined",
                    selected_icon="dashboard",
                    label="Dashboard"
                ),
                ft.NavigationBarDestination(
                    icon="person_search_outlined",
                    selected_icon="person_search",
                    label="Players"
                ),
                ft.NavigationBarDestination(
                    icon="groups_outlined",
                    selected_icon="groups",
                    label="Team Builder"
                ),
                ft.NavigationBarDestination(
                    icon="school_outlined",
                    selected_icon="school",
                    label="Learn"
                ),
            ],
            on_change=self.navigate,
            selected_index=0,
        )
        
        # Main layout
        self.page.add(
            ft.Column(
                controls=[
                    self.content_area,
                    self.nav_bar,
                ],
                spacing=0,
                expand=True,
            )
        )
    
    def navigate(self, e):
        """Handle navigation between pages"""
        index = e.control.selected_index
        
        # Map index to page
        pages = {
            0: ("dashboard", self.dashboard),
            1: ("players", self.player_analysis),
            2: ("team", self.team_builder),
            3: ("learn", self.learning),
        }
        
        page_name, page_obj = pages.get(index, ("dashboard", self.dashboard))
        self.current_page = page_name
        
        # Update content
        self.content_area.content = page_obj.build()
        self.page.update()
    
    def refresh_data(self, e):
        """Refresh FPL data"""
        # Show loading indicator
        self.page.splash = ft.ProgressBar()
        self.page.update()
        
        # Reload data
        self.data_service.clear_cache()
        
        # Rebuild current page
        if self.current_page == "dashboard":
            self.content_area.content = self.dashboard.build()
        elif self.current_page == "players":
            self.content_area.content = self.player_analysis.build()
        elif self.current_page == "team":
            self.content_area.content = self.team_builder.build()
        
        # Hide loading indicator
        self.page.splash = None
        self.page.update()
        
        # Show success
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("Data refreshed successfully!"))
        )
    
    def toggle_theme(self, e):
        """Toggle between dark and light theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.theme = get_app_theme(dark=False)
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.page.theme = get_app_theme(dark=True)
        
        self.page.update()


def main(page: ft.Page):
    """Main entry point for Flet app"""
    try:
        app = FPLAnalyticsApp(page)
    except Exception as e:
        logging.exception("Unhandled exception in FPLAnalyticsApp")
        # Also print to stderr to be sure it appears in the console
        print(f"FATAL: {e}\n{traceback.format_exc()}", file=sys.stderr)
        page.clean()
        page.add(ft.Text(f"An error occurred: {e}\n\n{traceback.format_exc()}", font_family="monospace"))
        page.update()

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('flet_core').setLevel(logging.INFO)
    ft.app(main)
