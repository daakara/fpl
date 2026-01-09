import flet as ft
import pandas as pd
from services.fpl_api_service import FPLDataService
from components.section_header import create_section_header
from components.views import create_error_view
from utils.theme import PLTheme

async def build_ai_tips(data_service: FPLDataService):
    """Build AI Tips with transfer suggestions and captain picks"""
    players_df = await data_service.get_players()
    
    if players_df.empty:
        return create_error_view(
            "Failed to load AI tips. Check your connection.",
            retry_callback=None
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
                                ft.Text(f"  Form {float(player['form']):.1f}", size=12, color=PLTheme.SUCCESS),
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
                                ft.Text(f"Form {player['form_float']:.1f}", size=12, color=PLTheme.SUCCESS),
                                ft.Text("•", size=12, color="#BDBDBD"),
                                ft.Text(f"🔥 {transfers_in:,} in", size=12, color=PLTheme.ACCENT),
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
            create_section_header("AI Recommendations", "💡"),
            create_section_header("Captain Picks", "⭐"),
            ft.Column(captain_items, spacing=0),
            create_section_header("Best Value Transfers", "💰"),
            ft.Column(transfer_items, spacing=0),
            create_section_header("Differentials (< 5% owned)", "🎯"),
            ft.Column(diff_items, spacing=0) if diff_items else ft.Text("No differentials available", size=14, color="#BDBDBD"),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )