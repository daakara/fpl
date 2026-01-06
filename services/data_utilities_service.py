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
        """Create comprehensive fallback data when API is unavailable - matches FPL API structure with proper types"""
        return {
            "elements": [  # Changed from 'players' to 'elements' to match FPL API
                {
                    "id": 1, "web_name": "Haaland", "element_type": 4, "team": 1, 
                    "now_cost": 151, "total_points": 156, "form": 8.2, "points_per_game": 8.9,
                    "selected_by_percent": 65.3, "minutes": 1345, "goals_scored": 18, "assists": 5,
                    "clean_sheets": 8, "goals_conceded": 12, "bonus": 15, "bps": 456
                },
                {
                    "id": 2, "web_name": "Salah", "element_type": 3, "team": 2,
                    "now_cost": 127, "total_points": 138, "form": 6.8, "points_per_game": 7.8,
                    "selected_by_percent": 58.7, "minutes": 1398, "goals_scored": 12, "assists": 9,
                    "clean_sheets": 6, "goals_conceded": 14, "bonus": 12, "bps": 398
                },
                {
                    "id": 3, "web_name": "Palmer", "element_type": 3, "team": 3,
                    "now_cost": 66, "total_points": 142, "form": 9.1, "points_per_game": 8.5,
                    "selected_by_percent": 72.1, "minutes": 1289, "goals_scored": 10, "assists": 11,
                    "clean_sheets": 4, "goals_conceded": 18, "bonus": 14, "bps": 412
                },
                {
                    "id": 4, "web_name": "Saka", "element_type": 3, "team": 4,
                    "now_cost": 82, "total_points": 125, "form": 7.5, "points_per_game": 7.2,
                    "selected_by_percent": 48.9, "minutes": 1412, "goals_scored": 8, "assists": 10,
                    "clean_sheets": 7, "goals_conceded": 10, "bonus": 11, "bps": 367
                },
                {
                    "id": 5, "web_name": "Son", "element_type": 3, "team": 5,
                    "now_cost": 95, "total_points": 118, "form": 6.9, "points_per_game": 7.1,
                    "selected_by_percent": 42.3, "minutes": 1356, "goals_scored": 11, "assists": 6,
                    "clean_sheets": 5, "goals_conceded": 15, "bonus": 10, "bps": 345
                }
            ],
            "teams": [
                {"id": 1, "name": "Manchester City", "short_name": "MCI", "strength": 5, "strength_overall_home": 1350, "strength_overall_away": 1320},
                {"id": 2, "name": "Liverpool", "short_name": "LIV", "strength": 5, "strength_overall_home": 1340, "strength_overall_away": 1310},
                {"id": 3, "name": "Chelsea", "short_name": "CHE", "strength": 4, "strength_overall_home": 1280, "strength_overall_away": 1250},
                {"id": 4, "name": "Arsenal", "short_name": "ARS", "strength": 5, "strength_overall_home": 1330, "strength_overall_away": 1300},
                {"id": 5, "name": "Tottenham", "short_name": "TOT", "strength": 4, "strength_overall_home": 1270, "strength_overall_away": 1240},
                {"id": 6, "name": "Manchester Utd", "short_name": "MUN", "strength": 4, "strength_overall_home": 1260, "strength_overall_away": 1230},
                {"id": 7, "name": "Newcastle", "short_name": "NEW", "strength": 4, "strength_overall_home": 1250, "strength_overall_away": 1220},
                {"id": 8, "name": "Aston Villa", "short_name": "AVL", "strength": 4, "strength_overall_home": 1240, "strength_overall_away": 1210},
                {"id": 9, "name": "Brighton", "short_name": "BHA", "strength": 3, "strength_overall_home": 1200, "strength_overall_away": 1170},
                {"id": 10, "name": "West Ham", "short_name": "WHU", "strength": 3, "strength_overall_home": 1190, "strength_overall_away": 1160},
                {"id": 11, "name": "Crystal Palace", "short_name": "CRY", "strength": 3, "strength_overall_home": 1180, "strength_overall_away": 1150},
                {"id": 12, "name": "Fulham", "short_name": "FUL", "strength": 3, "strength_overall_home": 1170, "strength_overall_away": 1140},
                {"id": 13, "name": "Brentford", "short_name": "BRE", "strength": 3, "strength_overall_home": 1160, "strength_overall_away": 1130},
                {"id": 14, "name": "Bournemouth", "short_name": "BOU", "strength": 2, "strength_overall_home": 1120, "strength_overall_away": 1090},
                {"id": 15, "name": "Wolves", "short_name": "WOL", "strength": 2, "strength_overall_home": 1110, "strength_overall_away": 1080},
                {"id": 16, "name": "Everton", "short_name": "EVE", "strength": 2, "strength_overall_home": 1100, "strength_overall_away": 1070},
                {"id": 17, "name": "Nottm Forest", "short_name": "NFO", "strength": 2, "strength_overall_home": 1090, "strength_overall_away": 1060},
                {"id": 18, "name": "Leicester", "short_name": "LEI", "strength": 2, "strength_overall_home": 1080, "strength_overall_away": 1050},
                {"id": 19, "name": "Ipswich", "short_name": "IPS", "strength": 1, "strength_overall_home": 1050, "strength_overall_away": 1020},
                {"id": 20, "name": "Southampton", "short_name": "SOU", "strength": 1, "strength_overall_home": 1040, "strength_overall_away": 1010}
            ],
            "events": [
                {"id": 10, "name": "Gameweek 10", "is_current": True, "is_next": False, "finished": False}
            ],
            "fixtures": [
                # Manchester City fixtures
                {"id": 1, "event": 11, "team_h": 1, "team_a": 2, "team_h_difficulty": 4, "team_a_difficulty": 5, "finished": False},
                {"id": 2, "event": 12, "team_h": 3, "team_a": 1, "team_h_difficulty": 5, "team_a_difficulty": 2, "finished": False},
                {"id": 3, "event": 13, "team_h": 1, "team_a": 4, "team_h_difficulty": 4, "team_a_difficulty": 5, "finished": False},
                {"id": 4, "event": 14, "team_h": 5, "team_a": 1, "team_h_difficulty": 5, "team_a_difficulty": 3, "finished": False},
                {"id": 5, "event": 15, "team_h": 1, "team_a": 3, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                
                # Liverpool fixtures
                {"id": 6, "event": 11, "team_h": 1, "team_a": 2, "team_h_difficulty": 4, "team_a_difficulty": 5, "finished": False},
                {"id": 7, "event": 12, "team_h": 2, "team_a": 4, "team_h_difficulty": 4, "team_a_difficulty": 4, "finished": False},
                {"id": 8, "event": 13, "team_h": 5, "team_a": 2, "team_h_difficulty": 5, "team_a_difficulty": 2, "finished": False},
                {"id": 9, "event": 14, "team_h": 2, "team_a": 3, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                {"id": 10, "event": 15, "team_h": 4, "team_a": 2, "team_h_difficulty": 4, "team_a_difficulty": 4, "finished": False},
                
                # Chelsea fixtures
                {"id": 11, "event": 11, "team_h": 4, "team_a": 3, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                {"id": 12, "event": 12, "team_h": 3, "team_a": 1, "team_h_difficulty": 5, "team_a_difficulty": 2, "finished": False},
                {"id": 13, "event": 13, "team_h": 3, "team_a": 5, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 14, "event": 14, "team_h": 2, "team_a": 3, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                {"id": 15, "event": 15, "team_h": 1, "team_a": 3, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                
                # Arsenal fixtures
                {"id": 16, "event": 11, "team_h": 4, "team_a": 3, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                {"id": 17, "event": 12, "team_h": 2, "team_a": 4, "team_h_difficulty": 4, "team_a_difficulty": 4, "finished": False},
                {"id": 18, "event": 13, "team_h": 1, "team_a": 4, "team_h_difficulty": 4, "team_a_difficulty": 5, "finished": False},
                {"id": 19, "event": 14, "team_h": 4, "team_a": 5, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 20, "event": 15, "team_h": 4, "team_a": 2, "team_h_difficulty": 4, "team_a_difficulty": 4, "finished": False},
                
                # Tottenham fixtures
                {"id": 21, "event": 11, "team_h": 5, "team_a": 1, "team_h_difficulty": 5, "team_a_difficulty": 3, "finished": False},
                {"id": 22, "event": 12, "team_h": 4, "team_a": 5, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                {"id": 23, "event": 13, "team_h": 5, "team_a": 2, "team_h_difficulty": 5, "team_a_difficulty": 2, "finished": False},
                {"id": 24, "event": 14, "team_h": 3, "team_a": 5, "team_h_difficulty": 4, "team_a_difficulty": 3, "finished": False},
                {"id": 25, "event": 15, "team_h": 5, "team_a": 4, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                
                # Manchester United fixtures
                {"id": 26, "event": 11, "team_h": 6, "team_a": 14, "team_h_difficulty": 2, "team_a_difficulty": 4, "finished": False},
                {"id": 27, "event": 12, "team_h": 7, "team_a": 6, "team_h_difficulty": 4, "team_a_difficulty": 4, "finished": False},
                {"id": 28, "event": 13, "team_h": 6, "team_a": 8, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                {"id": 29, "event": 14, "team_h": 1, "team_a": 6, "team_h_difficulty": 4, "team_a_difficulty": 5, "finished": False},
                {"id": 30, "event": 15, "team_h": 6, "team_a": 9, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                
                # Newcastle fixtures
                {"id": 31, "event": 11, "team_h": 15, "team_a": 7, "team_h_difficulty": 4, "team_a_difficulty": 2, "finished": False},
                {"id": 32, "event": 12, "team_h": 7, "team_a": 6, "team_h_difficulty": 4, "team_a_difficulty": 4, "finished": False},
                {"id": 33, "event": 13, "team_h": 10, "team_a": 7, "team_h_difficulty": 4, "team_a_difficulty": 3, "finished": False},
                {"id": 34, "event": 14, "team_h": 7, "team_a": 11, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 35, "event": 15, "team_h": 2, "team_a": 7, "team_h_difficulty": 4, "team_a_difficulty": 5, "finished": False},
                
                # Aston Villa fixtures
                {"id": 36, "event": 11, "team_h": 8, "team_a": 16, "team_h_difficulty": 2, "team_a_difficulty": 4, "finished": False},
                {"id": 37, "event": 12, "team_h": 12, "team_a": 8, "team_h_difficulty": 4, "team_a_difficulty": 3, "finished": False},
                {"id": 38, "event": 13, "team_h": 6, "team_a": 8, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                {"id": 39, "event": 14, "team_h": 8, "team_a": 13, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 40, "event": 15, "team_h": 3, "team_a": 8, "team_h_difficulty": 3, "team_a_difficulty": 4, "finished": False},
                
                # Brighton fixtures
                {"id": 41, "event": 11, "team_h": 9, "team_a": 19, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 42, "event": 12, "team_h": 17, "team_a": 9, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 43, "event": 13, "team_h": 9, "team_a": 11, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 44, "event": 14, "team_h": 10, "team_a": 9, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 45, "event": 15, "team_h": 6, "team_a": 9, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                
                # West Ham fixtures
                {"id": 46, "event": 11, "team_h": 18, "team_a": 10, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                {"id": 47, "event": 12, "team_h": 10, "team_a": 20, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 48, "event": 13, "team_h": 10, "team_a": 7, "team_h_difficulty": 4, "team_a_difficulty": 3, "finished": False},
                {"id": 49, "event": 14, "team_h": 10, "team_a": 9, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 50, "event": 15, "team_h": 14, "team_a": 10, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                
                # Crystal Palace fixtures
                {"id": 51, "event": 11, "team_h": 11, "team_a": 12, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 52, "event": 12, "team_h": 13, "team_a": 11, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 53, "event": 13, "team_h": 9, "team_a": 11, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 54, "event": 14, "team_h": 7, "team_a": 11, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 55, "event": 15, "team_h": 11, "team_a": 15, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                
                # Fulham fixtures
                {"id": 56, "event": 11, "team_h": 11, "team_a": 12, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 57, "event": 12, "team_h": 12, "team_a": 8, "team_h_difficulty": 4, "team_a_difficulty": 3, "finished": False},
                {"id": 58, "event": 13, "team_h": 14, "team_a": 12, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                {"id": 59, "event": 14, "team_h": 12, "team_a": 18, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 60, "event": 15, "team_h": 19, "team_a": 12, "team_h_difficulty": 3, "team_a_difficulty": 1, "finished": False},
                
                # Brentford fixtures
                {"id": 61, "event": 11, "team_h": 20, "team_a": 13, "team_h_difficulty": 3, "team_a_difficulty": 1, "finished": False},
                {"id": 62, "event": 12, "team_h": 13, "team_a": 11, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 63, "event": 13, "team_h": 16, "team_a": 13, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                {"id": 64, "event": 14, "team_h": 8, "team_a": 13, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 65, "event": 15, "team_h": 13, "team_a": 17, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                
                # Bournemouth fixtures
                {"id": 66, "event": 11, "team_h": 6, "team_a": 14, "team_h_difficulty": 2, "team_a_difficulty": 4, "finished": False},
                {"id": 67, "event": 12, "team_h": 14, "team_a": 15, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 68, "event": 13, "team_h": 14, "team_a": 12, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                {"id": 69, "event": 14, "team_h": 19, "team_a": 14, "team_h_difficulty": 2, "team_a_difficulty": 1, "finished": False},
                {"id": 70, "event": 15, "team_h": 14, "team_a": 10, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                
                # Wolves fixtures
                {"id": 71, "event": 11, "team_h": 15, "team_a": 7, "team_h_difficulty": 4, "team_a_difficulty": 2, "finished": False},
                {"id": 72, "event": 12, "team_h": 14, "team_a": 15, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 73, "event": 13, "team_h": 15, "team_a": 18, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 74, "event": 14, "team_h": 16, "team_a": 15, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 75, "event": 15, "team_h": 11, "team_a": 15, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                
                # Everton fixtures
                {"id": 76, "event": 11, "team_h": 8, "team_a": 16, "team_h_difficulty": 2, "team_a_difficulty": 4, "finished": False},
                {"id": 77, "event": 12, "team_h": 16, "team_a": 19, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 78, "event": 13, "team_h": 16, "team_a": 13, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                {"id": 79, "event": 14, "team_h": 16, "team_a": 15, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 80, "event": 15, "team_h": 17, "team_a": 16, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                
                # Nottm Forest fixtures
                {"id": 81, "event": 11, "team_h": 17, "team_a": 18, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 82, "event": 12, "team_h": 17, "team_a": 9, "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": False},
                {"id": 83, "event": 13, "team_h": 4, "team_a": 17, "team_h_difficulty": 2, "team_a_difficulty": 5, "finished": False},
                {"id": 84, "event": 14, "team_h": 17, "team_a": 20, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 85, "event": 15, "team_h": 13, "team_a": 17, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                
                # Leicester fixtures
                {"id": 86, "event": 11, "team_h": 18, "team_a": 10, "team_h_difficulty": 3, "team_a_difficulty": 2, "finished": False},
                {"id": 87, "event": 12, "team_h": 5, "team_a": 18, "team_h_difficulty": 2, "team_a_difficulty": 4, "finished": False},
                {"id": 88, "event": 13, "team_h": 15, "team_a": 18, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 89, "event": 14, "team_h": 12, "team_a": 18, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 90, "event": 15, "team_h": 18, "team_a": 19, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                
                # Ipswich fixtures
                {"id": 91, "event": 11, "team_h": 9, "team_a": 19, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 92, "event": 12, "team_h": 16, "team_a": 19, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 93, "event": 13, "team_h": 19, "team_a": 20, "team_h_difficulty": 2, "team_a_difficulty": 1, "finished": False},
                {"id": 94, "event": 14, "team_h": 19, "team_a": 14, "team_h_difficulty": 2, "team_a_difficulty": 1, "finished": False},
                {"id": 95, "event": 15, "team_h": 19, "team_a": 12, "team_h_difficulty": 3, "team_a_difficulty": 1, "finished": False},
                
                # Southampton fixtures
                {"id": 96, "event": 11, "team_h": 20, "team_a": 13, "team_h_difficulty": 3, "team_a_difficulty": 1, "finished": False},
                {"id": 97, "event": 12, "team_h": 10, "team_a": 20, "team_h_difficulty": 2, "team_a_difficulty": 3, "finished": False},
                {"id": 98, "event": 13, "team_h": 19, "team_a": 20, "team_h_difficulty": 2, "team_a_difficulty": 1, "finished": False},
                {"id": 99, "event": 14, "team_h": 17, "team_a": 20, "team_h_difficulty": 2, "team_a_difficulty": 2, "finished": False},
                {"id": 100, "event": 15, "team_h": 20, "team_a": 1, "team_h_difficulty": 5, "team_a_difficulty": 1, "finished": False}
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