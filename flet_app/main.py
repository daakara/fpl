"""
FPL Analytics - Flet Mobile App
Main entry point for iOS/Android native application
"""

import flet as ft
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
        
        # Configure page
        self.page.title = "FPL Analytics"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = get_app_theme(dark=True)
        self.page.padding = 0
        
        # Initialize pages
        self.dashboard = DashboardPage(self.data_service)
        self.player_analysis = PlayerAnalysisPage(self.data_service)
        self.team_builder = TeamBuilderPage(self.data_service)
        self.learning = LearningResourcesPage()
        
        # Navigation state
        self.current_page = "dashboard"
        
        # Build UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI with navigation"""
        # App bar
        self.page.appbar = ft.AppBar(
            title=ft.Text("FPL Analytics", weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(
                    icon=ft.icons.REFRESH,
                    tooltip="Refresh Data",
                    on_click=self.refresh_data
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Dark Mode",
                            checked=True,
                            on_click=self.toggle_theme
                        ),
                        ft.PopupMenuItem(),  # Divider
                        ft.PopupMenuItem(text="About"),
                    ]
                )
            ],
        )
        
        # Content area
        self.content_area = ft.Container(
            content=self.dashboard.build(),
            expand=True,
        )
        
        # Bottom navigation
        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(
                    icon=ft.icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.icons.DASHBOARD,
                    label="Dashboard"
                ),
                ft.NavigationDestination(
                    icon=ft.icons.PERSON_SEARCH_OUTLINED,
                    selected_icon=ft.icons.PERSON_SEARCH,
                    label="Players"
                ),
                ft.NavigationDestination(
                    icon=ft.icons.GROUPS_OUTLINED,
                    selected_icon=ft.icons.GROUPS,
                    label="Team Builder"
                ),
                ft.NavigationDestination(
                    icon=ft.icons.SCHOOL_OUTLINED,
                    selected_icon=ft.icons.SCHOOL,
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
            e.control.checked = False
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.page.theme = get_app_theme(dark=True)
            e.control.checked = True
        
        self.page.update()


def main(page: ft.Page):
    """Main entry point for Flet app"""
    FPLAnalyticsApp(page)


if __name__ == "__main__":
    # Run as desktop app for testing
    ft.app(target=main)
    
    # For mobile deployment, use:
    # ft.app(target=main, view=ft.AppView.FLET_APP)
