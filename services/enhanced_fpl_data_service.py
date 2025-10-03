"""
Enhanced FPL Data Service with Performance Monitoring and Advanced Caching
Refactored version with smaller functions and comprehensive caching strategy
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import warnings
import urllib3
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json

from utils.enhanced_performance_monitor import monitor_performance
from utils.error_handling import logger
from config.secure_config import get_secure_config

# Suppress warnings
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EnhancedFPLDataService:
    """Enhanced FPL Data Service with performance monitoring and advanced caching"""
    
    def __init__(self):
        """Initialize the enhanced FPL data service"""
        logger.info("Initializing Enhanced FPL Data Service...")
        
        self.config = get_secure_config()
        self.base_url = self.config.fpl_api_url
        self.timeout = self.config.api_timeout
        self.retries = self.config.api_retries
        
        # Initialize session with optimal settings
        self.session = self._create_optimized_session()
        
        # Cache settings
        self.cache_ttl = self.config.cache_ttl
        self.cache_prefix = "fpl_data"
        
        logger.info("Enhanced FPL Data Service initialized successfully")
    
    def _create_optimized_session(self) -> requests.Session:
        """Create an optimized requests session"""
        session = requests.Session()
        
        # Configure retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=self.retries,
            pool_connections=10,
            pool_maxsize=20
        )
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        
        # Set headers for better performance
        session.headers.update({
            'User-Agent': 'FPL-Analytics-Dashboard/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        return session
    
    @monitor_performance(track_args=True)
    def test_connection(self) -> bool:
        """Test connection to FPL API with enhanced error handling"""
        try:
            logger.info("Testing FPL API connection...")
            
            response = self.session.get(
                f"{self.base_url}/bootstrap-static/",
                timeout=self.timeout,
                verify=False
            )
            response.raise_for_status()
            
            # Validate response content
            if not response.content:
                raise ValueError("Empty response from FPL API")
            
            data = response.json()
            if not self._validate_api_response(data):
                raise ValueError("Invalid API response structure")
            
            logger.info("FPL API connection test successful")
            return True
            
        except requests.exceptions.Timeout:
            logger.error("FPL API connection timeout")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"FPL API connection failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {str(e)}")
            return False
    
    def _validate_api_response(self, data: Dict) -> bool:
        """Validate API response structure"""
        required_keys = ['elements', 'teams', 'events', 'element_types']
        return all(key in data for key in required_keys)
    
    @monitor_performance()
    @st.cache_data(ttl=1800, show_spinner="Loading FPL data...")
    def fetch_fpl_data_cached(_self) -> Dict:
        """
        Fetch FPL data with enhanced caching and error handling
        Using _self to make it work with st.cache_data
        """
        return _self._fetch_fpl_data_internal()
    
    def _fetch_fpl_data_internal(self) -> Dict:
        """Internal method for fetching FPL data"""
        logger.info("Fetching FPL data from API...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/bootstrap-static/",
                timeout=self.timeout,
                verify=False
            )
            response.raise_for_status()
            
            if not response.content:
                raise ValueError("Empty response from FPL API")
            
            data = response.json()
            
            if not self._validate_api_response(data):
                raise ValueError("Invalid API response structure")
            
            # Add metadata
            data['_metadata'] = {
                'fetch_timestamp': datetime.now().isoformat(),
                'data_hash': self._calculate_data_hash(data),
                'api_version': data.get('game_settings', {}).get('league_start_event_id', 'unknown')
            }
            
            logger.info(f"Successfully fetched FPL data with {len(data['elements'])} players")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch FPL data: {str(e)}")
            raise
    
    def _calculate_data_hash(self, data: Dict) -> str:
        """Calculate hash of data for cache validation"""
        # Create a simplified version for hashing
        hash_data = {
            'elements_count': len(data.get('elements', [])),
            'teams_count': len(data.get('teams', [])),
            'events_count': len(data.get('events', [])),
            'current_event': data.get('events', [{}])[0].get('id', 0) if data.get('events') else 0
        }
        return hashlib.md5(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
    
    @monitor_performance()
    def load_fpl_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and process FPL data with enhanced error handling"""
        try:
            # Fetch cached data
            raw_data = self.fetch_fpl_data_cached()
            
            # Process data in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                players_future = executor.submit(self._process_players_data, raw_data['elements'])
                teams_future = executor.submit(self._process_teams_data, raw_data['teams'])
                
                players_df = players_future.result()
                teams_df = teams_future.result()
            
            # Validate processed data
            self._validate_processed_data(players_df, teams_df)
            
            # Update session state
            self._update_data_metadata(raw_data, players_df, teams_df)
            
            logger.info(f"Successfully processed {len(players_df)} players and {len(teams_df)} teams")
            return players_df, teams_df
            
        except Exception as e:
            logger.error(f"Failed to load FPL data: {str(e)}")
            raise
    
    @monitor_performance()
    def _process_players_data(self, elements_data: List[Dict]) -> pd.DataFrame:
        """Process players data with optimized operations"""
        try:
            # Convert to DataFrame
            players_df = pd.DataFrame(elements_data)
            
            # Optimize data types
            players_df = self._optimize_player_datatypes(players_df)
            
            # Add calculated fields
            players_df = self._add_calculated_player_fields(players_df)
            
            # Clean and validate
            players_df = self._clean_player_data(players_df)
            
            return players_df
            
        except Exception as e:
            logger.error(f"Failed to process players data: {str(e)}")
            raise
    
    def _optimize_player_datatypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame data types for memory efficiency"""
        # Define optimal data types
        dtype_map = {
            'id': 'int16',
            'team': 'int8',
            'element_type': 'int8',
            'total_points': 'int16',
            'now_cost': 'int16',
            'selected_by_percent': 'float32',
            'form': 'float32',
            'points_per_game': 'float32',
            'minutes': 'int16',
            'goals_scored': 'int16',
            'assists': 'int16',
            'clean_sheets': 'int16',
            'goals_conceded': 'int16',
            'own_goals': 'int8',
            'penalties_saved': 'int8',
            'penalties_missed': 'int8',
            'yellow_cards': 'int8',
            'red_cards': 'int8',
            'saves': 'int16',
            'bonus': 'int16',
            'bps': 'int16',
            'influence': 'float32',
            'creativity': 'float32',
            'threat': 'float32',
            'ict_index': 'float32'
        }
        
        for col, dtype in dtype_map.items():
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
                except:
                    logger.warning(f"Could not convert {col} to {dtype}")
        
        return df
    
    def _add_calculated_player_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields to player data"""
        try:
            # Value metrics
            df['value_form'] = np.where(df['now_cost'] > 0, df['form'] / (df['now_cost'] / 10), 0)
            df['value_season'] = np.where(df['now_cost'] > 0, df['total_points'] / (df['now_cost'] / 10), 0)
            
            # Performance metrics
            df['points_per_million'] = np.where(df['now_cost'] > 0, df['total_points'] / (df['now_cost'] / 10), 0)
            df['form_rank'] = df['form'].rank(method='dense', ascending=False)
            df['value_rank'] = df['value_season'].rank(method='dense', ascending=False)
            
            # Position-based metrics
            for position in df['element_type'].unique():
                position_mask = df['element_type'] == position
                df.loc[position_mask, 'position_rank'] = df.loc[position_mask, 'total_points'].rank(
                    method='dense', ascending=False
                )
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to add calculated fields: {str(e)}")
            return df
    
    def _clean_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate player data"""
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Handle string columns
        string_columns = df.select_dtypes(include=['object']).columns
        df[string_columns] = df[string_columns].fillna('')
        
        # Remove invalid records
        df = df[df['id'] > 0]  # Valid player IDs
        df = df[df['team'] > 0]  # Valid team IDs
        
        return df
    
    @monitor_performance()
    def _process_teams_data(self, teams_data: List[Dict]) -> pd.DataFrame:
        """Process teams data with optimized operations"""
        try:
            teams_df = pd.DataFrame(teams_data)
            
            # Optimize data types
            teams_df['id'] = teams_df['id'].astype('int8')
            teams_df['strength'] = teams_df['strength'].astype('int8')
            teams_df['strength_overall_home'] = teams_df['strength_overall_home'].astype('int8')
            teams_df['strength_overall_away'] = teams_df['strength_overall_away'].astype('int8')
            teams_df['strength_attack_home'] = teams_df['strength_attack_home'].astype('int8')
            teams_df['strength_attack_away'] = teams_df['strength_attack_away'].astype('int8')
            teams_df['strength_defence_home'] = teams_df['strength_defence_home'].astype('int8')
            teams_df['strength_defence_away'] = teams_df['strength_defence_away'].astype('int8')
            
            return teams_df
            
        except Exception as e:
            logger.error(f"Failed to process teams data: {str(e)}")
            raise
    
    def _validate_processed_data(self, players_df: pd.DataFrame, teams_df: pd.DataFrame):
        """Validate processed data quality"""
        # Check minimum data requirements
        if len(players_df) < 400:  # Expecting ~600+ players
            raise ValueError(f"Insufficient player data: {len(players_df)} players")
        
        if len(teams_df) != 20:  # Premier League has 20 teams
            raise ValueError(f"Invalid team count: {len(teams_df)} teams")
        
        # Check for required columns
        required_player_cols = ['id', 'web_name', 'team', 'element_type', 'total_points', 'now_cost']
        missing_cols = [col for col in required_player_cols if col not in players_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required player columns: {missing_cols}")
        
        logger.info("Data validation successful")
    
    def _update_data_metadata(self, raw_data: Dict, players_df: pd.DataFrame, teams_df: pd.DataFrame):
        """Update session state with data metadata"""
        st.session_state.update({
            'data_loaded': True,
            'last_update': datetime.now().isoformat(),
            'data_metadata': {
                'players_count': len(players_df),
                'teams_count': len(teams_df),
                'fetch_timestamp': raw_data.get('_metadata', {}).get('fetch_timestamp'),
                'data_hash': raw_data.get('_metadata', {}).get('data_hash'),
                'memory_usage': {
                    'players_mb': players_df.memory_usage(deep=True).sum() / 1024 / 1024,
                    'teams_mb': teams_df.memory_usage(deep=True).sum() / 1024 / 1024
                }
            }
        })
    
    @monitor_performance()
    async def fetch_player_details_async(self, player_id: int) -> Dict:
        """Fetch detailed player information asynchronously"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/element-summary/{player_id}/",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Failed to fetch player {player_id} details: {str(e)}")
            raise
    
    @st.cache_data(ttl=3600)
    def get_fixture_difficulty(_self, team_id: int = None) -> pd.DataFrame:
        """Get fixture difficulty analysis with caching"""
        # Implementation would fetch and process fixture data
        # Placeholder for now
        return pd.DataFrame()
    
    def clear_cache(self, cache_type: str = "all"):
        """Clear specific cache types"""
        if cache_type == "all" or cache_type == "main_data":
            self.fetch_fpl_data_cached.clear()
        
        if cache_type == "all" or cache_type == "fixture_difficulty":
            self.get_fixture_difficulty.clear()
        
        logger.info(f"Cleared cache: {cache_type}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information and statistics"""
        return {
            'main_data_cache': {
                'has_data': hasattr(self.fetch_fpl_data_cached, 'cache_info'),
                'ttl': 1800
            },
            'fixture_cache': {
                'has_data': hasattr(self.get_fixture_difficulty, 'cache_info'),
                'ttl': 3600
            }
        }


# Factory function for service creation
@st.cache_resource
def get_enhanced_fpl_service():
    """Get or create cached enhanced FPL service instance"""
    return EnhancedFPLDataService()
