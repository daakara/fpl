"""
Advanced Analytics Service
Provides Expected Points, Differential Finding, and Captaincy Analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from utils.performance_optimizer import cache_5min, measure_perf


class ExpectedPointsEngine:
    """Calculate expected points for players based on multiple factors"""
    
    def __init__(self):
        """Initialize the Expected Points Engine"""
        self.fixture_difficulty_weights = {
            1: 1.3,   # Very Easy
            2: 1.15,  # Easy
            3: 1.0,   # Average
            4: 0.85,  # Hard
            5: 0.7    # Very Hard
        }
    
    @cache_5min
    @measure_perf
    def calculate_xp(self, player_data: pd.Series, fixtures: Optional[List[Dict]] = None, 
                     gameweek: int = 1) -> float:
        """
        Calculate expected points for a player in next gameweek
        
        Factors considered:
        - Historical performance (form, points per game)
        - Opposition difficulty
        - Home/Away
        - Fixture congestion
        - Injury probability
        
        Args:
            player_data: Player's data as pandas Series
            fixtures: List of upcoming fixtures (optional)
            gameweek: Gameweek number
            
        Returns:
            Expected points value
        """
        # Base expected points from recent form
        form = float(player_data.get('form', 0))
        ppg = float(player_data.get('points_per_game', 0))
        minutes = int(player_data.get('minutes', 0))
        
        # Base xP from weighted average of form and PPG
        base_xp = (form * 0.6) + (ppg * 0.4)
        
        # Adjust for playing time probability
        if minutes < 500:
            playing_time_prob = 0.6
        elif minutes < 1000:
            playing_time_prob = 0.8
        else:
            playing_time_prob = 0.95
        
        # Adjust for injury/suspension
        chance_of_playing = player_data.get('chance_of_playing_next_round')
        if chance_of_playing is not None and chance_of_playing < 100:
            injury_factor = chance_of_playing / 100
        else:
            injury_factor = 1.0
        
        # Fixture difficulty adjustment (if fixtures available)
        fixture_factor = 1.0
        if fixtures and len(fixtures) > 0:
            next_fixture = fixtures[0]
            difficulty = next_fixture.get('difficulty', 3)
            fixture_factor = self.fixture_difficulty_weights.get(difficulty, 1.0)
            
            # Home advantage
            is_home = next_fixture.get('is_home', True)
            if is_home:
                fixture_factor *= 1.1
        
        # Position-based adjustments
        element_type = player_data.get('element_type', 3)
        position_multipliers = {
            1: 0.85,  # GK - lower ceiling
            2: 0.9,   # DEF - moderate
            3: 1.05,  # MID - higher ceiling
            4: 1.1    # FWD - highest ceiling
        }
        position_factor = position_multipliers.get(element_type, 1.0)
        
        # Calculate final xP
        xp = base_xp * playing_time_prob * injury_factor * fixture_factor * position_factor
        
        # Round to 1 decimal place
        return round(max(0, xp), 1)
    
    @cache_5min
    def calculate_xp_for_all_players(self, df: pd.DataFrame, 
                                      fixtures: Optional[Dict] = None) -> pd.DataFrame:
        """
        Calculate expected points for all players
        
        Args:
            df: DataFrame of all players
            fixtures: Dictionary mapping team_id to fixtures
            
        Returns:
            DataFrame with xP column added
        """
        df = df.copy()
        
        # Calculate xP for each player
        xp_values = []
        for idx, player in df.iterrows():
            team_id = player.get('team', None)
            player_fixtures = fixtures.get(team_id, []) if fixtures else None
            xp = self.calculate_xp(player, player_fixtures)
            xp_values.append(xp)
        
        df['expected_points'] = xp_values
        df['xp_vs_form'] = df['expected_points'] - df['form']
        
        return df


class DifferentialFinder:
    """Find differential players - low ownership, high potential"""
    
    @staticmethod
    @cache_5min
    @measure_perf
    def find_differentials(df: pd.DataFrame, 
                          ownership_max: float = 5.0,
                          min_points: int = 30,
                          min_form: float = 5.0,
                          max_price: Optional[float] = None) -> pd.DataFrame:
        """
        Find differential players for mini-league gains
        
        Args:
            df: DataFrame of all players
            ownership_max: Maximum ownership percentage
            min_points: Minimum total points
            min_form: Minimum form rating
            max_price: Maximum price in millions (optional)
            
        Returns:
            DataFrame of differential candidates sorted by value
        """
        df = df.copy()
        
        # Ensure numeric types
        df['selected_by_percent'] = pd.to_numeric(df['selected_by_percent'], errors='coerce').fillna(0)
        df['total_points'] = pd.to_numeric(df['total_points'], errors='coerce').fillna(0)
        df['form'] = pd.to_numeric(df['form'], errors='coerce').fillna(0)
        
        # Calculate price in millions
        if 'cost_millions' not in df.columns:
            df['cost_millions'] = df['now_cost'] / 10
        
        # Apply filters
        filtered = df[
            (df['selected_by_percent'] <= ownership_max) &
            (df['total_points'] >= min_points) &
            (df['form'] >= min_form) &
            (df['minutes'] > 300)  # At least some playing time
        ].copy()
        
        # Apply price filter if specified
        if max_price is not None:
            filtered = filtered[filtered['cost_millions'] <= max_price]
        
        # Calculate differential score
        # Higher form + lower ownership + better value = better differential
        filtered['differential_score'] = (
            filtered['form'] * 2.0 +  # Form is important
            (ownership_max - filtered['selected_by_percent']) * 0.5 +  # Reward low ownership
            (filtered['total_points'] / filtered['cost_millions']) * 1.5  # Value matters
        )
        
        # Sort by differential score
        result = filtered.sort_values('differential_score', ascending=False)
        
        # Select relevant columns
        display_cols = [
            'web_name', 'team', 'element_type', 'cost_millions',
            'total_points', 'form', 'selected_by_percent',
            'differential_score', 'minutes', 'goals_scored', 'assists'
        ]
        
        # Only include columns that exist
        display_cols = [col for col in display_cols if col in result.columns]
        
        return result[display_cols].reset_index(drop=True)
    
    @staticmethod
    def find_premium_differentials(df: pd.DataFrame) -> pd.DataFrame:
        """Find premium differentials (>£9.0m, <20% owned)"""
        return DifferentialFinder.find_differentials(
            df,
            ownership_max=20.0,
            min_points=50,
            min_form=6.0,
            max_price=None  # No price limit for premiums
        )
    
    @staticmethod
    def find_budget_differentials(df: pd.DataFrame) -> pd.DataFrame:
        """Find budget differentials (<£6.0m, <10% owned)"""
        return DifferentialFinder.find_differentials(
            df,
            ownership_max=10.0,
            min_points=25,
            min_form=5.0,
            max_price=6.0
        )


class CaptaincyAnalyzer:
    """Analyze captaincy options with expected value calculations"""
    
    def __init__(self, xp_engine: ExpectedPointsEngine):
        """Initialize with Expected Points Engine"""
        self.xp_engine = xp_engine
    
    @cache_5min
    @measure_perf
    def calculate_captain_ev(self, player_data: pd.Series, 
                            fixtures: Optional[List[Dict]] = None) -> Tuple[float, Dict]:
        """
        Calculate Expected Value for captaining a player
        
        EV = (xP × 2) × P(starting) - (Risk Factor)
        
        Args:
            player_data: Player's data as pandas Series
            fixtures: Upcoming fixtures
            
        Returns:
            Tuple of (EV score, details dictionary)
        """
        # Get expected points
        xp = self.xp_engine.calculate_xp(player_data, fixtures)
        
        # Calculate probability of starting
        minutes = int(player_data.get('minutes', 0))
        if minutes > 1500:
            prob_starting = 0.95
        elif minutes > 1000:
            prob_starting = 0.85
        elif minutes > 500:
            prob_starting = 0.7
        else:
            prob_starting = 0.5
        
        # Adjust for injury
        chance_of_playing = player_data.get('chance_of_playing_next_round')
        if chance_of_playing is not None and chance_of_playing < 100:
            prob_starting *= (chance_of_playing / 100)
        
        # Calculate risk factor
        # Higher risk for:
        # - Players with injury concerns
        # - Rotation risk (good squad depth)
        # - Poor recent form
        form = float(player_data.get('form', 0))
        risk_factor = 0
        
        if chance_of_playing and chance_of_playing < 100:
            risk_factor += (100 - chance_of_playing) / 50  # Max 2 points
        
        if form < 5.0:
            risk_factor += (5.0 - form) * 0.5  # Poor form penalty
        
        # Captain EV = (xP * 2 * prob_starting) - risk_factor
        captain_ev = (xp * 2 * prob_starting) - risk_factor
        
        details = {
            'expected_points': xp,
            'doubled_xp': xp * 2,
            'prob_starting': round(prob_starting, 2),
            'risk_factor': round(risk_factor, 2),
            'captain_ev': round(captain_ev, 2)
        }
        
        return round(captain_ev, 2), details
    
    @cache_5min
    def get_top_captain_options(self, df: pd.DataFrame, 
                                fixtures: Optional[Dict] = None,
                                top_n: int = 10,
                                min_ownership: float = 10.0) -> pd.DataFrame:
        """
        Get top captaincy options ranked by EV
        
        Args:
            df: DataFrame of all players
            fixtures: Dictionary mapping team_id to fixtures
            top_n: Number of top options to return
            min_ownership: Minimum ownership to consider
            
        Returns:
            DataFrame of top captain options
        """
        df = df.copy()
        
        # Filter for regular starters with decent ownership
        candidates = df[
            (df['selected_by_percent'] >= min_ownership) &
            (df['minutes'] > 500)
        ].copy()
        
        # Calculate captain EV for each candidate
        ev_scores = []
        details_list = []
        
        for idx, player in candidates.iterrows():
            team_id = player.get('team', None)
            player_fixtures = fixtures.get(team_id, []) if fixtures else None
            ev, details = self.calculate_captain_ev(player, player_fixtures)
            ev_scores.append(ev)
            details_list.append(details)
        
        candidates['captain_ev'] = ev_scores
        candidates['captain_xp'] = [d['doubled_xp'] for d in details_list]
        candidates['starting_prob'] = [d['prob_starting'] for d in details_list]
        candidates['risk_factor'] = [d['risk_factor'] for d in details_list]
        
        # Sort by EV
        result = candidates.sort_values('captain_ev', ascending=False).head(top_n)
        
        # Select relevant columns
        display_cols = [
            'web_name', 'team', 'element_type', 'cost_millions',
            'selected_by_percent', 'form', 'captain_ev', 'captain_xp',
            'starting_prob', 'risk_factor'
        ]
        
        # Handle cost_millions if it doesn't exist
        if 'cost_millions' not in result.columns:
            result['cost_millions'] = result['now_cost'] / 10
        
        display_cols = [col for col in display_cols if col in result.columns]
        
        return result[display_cols].reset_index(drop=True)
    
    @staticmethod
    def get_differential_captain_options(df: pd.DataFrame, 
                                        fixtures: Optional[Dict] = None,
                                        max_ownership: float = 15.0) -> pd.DataFrame:
        """
        Get differential captaincy options (lower ownership)
        
        Args:
            df: DataFrame of all players
            fixtures: Fixture data
            max_ownership: Maximum ownership percentage
            
        Returns:
            DataFrame of differential captain options
        """
        analyzer = CaptaincyAnalyzer(ExpectedPointsEngine())
        
        # Filter for differential captains
        differentials = df[
            (df['selected_by_percent'] <= max_ownership) &
            (df['form'] >= 6.0) &
            (df['minutes'] > 800)
        ].copy()
        
        if len(differentials) == 0:
            return pd.DataFrame()
        
        # Get top differential captain options
        return analyzer.get_top_captain_options(
            differentials, 
            fixtures, 
            top_n=10,
            min_ownership=0  # No minimum for differentials
        )


class AdvancedAnalyticsService:
    """Main service coordinating all advanced analytics features"""
    
    def __init__(self):
        """Initialize all analytics engines"""
        self.xp_engine = ExpectedPointsEngine()
        self.differential_finder = DifferentialFinder()
        self.captaincy_analyzer = CaptaincyAnalyzer(self.xp_engine)
    
    def get_comprehensive_analytics(self, df: pd.DataFrame, 
                                   fixtures: Optional[Dict] = None) -> Dict:
        """
        Get all analytics in one comprehensive package
        
        Args:
            df: Player DataFrame
            fixtures: Fixture data
            
        Returns:
            Dictionary with all analytics results
        """
        # Calculate expected points for all
        df_with_xp = self.xp_engine.calculate_xp_for_all_players(df, fixtures)
        
        # Find differentials
        all_differentials = self.differential_finder.find_differentials(df_with_xp)
        premium_diff = self.differential_finder.find_premium_differentials(df_with_xp)
        budget_diff = self.differential_finder.find_budget_differentials(df_with_xp)
        
        # Get captain options
        top_captains = self.captaincy_analyzer.get_top_captain_options(df_with_xp, fixtures)
        diff_captains = self.captaincy_analyzer.get_differential_captain_options(df_with_xp, fixtures)
        
        return {
            'players_with_xp': df_with_xp,
            'all_differentials': all_differentials,
            'premium_differentials': premium_diff,
            'budget_differentials': budget_diff,
            'top_captains': top_captains,
            'differential_captains': diff_captains
        }
