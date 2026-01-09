"""
Data service for Flet app
Standalone version that directly accesses FPL API
"""

import requests
import pandas as pd
import logging
from typing import Dict, Optional, List


class FPLDataService:
    """Centralized data service for Flet app"""
    
    BASE_URL = "https://fantasy.premierleague.com/api"
    
    def __init__(self):
        """Initialize data service"""
        self._players_df: Optional[pd.DataFrame] = None
        self._teams_df: Optional[pd.DataFrame] = None
        self._fixtures_df: Optional[pd.DataFrame] = None
    
    def _fetch_bootstrap_data(self) -> Dict:
        """Get bootstrap-static data from FPL API"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/bootstrap-static/",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.exception(f"Error fetching bootstrap data: {e}")
            return {}
    
    def _fetch_fixtures(self) -> List[Dict]:
        """Get fixtures data from FPL API"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/fixtures/",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.exception(f"Error fetching fixtures: {e}")
            return []
    
    def get_players(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get players dataframe"""
        if self._players_df is None or force_refresh:
            data = self._fetch_bootstrap_data()
            
            if data and 'elements' in data:
                df = pd.DataFrame(data['elements'])
                
                # Add calculated columns
                if 'now_cost' in df.columns:
                    df['price'] = df['now_cost'] / 10
                if 'total_points' in df.columns and 'now_cost' in df.columns:
                    df['value_score'] = (df['total_points'] / (df['now_cost'] / 10)).fillna(0)
                
                self._players_df = df
            else:
                return pd.DataFrame()
        
        return self._players_df
    
    def get_teams(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get teams dataframe"""
        if self._teams_df is None or force_refresh:
            data = self._fetch_bootstrap_data()
            
            if data and 'teams' in data:
                self._teams_df = pd.DataFrame(data['teams'])
            else:
                return pd.DataFrame()
        
        return self._teams_df
    
    def get_fixtures(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get fixtures dataframe"""
        if self._fixtures_df is None or force_refresh:
            fixtures = self._fetch_fixtures()
            
            if fixtures:
                self._fixtures_df = pd.DataFrame(fixtures)
            else:
                return pd.DataFrame()
        
        return self._fixtures_df
    
    def generate_best_team(self, strategy: str = 'balanced') -> Dict:
        """Generate best team (simplified version)"""
        players_df = self.get_players()
        
        if players_df.empty:
            return {
                'success': False,
                'error': 'No player data available'
            }
        
        try:
            # Simple team selection based on strategy
            budget = 1000  # £100m
            
            # Sort by different criteria based on strategy
            if strategy == 'form':
                sort_col = 'form'
            elif strategy == 'value':
                sort_col = 'value_score'
            elif strategy == 'points':
                sort_col = 'total_points'
            else:  # balanced
                sort_col = 'total_points'
            
            # Required formation: 2 GK, 5 DEF, 5 MID, 3 FWD
            formation_requirements = {
                1: 2,   # GK
                2: 5,   # DEF
                3: 5,   # MID
                4: 3    # FWD
            }
            
            selected_players = []
            total_cost = 0
            
            # Select players for each position
            for position_id, count in formation_requirements.items():
                position_players = players_df[players_df['element_type'] == position_id].copy()
                
                # Sort by selected metric
                if sort_col in position_players.columns:
                    position_players = position_players.sort_values(sort_col, ascending=False)
                
                # Select top players within budget
                for _, player in position_players.iterrows():
                    if len([p for p in selected_players if p['element_type'] == position_id]) >= count:
                        break
                    
                    cost = player.get('now_cost', 0)
                    if total_cost + cost <= budget:
                        selected_players.append(player.to_dict())
                        total_cost += cost
            
            # Create squad DataFrame
            squad_df = pd.DataFrame(selected_players) if selected_players else pd.DataFrame()
            
            # Split into starting XI and bench (simple: best 11 + 4 bench)
            if not squad_df.empty:
                squad_df = squad_df.sort_values('total_points', ascending=False)
                starting_xi = squad_df.head(11)
                bench = squad_df.tail(4)
            else:
                starting_xi = pd.DataFrame()
                bench = pd.DataFrame()
            
            return {
                'success': True,
                'squad': squad_df,
                'starting_xi': starting_xi,
                'bench': bench,
                'stats': {
                    'total_cost': total_cost / 10,
                    'expected_points': squad_df['total_points'].sum() if not squad_df.empty else 0,
                    'formation': '4-4-2'
                },
                'formation': '4-4-2'
            }
        except Exception as e:
            logging.exception(f"Error generating team: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_price_predictions(self) -> Dict[str, pd.DataFrame]:
        """Get price change predictions (simplified)"""
        players_df = self.get_players()
        
        if players_df.empty:
            return {
                'risers': pd.DataFrame(),
                'fallers': pd.DataFrame()
            }
        
        # Simple heuristic: rising form = likely price rise
        players_df = players_df.copy()
        if 'form' in players_df.columns and 'selected_by_percent' in players_df.columns:
            players_df['form_num'] = pd.to_numeric(players_df['form'], errors='coerce').fillna(0)
            players_df['selected_num'] = pd.to_numeric(players_df['selected_by_percent'], errors='coerce').fillna(0)
            
            # High form + high ownership = likely risers
            risers = players_df[(players_df['form_num'] > 5) & (players_df['selected_num'] > 10)]
            risers = risers.sort_values('form_num', ascending=False).head(10)
            
            # Low form + high ownership = likely fallers
            fallers = players_df[(players_df['form_num'] < 3) & (players_df['selected_num'] > 5)]
            fallers = fallers.sort_values('form_num', ascending=True).head(10)
        else:
            risers = pd.DataFrame()
            fallers = pd.DataFrame()
        
        return {
            'risers': risers,
            'fallers': fallers
        }
    
    def get_top_players(self, by: str = 'points', limit: int = 10) -> pd.DataFrame:
        """Get top players by metric"""
        players_df = self.get_players()
        
        if players_df.empty:
            return pd.DataFrame()
        
        metric_map = {
            'points': 'total_points',
            'form': 'form',
            'value': 'value_score',
            'selected': 'selected_by_percent'
        }
        
        column = metric_map.get(by, 'total_points')
        
        if column in players_df.columns:
            players_df = players_df.copy()
            players_df[column] = pd.to_numeric(players_df[column], errors='coerce').fillna(0)
            return players_df.nlargest(limit, column)
        else:
            return players_df.head(limit)
    
    def search_players(self, query: str = "", position: Optional[str] = None,
                      team: Optional[str] = None, max_price: Optional[float] = None) -> pd.DataFrame:
        """Search and filter players"""
        players_df = self.get_players().copy()
        
        if players_df.empty:
            return pd.DataFrame()
        
        # Text search
        if query:
            mask = players_df['web_name'].str.contains(query, case=False, na=False)
            players_df = players_df[mask]
        
        # Position filter
        if position and position != 'All':
            position_map = {'GK': 1, 'DEF': 2, 'MID': 3, 'FWD': 4}
            pos_id = position_map.get(position)
            if pos_id:
                players_df = players_df[players_df['element_type'] == pos_id]
        
        # Team filter
        if team and team != 'All':
            try:
                team_id = int(team)
                players_df = players_df[players_df['team'] == team_id]
            except (ValueError, KeyError):
                pass
        
        # Price filter
        if max_price:
            if 'now_cost' in players_df.columns:
                players_df = players_df[players_df['now_cost'] / 10 <= max_price]
        
        return players_df
    
    def clear_cache(self):
        """Clear all cached data"""
        self._players_df = None
        self._teams_df = None
        self._fixtures_df = None
