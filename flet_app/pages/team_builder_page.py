"""
Team Builder page for Flet app
Build and optimize FPL squads
"""

import flet as ft
try:
    from ..utils.data_service import FPLDataService
except ImportError:
    from utils.data_service import FPLDataService


class TeamBuilderPage:
    """Team builder page component"""
    
    def __init__(self, data_service: FPLDataService):
        self.data_service = data_service
        self.selected_strategy = "balanced"
        self.generated_team = None
    
    def build(self) -> ft.Control:
        """Build team builder UI"""
        
        # Strategy selector
        strategy_section = self._build_strategy_section()
        
        # Team display
        team_section = self._build_team_section()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Team Builder",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(left=16, right=16, top=16, bottom=8)
                    ),
                    strategy_section,
                    ft.Divider(height=1, thickness=1),
                    team_section,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _build_strategy_section(self) -> ft.Control:
        """Build strategy selection section"""
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Select Strategy", size=16, weight=ft.FontWeight.BOLD),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value="balanced", label="Balanced - Mix of all factors"),
                            ft.Radio(value="form", label="Form - Recent performance"),
                            ft.Radio(value="value", label="Value - Points per million"),
                            ft.Radio(value="points", label="Points - Total points"),
                        ]),
                        value="balanced",
                        on_change=self._on_strategy_change,
                    ),
                    ft.ElevatedButton(
                        "Generate Best Team",
                        icon="auto_awesome",
                        on_click=self._generate_team,
                        expand=True,
                    ),
                ],
                spacing=12,
            ),
            padding=16,
        )
    
    def _build_team_section(self) -> ft.Control:
        """Build team display section"""
        
        if self.generated_team is None:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon("groups_outlined", size=64, color="grey400"),
                        ft.Text(
                            "No team generated yet",
                            size=18,
                            color="grey400"
                        ),
                        ft.Text(
                            "Select a strategy and click 'Generate Best Team'",
                            size=14,
                            color="grey600"
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                expand=True,
            )
        
        if not self.generated_team.get('success', False):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon("error_outline", size=64, color="red"),
                        ft.Text(
                            "Failed to generate team",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            self.generated_team.get('error', 'Unknown error'),
                            color="grey400"
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                expand=True,
                padding=32,
            )
        
        # Team stats
        stats = self.generated_team.get('stats', {})
        stats_row = ft.Row(
            controls=[
                self._create_stat_card("Total Cost", f"£{stats.get('total_cost', 0):.1f}m"),
                self._create_stat_card("Expected Pts", str(int(stats.get('total_points', 0)))),
                self._create_stat_card("Formation", stats.get('formation', 'N/A')),
            ],
            spacing=8,
        )
        
        # Starting XI
        starting_xi = self.generated_team.get('starting_xi', None)
        bench = self.generated_team.get('bench', None)
        
        starting_section = self._build_player_section("Starting XI", starting_xi)
        bench_section = self._build_player_section("Bench", bench)
        
        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(content=stats_row, padding=ft.padding.symmetric(horizontal=16)),
                    ft.Divider(height=1, thickness=1),
                    starting_section,
                    ft.Divider(height=1, thickness=1),
                    bench_section,
                ],
                spacing=8,
            ),
            expand=True,
        )
    
    def _create_stat_card(self, label: str, value: str) -> ft.Control:
        """Create a stat card"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(label, size=11, color="grey400"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=12,
            border_radius=8,
            bgcolor="surfacevariant",
            expand=True,
        )
    
    def _build_player_section(self, title: str, players_df) -> ft.Control:
        """Build a section showing players"""
        if players_df is None or players_df.empty:
            return ft.Container()
        
        player_tiles = []
        position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        
        for idx, player in players_df.iterrows():
            position = position_map.get(player.get('element_type', 0), 'N/A')
            
            player_tiles.append(
                ft.ListTile(
                    leading=ft.Container(
                        content=ft.Text(
                            position,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color="white"
                        ),
                        padding=8,
                        border_radius=4,
                        bgcolor=self._get_position_color(position),
                    ),
                    title=ft.Text(player.get('web_name', 'Unknown')),
                    subtitle=ft.Text(
                        f"£{player.get('now_cost', 0) / 10:.1f}m • {player.get('total_points', 0)} pts"
                    ),
                    trailing=ft.Text(
                        f"{player.get('form', 0):.1f}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="green"
                    ),
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            title,
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(left=16, right=16, top=8, bottom=4)
                    ),
                    ft.Column(controls=player_tiles, spacing=0),
                ],
                spacing=0,
            ),
        )
    
    def _get_position_color(self, position: str) -> str:
        """Get color for position"""
        colors = {
            'GK': "amber700",
            'DEF': "green700",
            'MID': "blue700",
            'FWD': "red700",
        }
        return colors.get(position, "grey700")
    
    def _on_strategy_change(self, e):
        """Handle strategy selection change"""
        self.selected_strategy = e.control.value
    
    def _generate_team(self, e):
        """Generate best team based on selected strategy"""
        # Show loading
        e.page.splash = ft.ProgressBar()
        e.page.update()
        
        # Generate team
        self.generated_team = self.data_service.generate_best_team(
            strategy=self.selected_strategy
        )
        
        # Hide loading
        e.page.splash = None
        
        # Show success message
        if self.generated_team.get('success', False):
            e.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Team generated successfully!"))
            )
        
        # Rebuild UI would happen via page update in real implementation
        e.page.update()
