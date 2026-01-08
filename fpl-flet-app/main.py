"""
FPL Analytics - Flet Mobile/Desktop App
Production-ready standalone implementation
Version: 2.0
"""

import flet as ft
import requests
import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime
import time

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Production configuration
class AppConfig:
    VERSION = "2.0"
    CACHE_DURATION = 300  # 5 minutes
    REQUEST_TIMEOUT = 10
    RETRY_ATTEMPTS = 3
    DEFAULT_TEAM_ID = 1437667


# Premier League Theme System
class PLTheme:
    """Official Premier League branding colors"""
    # Brand Colors
    PRIMARY = "#37003c"       # Premier League Purple
    ACCENT = "#00ff85"        # FPL Green
    SECONDARY = "#ff2882"     # Premier League Magenta
    
    # Semantic Colors
    SUCCESS = "#00ff85"
    WARNING = "#ffd700"
    ERROR = "#ff0000"
    INFO = "#0ea5e9"
    
    # Neutral Colors
    BACKGROUND = "#0e1117"
    SURFACE = "#1a1a2e"
    SURFACE_VARIANT = "#262640"
    ON_SURFACE = "#ffffff"
    ON_SURFACE_VARIANT = "#bdbdbd"
    ON_SURFACE_DIM = "#9e9e9e"
    DIVIDER = "#333333"
    
    # Position Colors
    GOALKEEPER = "#f59e0b"    # Amber
    DEFENDER = "#3b82f6"      # Blue
    MIDFIELDER = "#10b981"    # Green
    FORWARD = "#ef4444"       # Red


# Responsive Typography Scale
class Typography:
    """Mobile-first responsive typography"""
    # Desktop sizes
    DISPLAY = 32
    HEADING_1 = 28
    HEADING_2 = 24
    HEADING_3 = 20
    HEADING_4 = 18
    BODY_LARGE = 16
    BODY = 14
    CAPTION = 12
    OVERLINE = 11
    
    # Mobile scaling factor
    MOBILE_SCALE = 0.9
    
    @staticmethod
    def scale_for_mobile(size: int, is_mobile: bool = True) -> int:
        """Scale typography for mobile devices"""
        return int(size * Typography.MOBILE_SCALE) if is_mobile else size


# Spacing System
class Spacing:
    """Consistent spacing scale"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32


# UI Component Helpers
class UIComponents:
    """Reusable UI component builders for consistent design"""
    
    @staticmethod
    def create_skeleton_card(height: int = 80):
        """Create a loading skeleton card with shimmer effect"""
        return ft.Container(
            height=height,
            bgcolor=PLTheme.SURFACE_VARIANT,
            border_radius=12,
            animate_opacity=300,
            opacity=0.6,
        )
    
    @staticmethod
    def create_skeleton_list(count: int = 5):
        """Create multiple skeleton cards for list loading"""
        return ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            UIComponents.create_skeleton_card(60),
                            ft.Container(height=Spacing.SM),
                        ],
                    ),
                )
                for _ in range(count)
            ],
            spacing=Spacing.SM,
        )
    
    @staticmethod
    def create_stat_card(title: str, value: str, subtitle: str = "", icon: str = None, color: str = None):
        """Create a styled stat card with optional emoji icon"""
        if color is None:
            color = PLTheme.ACCENT
        """Create a styled stat card with optional emoji icon"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(icon if icon else "", size=20) if icon else ft.Container(),
                            ft.Text(title, size=14, color="#BDBDBD", weight=ft.FontWeight.W_500),
                        ],
                        spacing=8,
                    ) if icon else ft.Text(title, size=14, color="#BDBDBD", weight=ft.FontWeight.W_500),
                    ft.Text(value, size=Typography.HEADING_1, weight=ft.FontWeight.BOLD, color=PLTheme.ON_SURFACE),
                    ft.Text(subtitle, size=Typography.CAPTION, color=PLTheme.ON_SURFACE_DIM) if subtitle else ft.Container(),
                ],
                spacing=Spacing.XS,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=PLTheme.SURFACE,
            border_radius=12,
            padding=Spacing.LG,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color="#00000040",
                offset=ft.Offset(0, 2),
            ),
        )
    
    @staticmethod
    def create_section_header(text: str, icon: str = None):
        """Create a section header with optional emoji icon"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(icon if icon else "", size=Typography.HEADING_3) if icon else ft.Container(),
                    ft.Text(text, size=Typography.HEADING_2, weight=ft.FontWeight.BOLD, color=PLTheme.ON_SURFACE),
                ],
                spacing=Spacing.SM,
            ),
            padding=ft.Padding(top=Spacing.MD, bottom=Spacing.SM, left=0, right=0),
        )
    
    @staticmethod
    def create_player_card(name: str, stats: List[tuple], icon: str = "⚽", highlight: bool = False):
        """Create a player card with stats
        stats format: [(label, value, color), ...]
        """
        stat_items = []
        for label, value, color in stats:
            stat_items.extend([
                ft.Text(label, size=12, color=color),
                ft.Text("•", size=12, color="#BDBDBD") if stat_items else ft.Container(),
            ])
        # Remove last separator
        if stat_items and stat_items[-1].value == "•":
            stat_items = stat_items[:-1]
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(icon, size=16),
                            ft.Text(name, size=16, color="#FFFFFF", expand=True, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=8,
                    ),
                    ft.Row(stat_items, spacing=4, wrap=True) if stat_items else ft.Container(),
                ],
                spacing=6,
            ),
            bgcolor=PLTheme.SURFACE if highlight else "transparent",
            border_radius=8 if highlight else 0,
            padding=Spacing.MD,
            border=ft.Border(
                bottom=ft.BorderSide(1, PLTheme.DIVIDER),
            ),
        )
    
    @staticmethod
    def create_error_view(message: str, retry_callback=None):
        """Create an error view with optional retry button"""
        controls = [
            ft.Text("❌", size=64),
            ft.Text("Oops!", size=Typography.HEADING_1, weight=ft.FontWeight.BOLD, color=PLTheme.ON_SURFACE),
            ft.Text(message, size=Typography.BODY, color=PLTheme.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER),
        ]
        
        if retry_callback:
            controls.append(
                ft.FilledButton(
                    "↻ Retry",
                    on_click=retry_callback,
                    style=ft.ButtonStyle(
                        bgcolor=PLTheme.ACCENT,
                        color=PLTheme.PRIMARY,
                    ),
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls,
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=40,
            alignment=ft.alignment.center,
        )
    
    @staticmethod
    def create_loading_view(message: str = "Loading data..."):
        """Create a loading view"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(color=PLTheme.ACCENT, width=48, height=48),
                    ft.Container(height=Spacing.LG),
                    ft.Text(message, size=Typography.BODY, color=PLTheme.ON_SURFACE_VARIANT),
                ],
                spacing=Spacing.LG,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=Spacing.XXL,
            alignment=ft.alignment.center,
            expand=True,
        )


class FPLDataService:
    """Production-ready data service for FPL API with caching and error handling"""
    
    BASE_URL = "https://fantasy.premierleague.com/api"
    
    def __init__(self):
        self._players_df = None
        self._teams_df = None
        self._fixtures_df = None
        self._my_team_data = None
        self._cache_timestamp = None
        self._last_error = None
    
    def get_players(self, force_refresh=False):
        """Get players data with caching and retry logic"""
        # Check cache validity
        cache_valid = (self._cache_timestamp is not None and 
                      time.time() - self._cache_timestamp < AppConfig.CACHE_DURATION)
        
        if self._players_df is None or force_refresh or not cache_valid:
            for attempt in range(AppConfig.RETRY_ATTEMPTS):
                try:
                    logger.info(f"Fetching players data (attempt {attempt + 1}/{AppConfig.RETRY_ATTEMPTS})")
                    response = requests.get(
                        f"{self.BASE_URL}/bootstrap-static/",
                        timeout=AppConfig.REQUEST_TIMEOUT
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'elements' in data:
                        df = pd.DataFrame(data['elements'])
                        df['price'] = df['now_cost'] / 10
                        df['value_score'] = (df['total_points'] / (df['now_cost'] / 10)).fillna(0)
                        self._players_df = df
                        self._cache_timestamp = time.time()
                        self._last_error = None
                        logger.info("Successfully loaded players data")
                        
                        # Also cache teams data
                        if 'teams' in data:
                            self._teams_df = pd.DataFrame(data['teams'])
                        break
                    else:
                        self._players_df = pd.DataFrame()
                except Exception as e:
                    logger.error(f"Error fetching players (attempt {attempt + 1}): {e}")
                    self._last_error = str(e)
                    if attempt < AppConfig.RETRY_ATTEMPTS - 1:
                        time.sleep(1)  # Wait before retry
                    else:
                        self._players_df = pd.DataFrame()
        
        return self._players_df
    
    def get_teams(self):
        if self._teams_df is None:
            self.get_players()  # This will populate teams as well
        return self._teams_df if self._teams_df is not None else pd.DataFrame()
    
    def get_fixtures(self, force_refresh=False):
        if self._fixtures_df is None or force_refresh:
            try:
                response = requests.get(f"{self.BASE_URL}/fixtures/", timeout=10)
                response.raise_for_status()
                data = response.json()
                self._fixtures_df = pd.DataFrame(data)
            except Exception as e:
                logging.error(f"Error fetching fixtures: {e}")
                self._fixtures_df = pd.DataFrame()
        
        return self._fixtures_df
    
    def get_my_team(self, team_id: int, force_refresh=False):
        """Get user's FPL team data"""
        if self._my_team_data is None or force_refresh:
            try:
                response = requests.get(f"{self.BASE_URL}/entry/{team_id}/", timeout=10)
                response.raise_for_status()
                team_data = response.json()
                
                # Get current picks
                current_event = team_data.get('current_event', 1)
                picks_response = requests.get(
                    f"{self.BASE_URL}/entry/{team_id}/event/{current_event}/picks/",
                    timeout=10
                )
                picks_response.raise_for_status()
                picks_data = picks_response.json()
                
                self._my_team_data = {
                    'team_info': team_data,
                    'picks': picks_data,
                    'current_event': current_event
                }
            except Exception as e:
                logging.error(f"Error fetching team {team_id}: {e}")
                self._my_team_data = None
        
        return self._my_team_data
    
    def get_top_players(self, by='points', limit=5):
        df = self.get_players()
        if df.empty:
            return pd.DataFrame()
        
        column_map = {'points': 'total_points', 'form': 'form', 'value': 'value_score'}
        column = column_map.get(by, 'total_points')
        
        if column in df.columns:
            return df.nlargest(limit, column)
        return df.head(limit)
    
    def clear_cache(self):
        self._players_df = None
        self._teams_df = None
        self._fixtures_df = None
        self._my_team_data = None


class FPLApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.data_service = FPLDataService()
        self.current_view = "dashboard"
        self.team_id = None  # Will be set by user import
        self.is_loading = False
        self.loading_indicator = None
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
        
        # Build UI
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI with production features and mobile-first design"""
        # Loading indicator
        self.loading_indicator = ft.ProgressBar(visible=False, color=PLTheme.ACCENT)
        
        # App bar with branding
        self.page.appbar = ft.AppBar(
            title=ft.Row(
                [
                    ft.Text("⚽", size=24),
                    ft.Text("FPL Analytics", weight=ft.FontWeight.BOLD, size=Typography.HEADING_3, color=PLTheme.ON_SURFACE),
                ],
                spacing=Spacing.SM,
            ),
            center_title=False,
            bgcolor=PLTheme.PRIMARY,
            toolbar_height=56,
        )
        
        # Top navigation using simple Row (tabs API varies by Flet version)
        self.tab_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text("📊 Dashboard", size=14, color=PLTheme.ON_SURFACE),
                        padding=Spacing.MD,
                        on_click=lambda e: self.load_view("dashboard"),
                        ink=True,
                        border=ft.Border(bottom=ft.BorderSide(2, PLTheme.ACCENT)) if self.current_view == "dashboard" else None,
                    ),
                    ft.Container(
                        content=ft.Text("👥 My Team", size=14, color=PLTheme.ON_SURFACE),
                        padding=Spacing.MD,
                        on_click=lambda e: self.load_view("my_team"),
                        ink=True,
                        border=ft.Border(bottom=ft.BorderSide(2, PLTheme.ACCENT)) if self.current_view == "my_team" else None,
                    ),
                    ft.Container(
                        content=ft.Text("📅 Fixtures", size=14, color=PLTheme.ON_SURFACE),
                        padding=Spacing.MD,
                        on_click=lambda e: self.load_view("fixtures"),
                        ink=True,
                        border=ft.Border(bottom=ft.BorderSide(2, PLTheme.ACCENT)) if self.current_view == "fixtures" else None,
                    ),
                    ft.Container(
                        content=ft.Text("💡 AI Tips", size=14, color=PLTheme.ON_SURFACE),
                        padding=Spacing.MD,
                        on_click=lambda e: self.load_view("ai_tips"),
                        ink=True,
                        border=ft.Border(bottom=ft.BorderSide(2, PLTheme.ACCENT)) if self.current_view == "ai_tips" else None,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            bgcolor=PLTheme.PRIMARY,
            height=48,
        )
        
        # Pull-to-refresh gesture wrapper
        self.content_container = ft.Container(
            expand=True,
            padding=Spacing.LG,
            bgcolor=PLTheme.BACKGROUND,
        )
        
        # Main content with pull-to-refresh
        self.refresh_container = ft.Column(
            [
                self.content_container,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            on_scroll=self.handle_scroll,
        )
        
        # Add to page
        self.page.add(
            ft.Column(
                [
                    self.loading_indicator,
                    self.tab_bar,
                    self.refresh_container,
                ],
                spacing=0,
                expand=True,
            )
        )
        
        # Load initial view
        self.load_view("dashboard")
    
    def handle_scroll(self, e):
        """Handle scroll events for pull-to-refresh"""
        # Pull-to-refresh: when scrolled to top and pulling down
        if hasattr(e, 'pixels') and e.pixels < -50 and not self.is_loading:
            self.refresh_data()
    
    def refresh_data(self, e=None):
        """Refresh all data from API"""
        logger.info("Refreshing data...")
        self.loading_indicator.visible = True
        self.loading_indicator.update()
        
        try:
            # Force refresh all data
            self.data_service.get_players(force_refresh=True)
            self.data_service.get_fixtures(force_refresh=True)
            if self.team_id:
                self.data_service.get_my_team(self.team_id, force_refresh=True)
            
            # Reload current view
            self.load_view(self.current_view)
            
            # Show success feedback
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Data refreshed successfully!", color=PLTheme.PRIMARY),
                bgcolor=PLTheme.ACCENT,
                action_color=PLTheme.PRIMARY,
            )
            self.page.snack_bar.open = True
            self.page.update()
            
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Refresh failed: {str(e)}", color=PLTheme.ON_SURFACE),
                bgcolor=PLTheme.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
        finally:
            self.loading_indicator.visible = False
            self.loading_indicator.update()
    
    def handle_navigation(self, e):
        """Handle bottom navigation changes"""
        views = ["dashboard", "my_team", "fixtures", "ai_tips"]
        selected_index = e.control.selected_index
        self.load_view(views[selected_index])
    
    def load_view(self, view_name):
        """Load the specified view with error handling"""
        self.current_view = view_name
        logger.info(f"Loading view: {view_name}")
        
        try:
            if view_name == "dashboard":
                content = self.build_dashboard()
            elif view_name == "my_team":
                content = self.build_my_team()
            elif view_name == "fixtures":
                content = self.build_fixtures()
            elif view_name == "ai_tips":
                content = self.build_ai_tips()
            else:
                content = ft.Container()
            
            self.content_container.content = content
            self.content_container.update()
            logger.info("View loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading view {view_name}: {e}")
            self.content_container.content = UIComponents.create_error_view(
                f"Failed to load {view_name}",
                retry_callback=lambda _: self.load_view(view_name)
            )
            self.content_container.update()
    
    def build_dashboard(self):
        """Build enhanced dashboard view with gameweek stats"""
        logger.info("Building dashboard...")
        
        # Show skeleton while loading
        players_df = self.data_service.get_players()
        if players_df.empty:
            # Show skeleton loading state
            skeleton_view = ft.Column(
                [
                    UIComponents.create_section_header("Dashboard", "📊"),
                    ft.Row(
                        [
                            UIComponents.create_skeleton_card(100),
                            UIComponents.create_skeleton_card(100),
                            UIComponents.create_skeleton_card(100),
                        ],
                        spacing=Spacing.MD,
                    ),
                    UIComponents.create_section_header("Top Players", "🏆"),
                    UIComponents.create_skeleton_list(8),
                ],
                spacing=Spacing.LG,
                scroll=ft.ScrollMode.AUTO,
            )
            
            # Try to load data, show error if fails
            try:
                players_df = self.data_service.get_players(force_refresh=True)
                if players_df.empty:
                    return UIComponents.create_error_view(
                        "Failed to load player data. Check your connection.",
                        retry_callback=lambda _: self.refresh_data()
                    )
            except:
                return skeleton_view
        
        # Get current gameweek from bootstrap data
        try:
            response = requests.get(f"{self.data_service.BASE_URL}/bootstrap-static/", timeout=10)
            bootstrap = response.json()
            events = bootstrap.get('events', [])
            current_gw = next((gw for gw in events if gw.get('is_current')), events[0] if events else {})
            gw_number = current_gw.get('id', 1)
            gw_avg = current_gw.get('average_entry_score', 0)
            gw_highest = current_gw.get('highest_score', 0)
        except:
            gw_number = 1
            gw_avg = 0
            gw_highest = 0
        
        # Create enhanced KPI cards with icons
        kpi_cards = ft.Row(
            [
                UIComponents.create_stat_card(
                    "Gameweek",
                    f"GW {gw_number}",
                    icon="📅",
                    color="#00ff00"
                ),
                UIComponents.create_stat_card(
                    "GW Average",
                    str(int(gw_avg)),
                    subtitle="pts",
                    icon="📈",
                    color="#ffd700"
                ),
                UIComponents.create_stat_card(
                    "GW Highest",
                    str(int(gw_highest)),
                    subtitle="pts",
                    icon="⭐",
                    color="#ff8c00"
                ),
            ],
            spacing=12,
        )
        
        # Get top players by points with additional stats
        top_players = players_df.nlargest(10, 'total_points')[[
            'web_name', 'total_points', 'now_cost', 'form', 
            'transfers_in_event', 'transfers_out_event', 'selected_by_percent'
        ]]
        
        # Build enhanced player list with new card components
        player_items = []
        for idx, player in top_players.iterrows():
            transfers_in = int(player.get('transfers_in_event', 0))
            transfers_out = int(player.get('transfers_out_event', 0))
            net_transfers = transfers_in - transfers_out
            transfer_color = "#00ff00" if net_transfers > 0 else "#ff0000" if net_transfers < 0 else "#9E9E9E"
            
            stats = [
                (f"£{player['now_cost']/10:.1f}m", f"{int(player['total_points'])} pts", "#FFFFFF"),
                (f"Form {float(player['form']):.1f}", f"{float(player['selected_by_percent']):.1f}% owned", "#BDBDBD"),
                (f"Net: {net_transfers:+d}", "", transfer_color),
            ]
            
            player_items.append(
                UIComponents.create_player_card(
                    player['web_name'],
                    stats,
                    icon=f"{idx+1}.",
                    highlight=(idx < 3)  # Highlight top 3
                )
            )
        
        return ft.Column(
            [
                UIComponents.create_section_header("Dashboard", "📊"),
                kpi_cards,
                UIComponents.create_section_header("Top 10 Players", "🏆"),
                ft.Column(player_items, spacing=0),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def build_kpi_card(self, title, value, icon):
        """Build accessible KPI card with proper hierarchy"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=36, color="green", semantics_label=f"{title} icon"),
                    ft.Container(height=8),
                    ft.Text(
                        value,
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color="#FFFFFF",
                    ),
                    ft.Text(
                        title,
                        size=13,
                        color="#BDBDBD",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                tight=True,
            ),
            padding=20,
            border_radius=16,
            bgcolor="surfacevariant",
            expand=True,
            height=140,
            ink=True,
        )
    
    def build_top_players_list(self):
        """Build accessible top players list with proper touch targets"""
        top_players = self.data_service.get_top_players(by='points', limit=5)
        
        if top_players.empty:
            return ft.Container(
                content=ft.Text("No player data available", color="#BDBDBD", italic=True),
                padding=16,
            )
        
        tiles = []
        for idx, player in top_players.iterrows():
            rank_color = "green" if idx < 3 else "grey"
            tiles.append(
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Container(
                            ft.Text(
                                str(idx + 1),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=rank_color,
                            ),
                            width=36,
                            height=36,
                            border_radius=18,
                            bgcolor=f"{rank_color}12" if idx < 3 else None,
                            alignment=ft.alignment.Alignment(0, 0),
                        ),
                        title=ft.Text(
                            player.get('web_name', 'Unknown'),
                            weight=ft.FontWeight.W_500,
                            color="#FFFFFF",
                        ),
                        subtitle=ft.Text(
                            f"£{player.get('now_cost', 0) / 10:.1f}m • {player.get('total_points', 0)} pts",
                            size=13,
                            color="#BDBDBD",
                        ),
                        trailing=ft.Icon("chevron_right", color="#BDBDBD"),
                    ),
                    border_radius=12,
                    ink=True,
                    on_click=lambda e, p=player: None,  # Placeholder for player detail
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ft.Row(
                            [
                                ft.Icon("emoji_events", size=20, color="amber"),
                                ft.Container(width=8),
                                ft.Text(
                                    "Top Players by Points",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                            ],
                        ),
                        padding=ft.Padding(16, 16, 16, 8),
                    ),
                    ft.Column(tiles, spacing=4),
                ],
                spacing=0,
            ),
            padding=ft.Padding(0, 0, 0, 16),
        )
    
    def build_my_team(self):
        """Build My Team view with team import functionality"""
        
        # Team import section
        if self.team_id_input is None:
            self.team_id_input = ft.TextField(
                label="Enter your FPL Team ID",
                hint_text="e.g., 1437667",
                width=300,
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor="#2d2d2d",
                border_color="#00ff00",
                color="#FFFFFF",
            )
        
        if self.import_status_text is None:
            self.import_status_text = ft.Text("", size=14, color="#BDBDBD")
        
        import_section = ft.Container(
            content=ft.Column(
                [
                    UIComponents.create_section_header("Import Your Team", "⬇️"),
                    ft.Row(
                        [
                            self.team_id_input,
                            ft.FilledButton(
                                "Import Team",
                                on_click=self.import_team,
                                style=ft.ButtonStyle(
                                    bgcolor=PLTheme.ACCENT,
                                    color=PLTheme.PRIMARY,
                                ),
                            ),
                        ],
                        spacing=Spacing.SM,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    self.import_status_text,
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("How to find your Team ID:", size=12, color="#BDBDBD", weight=ft.FontWeight.BOLD),
                                ft.Text("1. Go to fantasy.premierleague.com", size=11, color="#9E9E9E"),
                                ft.Text("2. Click 'Points' or 'My Team'", size=11, color="#9E9E9E"),
                                ft.Text("3. Look at the URL - the number after 'entry/' is your Team ID", size=11, color="#9E9E9E"),
                                ft.Text("   Example: fantasy.premierleague.com/entry/1437667/event/20", size=11, color="#9E9E9E"),
                            ],
                            spacing=4,
                        ),
                        bgcolor=PLTheme.SURFACE,
                        padding=Spacing.MD,
                        border_radius=8,
                        margin=ft.Margin(top=Spacing.SM, left=0, right=0, bottom=0),
                    ),
                ],
                spacing=Spacing.MD,
            ),
            padding=Spacing.LG,
            bgcolor=PLTheme.SURFACE,
            border_radius=12,
            margin=ft.Margin(bottom=Spacing.LG, left=0, right=0, top=0),
        )
        
        # If no team imported yet, show only import section
        if self.team_id is None:
            return ft.Column(
                [
                    UIComponents.create_section_header("My Team", "👥"),
                    import_section,
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )
        
        # Fetch team data
        team_data = self.data_service.get_my_team(self.team_id)
        players_df = self.data_service.get_players()
        
        if team_data is None or players_df.empty:
            return ft.Column(
                [
                    UIComponents.create_section_header("My Team", "👥"),
                    import_section,
                    UIComponents.create_error_view(
                        "Failed to load team data. Check your Team ID and try again.",
                        retry_callback=lambda _: self.load_view("my_team")
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )
        
        team_info = team_data['team_info']
        picks = team_data['picks'].get('picks', [])
        
        # Team name and stats cards
        team_name = team_info.get('name', 'My Team')
        manager_name = f"{team_info.get('player_first_name', '')} {team_info.get('player_last_name', '')}".strip()
        
        team_header = ft.Container(
            content=ft.Column(
                [
                    ft.Text(team_name, size=24, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Text(f"Manager: {manager_name}", size=14, color="#BDBDBD"),
                    ft.Text(f"Team ID: {self.team_id}", size=12, color="#9E9E9E"),
                ],
                spacing=4,
            ),
            padding=Spacing.LG,
            bgcolor=PLTheme.SURFACE,
            border_radius=12,
            margin=ft.Margin(bottom=Spacing.MD, left=0, right=0, top=0),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color="#00000040",
                offset=ft.Offset(0, 2),
            ),
        )
        
        stats = ft.Row(
            [
                UIComponents.create_stat_card(
                    "Overall Rank",
                    f"{team_info.get('summary_overall_rank', 0):,}",
                    icon="🏆",
                ),
                UIComponents.create_stat_card(
                    "Total Points",
                    str(team_info.get('summary_overall_points', 0)),
                    icon="⚽",
                ),
                UIComponents.create_stat_card(
                    "Team Value",
                    f"£{team_info.get('last_deadline_value', 0) / 10:.1f}m",
                    icon="💰",
                ),
            ],
            spacing=12,
        )
        
        # Squad players with enhanced data
        squad_items = []
        starting_11 = picks[:11]
        bench = picks[11:15]
        
        # Starting XI
        squad_items.append(ft.Text("Starting XI", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"))
        for pick in starting_11:
            player_id = pick.get('element')
            player_data = players_df[players_df['id'] == player_id]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                is_captain = pick.get('is_captain', False)
                is_vice = pick.get('is_vice_captain', False)
                
                # Position type
                pos_type = player.get('element_type', 1)
                pos_names = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                position = pos_names.get(pos_type, '???')
                
                squad_items.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            "⭐" if is_captain else "🔶" if is_vice else "⚽",
                                            size=16,
                                        ),
                                        ft.Text(
                                            player.get('web_name', 'Unknown'),
                                            size=16,
                                            color="#FFFFFF",
                                            expand=True,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            f"{player.get('total_points', 0)} pts",
                                            size=14,
                                            color="#FFFFFF",
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    [
                                        ft.Text(f"  {position}", size=12, color="#BDBDBD"),
                                        ft.Text("•", size=12, color="#BDBDBD"),
                                        ft.Text(f"£{player.get('now_cost', 0)/10:.1f}m", size=12, color="#BDBDBD"),
                                        ft.Text("•", size=12, color="#BDBDBD"),
                                        ft.Text(f"Form {float(player.get('form', 0)):.1f}", size=12, color="#BDBDBD"),
                                        ft.Text("•", size=12, color="#BDBDBD"),
                                        ft.Text(f"Next: GW{player.get('event_points', 0)}", size=12, color="#BDBDBD"),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=4,
                        ),
                        padding=10,
                        border=ft.Border(bottom=ft.BorderSide(1, "#333333")),
                    )
                )
        
        # Bench
        squad_items.append(ft.Text("Bench", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"))
        for pick in bench:
            player_id = pick.get('element')
            player_data = players_df[players_df['id'] == player_id]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                pos_type = player.get('element_type', 1)
                pos_names = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                position = pos_names.get(pos_type, '???')
                
                squad_items.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(position, size=14, color="#9E9E9E"),
                                ft.Text(
                                    player.get('web_name', 'Unknown'),
                                    size=14,
                                    color="#9E9E9E",
                                    expand=True,
                                ),
                                ft.Text(
                                    f"£{player.get('now_cost', 0)/10:.1f}m",
                                    size=12,
                                    color="#9E9E9E",
                                ),
                            ],
                            spacing=Spacing.SM,
                        ),
                        padding=Spacing.SM,
                        border=ft.Border(
                            bottom=ft.BorderSide(1, PLTheme.DIVIDER),
                        ),
                    )
                )
        
        return ft.Column(
            [
                UIComponents.create_section_header("My Team", "👥"),
                import_section,
                team_header,
                stats,
                UIComponents.create_section_header("Squad", "⚽"),
                ft.Column(squad_items, spacing=0),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def import_team(self, e):
        """Import team data based on user input"""
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
            team_data = self.data_service.get_my_team(team_id, force_refresh=True)
            
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
            logger.info(f"Successfully imported team {team_id}")
            self.load_view("my_team")
            
        except ValueError:
            self.import_status_text.value = "❌ Invalid Team ID. Please enter numbers only."
            self.import_status_text.color = "#ff0000"
            self.import_status_text.update()
        except Exception as ex:
            logger.error(f"Error importing team: {ex}")
            self.import_status_text.value = f"❌ Error: {str(ex)}"
            self.import_status_text.color = "#ff0000"
            self.import_status_text.update()
    
    def build_my_team_old(self):
        """Build My Team view with accessible input - OLD VERSION"""
        if self.team_id is None:
            # Team ID input screen
            team_id_input = ft.TextField(
                label="FPL Team ID",
                hint_text="Enter your 7-digit team ID",
                keyboard_type=ft.KeyboardType.NUMBER,
                autofocus=True,
                max_length=7,
                border_radius=12,
                text_size=16,
                helper_text="Find it on the FPL website under 'Points' page",
            )
            
            def save_team_id(e):
                if not team_id_input.value or not team_id_input.value.strip():
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("Please enter your team ID"),
                            bgcolor="error",
                        )
                    )
                    return
                
                try:
                    self.team_id = int(team_id_input.value.strip())
                    self.load_view("my_team")
                except ValueError:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("Please enter a valid number"),
                            bgcolor="error",
                        )
                    )
            
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon("sports_soccer", size=80, color="green"),
                        ft.Container(height=16),
                        ft.Text(
                            "My FPL Team",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                            color="#FFFFFF",
                        ),
                        ft.Text(
                            "Enter your team ID to view your squad and stats",
                            color="#BDBDBD",
                            text_align=ft.TextAlign.CENTER,
                            size=15,
                        ),
                        ft.Container(height=32),
                        team_id_input,
                        ft.Container(height=16),
                        ft.FilledButton(
                            "Load My Team",
                            icon="login",
                            on_click=save_team_id,
                            width=280,
                            height=48,
                        ),
                        ft.Container(height=16),
                        ft.TextButton(
                            "How to find your team ID?",
                            icon="help_outline",
                            on_click=lambda e: self.page.show_snack_bar(
                                ft.SnackBar(
                                    content=ft.Text(
                                        "Go to fantasy.premierleague.com, click 'Points', your ID is in the URL"
                                    ),
                                    duration=5000,
                                )
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=32,
                expand=True,
            )
        
        # Load team data
        team_data = self.data_service.get_my_team(self.team_id)
        
        if team_data is None:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon("error_outline", size=64, color="red"),
                        ft.Text("Failed to load team", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        ft.Text("Check your team ID and connection", color="#BDBDBD"),
                        ft.ElevatedButton("Try Again", on_click=lambda e: self.load_view("my_team")),
                        ft.TextButton("Change Team ID", on_click=lambda e: setattr(self, 'team_id', None) or self.load_view("my_team")),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=32,
                expand=True,
            )
        
        # Display team
        team_info = team_data['team_info']
        picks_data = team_data['picks']
        
        # Team stats
        stats_row = ft.Row(
            [
                self.build_stat_card("Rank", f"{team_info.get('summary_overall_rank', 0):,}"),
                self.build_stat_card("Points", str(team_info.get('summary_overall_points', 0))),
                self.build_stat_card("Value", f"£{team_info.get('last_deadline_value', 0) / 10:.1f}m"),
            ],
            spacing=8,
        )
        
        # Squad list with position indicators
        players_df = self.data_service.get_players()
        picks = picks_data.get('picks', [])
        
        # Position mapping for better UX
        position_icons = {
            1: ("sports_soccer", "GK"),
            2: ("shield", "DEF"),
            3: ("speed", "MID"),
            4: ("whatshot", "FWD"),
        }
        
        squad_tiles = []
        for pick in picks[:11]:  # Starting XI
            player_id = pick.get('element')
            player_data = players_df[players_df['id'] == player_id]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                pos = pick.get('position', 1)
                icon, pos_label = position_icons.get(pos, ("person", "???"))
                
                squad_tiles.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(icon, size=20, color="green"),
                                        ft.Text(
                                            pos_label,
                                            size=10,
                                            weight=ft.FontWeight.BOLD,
                                            color="#BDBDBD",
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                    tight=True,
                                ),
                                width=48,
                            ),
                            title=ft.Text(
                                player.get('web_name', 'Unknown'),
                                weight=ft.FontWeight.W_500,
                                color="#FFFFFF",
                            ),
                            subtitle=ft.Text(
                                f"£{player.get('now_cost', 0) / 10:.1f}m • {player.get('total_points', 0)} pts",
                                size=13,
                                color="#BDBDBD",
                            ),
                            trailing=ft.Row(
                                [
                                    ft.Icon(
                                        "stars",
                                        color="amber",
                                        size=20,
                                        tooltip="Captain",
                                    ) if pick.get('is_captain') else ft.Container(width=0),
                                    ft.Icon(
                                        "chevron_right",
                                        color="#BDBDBD",
                                        size=20,
                                    ),
                                ],
                                spacing=4,
                                tight=True,
                            ),
                        ),
                        border_radius=12,
                        ink=True,
                    )
                )
        
        return ft.Container(
            content=ft.ListView(
                [
                    ft.Container(
                        ft.Text(f"{team_info.get('name', 'My Team')}", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        padding=ft.Padding(16, 16, 16, 8),
                    ),
                    ft.Container(stats_row, padding=16),
                    ft.Divider(height=1, thickness=1),
                    ft.Container(
                        ft.Text("Starting XI", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        padding=ft.Padding(16, 8, 16, 4),
                    ),
                    ft.Column(squad_tiles, spacing=4),
                ],
                padding=0,
                spacing=8,
            ),
            expand=True,
        )
    
    def build_fixtures(self):
        """Build comprehensive Fixture Analysis view"""
        fixtures_df = self.data_service.get_fixtures()
        teams_df = self.data_service.get_teams()
        players_df = self.data_service.get_players()
        
        if fixtures_df.empty or teams_df.empty:
            return ft.Column(
                [
                    ft.Text("Fixture Analysis", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Text("Loading fixtures...", size=16, color="#BDBDBD"),
                ],
                spacing=20,
            )
        
        # Create team map with full stats
        team_map = {team['id']: {
            'name': team['short_name'],
            'strength': team.get('strength', 3),
            'strength_attack_home': team.get('strength_attack_home', 0),
            'strength_attack_away': team.get('strength_attack_away', 0),
            'strength_defence_home': team.get('strength_defence_home', 0),
            'strength_defence_away': team.get('strength_defence_away', 0),
        } for _, team in teams_df.iterrows()}
        
        # Get upcoming fixtures
        upcoming = fixtures_df[fixtures_df['finished'] == False].head(10)
        
        # Difficulty colors
        difficulty_colors = {1: "#00ff00", 2: "#90ee90", 3: "#ffd700", 4: "#ff8c00", 5: "#ff0000"}
        
        # Build fixture analysis cards
        fixture_items = []
        for _, fixture in upcoming.iterrows():
            home_id = fixture['team_h']
            away_id = fixture['team_a']
            home_team = team_map.get(home_id, {})
            away_team = team_map.get(away_id, {})
            
            home_name = home_team.get('name', 'TBD')
            away_name = away_team.get('name', 'TBD')
            h_diff = int(fixture.get('team_h_difficulty', 3))
            a_diff = int(fixture.get('team_a_difficulty', 3))
            
            # Attack and defense strengths
            home_att = home_team.get('strength_attack_home', 0)
            home_def = home_team.get('strength_defence_home', 0)
            away_att = away_team.get('strength_attack_away', 0)
            away_def = away_team.get('strength_defence_away', 0)
            
            fixture_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            # Match header
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(home_name, size=16, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                                        bgcolor=difficulty_colors.get(h_diff, "#9E9E9E"),
                                        padding=8,
                                        border_radius=5,
                                        expand=True,
                                    ),
                                    ft.Text("vs", size=14, color="#BDBDBD"),
                                    ft.Container(
                                        content=ft.Text(away_name, size=16, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                                        bgcolor=difficulty_colors.get(a_diff, "#9E9E9E"),
                                        padding=8,
                                        border_radius=5,
                                        expand=True,
                                    ),
                                ],
                                spacing=5,
                            ),
                            # Team stats
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(f"⚔️ {home_att}", size=12, color="#BDBDBD"),
                                            ft.Text(f"🛡️ {home_def}", size=12, color="#BDBDBD"),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                    ft.Container(width=40),
                                    ft.Column(
                                        [
                                            ft.Text(f"⚔️ {away_att}", size=12, color="#BDBDBD"),
                                            ft.Text(f"🛡️ {away_def}", size=12, color="#BDBDBD"),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                ],
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=12,
                    bgcolor="#1a1a1a",
                    border_radius=10,
                    margin=ft.Margin(bottom=8),
                )
            )
        
        # Calculate fixture difficulty for next 5 gameweeks per team
        fdr_items = []
        for team_id, team_info in list(team_map.items())[:8]:  # Show top 8 teams
            team_name = team_info['name']
            team_fixtures = fixtures_df[
                ((fixtures_df['team_h'] == team_id) | (fixtures_df['team_a'] == team_id)) & 
                (fixtures_df['finished'] == False)
            ].head(5)
            
            difficulties = []
            for _, fix in team_fixtures.iterrows():
                if fix['team_h'] == team_id:
                    diff = int(fix.get('team_h_difficulty', 3))
                else:
                    diff = int(fix.get('team_a_difficulty', 3))
                difficulties.append(diff)
            
            # Fill with neutral if less than 5
            while len(difficulties) < 5:
                difficulties.append(3)
            
            # Average difficulty
            avg_diff = sum(difficulties) / len(difficulties)
            
            fdr_items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(team_name, size=14, color="#FFFFFF", expand=True),
                            ft.Row(
                                [
                                    ft.Container(
                                        width=8,
                                        height=20,
                                        bgcolor=difficulty_colors.get(d, "#9E9E9E"),
                                        border_radius=2,
                                    ) for d in difficulties
                                ],
                                spacing=2,
                            ),
                            ft.Text(f"{avg_diff:.1f}", size=14, color="#BDBDBD"),
                        ],
                        spacing=10,
                    ),
                    padding=10,
                    border=ft.Border(bottom=ft.BorderSide(1, "#333333")),
                )
            )
        
        return ft.Column(
            [
                ft.Text("Fixture Analysis", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Text("🟢Easy 🟡Medium 🔴Hard | ⚔️Attack 🛡️Defense", size=12, color="#BDBDBD"),
                ft.Text("Next 10 Fixtures", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Column(fixture_items, spacing=0),
                ft.Text("Fixture Difficulty (Next 5 GWs)", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Column(fdr_items, spacing=0),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def build_fixtures_old(self):
        """Build Fixtures Analysis view - OLD VERSION"""
        fixtures_df = self.data_service.get_fixtures()
        teams_df = self.data_service.get_teams()
        
        if fixtures_df.empty or teams_df.empty:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon("calendar_month", size=64, color="#9E9E9E"),
                        ft.Text("Loading fixtures...", size=20),
                        ft.ProgressRing(),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                expand=True,
            )
        
        # Get upcoming fixtures (not finished)
        upcoming = fixtures_df[fixtures_df['finished'] == False].head(10)
        
        # Difficulty color mapping for better visual feedback
        def get_fdr_color(fdr):
            if fdr <= 2:
                return "green"
            elif fdr == 3:
                return "grey"
            else:
                return "red"
        
        fixture_tiles = []
        for _, fixture in upcoming.iterrows():
            home_team = teams_df[teams_df['id'] == fixture['team_h']].iloc[0] if not teams_df[teams_df['id'] == fixture['team_h']].empty else None
            away_team = teams_df[teams_df['id'] == fixture['team_a']].iloc[0] if not teams_df[teams_df['id'] == fixture['team_a']].empty else None
            
            if home_team is not None and away_team is not None:
                home_fdr = fixture.get('team_h_difficulty', 3)
                away_fdr = fixture.get('team_a_difficulty', 3)
                
                fixture_tiles.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Container(
                                ft.Text(
                                    f"GW{fixture.get('event', '?')}",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color="green",
                                ),
                                width=48,
                                padding=8,
                                border_radius=8,
                                bgcolor="green12",
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                            title=ft.Text(
                                f"{home_team['short_name']} vs {away_team['short_name']}",
                                weight=ft.FontWeight.W_500,
                                color="#FFFFFF",
                            ),
                            subtitle=ft.Text(
                                f"{home_team['name']} (H) • {away_team['name']} (A)",
                                size=12,
                                color="#BDBDBD",
                            ),
                            trailing=ft.Row(
                                [
                                    ft.Container(
                                        ft.Text(
                                            str(home_fdr),
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color="#FFFFFF",
                                        ),
                                        bgcolor=get_fdr_color(home_fdr),
                                        width=28,
                                        height=28,
                                        border_radius=14,
                                        alignment=ft.alignment.Alignment(0, 0),
                                        tooltip=f"Home difficulty: {home_fdr}",
                                    ),
                                    ft.Text(":", size=16, color="#9E9E9E"),
                                    ft.Container(
                                        ft.Text(
                                            str(away_fdr),
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color="#FFFFFF",
                                        ),
                                        bgcolor=get_fdr_color(away_fdr),
                                        width=28,
                                        height=28,
                                        border_radius=14,
                                        alignment=ft.alignment.Alignment(0, 0),
                                        tooltip=f"Away difficulty: {away_fdr}",
                                    ),
                                ],
                                spacing=6,
                                tight=True,
                            ),
                        ),
                        border_radius=12,
                        ink=True,
                        margin=ft.Margin(bottom=4),
                    )
                )
        
        return ft.Container(
            content=ft.ListView(
                [
                    ft.Container(
                        ft.Column(
                            [
                                ft.Text("Upcoming Fixtures", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                ft.Text("Plan your transfers around fixture difficulty", size=14, color="#BDBDBD"),
                            ],
                            spacing=4,
                        ),
                        padding=ft.Padding(16, 16, 16, 8),
                    ),
                    ft.Container(
                        ft.Row(
                            [
                                ft.Icon("info_outline", size=16, color="#BDBDBD"),
                                ft.Container(width=8),
                                ft.Text("FDR: ", size=12, color="#BDBDBD", weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    ft.Text("1-2", size=11, color="#FFFFFF"),
                                    bgcolor="green",
                                    padding=4,
                                    border_radius=4,
                                ),
                                ft.Text("Easy", size=12, color="#BDBDBD"),
                                ft.Container(width=8),
                                ft.Container(
                                    ft.Text("3", size=11, color="#FFFFFF"),
                                    bgcolor="#9E9E9E",
                                    padding=4,
                                    border_radius=4,
                                ),
                                ft.Text("Medium", size=12, color="#BDBDBD"),
                                ft.Container(width=8),
                                ft.Container(
                                    ft.Text("4-5", size=11, color="#FFFFFF"),
                                    bgcolor="red",
                                    padding=4,
                                    border_radius=4,
                                ),
                                ft.Text("Hard", size=12, color="#BDBDBD"),
                            ],
                        ),
                        padding=ft.Padding(16, 0, 16, 12),
                    ),
                    ft.Column(fixture_tiles, spacing=0),
                ],
                padding=0,
                spacing=8,
            ),
            expand=True,
        )
    
    def build_ai_tips(self):
        """Build AI Tips with transfer suggestions and captain picks"""
        players_df = self.data_service.get_players()
        
        if players_df.empty:
            return ft.Column(
                [
                    ft.Text("AI Tips", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Text("Loading recommendations...", size=16, color="#BDBDBD"),
                ],
                spacing=20,
            )
        
        # Convert form to float for sorting
        players_df['form_float'] = pd.to_numeric(players_df['form'], errors='coerce').fillna(0)
        
        # Captain picks - top form players with detailed stats
        captain_picks = players_df[players_df['form_float'] > 0].nlargest(5, 'form_float')[['web_name', 'form', 'total_points', 'now_cost', 'selected_by_percent']]
        captain_items = []
        for idx, player in captain_picks.iterrows():
            captain_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("⭐", size=16),
                                    ft.Text(player['web_name'], size=16, color="#FFFFFF", expand=True, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{int(player['total_points'])} pts", size=14, color="#FFFFFF"),
                                ],
                            ),
                            ft.Row(
                                [
                                    ft.Text(f"  Form {float(player['form']):.1f}", size=12, color="#00ff00"),
                                    ft.Text("•", size=12, color="#BDBDBD"),
                                    ft.Text(f"£{player['now_cost']/10:.1f}m", size=12, color="#BDBDBD"),
                                    ft.Text("•", size=12, color="#BDBDBD"),
                                    ft.Text(f"{float(player['selected_by_percent']):.1f}% owned", size=12, color="#BDBDBD"),
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=10,
                    border=ft.Border(bottom=ft.BorderSide(1, "#333333")),
                )
            )
        
        # Best value transfers - form/price ratio with transfers data
        best_value = players_df.nlargest(5, 'value_score')[['web_name', 'price', 'total_points', 'form_float', 'transfers_in_event']]
        transfer_items = []
        for idx, player in best_value.iterrows():
            transfers_in = int(player.get('transfers_in_event', 0))
            transfer_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("💰", size=16),
                                    ft.Text(player['web_name'], size=16, color="#FFFFFF", expand=True, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"£{player['price']:.1f}m", size=14, color="#FFFFFF"),
                                ],
                            ),
                            ft.Row(
                                [
                                    ft.Text(f"  {int(player['total_points'])} pts", size=12, color="#BDBDBD"),
                                    ft.Text("•", size=12, color="#BDBDBD"),
                                    ft.Text(f"Form {player['form_float']:.1f}", size=12, color="#00ff00"),
                                    ft.Text("•", size=12, color="#BDBDBD"),
                                    ft.Text(f"🔥 {transfers_in:,} in", size=12, color="#ff8c00"),
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=10,
                    border=ft.Border(bottom=ft.BorderSide(1, "#333333")),
                )
            )
        
        # Differentials - low ownership, high points with more details
        players_df['ownership_float'] = pd.to_numeric(players_df['selected_by_percent'], errors='coerce').fillna(100)
        differentials = players_df[players_df['ownership_float'] < 5]
        if not differentials.empty:
            differentials = differentials.nlargest(5, 'total_points')[['web_name', 'selected_by_percent', 'total_points', 'now_cost', 'form_float']]
            diff_items = []
            for idx, player in differentials.iterrows():
                diff_items.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("🎯", size=16),
                                        ft.Text(player['web_name'], size=16, color="#FFFFFF", expand=True, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"{int(player['total_points'])} pts", size=14, color="#FFFFFF"),
                                    ],
                                ),
                                ft.Row(
                                    [
                                        ft.Text(f"  {float(player['selected_by_percent']):.1f}% owned", size=12, color="#ffd700"),
                                        ft.Text("•", size=12, color="#BDBDBD"),
                                        ft.Text(f"£{player['now_cost']/10:.1f}m", size=12, color="#BDBDBD"),
                                        ft.Text("•", size=12, color="#BDBDBD"),
                                        ft.Text(f"Form {player['form_float']:.1f}", size=12, color="#BDBDBD"),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=4,
                        ),
                        padding=10,
                        border=ft.Border(bottom=ft.BorderSide(1, "#333333")),
                    )
                )
        else:
            diff_items = []
        
        return ft.Column(
            [
                ft.Text("AI Recommendations", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Text("Captain Picks", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Column(captain_items, spacing=0),
                ft.Text("Best Value Transfers", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Column(transfer_items, spacing=0),
                ft.Text("Differentials (< 5% owned)", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Column(diff_items, spacing=0) if diff_items else ft.Text("No differentials available", size=14, color="#BDBDBD"),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def build_ai_tips_old(self):
        """Build AI Recommendations view - OLD VERSION"""
        players_df = self.data_service.get_players()
        
        if players_df.empty:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon("psychology", size=64, color="#9E9E9E"),
                        ft.Text("Loading AI insights...", size=20),
                        ft.ProgressRing(),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                expand=True,
            )
        
        # Simple AI recommendations based on form and value
        # High form players
        in_form = players_df[players_df['form'].astype(float) > 5].nlargest(5, 'form')
        
        # Best value players (high points per million)
        value_picks = players_df.nlargest(5, 'value_score')
        
        # Differentials (low ownership, high points)
        differentials = players_df[
            (players_df['selected_by_percent'].astype(float) < 5) &
            (players_df['total_points'] > 50)
        ].nlargest(5, 'total_points')
        
        def build_recommendation_section(title, df, icon, description):
            """Build recommendation section with proper hierarchy"""
            if df.empty:
                tiles = [
                    ft.Container(
                        ft.Text("No recommendations available", color="#BDBDBD", italic=True),
                        padding=16,
                    )
                ]
            else:
                tiles = []
                for idx, player in df.iterrows():
                    tiles.append(
                        ft.Container(
                            content=ft.ListTile(
                                leading=ft.Container(
                                    ft.Icon(icon, color="green", size=24),
                                    width=40,
                                    height=40,
                                    border_radius=20,
                                    bgcolor="green12",
                                    alignment=ft.alignment.Alignment(0, 0),
                                ),
                                title=ft.Text(
                                    player.get('web_name', 'Unknown'),
                                    weight=ft.FontWeight.W_500,
                                    color="#FFFFFF",
                                ),
                                subtitle=ft.Text(
                                    f"£{player.get('now_cost', 0) / 10:.1f}m • Form: {player.get('form', 0)} • Own: {player.get('selected_by_percent', 0)}%",
                                    size=12,
                                    color="#BDBDBD",
                                ),
                                trailing=ft.Column(
                                    [
                                        ft.Text(
                                            f"{player.get('total_points', 0)}",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color="green",
                                        ),
                                        ft.Text("pts", size=10, color="#BDBDBD"),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=0,
                                    tight=True,
                                ),
                            ),
                            border_radius=12,
                            ink=True,
                            margin=ft.Margin(bottom=4),
                        )
                    )
            
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    ft.Text(description, size=13, color="#BDBDBD"),
                                ],
                                spacing=4,
                            ),
                            padding=ft.Padding(16, 16, 16, 8),
                        ),
                        ft.Column(tiles, spacing=0),
                    ],
                    spacing=0,
                ),
                margin=ft.Margin(bottom=8),
            )
        
        return ft.Container(
            content=ft.ListView(
                [
                    ft.Container(
                        ft.Column(
                            [
                                ft.Text(
                                    "AI Recommendations",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    "Smart picks based on form, value, and ownership",
                                    size=14,
                                    color="#BDBDBD",
                                ),
                            ],
                            spacing=4,
                        ),
                        padding=ft.Padding(16, 16, 16, 8),
                    ),
                    build_recommendation_section(
                        "🔥 In Form Players",
                        in_form,
                        "trending_up",
                        "Players with exceptional recent performance",
                    ),
                    ft.Divider(height=1, thickness=1, color="grey800"),
                    build_recommendation_section(
                        "💎 Best Value Picks",
                        value_picks,
                        "payments",
                        "Maximum points per million spent",
                    ),
                    ft.Divider(height=1, thickness=1, color="grey800"),
                    build_recommendation_section(
                        "🎯 Differential Options",
                        differentials,
                        "psychology",
                        "Low ownership gems for rank climbing",
                    ),
                    ft.Container(height=16),
                ],
                padding=0,
                spacing=8,
            ),
            expand=True,
        )
    
    def build_stat_card(self, label, value):
        """Helper to build accessible stat cards"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        value,
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color="#FFFFFF",
                    ),
                    ft.Text(
                        label,
                        size=12,
                        color="#BDBDBD",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                tight=True,
            ),
            padding=16,
            border_radius=12,
            bgcolor="surfacevariant",
            expand=True,
        )
    
    def refresh_data(self, e):
        self.page.splash = ft.ProgressBar()
        self.page.update()
        
        self.data_service.clear_cache()
        self.page.clean()
        self.build_ui()
        
        self.page.splash = None
        self.page.update()
        
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Data refreshed!")))


def main(page: ft.Page):
    try:
        FPLApp(page)
    except Exception as e:
        logging.exception("Error starting app")
        page.add(ft.Text(f"Error: {e}", color="red"))


if __name__ == "__main__":
    ft.run(main)
