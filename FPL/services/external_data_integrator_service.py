"""
External Data Integrator Service - Real-time data from external sources
Integrates injury news, press conferences, and other external data
"""

import pandas as pd
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

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
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def get_injury_news(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get injury and fitness news for players
        
        Args:
            df: Player dataframe
            
        Returns:
            DataFrame with enhanced injury information
        """
        df = df.copy()
        
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
    
    def get_press_conference_insights(self) -> List[Dict]:
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
