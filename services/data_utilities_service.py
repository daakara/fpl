"""
Data Utilities Service
Handles data processing, extraction, and utility functions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataUtilitiesService:
    """Service for data processing and utility functions"""
    
    def __init__(self):
        """Initialize the data utilities service"""
        pass
    
    def create_fallback_data(self):
        """Create comprehensive fallback data when API is unavailable - matches FPL API structure"""
        return {
            "elements": [  # Changed from 'players' to 'elements' to match FPL API
                {
                    "id": 1, "web_name": "Haaland", "element_type": 4, "team": 1, 
                    "now_cost": 151, "total_points": 156, "form": "8.2", "points_per_game": "8.9",
                    "selected_by_percent": "65.3", "minutes": 1345, "goals_scored": 18, "assists": 5,
                    "clean_sheets": 8, "goals_conceded": 12, "bonus": 15, "bps": 456
                },
                {
                    "id": 2, "web_name": "Salah", "element_type": 3, "team": 2,
                    "now_cost": 127, "total_points": 138, "form": "6.8", "points_per_game": "7.8",
                    "selected_by_percent": "58.7", "minutes": 1398, "goals_scored": 12, "assists": 9,
                    "clean_sheets": 6, "goals_conceded": 14, "bonus": 12, "bps": 398
                },
                {
                    "id": 3, "web_name": "Palmer", "element_type": 3, "team": 3,
                    "now_cost": 66, "total_points": 142, "form": "9.1", "points_per_game": "8.5",
                    "selected_by_percent": "72.1", "minutes": 1289, "goals_scored": 10, "assists": 11,
                    "clean_sheets": 4, "goals_conceded": 18, "bonus": 14, "bps": 412
                },
                {
                    "id": 4, "web_name": "Saka", "element_type": 3, "team": 4,
                    "now_cost": 82, "total_points": 125, "form": "7.5", "points_per_game": "7.2",
                    "selected_by_percent": "48.9", "minutes": 1412, "goals_scored": 8, "assists": 10,
                    "clean_sheets": 7, "goals_conceded": 10, "bonus": 11, "bps": 367
                },
                {
                    "id": 5, "web_name": "Son", "element_type": 3, "team": 5,
                    "now_cost": 95, "total_points": 118, "form": "6.9", "points_per_game": "7.1",
                    "selected_by_percent": "42.3", "minutes": 1356, "goals_scored": 11, "assists": 6,
                    "clean_sheets": 5, "goals_conceded": 15, "bonus": 10, "bps": 345
                }
            ],
            "teams": [
                {"id": 1, "name": "Manchester City", "short_name": "MCI", "strength": 5, "strength_overall_home": 1350, "strength_overall_away": 1320},
                {"id": 2, "name": "Liverpool", "short_name": "LIV", "strength": 5, "strength_overall_home": 1340, "strength_overall_away": 1310},
                {"id": 3, "name": "Chelsea", "short_name": "CHE", "strength": 4, "strength_overall_home": 1280, "strength_overall_away": 1250},
                {"id": 4, "name": "Arsenal", "short_name": "ARS", "strength": 5, "strength_overall_home": 1330, "strength_overall_away": 1300},
                {"id": 5, "name": "Tottenham", "short_name": "TOT", "strength": 4, "strength_overall_home": 1270, "strength_overall_away": 1240}
            ],
            "events": [
                {"id": 10, "name": "Gameweek 10", "is_current": True, "is_next": False, "finished": False}
            ],
            "current_gameweek": 10,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_current_gameweek(self, data):
        """Extract current gameweek from FPL data"""
        if isinstance(data, dict) and 'events' in data:
            events = data.get('events', [])
            for event in events:
                if event.get('is_current', False):
                    return event.get('id', 1)
        return 10  # Fallback to GW 10
    
    def get_live_players_sample(self, data, count=5):
        """Get sample of live players for display"""
        if isinstance(data, dict) and 'elements' in data:
            players = data.get('elements', [])[:count]
            return [p.get('web_name', 'Unknown') for p in players]
        return ['Haaland', 'Salah', 'Palmer', 'Saka', 'Son'][:count]
    
    def get_live_teams(self, data):
        """Get live teams data"""
        if isinstance(data, dict) and 'teams' in data:
            return data.get('teams', [])
        return []
    
    def prepare_performance_data(self, current_gw):
        """Prepare performance analytics data"""
        gw_range = max(1, current_gw - 9), current_gw + 1
        return pd.DataFrame({
            'Gameweek': range(gw_range[0], gw_range[1]),
            'Average Score': [45 + (i*2) for i in range(gw_range[1] - gw_range[0])],
            'Top 10K Average': [55 + (i*2) for i in range(gw_range[1] - gw_range[0])],
            'Your Score': [48 + (i*1.5) for i in range(gw_range[1] - gw_range[0])]
        })
    
    def prepare_team_performance_data(self):
        """Prepare team performance metrics"""
        return pd.DataFrame({
            'Metric': ['Total Points', 'Average/GW', 'Best GW', 'Worst GW', 'Consistency'],
            'Your Team': ['520', '52.0', '65', '42', '78%'],
            'Average': ['485', '48.5', '61', '39', '72%'],
            'Top 10K': ['590', '59.0', '71', '49', '85%']
        })
    
    def extract_player_data_for_analysis(self, data, player_name):
        """Extract specific player data for analysis"""
        if isinstance(data, dict) and 'elements' in data:
            players = data.get('elements', [])
            teams_dict = {team['id']: team for team in data.get('teams', [])}
            
            player_data = next((p for p in players if p.get('web_name') == player_name), None)
            
            if player_data:
                team_info = teams_dict.get(player_data.get('team'), {})
                return {
                    'price': player_data.get('now_cost', 0) / 10,
                    'total_points': player_data.get('total_points', 0),
                    'form': player_data.get('form', '0'),
                    'ownership': player_data.get('selected_by_percent', '0'),
                    'team': team_info.get('name', 'Unknown'),
                    'team_short': team_info.get('short_name', 'UNK')
                }
        
        # Fallback data
        fallback_data = {
            'Haaland': {'price': 15.1, 'total_points': 156, 'form': '8.2', 'ownership': '45.2%', 'team': 'Manchester City', 'team_short': 'MCI'},
            'Palmer': {'price': 6.6, 'total_points': 142, 'form': '9.1', 'ownership': '28.4%', 'team': 'Chelsea', 'team_short': 'CHE'},
            'Salah': {'price': 12.7, 'total_points': 138, 'form': '6.8', 'ownership': '35.8%', 'team': 'Liverpool', 'team_short': 'LIV'}
        }
        
        return fallback_data.get(player_name, {
            'price': 8.0, 'total_points': 100, 'form': '6.0', 'ownership': '20.0%', 'team': 'Unknown', 'team_short': 'UNK'
        })
    
    def simulate_fixtures(self, team_short, gameweeks=5):
        """Simulate upcoming fixtures for a team"""
        # Common Premier League teams
        all_teams = ['ARS', 'AVL', 'BOU', 'BRE', 'BHA', 'CHE', 'CRY', 'EVE', 
                    'FUL', 'IPS', 'LEI', 'LIV', 'MCI', 'MUN', 'NEW', 'NFO', 
                    'SOU', 'TOT', 'WHU', 'WOL']
        
        available_teams = [t for t in all_teams if t != team_short]
        import random
        opponents = random.sample(available_teams, min(gameweeks, len(available_teams)))
        
        fixtures = []
        for i, opponent in enumerate(opponents):
            difficulty = random.randint(2, 4)  # Random difficulty 2-4
            home = random.choice([True, False])
            venue = "H" if home else "A"
            
            fixtures.append({
                'GW': f"GW{10+i}",
                'Opponent': f"{opponent}({venue})",
                'Difficulty': difficulty
            })
        
        return pd.DataFrame(fixtures)
    
    def calculate_team_value(self, players_data):
        """Calculate total team value"""
        if not players_data:
            return 100.0  # Default fallback
            
        total_value = sum(player.get('price', 0) for player in players_data)
        return round(total_value, 1)
    
    def format_currency(self, amount):
        """Format currency values consistently"""
        if amount >= 1:
            return f"£{amount:.1f}m"
        else:
            return f"£{amount*10:.0f}k"
    
    def validate_data_structure(self, data):
        """Validate that data has expected structure"""
        if not isinstance(data, dict):
            return False
        
        # Check for essential keys
        required_keys = ['elements', 'teams']
        return all(key in data for key in required_keys)
    
    def get_data_freshness(self, data):
        """Get information about data freshness"""
        if isinstance(data, dict):
            # For live data, check last updated
            if 'last_updated' in data:
                try:
                    last_updated = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
                    age = datetime.now() - last_updated
                    if age.total_seconds() < 300:  # 5 minutes
                        return "🟢 Fresh"
                    elif age.total_seconds() < 1800:  # 30 minutes
                        return "🟡 Recent"
                    else:
                        return "🔴 Stale"
                except:
                    pass
        
        return "🟡 Cached"