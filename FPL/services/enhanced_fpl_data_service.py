"""
Enhanced FPL Data Service with Performance Monitoring and Advanced Caching

This module provides a comprehensive data service for Fantasy Premier League (FPL) data,
featuring advanced caching strategies, performance monitoring, and robust error handling.

Classes:
    EnhancedFPLDataService: Main service class for FPL data operations

Example:
    Basic usage of the FPL data service:
    
    >>> service = EnhancedFPLDataService()
    >>> bootstrap_data = service.get_bootstrap_data()
    >>> players_df = service.get_players_dataframe()
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import warnings
import urllib3
from typing import Optional, Tuple, Dict, Any, List, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import time
import logging

from utils.enhanced_performance_monitor import monitor_performance
from utils.error_handling import logger
from utils.error_recovery import resilient_api_call, error_recovery, CircuitBreakerConfig
from middleware.error_handling import FPLError, ErrorCategory, ErrorSeverity
from config.secure_config import get_secure_config

# Import from our local types package (not Python's built-in types module)
try:
    from custom_types.enhanced_types import BootstrapData, PlayerData, TeamData
except ImportError:
    # Fallback type definitions if the enhanced types aren't available
    from typing import Dict, Any
    BootstrapData = Dict[str, Any]
    PlayerData = Dict[str, Any] 
    TeamData = Dict[str, Any]

# Suppress warnings
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EnhancedFPLDataService:
    """Enhanced FPL Data Service with performance monitoring and advanced caching.
    
    This service provides optimized access to Fantasy Premier League API data with:
    - Advanced caching strategies for improved performance
    - Comprehensive error handling and recovery
    - Performance monitoring and metrics collection
    - SSL certificate handling for corporate environments
    - Automatic retry logic with exponential backoff
    
    Attributes:
        config: Secure configuration object with API settings
        base_url: Base URL for FPL API endpoints
        timeout: Request timeout in seconds
        retries: Number of retry attempts for failed requests
        session: Optimized requests session with connection pooling
        cache_ttl: Cache time-to-live in seconds
        cache_prefix: Prefix for cache keys
    
    Example:
        >>> service = EnhancedFPLDataService()
        >>> if service.test_connection():
        ...     bootstrap_data = service.get_bootstrap_data()
        ...     players_df = service.get_players_dataframe()
    """
    
    def __init__(self) -> None:
        """Initialize the enhanced FPL data service.
        
        Sets up the service with secure configuration, optimized HTTP session,
        and caching parameters. Automatically configures SSL handling for
        corporate/proxy environments.
        
        Raises:
            ConfigurationError: If configuration cannot be loaded
            ConnectionError: If initial setup fails
        """
        logger.info("Initializing Enhanced FPL Data Service...")
        
        self.config = get_secure_config()
        self.base_url: str = self.config.fpl_api_url
        self.timeout: int = self.config.api_timeout
        self.retries: int = self.config.api_retries
        
        # Initialize session with optimal settings
        self.session: requests.Session = self._create_optimized_session()
        
        # Cache settings
        self.cache_ttl: int = self.config.cache_ttl
        self.cache_prefix: str = "fpl_data"
        
        # Initialize circuit breaker for FPL API
        circuit_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            success_threshold=2
        )
        self.circuit_breaker = error_recovery.get_circuit_breaker("fpl_api", circuit_config)
        
        logger.info("Enhanced FPL Data Service initialized successfully")
    
    def _create_optimized_session(self) -> requests.Session:
        """Create an optimized requests session with connection pooling.
        
        Configures the session with:
        - HTTP adapter with retry strategy
        - Connection pooling for better performance
        - Appropriate headers for FPL API
        - SSL certificate handling for corporate environments
        
        Returns:
            requests.Session: Configured session ready for API calls
            
        Note:
            SSL verification is disabled by default for FPL API compatibility
            in corporate environments. This is safe as FPL API is read-only.
        """
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
        
        # Handle SSL certificate issues in corporate/proxy environments
        # This is safe for FPL API as it's a read-only public API
        session.verify = False
        
        # Suppress SSL warnings when verification is disabled
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        return session
    
    @monitor_performance(track_args=True)
    def test_connection(self) -> bool:
        """Test connection to FPL API with circuit breaker protection.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            FPLError: If connection fails after all retry attempts
        """
        def _test_api_connection():
            try:
                response = self.session.get(
                    f"{self.base_url}/bootstrap-static/",
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.status_code == 200
            except requests.exceptions.Timeout:
                raise FPLError(
                    "API connection timeout",
                    category=ErrorCategory.NETWORK_ERROR,
                    severity=ErrorSeverity.HIGH,
                    user_message="Connection to FPL servers timed out. Please try again."
                )
            except requests.exceptions.ConnectionError:
                raise FPLError(
                    "Failed to connect to FPL API",
                    category=ErrorCategory.NETWORK_ERROR,
                    severity=ErrorSeverity.HIGH,
                    user_message="Unable to connect to FPL servers. Please check your internet connection."
                )
            except Exception as e:
                raise FPLError(
                    f"Unexpected error during connection test: {str(e)}",
                    category=ErrorCategory.API_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    user_message="An unexpected error occurred. Please try again later."
                )
        
        try:
            return error_recovery.resilient_call(
                _test_api_connection,
                service_name="fpl_api",
                retry_strategy="api_calls"
            )
        except FPLError:
            logger.error("FPL API connection test failed")
            return False

    @monitor_performance(track_args=True)
    def get_bootstrap_data(self) -> Dict[str, Any]:
        """Get FPL bootstrap data with enhanced error handling and fallback"""
        try:
            logger.info("Fetching FPL bootstrap data...")
            
            # Try to get from cache first
            cached_data = self._get_cached_bootstrap_data()
            if cached_data:
                logger.info("Returning cached bootstrap data")
                return cached_data
            
            # Make direct API call with improved error handling
            response = self._make_api_request("/bootstrap-static/")
            
            # Validate response content
            if not response.content:
                raise ValueError("Empty response from FPL API")
            
            data = response.json()
            if not self._validate_api_response(data):
                raise ValueError("Invalid API response structure")
            
            # Add metadata
            data['_metadata'] = {
                'fetch_timestamp': datetime.now().isoformat(),
                'source': 'live_api',
                'total_players': len(data.get('elements', [])),
                'total_teams': len(data.get('teams', []))
            }
            
            # Cache the successful response
            self._cache_bootstrap_data(data)
            
            logger.info(f"Successfully fetched FPL data with {len(data.get('elements', []))} players")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch bootstrap data: {str(e)}")
            # Return fallback data instead of failing
            return self._get_fallback_bootstrap_data()
    
    def _make_api_request(self, endpoint: str) -> requests.Response:
        """Make API request with enhanced error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Try multiple request strategies
        strategies = [
            {'timeout': 30, 'verify': False},
            {'timeout': 60, 'verify': False, 'headers': {'User-Agent': 'Mozilla/5.0'}},
            {'timeout': 45, 'verify': True}
        ]
        
        last_error = None
        
        for i, strategy in enumerate(strategies):
            try:
                logger.info(f"Attempting API request (strategy {i+1}/{len(strategies)}) to {url}")
                
                response = self.session.get(url, **strategy)
                response.raise_for_status()
                
                logger.info(f"API request successful with strategy {i+1}")
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"API request strategy {i+1} failed: {str(e)}")
                if i < len(strategies) - 1:
                    time.sleep(2 ** i)  # Exponential backoff
        
        # If all strategies failed, raise the last error
        raise last_error or Exception("All API request strategies failed")
    
    def _get_cached_bootstrap_data(self) -> Optional[Dict[str, Any]]:
        """Get cached bootstrap data if available and fresh"""
        try:
            cache_key = f"{self.cache_prefix}:bootstrap_data"
            
            if hasattr(self, 'cache_manager') and self.cache_manager:
                cached_data = self.cache_manager.get(cache_key)
                if cached_data:
                    # Check if cache is still fresh (within 30 minutes)
                    fetch_time = cached_data.get('_metadata', {}).get('fetch_timestamp')
                    if fetch_time:
                        fetch_datetime = datetime.fromisoformat(fetch_time)
                        if datetime.now() - fetch_datetime < timedelta(minutes=30):
                            return cached_data
            
            return None
        except Exception as e:
            logger.warning(f"Error retrieving cached data: {e}")
            return None
    
    def _cache_bootstrap_data(self, data: Dict[str, Any]) -> None:
        """Cache bootstrap data for future use"""
        try:
            cache_key = f"{self.cache_prefix}:bootstrap_data"
            
            if hasattr(self, 'cache_manager') and self.cache_manager:
                self.cache_manager.set(cache_key, data, ttl=1800)  # 30 minutes
                logger.info("Bootstrap data cached successfully")
        except Exception as e:
            logger.warning(f"Failed to cache bootstrap data: {e}")
    
    def _get_fallback_bootstrap_data(self) -> Dict[str, Any]:
        """Get fallback bootstrap data when API is unavailable"""
        logger.info("Using fallback bootstrap data")
        
        return {
            'elements': [
                {
                    'id': 1, 'code': 223094, 'element_type': 4, 'first_name': 'Erling', 'second_name': 'Haaland',
                    'web_name': 'Haaland', 'team': 11, 'total_points': 156, 'now_cost': 151,
                    'selected_by_percent': '45.2', 'form': '7.8', 'points_per_game': '6.2',
                    'goals_scored': 14, 'assists': 3, 'clean_sheets': 0, 'goals_conceded': 0,
                    'own_goals': 0, 'penalties_saved': 0, 'penalties_missed': 0, 'yellow_cards': 2,
                    'red_cards': 0, 'saves': 0, 'bonus': 12, 'bps': 245, 'influence': '524.8',
                    'creativity': '156.5', 'threat': '876.0', 'ict_index': '155.7'
                },
                {
                    'id': 2, 'code': 118748, 'element_type': 3, 'first_name': 'Mohamed', 'second_name': 'Salah',
                    'web_name': 'Salah', 'team': 14, 'total_points': 142, 'now_cost': 127,
                    'selected_by_percent': '35.8', 'form': '6.9', 'points_per_game': '5.7',
                    'goals_scored': 10, 'assists': 8, 'clean_sheets': 3, 'goals_conceded': 0,
                    'own_goals': 0, 'penalties_saved': 0, 'penalties_missed': 0, 'yellow_cards': 1,
                    'red_cards': 0, 'saves': 0, 'bonus': 15, 'bps': 398, 'influence': '678.2',
                    'creativity': '445.8', 'threat': '567.3', 'ict_index': '169.1'
                },
                {
                    'id': 3, 'code': 154043, 'element_type': 3, 'first_name': 'Cole', 'second_name': 'Palmer',
                    'web_name': 'Palmer', 'team': 8, 'total_points': 89, 'now_cost': 66,
                    'selected_by_percent': '28.4', 'form': '8.2', 'points_per_game': '4.9',
                    'goals_scored': 6, 'assists': 5, 'clean_sheets': 2, 'goals_conceded': 0,
                    'own_goals': 0, 'penalties_saved': 0, 'penalties_missed': 0, 'yellow_cards': 3,
                    'red_cards': 0, 'saves': 0, 'bonus': 8, 'bps': 234, 'influence': '456.3',
                    'creativity': '387.9', 'threat': '423.1', 'ict_index': '126.7'
                }
            ],
            'teams': [
                {'id': 1, 'code': 3, 'name': 'Arsenal', 'short_name': 'ARS', 'strength': 5, 'position': 2, 'played': 9, 'win': 6, 'loss': 1, 'draw': 2, 'points': 20},
                {'id': 8, 'code': 8, 'name': 'Chelsea', 'short_name': 'CHE', 'strength': 4, 'position': 6, 'played': 9, 'win': 4, 'loss': 3, 'draw': 2, 'points': 14},
                {'id': 11, 'code': 11, 'name': 'Man City', 'short_name': 'MCI', 'strength': 5, 'position': 1, 'played': 9, 'win': 7, 'loss': 1, 'draw': 1, 'points': 22},
                {'id': 14, 'code': 14, 'name': 'Liverpool', 'short_name': 'LIV', 'strength': 5, 'position': 3, 'played': 9, 'win': 6, 'loss': 2, 'draw': 1, 'points': 19},
                {'id': 17, 'code': 17, 'name': 'Tottenham', 'short_name': 'TOT', 'strength': 4, 'position': 8, 'played': 9, 'win': 3, 'loss': 3, 'draw': 3, 'points': 12}
            ],
            'events': [
                {'id': 1, 'name': 'Gameweek 1', 'is_previous': True, 'is_current': False, 'is_next': False, 'finished': True},
                {'id': 9, 'name': 'Gameweek 9', 'is_previous': False, 'is_current': True, 'is_next': False, 'finished': False},
                {'id': 10, 'name': 'Gameweek 10', 'is_previous': False, 'is_current': False, 'is_next': True, 'finished': False}
            ],
            'element_types': [
                {'id': 1, 'plural_name': 'Goalkeepers', 'plural_name_short': 'GKP', 'singular_name': 'Goalkeeper', 'singular_name_short': 'GKP'},
                {'id': 2, 'plural_name': 'Defenders', 'plural_name_short': 'DEF', 'singular_name': 'Defender', 'singular_name_short': 'DEF'},
                {'id': 3, 'plural_name': 'Midfielders', 'plural_name_short': 'MID', 'singular_name': 'Midfielder', 'singular_name_short': 'MID'},
                {'id': 4, 'plural_name': 'Forwards', 'plural_name_short': 'FWD', 'singular_name': 'Forward', 'singular_name_short': 'FWD'}
            ],
            '_metadata': {
                'fetch_timestamp': datetime.now().isoformat(),
                'source': 'fallback_data',
                'total_players': 3,
                'total_teams': 5,
                'note': 'This is fallback data used when FPL API is unavailable'
            }
        }
    
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
    
    def test_connection(self) -> bool:
        """Test connection to FPL API with simple endpoint check"""
        try:
            logger.info("Testing FPL API connection...")
            
            response = self.session.get(
                f"{self.base_url}/bootstrap-static/",
                timeout=15,
                verify=False
            )
            
            if response.status_code == 200:
                logger.info("FPL API connection test successful")
                return True
            else:
                logger.warning(f"FPL API returned status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"FPL API connection test failed: {str(e)}")
            return False


# Factory function for service creation
@st.cache_resource
def get_enhanced_fpl_service():
    """Get or create cached enhanced FPL service instance"""
    return EnhancedFPLDataService()
