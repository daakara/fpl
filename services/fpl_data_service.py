"""
FPL Data Service - Handles all data loading and processing
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import warnings
import urllib3
from typing import Optional, Tuple, Dict, Any

from utils.error_handling import logger

# Suppress warnings
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@st.cache_resource
def get_fpl_service():
    """Get or create a cached FPL data service instance"""
    return FPLDataService()

class FPLDataService:
    """Service for loading and processing FPL data"""
    
    def __init__(self):
        logger.info("Initializing FPL Data Service...")
        self.base_url = "https://fantasy.premierleague.com/api"
        
    def test_connection(self):
        """Test the connection to the FPL API"""
        try:
            logger.info("Testing FPL API connection...")
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('https://', adapter)
            
            response = session.get(f"{self.base_url}/bootstrap-static/", 
                                verify=False, 
                                timeout=15)
            response.raise_for_status()
            logger.info("FPL API connection test successful")
            
        except requests.exceptions.Timeout:
            logger.error("FPL API connection test timed out")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"FPL API connection test failed: {str(e)}")
            raise
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def fetch_fpl_data(base_url: str) -> Dict:
        """Fetch FPL data from API with caching"""
        logger.info("Attempting to fetch FPL data from API...")
        
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('https://', adapter)

        response = session.get(f"{base_url}/bootstrap-static/", 
                            verify=False, 
                            timeout=10)
        response.raise_for_status()
        
        if not response.content:
            raise ValueError("Empty response received from FPL API")
            
        data = response.json()
        if not data or 'elements' not in data or 'teams' not in data:
            raise ValueError("Invalid data structure received from FPL API")
            
        logger.info("Successfully fetched FPL data.")
        return data

    def load_fpl_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and process FPL data"""
        try:
            # Use cached fetch method
            data = self.fetch_fpl_data(self.base_url)
            
            # Process teams data first
            teams_df = pd.DataFrame(data['teams'])
            if teams_df.empty:
                raise ValueError("No team data available")
                
            # Ensure required team columns exist
            teams_df['name'] = teams_df['name'].fillna('')
            teams_df['short_name'] = teams_df.get('short_name', teams_df['name'].str[:3].str.upper())
            teams_df['team_short_name'] = teams_df['short_name']
            
            # Create and process player DataFrame
            players_df = pd.DataFrame(data['elements'])
            if players_df.empty:
                raise ValueError("No player data available")
                
            # Convert numeric columns
            numeric_columns = [
                'total_points', 'now_cost', 'form', 'selected_by_percent', 
                'minutes', 'goals_scored', 'assists', 'clean_sheets',
                'bonus', 'bps', 'influence', 'creativity', 'threat', 
                'ict_index', 'points_per_game', 'value_form', 'value_season'
            ]
            
            for col in numeric_columns:
                if col in players_df.columns:
                    players_df[col] = pd.to_numeric(players_df[col], errors='coerce')
            
            # Add team info to players - only merge on essential columns
            teams_df_minimal = teams_df[['id', 'name', 'team_short_name']].copy()
            teams_df_minimal = teams_df_minimal.rename(columns={'id': 'team_id_match'})
            players_df = players_df.merge(
                teams_df_minimal,
                left_on='team',
                right_on='team_id_match',
                how='left',  # Use left join to keep all players
                suffixes=('', '_team')
            )
            # Drop the temporary matching column
            players_df = players_df.drop('team_id_match', axis=1, errors='ignore')
            
            # Verify critical columns exist
            if 'id' not in players_df.columns:
                logger.error("CRITICAL: 'id' column missing from players_df after merge!")
                logger.error(f"Available columns: {list(players_df.columns)}")
            else:
                logger.info(f"✓ Player 'id' column preserved. Total players: {len(players_df)}")
            
            # Handle any missing team names
            players_df['team_short_name'] = players_df['team_short_name'].fillna('UNK')
            
            # Add derived columns with error handling
            try:
                # Position mapping
                position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                players_df['position_name'] = players_df.get('element_type', 0).map(position_map).fillna('UNK')
                
                # Cost calculation
                players_df['cost_millions'] = players_df.get('now_cost', 0) / 10.0
                
                # Performance metrics with safe division
                total_points = players_df.get('total_points', 0).replace(0, 1)
                cost = players_df['cost_millions'].replace(0, 1)
                minutes = players_df.get('minutes', 0)
                
                players_df['points_per_mil'] = total_points / cost
                players_df['minutes_per_point'] = minutes / total_points
                
                # Handle other required columns with defaults
                players_df['points_per_game'] = players_df.get('points_per_game', 0)
                players_df['selected_by_percent'] = players_df.get('selected_by_percent', 0)
                players_df['form'] = players_df.get('form', 0)
                
                logger.info("Successfully processed all player metrics")
                
            except Exception as e:
                logger.error(f"Error processing player metrics: {e}")
                # Continue with partial data rather than failing completely
            
            logger.info("Successfully processed FPL data.")
            return players_df, teams_df
            
        except Exception as e:
            st.error(f"Error loading FPL data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()
    
    def load_fixture_data(self) -> pd.DataFrame:
        """Load fixture data from FPL API"""
        try:
            logger.info("Fetching fixture data...")
            response = requests.get(f"{self.base_url}/fixtures/", verify=False, timeout=30)
            response.raise_for_status()
            
            fixtures_data = response.json()
            fixtures_df = pd.DataFrame(fixtures_data)
            
            if fixtures_df.empty:
                logger.warning("No fixture data available")
                return pd.DataFrame()
            
            # Convert relevant columns to numeric
            numeric_cols = ['team_h_score', 'team_a_score', 'team_h_difficulty', 'team_a_difficulty']
            for col in numeric_cols:
                if col in fixtures_df.columns:
                    fixtures_df[col] = pd.to_numeric(fixtures_df[col], errors='coerce')
            
            logger.info("Successfully loaded fixture data")
            return fixtures_df
            
        except Exception as e:
            logger.error(f"Error loading fixture data: {e}")
            return pd.DataFrame()

    def _validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Comprehensive data validation and cleaning"""
        if df.empty:
            return df
        
        # Ensure all numeric columns are properly typed
        for col in self.numeric_columns:
            if col in df.columns:
                # Convert to numeric, handling any string values
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaN values with appropriate defaults
                if col in ['total_points', 'goals_scored', 'assists', 'clean_sheets', 'bonus', 'minutes']:
                    df[col] = df[col].fillna(0)
                elif col in ['form', 'selected_by_percent', 'points_per_game']:
                    df[col] = df[col].fillna(0.0)
                elif col == 'now_cost':
                    df[col] = df[col].fillna(40)  # Default minimum price
                else:
                    df[col] = df[col].fillna(0)
        
        # Validate calculated fields
        df['cost_millions'] = pd.to_numeric(df['cost_millions'], errors='coerce').fillna(4.0)
        df['points_per_million'] = pd.to_numeric(df['points_per_million'], errors='coerce').fillna(0.0)
        
        # Ensure no infinite values
        df = df.replace([np.inf, -np.inf], 0)
        
        # Validate string columns
        string_columns = ['web_name', 'first_name', 'second_name', 'team_name', 'team_short_name', 'position_name']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('Unknown')
        
        return df
    
    def _process_players_data(self, data):
        """Process and enhance players data"""
        players_df = pd.DataFrame(data['elements'])
        teams_df = pd.DataFrame(data['teams'])
        element_types_df = pd.DataFrame(data['element_types'])
        
        # Create lookup dictionaries
        team_lookup = dict(zip(teams_df['id'], teams_df['name']))
        team_short_lookup = dict(zip(teams_df['id'], teams_df['short_name']))
        position_lookup = dict(zip(element_types_df['id'], element_types_df['singular_name']))
        
        # Add team and position information
        players_df['team_name'] = players_df['team'].map(team_lookup)
        players_df['team_short_name'] = players_df['team'].map(team_short_lookup)
        players_df['position_name'] = players_df['element_type'].map(position_lookup)
        
        # Fill missing values
        players_df['team_name'] = players_df['team_name'].fillna('Unknown Team')
        players_df['team_short_name'] = players_df['team_short_name'].fillna('UNK')
        players_df['position_name'] = players_df['position_name'].fillna('Unknown Position')
        
        # Calculate derived metrics
        players_df['cost_millions'] = players_df['now_cost'] / 10
        players_df['points_per_million'] = np.where(
            players_df['cost_millions'] > 0,
            players_df['total_points'] / players_df['cost_millions'],
            0
        ).round(2)
        
        # Ensure numeric columns
        players_df['form'] = pd.to_numeric(players_df.get('form', 0), errors='coerce').fillna(0.0)
        players_df['selected_by_percent'] = pd.to_numeric(players_df.get('selected_by_percent', 0), errors='coerce').fillna(0.0)
        
        return players_df
    
    def _process_teams_data(self, data):
        """Process teams data"""
        teams_df = pd.DataFrame(data['teams'])
        return teams_df
    
    def get_current_gameweek(self):
        """Get current gameweek from FPL API"""
        try:
            url = f"{self.base_url}/bootstrap-static/"
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            events = data.get('events', [])
            current_event = next((event for event in events if event['is_current']), None)
            return current_event['id'] if current_event else 1
        except:
            return 1
    
    def load_team_data(self, team_id, gameweek=None):
        """Load specific FPL team data"""
        try:
            # Validate team_id
            try:
                team_id = int(team_id)
                if team_id <= 0:
                    raise ValueError("Team ID must be a positive number")
            except (ValueError, TypeError):
                raise ValueError("Invalid team ID format. Please enter a valid number (e.g., 1437667)")

            if gameweek is None:
                gameweek = self.get_current_gameweek()
            
            logger.info(f"Loading data for team {team_id} for gameweek {gameweek}")
            
            # FPL API endpoints
            entry_url = f"{self.base_url}/entry/{team_id}/"
            picks_url = f"{self.base_url}/entry/{team_id}/event/{gameweek}/picks/"
            
            # Load entry data
            logger.info("Fetching team entry data...")
            entry_response = requests.get(entry_url, timeout=10, verify=False)
            entry_response.raise_for_status()
            entry_data = entry_response.json()
            
            if not entry_data:
                raise ValueError(f"No data found for team ID {team_id}. Please check if the ID is correct and the team is public.")
            
            # Load picks data
            logger.info("Fetching team picks data...")
            try:
                picks_response = requests.get(picks_url, timeout=10, verify=False)
                picks_response.raise_for_status()
                picks_data = picks_response.json()
                entry_data['picks'] = picks_data.get('picks', [])
                entry_data['gameweek'] = gameweek
                
                if not entry_data['picks']:
                    logger.warning(f"No picks found for team {team_id} in gameweek {gameweek}")
            except Exception as e:
                logger.error(f"Error fetching picks data: {str(e)}")
                entry_data['picks'] = []
                entry_data['gameweek'] = gameweek
            
            logger.info("Successfully loaded team data")
            return entry_data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Team ID {team_id} not found. Please check if the ID is correct.")
            elif e.response.status_code == 403:
                raise ValueError("Unable to access team data. Please ensure your team is set to public in FPL settings.")
            else:
                raise ValueError(f"Error accessing FPL API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading team data: {str(e)}")
            
        except Exception as e:
            st.error(f"Error loading team data: {str(e)}")
            return None
