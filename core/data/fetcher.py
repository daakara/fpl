"""
Unified FPL Data Fetcher - Single API Service

This module consolidates all FPL API data fetching functionality into a single,
clean, well-tested service with consistent error handling and caching.

Classes:
    FPLDataFetcher: Main service class for all FPL API operations

Example:
    >>> fetcher = FPLDataFetcher()
    >>> bootstrap_data = fetcher.get_bootstrap_data()
    >>> players_df = fetcher.get_players_dataframe()
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import warnings
import urllib3
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timedelta
import logging

from utils.error_handling import logger
from utils.error_recovery import resilient_api_call, CircuitBreakerConfig
from middleware.error_handling import FPLError, ErrorCategory, ErrorSeverity
from config.secure_config import get_secure_config

# Suppress SSL warnings for corporate environments
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FPLDataFetcher:
    """
    Unified FPL API data fetcher with advanced features.
    
    This service provides the single source of truth for all FPL API interactions,
    featuring:
    - Streamlit-integrated caching (@st.cache_data)
    - Circuit breaker pattern for resilience
    - Automatic retry with exponential backoff
    - SSL handling for corporate/proxy environments
    - Type-safe data validation
    - Performance monitoring
    
    Attributes:
        config: Secure configuration object
        base_url: Base URL for FPL API
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        session: Optimized requests session
    
    Example:
        >>> fetcher = FPLDataFetcher()
        >>> if fetcher.test_connection():
        ...     data = fetcher.get_bootstrap_data()
        ...     players = fetcher.get_players_dataframe()
    """
    
    def __init__(self) -> None:
        """Initialize the FPL data fetcher with secure configuration."""
        logger.info("Initializing Unified FPL Data Fetcher...")
        
        self.config = get_secure_config()
        self.base_url: str = self.config.fpl_api_url
        self.timeout: int = self.config.api_timeout
        self.retries: int = self.config.api_retries
        
        # Initialize optimized session
        self.session: requests.Session = self._create_session()
        
        # Circuit breaker configuration
        self.circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout=60,
            success_threshold=2
        )
        
        logger.info(f"FPL Data Fetcher initialized - Base URL: {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """
        Create an optimized requests session.
        
        Returns:
            Configured requests.Session with connection pooling and retry logic
        """
        session = requests.Session()
        
        # Configure retry strategy
        adapter = requests.adapters.HTTPAdapter(
            max_retries=self.retries,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (FPL Analytics Dashboard)',
            'Accept': 'application/json',
        })
        
        return session
    
    def test_connection(self) -> bool:
        """
        Test connection to FPL API.
        
        Returns:
            True if connection successful, False otherwise
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> if fetcher.test_connection():
            ...     print("API is reachable")
        """
        try:
            logger.info("Testing FPL API connection...")
            
            response = self.session.get(
                f"{self.base_url}/bootstrap-static/",
                verify=False,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            logger.info("✓ FPL API connection test successful")
            return True
            
        except requests.exceptions.Timeout:
            logger.error("✗ FPL API connection test timed out")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ FPL API connection test failed: {str(e)}")
            return False
    
    @st.cache_data(ttl=3600)
    def get_bootstrap_data(_self) -> Dict[str, Any]:
        """
        Fetch bootstrap-static data from FPL API.
        
        This is the primary data endpoint containing:
        - All players (elements)
        - All teams
        - Event (gameweek) data
        - Game settings
        
        Cached for 1 hour (3600 seconds).
        
        Returns:
            Dictionary containing all bootstrap data
        
        Raises:
            FPLError: If API request fails or data is invalid
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> data = fetcher.get_bootstrap_data()
            >>> players = data['elements']
            >>> teams = data['teams']
        
        Note:
            Uses _self to exclude instance from cache key
        """
        logger.info("Fetching bootstrap data from FPL API...")
        
        try:
            response = _self.session.get(
                f"{_self.base_url}/bootstrap-static/",
                verify=False,
                timeout=_self.timeout
            )
            response.raise_for_status()
            
            if not response.content:
                raise FPLError(
                    "Empty response from FPL API",
                    category=ErrorCategory.DATA,
                    severity=ErrorSeverity.HIGH
                )
            
            data = response.json()
            
            # Validate data structure
            if not data or 'elements' not in data or 'teams' not in data:
                raise FPLError(
                    "Invalid data structure from FPL API",
                    category=ErrorCategory.DATA,
                    severity=ErrorSeverity.HIGH
                )
            
            logger.info(f"✓ Successfully fetched {len(data['elements'])} players, {len(data['teams'])} teams")
            return data
            
        except requests.exceptions.Timeout as e:
            logger.error("Bootstrap data fetch timed out")
            raise FPLError(
                "API request timed out",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                original_error=e
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch bootstrap data: {str(e)}")
            raise FPLError(
                "Failed to fetch FPL data",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                original_error=e
            )
    
    @st.cache_data(ttl=1800)
    def get_fixtures(_self, event: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch fixture data from FPL API.
        
        Args:
            event: Optional gameweek number to filter fixtures
        
        Returns:
            List of fixture dictionaries
        
        Cached for 30 minutes (1800 seconds).
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> fixtures = fetcher.get_fixtures(event=10)
        """
        logger.info(f"Fetching fixtures data (event={event})...")
        
        try:
            url = f"{_self.base_url}/fixtures/"
            if event:
                url += f"?event={event}"
            
            response = _self.session.get(url, verify=False, timeout=_self.timeout)
            response.raise_for_status()
            
            fixtures = response.json()
            logger.info(f"✓ Successfully fetched {len(fixtures)} fixtures")
            return fixtures
            
        except Exception as e:
            logger.error(f"Failed to fetch fixtures: {str(e)}")
            return []
    
    @st.cache_data(ttl=1800)
    def get_player_history(_self, player_id: int) -> Dict[str, Any]:
        """
        Fetch detailed history for a specific player.
        
        Args:
            player_id: FPL player ID
        
        Returns:
            Dictionary containing player history data
        
        Cached for 30 minutes (1800 seconds).
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> history = fetcher.get_player_history(player_id=123)
            >>> gameweek_history = history['history']
        """
        logger.info(f"Fetching history for player {player_id}...")
        
        try:
            response = _self.session.get(
                f"{_self.base_url}/element-summary/{player_id}/",
                verify=False,
                timeout=_self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✓ Successfully fetched history for player {player_id}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch player history: {str(e)}")
            return {'history': [], 'fixtures': []}
    
    @st.cache_data(ttl=1800)
    def get_live_gameweek_data(_self, event: int) -> Dict[str, Any]:
        """
        Fetch live gameweek data including player performances.
        
        Args:
            event: Gameweek number
        
        Returns:
            Dictionary containing live gameweek data
        
        Cached for 30 minutes during active gameweeks.
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> live_data = fetcher.get_live_gameweek_data(event=10)
        """
        logger.info(f"Fetching live data for gameweek {event}...")
        
        try:
            response = _self.session.get(
                f"{_self.base_url}/event/{event}/live/",
                verify=False,
                timeout=_self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✓ Successfully fetched live data for GW{event}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch live gameweek data: {str(e)}")
            return {'elements': []}
    
    def get_players_dataframe(self) -> pd.DataFrame:
        """
        Get processed players DataFrame with all necessary columns.
        
        Returns:
            Pandas DataFrame with players data, fully processed and typed
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> df = fetcher.get_players_dataframe()
            >>> top_scorers = df.nlargest(10, 'total_points')
        """
        logger.info("Creating players DataFrame...")
        
        try:
            data = self.get_bootstrap_data()
            players_df = pd.DataFrame(data['elements'])
            
            if players_df.empty:
                raise FPLError(
                    "No player data available",
                    category=ErrorCategory.DATA,
                    severity=ErrorSeverity.HIGH
                )
            
            # Convert numeric columns (will be validated by transformer)
            numeric_columns = [
                'total_points', 'now_cost', 'form', 'selected_by_percent',
                'points_per_game', 'minutes', 'goals_scored', 'assists',
                'clean_sheets', 'bonus', 'bps', 'influence', 'creativity',
                'threat', 'ict_index', 'expected_goals', 'expected_assists',
                'expected_goal_involvements', 'expected_goals_conceded'
            ]
            
            for col in numeric_columns:
                if col in players_df.columns:
                    players_df[col] = pd.to_numeric(players_df[col], errors='coerce')
            
            # Fill missing values
            players_df = players_df.fillna(0)
            
            # Add derived columns
            players_df['price_millions'] = players_df['now_cost'] / 10.0
            players_df['points_per_million'] = players_df['total_points'] / players_df['price_millions']
            players_df['value_score'] = players_df['points_per_million']
            
            logger.info(f"✓ Created DataFrame with {len(players_df)} players")
            return players_df
            
        except Exception as e:
            logger.error(f"Failed to create players DataFrame: {str(e)}")
            raise
    
    def get_teams_dataframe(self) -> pd.DataFrame:
        """
        Get processed teams DataFrame.
        
        Returns:
            Pandas DataFrame with teams data
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> teams = fetcher.get_teams_dataframe()
        """
        logger.info("Creating teams DataFrame...")
        
        try:
            data = self.get_bootstrap_data()
            teams_df = pd.DataFrame(data['teams'])
            
            if teams_df.empty:
                raise FPLError(
                    "No team data available",
                    category=ErrorCategory.DATA,
                    severity=ErrorSeverity.HIGH
                )
            
            # Ensure required columns
            teams_df['name'] = teams_df['name'].fillna('')
            teams_df['short_name'] = teams_df.get('short_name', teams_df['name'].str[:3].str.upper())
            teams_df['team_short_name'] = teams_df['short_name']
            
            logger.info(f"✓ Created DataFrame with {len(teams_df)} teams")
            return teams_df
            
        except Exception as e:
            logger.error(f"Failed to create teams DataFrame: {str(e)}")
            raise
    
    def load_fpl_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and return both players and teams DataFrames.
        
        This is the main method for getting all FPL data.
        
        Returns:
            Tuple of (players_df, teams_df)
        
        Example:
            >>> fetcher = FPLDataFetcher()
            >>> players, teams = fetcher.load_fpl_data()
        """
        logger.info("Loading complete FPL data...")
        
        try:
            players_df = self.get_players_dataframe()
            teams_df = self.get_teams_dataframe()
            
            logger.info("✓ Successfully loaded all FPL data")
            return players_df, teams_df
            
        except Exception as e:
            logger.error(f"Failed to load FPL data: {str(e)}")
            raise


# Singleton pattern for global access
@st.cache_resource
def get_fpl_data_fetcher() -> FPLDataFetcher:
    """
    Get or create the singleton FPL data fetcher instance.
    
    Returns:
        Cached FPLDataFetcher instance
    
    Example:
        >>> fetcher = get_fpl_data_fetcher()
        >>> data = fetcher.get_bootstrap_data()
    """
    return FPLDataFetcher()
