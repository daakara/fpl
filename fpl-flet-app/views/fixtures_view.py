import flet as ft
from services.fpl_api_service import FPLDataService
from components.section_header import create_section_header
from components.views import create_error_view
from utils.theme import PLTheme, Spacing

async def build_fixtures(data_service: FPLDataService):
    """Build comprehensive Fixture Analysis view"""
    fixtures_df = await data_service.get_fixtures()
    teams_df = await data_service.get_teams()
    
    if fixtures_df.empty or teams_df.empty:
        return create_error_view(
            "Failed to load fixtures data. Check your connection.",
            retry_callback=None
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
            create_section_header("Fixture Analysis", "📅"),
            ft.Text("🟢Easy 🟡Medium 🔴Hard | ⚔️Attack 🛡️Defense", size=12, color="#BDBDBD"),
            create_section_header("Next 10 Fixtures", "➡️"),
            ft.Column(fixture_items, spacing=0),
            create_section_header("Fixture Difficulty (Next 5 GWs)", "🗓️"),
            ft.Column(fdr_items, spacing=0),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )
