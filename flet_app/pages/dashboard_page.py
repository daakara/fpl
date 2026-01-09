"""
Dashboard page for Flet app
Shows key metrics, top players, and price predictions
"""

import flet as ft
from typing import Optional
try:
    from ..utils.data_service import FPLDataService
except ImportError:
    from utils.data_service import FPLDataService


class DashboardPage:
    """Dashboard page component"""
    
    def __init__(self, app, data_service: FPLDataService):
        self.app = app
        self.data_service = data_service
    
    def build(self) -> ft.Control:
        """Build dashboard UI"""
        
        # Get data
        players_df = self.data_service.get_players()
        price_predictions = self.data_service.get_price_predictions()
        
        # Check if data loaded
        if players_df.empty:
            return self._build_error_view()
        
        # Build sections
        kpis = self._build_kpis(players_df)
        top_players = self._build_top_players()
        price_changes = self._build_price_changes(price_predictions)
        
        # Main layout
        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Dashboard",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(left=16, right=16, top=16, bottom=8)
                    ),
                    kpis,
                    ft.Divider(height=1, thickness=1),
                    top_players,
                    ft.Divider(height=1, thickness=1),
                    price_changes,
                ],
                padding=0,
                spacing=8,
            ),
            expand=True,
        )
    
    def _build_kpis(self, df) -> ft.Control:
        """Build KPI cards"""
        total_players = len(df)
        avg_price = df['now_cost'].mean() / 10 if 'now_cost' in df.columns else 0
        top_scorer_points = df['total_points'].max() if 'total_points' in df.columns else 0
        
        kpi_cards = ft.Row(
            controls=[
                self._create_kpi_card("Players", str(total_players), "people"),
                self._create_kpi_card("Avg Price", f"£{avg_price:.1f}m", "attach_money"),
                self._create_kpi_card("Top Points", str(int(top_scorer_points)), "star"),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
        )
        
        return ft.Container(
            content=kpi_cards,
            padding=16,
        )
    
    def _create_kpi_card(self, title: str, value: str, icon) -> ft.Control:
        """Create a KPI card"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=32, color="green"),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(title, size=12, color="grey400"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            padding=16,
            border_radius=12,
            bgcolor="surfacevariant",
            expand=True,
        )
    
    def _build_top_players(self) -> ft.Control:
        """Build top players section"""
        top_by_points = self.data_service.get_top_players(by='points', limit=5)
        
        if top_by_points.empty:
            return ft.Container()
        
        player_tiles = []
        for idx, player in top_by_points.iterrows():
            player_tiles.append(
                ft.ListTile(
                    leading=ft.Container(
                        content=ft.Text(
                            str(player.get('id', idx + 1)),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="green"
                        ),
                        width=40,
                        alignment=ft.alignment.Alignment(0, 0),
                    ),
                    title=ft.Text(player.get('web_name', 'Unknown')),
                    subtitle=ft.Text(
                        f"£{player.get('now_cost', 0) / 10:.1f}m • {player.get('total_points', 0)} pts"
                    ),
                    trailing=ft.Icon("chevron_right"),
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Top Players by Points",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(left=16, right=16, top=8, bottom=4)
                    ),
                    ft.Column(controls=player_tiles, spacing=0),
                ],
                spacing=0,
            ),
        )
    
    def _build_price_changes(self, predictions: dict) -> ft.Control:
        """Build price changes section"""
        risers = predictions.get('risers', None)
        fallers = predictions.get('fallers', None)
        
        if risers is None or risers.empty:
            return ft.Container()
        
        # Build price lists without tabs for now (Flet 0.80 Tab API changed)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Price Predictions",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(left=16, right=16, top=8, bottom=4)
                    ),
                    ft.Text("Price Risers", size=14, weight=ft.FontWeight.BOLD),
                    self._build_price_list(risers, rising=True),
                    ft.Divider(height=20),
                    ft.Text("Price Fallers", size=14, weight=ft.FontWeight.BOLD),
                    self._build_price_list(fallers, rising=False),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
            ),
            padding=12,
            height=350,
        )
    
    def _build_price_list(self, df, rising: bool = True) -> ft.Control:
        """Build price change player list"""
        if df.empty:
            return ft.Container(
                content=ft.Text("No predictions available"),
                padding=16,
            )
        
        items = []
        for idx, player in df.head(5).iterrows():
            items.append(
                ft.ListTile(
                    leading=ft.Icon(
                        "arrow_upward" if rising else "arrow_downward",
                        color="green" if rising else "red"
                    ),
                    title=ft.Text(player.get('web_name', 'Unknown')),
                    subtitle=ft.Text(
                        f"£{player.get('now_cost', 0) / 10:.1f}m • {player.get('transfers_in_event', 0):,} transfers"
                    ),
                )
            )
        
        return ft.ListView(
            controls=items,
            spacing=0,
        )
    
    def _build_error_view(self) -> ft.Control:
        """Build error view when data fails to load"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon("error_outline", size=64, color="red"),
                    ft.Text(
                        "Failed to load FPL data",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        "Please check your internet connection and try again",
                        color="grey400"
                    ),
                    ft.ElevatedButton(
                        "Retry",
                        on_click=self.app.refresh_data
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=32,
            expand=True,
        )
