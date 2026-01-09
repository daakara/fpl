import flet as ft
from services.fpl_api_service import FPLDataService
from services.player_recommendation_service import PlayerRecommendationService
from services.data_utilities_service import DataUtilitiesService
from components.skeleton import create_skeleton_list, create_skeleton_card
from components.stat_card import create_stat_card
from components.section_header import create_section_header
from components.player_card import create_player_card
from components.views import create_error_view
from utils.theme import Spacing, PLTheme

async def build_dashboard(data_service: FPLDataService, rec_service: PlayerRecommendationService, util_service: DataUtilitiesService):
    """Build enhanced dashboard view with gameweek stats"""
    
    # Show skeleton while loading
    players_df = await data_service.get_players()
    if players_df.empty:
        players_df = await data_service.get_players(force_refresh=True)
        if players_df.empty:
            return create_error_view(
                "Failed to load player data. Check your connection.",
                retry_callback=None
            )
    
    # Try to load bootstrap data from the service
    try:
        bootstrap_data = data_service.get_players_raw_bootstrap_data()
        
        if not bootstrap_data:
            return create_error_view(
                "Failed to load essential FPL data. Check your connection.",
                retry_callback=None
            )

        events = bootstrap_data.get('events', [])
        current_gw = next((gw for gw in events if gw.get('is_current')), events[0] if events else {})
        gw_number = current_gw.get('id', 1)
        gw_avg = current_gw.get('average_entry_score', 0)
        gw_highest = current_gw.get('highest_score', 0)

        # Generate recommendations
        recommendations = rec_service.generate_live_player_recommendations(bootstrap_data)
    except Exception as e:
        return create_error_view(
            f"Error loading dashboard data: {e}",
            retry_callback=None
        )
    
    # Create enhanced KPI cards with icons
    kpi_cards = ft.Row(
        [
            create_stat_card(
                "Gameweek",
                f"GW {gw_number}",
                icon="📅",
                color="#00ff00"
            ),
            create_stat_card(
                "GW Average",
                str(int(gw_avg)),
                subtitle="pts",
                icon="📈",
                color="#ffd700"
            ),
            create_stat_card(
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
            create_player_card(
                player['web_name'],
                stats,
                icon=f"{idx+1}.",
                highlight=(idx < 3)
            )
        )
    
    return ft.Column(
        [
            create_section_header("Dashboard", "📊"),
            kpi_cards,
            create_section_header("Player Recommendations", "💡"),
            ft.Row(
                [
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("🔥 Hot Pick", weight=ft.FontWeight.BOLD, size=16, color="#FF6D00"),
                                    ft.Text(f"{recommendations.get('hot_pick', {}).get('name', 'N/A')}", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(recommendations.get('hot_pick', {}).get('reason', ''), size=12, color=PLTheme.ON_SURFACE_DIM),
                                ],
                                spacing=Spacing.XS,
                            ),
                            padding=Spacing.MD,
                            bgcolor="#263238",
                        ),
                        elevation=1,
                        expand=1,
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("💎 Value Pick", weight=ft.FontWeight.BOLD, size=16, color="#00C853"),
                                    ft.Text(f"{recommendations.get('value_pick', {}).get('name', 'N/A')}", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(recommendations.get('value_pick', {}).get('reason', ''), size=12, color=PLTheme.ON_SURFACE_DIM),
                                ],
                                spacing=Spacing.XS,
                            ),
                            padding=Spacing.MD,
                            bgcolor="#263238",
                        ),
                        elevation=1,
                        expand=1,
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("⚠️ Avoid Pick", weight=ft.FontWeight.BOLD, size=16, color="#F44336"),
                                    ft.Text(f"{recommendations.get('avoid_pick', {}).get('name', 'N/A')}", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(recommendations.get('avoid_pick', {}).get('reason', ''), size=12, color=PLTheme.ON_SURFACE_DIM),
                                ],
                                spacing=Spacing.XS,
                            ),
                            padding=Spacing.MD,
                            bgcolor="#263238",
                        ),
                        elevation=1,
                        expand=1,
                    ),
                ],
                spacing=Spacing.MD,
            ),
            create_section_header("Top 10 Players", "🏆"),
            ft.Column(player_items, spacing=0),
        ],
        spacing=20,
    )
