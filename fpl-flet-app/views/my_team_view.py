import flet as ft
from services.fpl_api_service import FPLDataService
from components.section_header import create_section_header
from components.stat_card import create_stat_card
from components.views import create_error_view
from utils.theme import PLTheme, Spacing

async def build_my_team(data_service: FPLDataService, team_id_input: ft.TextField, import_status_text: ft.Text, import_team_callback):
    """Build My Team view with team import functionality"""
    
    import_section = ft.Container(
        content=ft.Column(
            [
                create_section_header("Import Your Team", "⬇️"),
                ft.Row(
                    [
                        team_id_input,
                        ft.FilledButton(
                            "Import Team",
                            on_click=import_team_callback,
                            style=ft.ButtonStyle(
                                bgcolor=PLTheme.ACCENT,
                                color=PLTheme.PRIMARY,
                            ),
                        ),
                    ],
                    spacing=Spacing.SM,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                import_status_text,
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
    if not data_service.is_team_data_loaded():
        return ft.Column(
            [
                create_section_header("My Team", "👥"),
                import_section,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
    
    # Retrieve team data from the service (it should already be loaded if is_team_data_loaded() is True)
    team_data = data_service.get_loaded_team_data()
    players_df = await data_service.get_players()
    
    if team_data is None or players_df.empty:
        return ft.Column(
            [
                create_section_header("My Team", "👥"),
                import_section,
                create_error_view(
                    "Failed to load team data. Check your Team ID and try again.",
                    retry_callback=lambda _: import_team_callback(None)
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
                ft.Text(f"Team ID: {team_info.get('id')}", size=12, color="#9E9E9E"),
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
            create_stat_card(
                "Overall Rank",
                f"{team_info.get('summary_overall_rank', 0):,}",
                icon="🏆",
            ),
            create_stat_card(
                "Total Points",
                str(team_info.get('summary_overall_points', 0)),
                icon="⚽",
            ),
            create_stat_card(
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
                                    ft.Text(f"GW Points: {player.get('event_points', 0)}", size=12, color="#BDBDBD"),
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
            create_section_header("My Team", "👥"),
            import_section,
            team_header,
            stats,
            create_section_header("Squad", "⚽"),
            ft.Column(squad_items, spacing=0),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )
