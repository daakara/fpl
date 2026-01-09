"""
Price Change Predictor Service - Predict player price rises and falls
Based on FPL's price change algorithm using net transfers
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class PriceChangePredictorService:
    """
    Predicts player price changes based on transfer activity
    
    FPL Price Change Algorithm (approximate):
    - Price rises: When net transfers reach ~100k-150k (varies by ownership)
    - Price falls: When net transfers reach ~ -100k-150k (varies by ownership)
    - Higher ownership = easier to change price
    """
    
    # Thresholds (approximate - FPL doesn't publish exact algorithm)
    BASE_RISE_THRESHOLD = 100000  # Net transfers needed for price rise
    BASE_FALL_THRESHOLD = -100000  # Net transfers needed for price fall
    
    def __init__(self):
        """Initialize the price change predictor"""
        self.predictions = []
    
    def predict_price_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict which players will change price
        
        Args:
            df: Player dataframe with transfers data
            
        Returns:
            DataFrame with price change predictions
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to predict_price_changes")
            return df
        
        df = df.copy()
        
        # Calculate net transfers
        if 'transfers_in' in df.columns and 'transfers_out' in df.columns:
            df['net_transfers'] = df['transfers_in'] - df['transfers_out']
        else:
            logger.warning("Missing transfer data for price predictions")
            return df
        
        # Calculate net transfers this gameweek
        if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
            df['net_transfers_event'] = df['transfers_in_event'] - df['transfers_out_event']
        else:
            df['net_transfers_event'] = 0
        
        # Calculate ownership factor (higher ownership = easier price change)
        if 'selected_by_percent' in df.columns:
            df['ownership_factor'] = df['selected_by_percent'] / 10  # Scale factor
        else:
            df['ownership_factor'] = 1.0
        
        # Adjusted thresholds based on ownership
        df['rise_threshold'] = self.BASE_RISE_THRESHOLD / (1 + df['ownership_factor'] * 0.1)
        df['fall_threshold'] = self.BASE_FALL_THRESHOLD / (1 + df['ownership_factor'] * 0.1)
        
        # Calculate price change probability (0-100)
        df['price_change_probability'] = 0
        
        # Rising players
        rise_mask = df['net_transfers_event'] > 0
        df.loc[rise_mask, 'price_change_probability'] = (
            (df.loc[rise_mask, 'net_transfers_event'] / df.loc[rise_mask, 'rise_threshold']) * 100
        ).clip(0, 100)
        
        # Falling players
        fall_mask = df['net_transfers_event'] < 0
        df.loc[fall_mask, 'price_change_probability'] = (
            (abs(df.loc[fall_mask, 'net_transfers_event']) / abs(df.loc[fall_mask, 'fall_threshold'])) * 100
        ).clip(0, 100)
        
        # Predict price change direction
        df['predicted_price_change'] = 0
        df.loc[df['price_change_probability'] > 80, 'predicted_price_change'] = 1  # Likely rise
        df.loc[(df['price_change_probability'] > 50) & (df['predicted_price_change'] == 0), 'predicted_price_change'] = 1  # Possible rise
        df.loc[(df['net_transfers_event'] < 0) & (df['price_change_probability'] > 80), 'predicted_price_change'] = -1  # Likely fall
        
        # Add prediction confidence
        df['prediction_confidence'] = 'Low'
        df.loc[df['price_change_probability'] > 50, 'prediction_confidence'] = 'Medium'
        df.loc[df['price_change_probability'] > 80, 'prediction_confidence'] = 'High'
        
        logger.info(f"Predicted price changes for {len(df)} players")
        
        return df
    
    def get_rising_players(self, df: pd.DataFrame, min_probability: float = 50) -> pd.DataFrame:
        """
        Get players likely to rise in price
        
        Args:
            df: Player dataframe with predictions
            min_probability: Minimum probability threshold (0-100)
            
        Returns:
            DataFrame of rising players sorted by probability
        """
        if 'price_change_probability' not in df.columns:
            df = self.predict_price_changes(df)
        
        rising = df[
            (df['net_transfers_event'] > 0) &
            (df['price_change_probability'] >= min_probability)
        ].copy()
        
        return rising.sort_values('price_change_probability', ascending=False)
    
    def get_falling_players(self, df: pd.DataFrame, min_probability: float = 50) -> pd.DataFrame:
        """
        Get players likely to fall in price
        
        Args:
            df: Player dataframe with predictions
            min_probability: Minimum probability threshold (0-100)
            
        Returns:
            DataFrame of falling players sorted by probability
        """
        if 'price_change_probability' not in df.columns:
            df = self.predict_price_changes(df)
        
        falling = df[
            (df['net_transfers_event'] < 0) &
            (df['price_change_probability'] >= min_probability)
        ].copy()
        
        return falling.sort_values('price_change_probability', ascending=False)
    
    def get_price_change_alerts(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Get categorized price change alerts
        
        Args:
            df: Player dataframe
            
        Returns:
            Dictionary with 'urgent_rises', 'urgent_falls', 'watch_rises', 'watch_falls'
        """
        df = self.predict_price_changes(df)
        
        return {
            'urgent_rises': self.get_rising_players(df, min_probability=80),
            'urgent_falls': self.get_falling_players(df, min_probability=80),
            'watch_rises': self.get_rising_players(df, min_probability=50).head(20),
            'watch_falls': self.get_falling_players(df, min_probability=50).head(20)
        }
    
    def calculate_transfer_momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate transfer momentum (trend over recent gameweeks)
        
        Args:
            df: Player dataframe
            
        Returns:
            DataFrame with momentum metrics
        """
        df = df.copy()
        
        # Calculate momentum as percentage of total transfers
        if 'transfers_in' in df.columns:
            total_transfers = df['transfers_in'].sum()
            if total_transfers > 0:
                df['transfer_momentum'] = (df['transfers_in'] / total_transfers) * 100
            else:
                df['transfer_momentum'] = 0
        
        # Add momentum category
        df['momentum_category'] = 'Stable'
        df.loc[df.get('transfer_momentum', 0) > 2, 'momentum_category'] = 'Rising'
        df.loc[df.get('transfer_momentum', 0) > 5, 'momentum_category'] = 'Hot'
        
        # For players being transferred out
        if 'transfers_out' in df.columns:
            high_out = df['transfers_out'] > df['transfers_out'].quantile(0.75)
            df.loc[high_out, 'momentum_category'] = 'Falling'
        
        return df
    
    def get_price_targets(self, df: pd.DataFrame, budget: float = 100.0) -> pd.DataFrame:
        """
        Get players to target before price rises (within budget)
        
        Args:
            df: Player dataframe
            budget: Available budget in millions
            
        Returns:
            DataFrame of target players
        """
        df = self.predict_price_changes(df)
        
        # Filter for rising players within budget
        targets = df[
            (df['predicted_price_change'] == 1) &
            (df['price_change_probability'] > 60) &
            (df['now_cost'] / 10 <= budget)
        ].copy()
        
        # Add value metrics
        if 'form' in targets.columns:
            targets['value_potential'] = targets['form'] * targets['price_change_probability'] / 100
        
        return targets.sort_values('price_change_probability', ascending=False)
    
    def estimate_next_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estimate what the price will be after next change
        
        Args:
            df: Player dataframe with predictions
            
        Returns:
            DataFrame with estimated_next_price column
        """
        df = df.copy()
        
        if 'now_cost' not in df.columns:
            logger.warning("Missing now_cost for price estimation")
            return df
        
        if 'predicted_price_change' not in df.columns:
            df = self.predict_price_changes(df)
        
        # FPL prices change in £0.1m increments
        df['estimated_next_price'] = df['now_cost'] + (df['predicted_price_change'] * 1)
        
        # Add price change amount in £
        df['estimated_change_amount'] = df['predicted_price_change'] * 0.1
        
        return df
