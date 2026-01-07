"""
Data service for Flet app
Reuses logic from main Streamlit app
"""

import sys
import os
from typing import Dict, Optional
import pandas as pd

# Add parent directory to path to import from main app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from services.enhanced_fpl_data_service import get_enhanced_fpl_service
from services.data_quality_service import DataQualityService
from services.price_change_predictor_service import PriceChangePredictorService
from utils.best_team_generator import generate_best_team


class FPLDataService:
    """Centralized data service for Flet app"""
    
    def __init__(self):
        """Initialize data service"""
        self.fpl_service = get_enhanced_fpl_service()
        self.data_quality = DataQualityService()
        self.price_predictor = PriceChangePredictorService()
        
        # Cache
        self._players_df: Optional[pd.DataFrame] = None
        self._teams_df: Optional[pd.DataFrame] = None
        self._fixtures_df: Optional[pd.DataFrame] = None
    
    def get_players(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get players dataframe with all enrichments"""
        if self._players_df is None or force_refresh:
            # Fetch from API
            data = self.fpl_service.get_bootstrap_data()
            
            if data and 'elements' in data:
                # Convert to DataFrame
                df = pd.DataFrame(data['elements'])
                
                # Validate and clean
                df = self.data_quality.validate_and_clean_players(df)
                
                # Add price predictions
                df = self.price_predictor.predict_price_changes(df)
                
                # Cache
                self._players_df = df
            else:
                # Return empty DataFrame if API fails
                return pd.DataFrame()
        
        return self._players_df
    
    def get_teams(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get teams dataframe"""
        if self._teams_df is None or force_refresh:
            data = self.fpl_service.get_bootstrap_data()
            
            if data and 'teams' in data:
                df = pd.DataFrame(data['teams'])
                df = self.data_quality.validate_and_clean_teams(df)
                self._teams_df = df
            else:
                return pd.DataFrame()
        
        return self._teams_df
    
    def get_fixtures(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get fixtures dataframe"""
        if self._fixtures_df is None or force_refresh:
            fixtures = self.fpl_service.get_fixtures()
            
            if fixtures:
                self._fixtures_df = pd.DataFrame(fixtures)
            else:
                return pd.DataFrame()
        
        return self._fixtures_df
    
    def generate_best_team(self, strategy: str = 'balanced') -> Dict:
        """Generate best team using existing logic"""
        players_df = self.get_players()
        
        if players_df.empty:
            return {
                'success': False,
                'error': 'No player data available'
            }
        
        try:
            result = generate_best_team(players_df, strategy=strategy)
            return {
                'success': True,
                'squad': result.get('squad', pd.DataFrame()),
                'starting_xi': result.get('starting_xi', pd.DataFrame()),
                'bench': result.get('bench', pd.DataFrame()),
                'stats': result.get('stats', {}),
                'formation': result.get('formation', '4-4-2')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_price_predictions(self) -> Dict[str, pd.DataFrame]:
        """Get price change predictions"""
        players_df = self.get_players()
        
        if players_df.empty:
            return {
                'risers': pd.DataFrame(),
                'fallers': pd.DataFrame(),
                'watchlist': pd.DataFrame()
            }
        
        # Already added during get_players()
        risers = players_df[players_df.get('price_change_prediction', '') == 'rise'].head(10)
        fallers = players_df[players_df.get('price_change_prediction', '') == 'fall'].head(10)
        watchlist = players_df[players_df.get('price_change_prediction', '') == 'watch'].head(10)
        
        return {
            'risers': risers,
            'fallers': fallers,
            'watchlist': watchlist
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
            return players_df.nlargest(limit, column)
        else:
            return pd.DataFrame()
    
    def search_players(self, query: str, position: Optional[str] = None,
                      team: Optional[str] = None, max_price: Optional[float] = None) -> pd.DataFrame:
        """Search and filter players"""
        players_df = self.get_players()
        
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
            players_df = players_df[players_df['team'] == int(team)]
        
        # Price filter
        if max_price:
            players_df = players_df[players_df['now_cost'] / 10 <= max_price]
        
        return players_df
    
    def clear_cache(self):
        """Clear all cached data"""
        self._players_df = None
        self._teams_df = None
        self._fixtures_df = None
