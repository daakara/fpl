"""
External Data Integrator Service - Real-time data from external sources
Integrates injury news, press conferences, and other external data
"""

import pandas as pd
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class ExternalDataIntegratorService:
    """
    Integrates external data sources for enhanced FPL analysis
    - Injury news and fitness updates
    - Press conference insights
    - Bookmaker odds (for fixture predictions)
    - Weather data (for match conditions)
    """
    
    def __init__(self):
        """Initialize the external data integrator"""
        self.injury_data_cache = None
        self.transfer_data_cache = None
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self.injury_url = "https://www.premierleague.com/en/latest-player-injuries"
        self.transfer_url = "https://www.premierleague.com/en/transfers"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_injury_news(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get injury and fitness news for players
        Enhanced with real Premier League injury data
        
        Args:
            df: Player dataframe
            
        Returns:
            DataFrame with enhanced injury information
        """
        df = df.copy()
        
        # Fetch real injury data from Premier League
        try:
            pl_injuries = self.fetch_premier_league_injuries()
            
            # Create a mapping of player names to injury info
            injury_map = {}
            for injury in pl_injuries:
                injury_map[injury['player_name'].lower()] = injury
            
            # Add Premier League injury data to dataframe
            df['pl_injury_status'] = None
            df['pl_expected_return'] = None
            
            if 'web_name' in df.columns:
                for idx, row in df.iterrows():
                    player_name = str(row['web_name']).lower()
                    # Try exact match first
                    if player_name in injury_map:
                        df.at[idx, 'pl_injury_status'] = injury_map[player_name]['injury_status']
                        df.at[idx, 'pl_expected_return'] = injury_map[player_name]['expected_return']
                    else:
                        # Try partial match (last name)
                        for inj_name in injury_map.keys():
                            if player_name in inj_name or inj_name in player_name:
                                df.at[idx, 'pl_injury_status'] = injury_map[inj_name]['injury_status']
                                df.at[idx, 'pl_expected_return'] = injury_map[inj_name]['expected_return']
                                break
        except Exception as e:
            logger.warning(f"Could not fetch Premier League injury data: {e}")
        
        # Use FPL API data as primary source
        # Enhance with derived metrics
        
        # Calculate injury risk score based on multiple factors
        df['injury_risk_score'] = 0
        
        # Factor 1: Chance of playing
        if 'chance_of_playing_next_round' in df.columns:
            df['injury_risk_score'] += (100 - df['chance_of_playing_next_round']) / 10
        
        # Factor 2: Recent minutes (low minutes might indicate injury/rotation)
        if 'minutes' in df.columns:
            # Players with very low minutes in recent weeks
            low_minutes_mask = df['minutes'] < 90  # Less than one full game
            df.loc[low_minutes_mask, 'injury_risk_score'] += 2
        
        # Factor 3: News indicator
        if 'news' in df.columns:
            has_news = df['news'].str.len() > 0
            df.loc[has_news, 'injury_risk_score'] += 3
        
        # Factor 4: Status (injured, suspended, etc.)
        if 'status' in df.columns:
            df.loc[df['status'] == 'd', 'injury_risk_score'] += 5  # Doubtful
            df.loc[df['status'] == 'i', 'injury_risk_score'] += 7  # Injured
            df.loc[df['status'] == 's', 'injury_risk_score'] += 10  # Suspended
            df.loc[df['status'] == 'u', 'injury_risk_score'] += 8  # Unavailable
        
        # Factor 5: Premier League official injury status
        if 'pl_injury_status' in df.columns:
            has_pl_injury = df['pl_injury_status'].notna()
            df.loc[has_pl_injury, 'injury_risk_score'] += 5
        
        # Categorize injury risk
        df['injury_risk_category'] = 'Low'
        df.loc[df['injury_risk_score'] > 5, 'injury_risk_category'] = 'Medium'
        df.loc[df['injury_risk_score'] > 10, 'injury_risk_category'] = 'High'
        df.loc[df['injury_risk_score'] > 15, 'injury_risk_category'] = 'Critical'
        
        # Add injury impact on ownership
        if 'selected_by_percent' in df.columns:
            df['injury_ownership_impact'] = df['injury_risk_score'] * df['selected_by_percent']
        
        logger.info(f"Enhanced injury data for {len(df)} players")
        
        return df
    
    def get_fitness_alerts(self, df: pd.DataFrame) -> List[Dict]:
        """
        Get urgent fitness alerts for high-ownership players
        
        Args:
            df: Player dataframe
            
        Returns:
            List of alert dictionaries
        """
        df = self.get_injury_news(df)
        
        alerts = []
        
        # Alert for high-risk, high-ownership players
        high_risk = df[
            (df['injury_risk_category'].isin(['High', 'Critical'])) &
            (df.get('selected_by_percent', 0) > 10)
        ]
        
        for _, player in high_risk.iterrows():
            alerts.append({
                'player_name': player.get('web_name', 'Unknown'),
                'risk_level': player['injury_risk_category'],
                'ownership': player.get('selected_by_percent', 0),
                'news': player.get('news', 'No details available'),
                'chance_of_playing': player.get('chance_of_playing_next_round', 100),
                'alert_type': 'injury',
                'urgency': 'high' if player['injury_risk_score'] > 15 else 'medium'
            })
        
        return alerts
    
    def fetch_premier_league_injuries(self) -> List[Dict]:
        """
        Fetch real injury data from Premier League website
        
        Returns:
            List of injury dictionaries with player name, team, and status
        """
        # Check cache first
        if self.injury_data_cache and self.cache_timestamp:
            if datetime.now() - self.cache_timestamp < self.cache_duration:
                logger.info("Returning cached injury data")
                return self.injury_data_cache
        
        try:
            logger.info(f"Fetching injury data from {self.injury_url}")
            response = requests.get(self.injury_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            injuries = []
            
            # Parse the injury table
            # The structure may vary, so we'll use multiple approaches
            
            # Approach 1: Look for injury table/list
            injury_items = soup.find_all(['tr', 'div'], class_=re.compile('injury|player-status', re.I))
            
            for item in injury_items:
                try:
                    player_name = None
                    team_name = None
                    injury_status = None
                    expected_return = None
                    
                    # Extract player name
                    name_elem = item.find(['span', 'div', 'a'], class_=re.compile('player.*name', re.I))
                    if name_elem:
                        player_name = name_elem.get_text(strip=True)
                    
                    # Extract team name
                    team_elem = item.find(['span', 'div'], class_=re.compile('team', re.I))
                    if team_elem:
                        team_name = team_elem.get_text(strip=True)
                    
                    # Extract injury status
                    status_elem = item.find(['span', 'div'], class_=re.compile('status|injury', re.I))
                    if status_elem:
                        injury_status = status_elem.get_text(strip=True)
                    
                    # Extract expected return date
                    return_elem = item.find(['span', 'div'], class_=re.compile('return|date', re.I))
                    if return_elem:
                        expected_return = return_elem.get_text(strip=True)
                    
                    if player_name:
                        injuries.append({
                            'player_name': player_name,
                            'team': team_name or 'Unknown',
                            'injury_status': injury_status or 'Injured',
                            'expected_return': expected_return or 'TBD',
                            'source': 'Premier League Official',
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
                        })
                except Exception as e:
                    logger.debug(f"Error parsing injury item: {e}")
                    continue
            
            # Cache the results
            if injuries:
                self.injury_data_cache = injuries
                self.cache_timestamp = datetime.now()
                logger.info(f"Successfully fetched {len(injuries)} injury records")
            else:
                logger.warning("No injury data found - check website structure")
                # Return empty list but don't cache
                
            return injuries
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch injury data: {e}")
            # Return cached data if available, otherwise empty list
            return self.injury_data_cache if self.injury_data_cache else []
        except Exception as e:
            logger.error(f"Error parsing injury data: {e}")
            return self.injury_data_cache if self.injury_data_cache else []
    
    def fetch_premier_league_transfers(self) -> List[Dict]:
        """
        Fetch real transfer data from Premier League website
        
        Returns:
            List of transfer dictionaries with player, clubs, and transfer details
        """
        # Check cache first
        if self.transfer_data_cache and self.cache_timestamp:
            if datetime.now() - self.cache_timestamp < self.cache_duration:
                logger.info("Returning cached transfer data")
                return self.transfer_data_cache
        
        try:
            logger.info(f"Fetching transfer data from {self.transfer_url}")
            response = requests.get(self.transfer_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            transfers = []
            
            # Parse the transfer table
            transfer_items = soup.find_all(['tr', 'div'], class_=re.compile('transfer', re.I))
            
            for item in transfer_items:
                try:
                    player_name = None
                    from_club = None
                    to_club = None
                    transfer_type = None
                    transfer_fee = None
                    transfer_date = None
                    
                    # Extract player name
                    name_elem = item.find(['span', 'div', 'a'], class_=re.compile('player.*name', re.I))
                    if name_elem:
                        player_name = name_elem.get_text(strip=True)
                    
                    # Extract clubs
                    club_elems = item.find_all(['span', 'div'], class_=re.compile('club|team', re.I))
                    if len(club_elems) >= 2:
                        from_club = club_elems[0].get_text(strip=True)
                        to_club = club_elems[1].get_text(strip=True)
                    elif len(club_elems) == 1:
                        to_club = club_elems[0].get_text(strip=True)
                    
                    # Extract transfer type (loan, permanent, etc.)
                    type_elem = item.find(['span', 'div'], class_=re.compile('type', re.I))
                    if type_elem:
                        transfer_type = type_elem.get_text(strip=True)
                    
                    # Extract transfer fee
                    fee_elem = item.find(['span', 'div'], class_=re.compile('fee|price', re.I))
                    if fee_elem:
                        transfer_fee = fee_elem.get_text(strip=True)
                    
                    # Extract transfer date
                    date_elem = item.find(['span', 'div', 'time'], class_=re.compile('date', re.I))
                    if date_elem:
                        transfer_date = date_elem.get_text(strip=True)
                    
                    if player_name:
                        transfers.append({
                            'player_name': player_name,
                            'from_club': from_club or 'Unknown',
                            'to_club': to_club or 'Unknown',
                            'transfer_type': transfer_type or 'Permanent',
                            'transfer_fee': transfer_fee or 'Undisclosed',
                            'transfer_date': transfer_date or 'Recent',
                            'source': 'Premier League Official',
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
                        })
                except Exception as e:
                    logger.debug(f"Error parsing transfer item: {e}")
                    continue
            
            # Cache the results
            if transfers:
                self.transfer_data_cache = transfers
                self.cache_timestamp = datetime.now()
                logger.info(f"Successfully fetched {len(transfers)} transfer records")
            else:
                logger.warning("No transfer data found - check website structure")
                
            return transfers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch transfer data: {e}")
            return self.transfer_data_cache if self.transfer_data_cache else []
        except Exception as e:
            logger.error(f"Error parsing transfer data: {e}")
            return self.transfer_data_cache if self.transfer_data_cache else []
    
    def get_injury_news(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get simulated press conference insights
        (In production, this would scrape from official sources)
        
        Returns:
            List of press conference insights
        """
        # Simulated data - in production, integrate with real sources
        insights = [
            {
                'team': 'Manchester City',
                'manager': 'Pep Guardiola',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'key_points': [
                    'Haaland trained fully this week',
                    'De Bruyne needs assessment',
                    'Rotation expected due to fixture congestion'
                ]
            },
            {
                'team': 'Liverpool',
                'manager': 'Jürgen Klopp',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'key_points': [
                    'Salah available for selection',
                    'No new injury concerns',
                    'Full squad available'
                ]
            }
        ]
        
        logger.info(f"Retrieved {len(insights)} press conference insights")
        return insights
    
    def get_weather_data(self, fixture_id: int) -> Dict:
        """
        Get weather data for a fixture (affects player performance)
        (Simulated - in production, integrate with weather API)
        
        Args:
            fixture_id: FPL fixture ID
            
        Returns:
            Weather data dictionary
        """
        # Simulated weather data
        import random
        
        conditions = ['Clear', 'Cloudy', 'Rainy', 'Windy']
        
        return {
            'fixture_id': fixture_id,
            'condition': random.choice(conditions),
            'temperature': random.randint(5, 20),  # Celsius
            'wind_speed': random.randint(0, 30),  # km/h
            'precipitation': random.randint(0, 100),  # percentage
            'impact_on_play': 'Low' if random.random() > 0.3 else 'Medium'
        }
    
    def get_bookmaker_odds(self, team_id: int, opponent_id: int) -> Dict:
        """
        Get bookmaker odds for match outcomes
        (Simulated - in production, integrate with odds API)
        
        Args:
            team_id: Home team ID
            opponent_id: Away team ID
            
        Returns:
            Odds data dictionary
        """
        import random
        
        # Simulated odds (in production, use real bookmaker API)
        home_win = round(random.uniform(1.5, 4.0), 2)
        draw = round(random.uniform(2.5, 4.0), 2)
        away_win = round(random.uniform(1.5, 6.0), 2)
        
        # Over/Under goals
        over_2_5 = round(random.uniform(1.6, 2.2), 2)
        under_2_5 = round(random.uniform(1.6, 2.2), 2)
        
        # Both teams to score
        btts_yes = round(random.uniform(1.7, 2.1), 2)
        btts_no = round(random.uniform(1.7, 2.1), 2)
        
        return {
            'home_team_id': team_id,
            'away_team_id': opponent_id,
            'home_win_odds': home_win,
            'draw_odds': draw,
            'away_win_odds': away_win,
            'over_2_5_odds': over_2_5,
            'under_2_5_odds': under_2_5,
            'btts_yes_odds': btts_yes,
            'btts_no_odds': btts_no,
            'implied_home_win_probability': round(1 / home_win * 100, 1),
            'implied_away_win_probability': round(1 / away_win * 100, 1)
        }
    
    def get_team_news_summary(self, team_id: int, df: pd.DataFrame) -> Dict:
        """
        Get comprehensive team news summary
        
        Args:
            team_id: FPL team ID
            df: Player dataframe
            
        Returns:
            Team news summary dictionary
        """
        team_players = df[df['team'] == team_id].copy()
        team_players = self.get_injury_news(team_players)
        
        # Count players by injury risk
        risk_counts = team_players['injury_risk_category'].value_counts().to_dict()
        
        # Get injured players
        injured = team_players[team_players['injury_risk_category'].isin(['High', 'Critical'])]
        
        # Calculate team availability
        total_players = len(team_players)
        available_players = len(team_players[team_players['injury_risk_category'] == 'Low'])
        availability_percentage = (available_players / total_players * 100) if total_players > 0 else 0
        
        return {
            'team_id': team_id,
            'total_players': total_players,
            'available_players': available_players,
            'availability_percentage': round(availability_percentage, 1),
            'risk_distribution': risk_counts,
            'injured_players': injured[['web_name', 'injury_risk_category', 'news']].to_dict('records') if len(injured) > 0 else [],
            'summary': f"{available_players}/{total_players} players available ({round(availability_percentage, 1)}%)"
        }
    
    def get_rotation_risk(self, df: pd.DataFrame, fixture_congestion: bool = False) -> pd.DataFrame:
        """
        Assess rotation risk for players
        
        Args:
            df: Player dataframe
            fixture_congestion: Whether there's fixture congestion
            
        Returns:
            DataFrame with rotation risk scores
        """
        df = df.copy()
        
        df['rotation_risk'] = 0
        
        # Factor 1: High minutes recently (fatigue risk)
        if 'minutes' in df.columns:
            high_minutes = df['minutes'] > 270  # More than 3 full games
            df.loc[high_minutes, 'rotation_risk'] += 3
        
        # Factor 2: Age (older players more likely to be rested)
        if 'age' in df.columns:
            df.loc[df['age'] > 30, 'rotation_risk'] += 2
            df.loc[df['age'] > 33, 'rotation_risk'] += 2
        
        # Factor 3: Fixture congestion multiplier
        if fixture_congestion:
            df['rotation_risk'] = df['rotation_risk'] * 1.5
        
        # Factor 4: Team (some managers rotate more)
        # This would be enhanced with actual team rotation patterns
        
        # Categorize rotation risk
        df['rotation_risk_category'] = 'Low'
        df.loc[df['rotation_risk'] > 3, 'rotation_risk_category'] = 'Medium'
        df.loc[df['rotation_risk'] > 6, 'rotation_risk_category'] = 'High'
        
        return df
    
    def get_comprehensive_alerts(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Get all types of alerts in one call
        
        Args:
            df: Player dataframe
            
        Returns:
            Dictionary of categorized alerts
        """
        # Get injury alerts
        injury_alerts = self.get_fitness_alerts(df)
        
        # Get rotation risk
        df_with_rotation = self.get_rotation_risk(df, fixture_congestion=True)
        rotation_alerts = []
        
        high_rotation_risk = df_with_rotation[
            (df_with_rotation['rotation_risk_category'] == 'High') &
            (df_with_rotation.get('selected_by_percent', 0) > 5)
        ]
        
        for _, player in high_rotation_risk.iterrows():
            rotation_alerts.append({
                'player_name': player.get('web_name', 'Unknown'),
                'risk_level': player['rotation_risk_category'],
                'ownership': player.get('selected_by_percent', 0),
                'minutes': player.get('minutes', 0),
                'alert_type': 'rotation',
                'urgency': 'medium'
            })
        
        return {
            'injury_alerts': injury_alerts,
            'rotation_alerts': rotation_alerts,
            'press_conference_insights': self.get_press_conference_insights()
        }
