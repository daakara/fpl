"""
FPL Connection Manager
Handles all FPL API connections with robust error handling and SSL certificate management
"""

import requests
import urllib3
from typing import Optional, Dict, Any
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress SSL warnings globally for FPL API connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class FPLConnectionManager:
    """Centralized connection management for FPL API"""
    
    def __init__(self, base_url: str = "https://fantasy.premierleague.com/api"):
        self.base_url = base_url
        self.session = self._create_robust_session()
        
    def _create_robust_session(self) -> requests.Session:
        """Create a robust session that handles proxy and SSL issues"""
        session = requests.Session()
        
        # Configure aggressive retry strategy for connection issues
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,
            pool_maxsize=30
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers that work well with FPL API
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
        
        # Handle SSL issues in corporate environments
        session.verify = False
        
        return session
    
    def test_connection(self, timeout: int = 15) -> Dict[str, Any]:
        """
        Comprehensive connection test with detailed diagnostics
        Returns connection status and diagnostic information
        """
        result = {
            'success': False,
            'error': None,
            'response_time': None,
            'data_available': False,
            'players_count': 0,
            'teams_count': 0
        }
        
        try:
            start_time = time.time()
            
            logger.info("Testing FPL API connection...")
            response = self.session.get(
                f"{self.base_url}/bootstrap-static/",
                timeout=timeout
            )
            
            result['response_time'] = time.time() - start_time
            response.raise_for_status()
            
            # Parse and validate response
            data = response.json()
            result['data_available'] = True
            result['players_count'] = len(data.get('elements', []))
            result['teams_count'] = len(data.get('teams', []))
            result['success'] = True
            
            logger.info(f"FPL API connection successful - {result['players_count']} players, {result['teams_count']} teams")
            
        except requests.exceptions.SSLError as e:
            result['error'] = f"SSL Certificate Error: {str(e)}"
            logger.error(f"SSL error: {e}")
            
        except requests.exceptions.ProxyError as e:
            result['error'] = f"Proxy Error: {str(e)}"
            logger.error(f"Proxy error: {e}")
            
        except requests.exceptions.ConnectionError as e:
            result['error'] = f"Connection Error: {str(e)}"
            logger.error(f"Connection error: {e}")
            
        except requests.exceptions.Timeout as e:
            result['error'] = f"Timeout Error: {str(e)}"
            logger.error(f"Timeout error: {e}")
            
        except requests.exceptions.RequestException as e:
            result['error'] = f"Request Error: {str(e)}"
            logger.error(f"Request error: {e}")
            
        except Exception as e:
            result['error'] = f"Unexpected Error: {str(e)}"
            logger.error(f"Unexpected error: {e}")
        
        return result
    
    def get_data(self, endpoint: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get data from FPL API endpoint with robust error handling
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get data from {endpoint}: {e}")
            return None

# Global connection manager instance
connection_manager = FPLConnectionManager()

def get_fpl_connection() -> FPLConnectionManager:
    """Get the global FPL connection manager"""
    return connection_manager

def test_fpl_connection() -> Dict[str, Any]:
    """Quick connection test function"""
    return connection_manager.test_connection()
