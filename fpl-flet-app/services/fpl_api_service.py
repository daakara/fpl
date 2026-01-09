import httpx
import pandas as pd
import time
import asyncio
import logging
import functools
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

# Custom async decorator for retrying API calls
def async_retry_api_call(max_retries=AppConfig.RETRY_ATTEMPTS, delay=1, backoff=2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            m_delay = delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.TimeoutException, httpx.ConnectError) as e:
                    logger.warning(f"API call timed out or connection error: {e}. Attempt {attempt + 1}/{max_retries}")
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        logger.warning(f"API rate limit hit: {e}. Attempt {attempt + 1}/{max_retries}")
                    else:
                        logger.error(f"HTTP error during API call: {e}. Not retrying.")
                        raise
                except Exception as e:
                    logger.error(f"Unhandled exception during API call: {e}. Not retrying.")
                    raise

                if attempt < max_retries - 1:
                    await asyncio.sleep(m_delay)
                    m_delay *= backoff
            
            logger.error(f"API call failed after {max_retries} attempts.")
            raise ConnectionError("FPL API unavailable after multiple retries.")
        return wrapper
    return decorator

class FPLDataService:
    """Production-ready async data service for FPL API with caching and error handling"""
    
    BASE_URL = "https://fantasy.premierleague.com/api"
    
    def __init__(self):
        self._players_df = None
        self._teams_df = None
        self._fixtures_df = None
        self._my_team_data = None
        self._raw_bootstrap_data = None
        self._cache_timestamp = None
        self._last_error = None
        self._client = None
        self._cached_team_id = None  # Track which team is cached
    
    async def _get_client(self):
        """Get or create async HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=AppConfig.REQUEST_TIMEOUT)
        return self._client
    
    async def close(self):
        """Close the HTTP client"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    @async_retry_api_call()
    async def get_players(self, force_refresh=False):
        """Get players data with caching and retry logic"""
        # Check cache validity
        cache_valid = (self._cache_timestamp is not None and 
                      time.time() - self._cache_timestamp < AppConfig.CACHE_DURATION)
        
        if self._players_df is None or force_refresh or not cache_valid:
            logger.info("Fetching players data from API")
            client = await self._get_client()
            response = await client.get(f"{self.BASE_URL}/bootstrap-static/")
            response.raise_for_status()
            data = response.json()
            self._raw_bootstrap_data = data
            
            if 'elements' in data:
                df = pd.DataFrame(data['elements'])
                df['price'] = df['now_cost'] / 10
                df['value_score'] = (df['total_points'] / (df['now_cost'] / 10)).fillna(0)
                self._players_df = df
                self._cache_timestamp = time.time()
                self._last_error = None
                logger.info("Successfully loaded players data")
                
                # Also cache teams data
                if 'teams' in data:
                    self._teams_df = pd.DataFrame(data['teams'])
            else:
                self._players_df = pd.DataFrame()
        
        return self._players_df
    
    async def get_teams(self):
        if self._teams_df is None:
            await self.get_players()
        return self._teams_df if self._teams_df is not None else pd.DataFrame()
    
    @async_retry_api_call()
    async def get_fixtures(self, force_refresh=False):
        if self._fixtures_df is None or force_refresh:
            logger.info("Fetching fixtures data from API")
            client = await self._get_client()
            response = await client.get(f"{self.BASE_URL}/fixtures/")
            response.raise_for_status()
            data = response.json()
            self._fixtures_df = pd.DataFrame(data)
        
        return self._fixtures_df
    
    @async_retry_api_call()
    async def _fetch_team_data_api(self, team_id: int):
        logger.info(f"Fetching team info for ID: {team_id}")
        client = await self._get_client()
        response = await client.get(f"{self.BASE_URL}/entry/{team_id}/")
        response.raise_for_status()
        return response.json()

    @async_retry_api_call()
    async def _fetch_team_picks_api(self, team_id: int, current_event: int):
        logger.info(f"Fetching team picks for ID: {team_id}, event: {current_event}")
        client = await self._get_client()
        picks_response = await client.get(
            f"{self.BASE_URL}/entry/{team_id}/event/{current_event}/picks/"
        )
        picks_response.raise_for_status()
        return picks_response.json()

    async def get_my_team(self, team_id: int, force_refresh=False):
        """Get user's FPL team data"""
        # Check if we need to refresh (new team ID or forced refresh or no cached data)
        team_id_changed = self._cached_team_id != team_id
        
        if self._my_team_data is None or force_refresh or team_id_changed:
            try:
                logger.info(f"Fetching team data for team ID: {team_id}")
                team_data = await self._fetch_team_data_api(team_id)
                
                # Get current picks
                current_event = team_data.get('current_event', 1)
                picks_data = await self._fetch_team_picks_api(team_id, current_event)
                
                self._my_team_data = {
                    'team_info': team_data,
                    'picks': picks_data,
                    'current_event': current_event,
                    'team_id': team_id  # Store the team ID with the data
                }
                self._cached_team_id = team_id  # Update cached team ID
                logger.info(f"Successfully loaded team: {team_data.get('name', 'Unknown')}")
            except Exception as e:
                logger.error(f"Error fetching team {team_id}: {e}")
                self._my_team_data = None
                self._cached_team_id = None
        else:
            logger.info(f"Returning cached team data for team ID: {team_id}")
        
        return self._my_team_data
    
    def get_players_raw_bootstrap_data(self):
        """Returns the raw bootstrap-static data, ensuring it's fetched if not already."""
        if self._raw_bootstrap_data is None:
            # Note: This is a sync method that returns cached data only
            # If not cached, caller should await get_players() first
            logger.warning("get_players_raw_bootstrap_data called but data not cached. Call await get_players() first.")
            return None
                
        return self._raw_bootstrap_data
    
    def is_team_data_loaded(self) -> bool:
        """Checks if team data has been loaded."""
        return self._my_team_data is not None
    
    def get_loaded_team_data(self) -> dict:
        """Returns the currently loaded team data, or None if not loaded."""
        return self._my_team_data
    
    async def get_top_players(self, by='points', limit=5):
        df = await self.get_players()
        if df.empty:
            return pd.DataFrame()
        
        column_map = {'points': 'total_points', 'form': 'form', 'value': 'value_score'}
        column = column_map.get(by, 'total_points')
        
        if column in df.columns:
            return df.nlargest(limit, column)
        return df.head(limit)
    
    def clear_cache(self):
        self._players_df = None
        self._teams_df = None
        self._fixtures_df = None
        self._my_team_data = None
        self._raw_bootstrap_data = None
