"""
Player Analysis page for Flet app
Search, filter, and analyze players
"""

import flet as ft
try:
    from ..utils.data_service import FPLDataService
except ImportError:
    from utils.data_service import FPLDataService


class PlayerAnalysisPage:
    """Player analysis page component"""
    
    def __init__(self, data_service: FPLDataService):
        self.data_service = data_service
        
        # Search/filter state
        self.search_query = ""
        self.position_filter = "All"
        self.max_price = 15.0
        self.current_page = 0
        self.page_size = 20
    
    def build(self) -> ft.Control:
        """Build player analysis UI"""
        
        # Search and filters
        search_section = self._build_search_section()
        
        # Player list
        player_list = self._build_player_list()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Player Analysis",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(left=16, right=16, top=16, bottom=8)
                    ),
                    search_section,
                    ft.Divider(height=1, thickness=1),
                    player_list,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _build_search_section(self) -> ft.Control:
        """Build search and filter section"""
        
        # Search field
        search_field = ft.TextField(
            label="Search players",
            prefix_icon="search",
            on_change=self._on_search_change,
            expand=True,
        )
        
        # Position filter
        position_dropdown = ft.Dropdown(
            label="Position",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("GK"),
                ft.dropdown.Option("DEF"),
                ft.dropdown.Option("MID"),
                ft.dropdown.Option("FWD"),
            ],
            value="All",
            on_change=self._on_position_change,
            width=120,
        )
        
        # Price filter
        price_slider = ft.Slider(
            min=4.0,
            max=15.0,
            value=15.0,
            label="Max £{value}m",
            on_change=self._on_price_change,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[search_field, position_dropdown],
                        spacing=8,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Max Price", size=12, color="grey400"),
                                price_slider,
                            ],
                            spacing=0,
                        ),
                        padding=ft.padding.only(top=8),
                    ),
                ],
                spacing=8,
            ),
            padding=16,
        )
    
    def _build_player_list(self) -> ft.Control:
        """Build player list with pagination"""
        
        # Get filtered players
        players_df = self.data_service.search_players(
            query=self.search_query,
            position=self.position_filter,
            max_price=self.max_price
        )
        
        if players_df.empty:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon("search_off", size=64, color="grey400"),
                        ft.Text("No players found", size=18, color="grey400"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                expand=True,
            )
        
        # Pagination
        total_players = len(players_df)
        total_pages = (total_players + self.page_size - 1) // self.page_size
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, total_players)
        page_players = players_df.iloc[start_idx:end_idx]
        
        # Player cards
        player_cards = []
        for idx, player in page_players.iterrows():
            player_cards.append(self._create_player_card(player))
        
        # Pagination controls
        pagination = ft.Row(
            controls=[
                ft.Text(f"{self.current_page + 1} / {total_pages}"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            f"{total_players} players found",
                            size=14,
                            color="grey400"
                        ),
                        padding=ft.padding.only(left=16, right=16, bottom=8)
                    ),
                    ft.ListView(
                        controls=player_cards,
                        spacing=8,
                        padding=ft.padding.symmetric(horizontal=16),
                        expand=True,
                    ),
                    pagination,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _create_player_card(self, player) -> ft.Control:
        """Create a player card"""
        position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        position = position_map.get(player.get('element_type', 0), 'N/A')
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        # Player info
                        ft.Column(
                            controls=[
                                ft.Text(
                                    player.get('web_name', 'Unknown'),
                                    size=16,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    f"{position} • £{player.get('now_cost', 0) / 10:.1f}m",
                                    size=12,
                                    color="grey400"
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        # Stats
                        ft.Column(
                            controls=[
                                self._create_stat("Pts", str(int(player.get('total_points', 0)))),
                                self._create_stat("Form", f"{player.get('form', 0):.1f}"),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            spacing=4,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=16,
            ),
        )
    
    def _create_stat(self, label: str, value: str) -> ft.Control:
        """Create a stat row"""
        return ft.Row(
            controls=[
                ft.Text(label, size=11, color="grey400"),
                ft.Text(value, size=14, weight=ft.FontWeight.BOLD),
            ],
            spacing=8,
        )
    
    def _on_search_change(self, e):
        """Handle search input change"""
        self.search_query = e.control.value
        self.current_page = 0
        # Rebuild would happen via page update in real implementation
    
    def _on_position_change(self, e):
        """Handle position filter change"""
        self.position_filter = e.control.value
        self.current_page = 0
    
    def _on_price_change(self, e):
        """Handle price slider change"""
        self.max_price = e.control.value
        self.current_page = 0
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
    
    def _next_page(self):
        """Go to next page"""
        self.current_page += 1
