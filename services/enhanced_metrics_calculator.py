"""
Enhanced Metrics Calculator for FPL Dashboard
Implements 12+ intelligent KPIs and advanced analytics
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedMetricsCalculator:
    """Calculate advanced FPL metrics and KPIs"""
    
    def __init__(self, players_df: Optional[pd.DataFrame] = None, teams_df: Optional[pd.DataFrame] = None):
        self.players_df = players_df.copy() if players_df is not None else pd.DataFrame()
        self.teams_df = teams_df.copy() if teams_df is not None else pd.DataFrame()
        if not self.players_df.empty:
            self._prepare_data()
    
    def set_data(self, players_df: pd.DataFrame, teams_df: pd.DataFrame):
        """Set or update the data for calculations"""
        self.players_df = players_df.copy()
        self.teams_df = teams_df.copy()
        self._prepare_data()
    
    def has_data(self) -> bool:
        """Check if data is available"""
        return not self.players_df.empty
    
    def _prepare_data(self):
        """Prepare and clean data for calculations"""
        # Ensure numeric columns
        numeric_cols = ['total_points', 'now_cost', 'selected_by_percent', 'form', 
                       'points_per_game', 'minutes', 'goals_scored', 'assists',
                       'clean_sheets', 'bonus', 'transfers_in_event', 'transfers_out_event']
        
        for col in numeric_cols:
            if col in self.players_df.columns:
                self.players_df[col] = pd.to_numeric(self.players_df[col], errors='coerce').fillna(0)
        
        # Calculate derived metrics
        self.players_df['price_millions'] = self.players_df['now_cost'] / 10
        self.players_df['points_per_million'] = np.where(
            self.players_df['price_millions'] > 0,
            self.players_df['total_points'] / self.players_df['price_millions'],
            0
        )
        self.players_df['value_score'] = self.players_df['points_per_million'] * 100
        
        # Calculate transfer balance
        if 'transfers_in_event' in self.players_df.columns and 'transfers_out_event' in self.players_df.columns:
            self.players_df['transfers_balance'] = (
                self.players_df['transfers_in_event'] - self.players_df['transfers_out_event']
            )
        else:
            self.players_df['transfers_balance'] = 0
    
    def calculate_primary_metrics(self) -> Dict:
        """Calculate primary KPI metrics row"""
        if self.players_df.empty:
            return {}
        
        try:
            # Filter active players (>300 minutes)
            active_players = self.players_df[self.players_df['minutes'] >= 300]
            
            # 1. Active Players Count
            active_count = len(active_players)
            
            # 2. Market Dynamics (price change velocity)
            price_change_velocity = self._calculate_price_velocity()
            
            # 3. Points Leader + Gap Analysis
            top_scorer = self.players_df.loc[self.players_df['total_points'].idxmax()]
            points_gap = top_scorer['total_points'] - self.players_df['total_points'].quantile(0.9)
            
            # 4. Value Matrix (best value by position)
            value_matrix = self._calculate_value_matrix()
            
            # 5. Form King (current form leader with streak)
            form_king = self._calculate_form_king()
            
            return {
                'active_players': {
                    'count': active_count,
                    'percentage': (active_count / len(self.players_df)) * 100
                },
                'market_dynamics': {
                    'velocity': price_change_velocity,
                    'trend': 'rising' if price_change_velocity > 0 else 'falling'
                },
                'points_leader': {
                    'player': f"{top_scorer['first_name']} {top_scorer['second_name']}",
                    'points': top_scorer['total_points'],
                    'gap_to_90th': points_gap
                },
                'value_matrix': value_matrix,
                'form_king': form_king
            }
        except Exception as e:
            logger.error(f"Error calculating primary metrics: {e}")
            return {}
    
    def calculate_secondary_metrics(self) -> Dict:
        """Calculate secondary KPI metrics row"""
        if self.players_df.empty:
            return {}
        
        try:
            # 1. Hot Streak Count (3+ consecutive strong games)
            hot_streak_count = self._calculate_hot_streaks()
            
            # 2. Transfer Velocity (net transfers in last 24h)
            transfer_velocity = self.players_df['transfers_balance'].sum()
            
            # 3. Bonus Point Kings
            bonus_kings = self._calculate_bonus_kings()
            
            # 4. Consistency Index
            consistency_index = self._calculate_consistency_index()
            
            return {
                'hot_streaks': hot_streak_count,
                'transfer_velocity': {
                    'net_transfers': transfer_velocity,
                    'most_transferred_in': self._get_top_transfers('in'),
                    'most_transferred_out': self._get_top_transfers('out')
                },
                'bonus_kings': bonus_kings,
                'consistency_index': consistency_index
            }
        except Exception as e:
            logger.error(f"Error calculating secondary metrics: {e}")
            return {}
    
    def _calculate_price_velocity(self) -> float:
        """Calculate market price change velocity"""
        # Simplified calculation - in reality would use historical price data
        transfer_impact = self.players_df['transfers_balance'].abs().sum()
        return transfer_impact / len(self.players_df)
    
    def _calculate_value_matrix(self) -> Dict:
        """Calculate best value players by position"""
        positions = self.players_df['element_type'].unique()
        value_matrix = {}
        
        for pos in positions:
            pos_players = self.players_df[self.players_df['element_type'] == pos]
            if not pos_players.empty:
                best_value = pos_players.loc[pos_players['points_per_million'].idxmax()]
                value_matrix[f'position_{pos}'] = {
                    'player': f"{best_value['first_name']} {best_value['second_name']}",
                    'value': best_value['points_per_million'],
                    'price': best_value['price_millions']
                }
        
        return value_matrix
    
    def _calculate_form_king(self) -> Dict:
        """Calculate current form leader with streak analysis"""
        # Sort by form and get top player
        form_sorted = self.players_df.sort_values('form', ascending=False)
        top_form = form_sorted.iloc[0]
        
        return {
            'player': f"{top_form['first_name']} {top_form['second_name']}",
            'form': top_form['form'],
            'points_last_games': top_form['form'] * 5,  # Approximate
            'streak_games': min(10, int(top_form['form']))  # Simplified streak calculation
        }
    
    def _calculate_hot_streaks(self) -> Dict:
        """Calculate players with hot streaks (3+ consecutive strong games)"""
        # Simplified hot streak calculation based on form
        hot_players = self.players_df[self.players_df['form'] >= 6.0]
        
        return {
            'count': len(hot_players),
            'players': [
                {
                    'name': f"{p['first_name']} {p['second_name']}",
                    'form': p['form'],
                    'position': p['element_type']
                }
                for _, p in hot_players.head(5).iterrows()
            ]
        }
    
    def _get_top_transfers(self, direction: str) -> List[Dict]:
        """Get top transferred in/out players"""
        column = f'transfers_{direction}_event'
        if column not in self.players_df.columns:
            return []
        
        top_transfers = self.players_df.nlargest(3, column)
        return [
            {
                'name': f"{p['first_name']} {p['second_name']}",
                'transfers': p[column],
                'price': p['price_millions']
            }
            for _, p in top_transfers.iterrows()
        ]
    
    def _calculate_bonus_kings(self) -> Dict:
        """Calculate top bonus point accumulators"""
        if 'bonus' not in self.players_df.columns:
            return {'count': 0, 'players': []}
        
        top_bonus = self.players_df.nlargest(5, 'bonus')
        
        return {
            'count': len(self.players_df[self.players_df['bonus'] > 0]),
            'players': [
                {
                    'name': f"{p['first_name']} {p['second_name']}",
                    'bonus': p['bonus'],
                    'bonus_per_game': p['bonus'] / max(1, p['minutes'] / 90)
                }
                for _, p in top_bonus.iterrows()
            ]
        }
    
    def _calculate_consistency_index(self) -> Dict:
        """Calculate consistency index (low variance, high average)"""
        # Simplified consistency calculation
        active_players = self.players_df[self.players_df['minutes'] >= 300]
        
        if active_players.empty:
            return {'average_score': 0, 'top_consistent': []}
        
        # Use form as proxy for consistency (in reality would use game-by-game data)
        avg_form = active_players['form'].mean()
        form_std = active_players['form'].std()
        
        # Find most consistent players (high form, low variance approximation)
        consistent_players = active_players[
            (active_players['form'] >= avg_form) & 
            (active_players['points_per_game'] >= active_players['points_per_game'].quantile(0.7))
        ].head(5)
        
        return {
            'average_score': avg_form,
            'league_consistency': 100 - (form_std * 10),  # Normalized consistency score
            'top_consistent': [
                {
                    'name': f"{p['first_name']} {p['second_name']}",
                    'form': p['form'],
                    'ppg': p['points_per_game']
                }
                for _, p in consistent_players.iterrows()
            ]
        }
    
    def calculate_advanced_analytics(self) -> Dict:
        """Calculate advanced analytics for Phase 2"""
        if self.players_df.empty:
            return {}
            
        try:
            return {
                'performance_trends': self._analyze_performance_trends(),
                'market_insights': self._analyze_market_insights(),
                'position_analysis': self._analyze_position_performance(),
                'fixture_impact': self._analyze_fixture_impact()
            }
        except Exception as e:
            logger.error(f"Error calculating advanced analytics: {e}")
            return {}
    
    def _analyze_performance_trends(self) -> Dict:
        """Analyze performance trends and patterns"""
        return {
            'rising_stars': self._find_rising_stars(),
            'falling_players': self._find_falling_players(),
            'breakout_candidates': self._find_breakout_candidates()
        }
    
    def _analyze_market_insights(self) -> Dict:
        """Analyze market trends and opportunities"""
        return {
            'undervalued_players': self._find_undervalued_players(),
            'overvalued_players': self._find_overvalued_players(),
            'price_change_predictions': self._predict_price_changes()
        }
    
    def _analyze_position_performance(self) -> Dict:
        """Analyze performance by position"""
        position_stats = {}
        
        for pos in self.players_df['element_type'].unique():
            pos_players = self.players_df[self.players_df['element_type'] == pos]
            
            position_stats[f'position_{pos}'] = {
                'avg_points': pos_players['total_points'].mean(),
                'avg_price': pos_players['price_millions'].mean(),
                'top_performer': pos_players.loc[pos_players['total_points'].idxmax()]['web_name'] if not pos_players.empty else 'N/A',
                'value_picks': len(pos_players[pos_players['points_per_million'] >= pos_players['points_per_million'].quantile(0.8)])
            }
        
        return position_stats
    
    def _analyze_fixture_impact(self) -> Dict:
        """Analyze fixture difficulty impact on performance"""
        # Simplified fixture analysis
        return {
            'easy_fixture_performers': self._find_easy_fixture_performers(),
            'difficult_fixture_performers': self._find_difficult_fixture_performers(),
            'fixture_dependent_players': self._find_fixture_dependent_players()
        }
    
    def _find_rising_stars(self) -> List[Dict]:
        """Find players with improving performance"""
        rising = self.players_df[
            (self.players_df['form'] >= 5.0) &
            (self.players_df['total_points'] >= self.players_df['total_points'].quantile(0.6)) &
            (self.players_df['selected_by_percent'] <= 10.0)
        ].head(5)
        
        return [
            {
                'name': f"{p['first_name']} {p['second_name']}",
                'form': p['form'],
                'ownership': p['selected_by_percent'],
                'value': p['points_per_million']
            }
            for _, p in rising.iterrows()
        ]
    
    def _find_falling_players(self) -> List[Dict]:
        """Find players with declining performance"""
        falling = self.players_df[
            (self.players_df['form'] <= 3.0) &
            (self.players_df['selected_by_percent'] >= 10.0)
        ].head(5)
        
        return [
            {
                'name': f"{p['first_name']} {p['second_name']}",
                'form': p['form'],
                'ownership': p['selected_by_percent'],
                'price': p['price_millions']
            }
            for _, p in falling.iterrows()
        ]
    
    def _find_breakout_candidates(self) -> List[Dict]:
        """Find potential breakout players"""
        breakout = self.players_df[
            (self.players_df['form'] >= 4.5) &
            (self.players_df['price_millions'] <= 7.0) &
            (self.players_df['minutes'] >= 200) &
            (self.players_df['selected_by_percent'] <= 5.0)
        ].head(5)
        
        return [
            {
                'name': f"{p['first_name']} {p['second_name']}",
                'form': p['form'],
                'price': p['price_millions'],
                'ownership': p['selected_by_percent'],
                'potential': p['points_per_million']
            }
            for _, p in breakout.iterrows()
        ]
    
    def _find_undervalued_players(self) -> List[Dict]:
        """Find undervalued players based on performance vs price"""
        undervalued = self.players_df[
            self.players_df['points_per_million'] >= self.players_df['points_per_million'].quantile(0.8)
        ].head(10)
        
        return [
            {
                'name': f"{p['first_name']} {p['second_name']}",
                'value_score': p['points_per_million'],
                'price': p['price_millions'],
                'total_points': p['total_points']
            }
            for _, p in undervalued.iterrows()
        ]
    
    def _find_overvalued_players(self) -> List[Dict]:
        """Find overvalued players"""
        overvalued = self.players_df[
            (self.players_df['price_millions'] >= 8.0) &
            (self.players_df['points_per_million'] <= self.players_df['points_per_million'].quantile(0.3))
        ].head(5)
        
        return [
            {
                'name': f"{p['first_name']} {p['second_name']}",
                'value_score': p['points_per_million'],
                'price': p['price_millions'],
                'ownership': p['selected_by_percent']
            }
            for _, p in overvalued.iterrows()
        ]
    
    def _predict_price_changes(self) -> Dict:
        """Predict potential price changes"""
        # Players likely to rise
        rise_candidates = self.players_df[
            self.players_df['transfers_balance'] >= self.players_df['transfers_balance'].quantile(0.9)
        ].head(5)
        
        # Players likely to fall
        fall_candidates = self.players_df[
            self.players_df['transfers_balance'] <= self.players_df['transfers_balance'].quantile(0.1)
        ].head(5)
        
        return {
            'likely_to_rise': [
                {
                    'name': f"{p['first_name']} {p['second_name']}",
                    'transfer_balance': p['transfers_balance'],
                    'probability': min(95, abs(p['transfers_balance']) / 50000 * 100)
                }
                for _, p in rise_candidates.iterrows()
            ],
            'likely_to_fall': [
                {
                    'name': f"{p['first_name']} {p['second_name']}",
                    'transfer_balance': p['transfers_balance'],
                    'probability': min(95, abs(p['transfers_balance']) / 50000 * 100)
                }
                for _, p in fall_candidates.iterrows()
            ]
        }
    
    def _find_easy_fixture_performers(self) -> List[Dict]:
        """Find players who perform well against easy fixtures"""
        # Simplified - would need fixture difficulty data
        return []
    
    def _find_difficult_fixture_performers(self) -> List[Dict]:
        """Find players who perform well against difficult fixtures"""
        # Simplified - would need fixture difficulty data
        return []
    
    def _find_fixture_dependent_players(self) -> List[Dict]:
        """Find players whose performance varies significantly with fixture difficulty"""
        # Simplified - would need fixture difficulty data
        return []
    
    def calculate_all_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all enhanced metrics for the given dataframe"""
        if df.empty:
            return df
        
        # Set data if not already set or if different data provided
        if self.players_df.empty or not df.equals(self.players_df):
            self.players_df = df.copy()
            if not self.players_df.empty:
                self._prepare_data()
        
        # Return the enhanced dataframe with all calculated metrics
        return self.players_df

print("✅ Enhanced Metrics Calculator created successfully!")
