"""
Data Transformer - Type conversion and data enrichment

This module handles all data transformations, type conversions, and
feature engineering for FPL data.

Classes:
    DataTransformer: Main transformation class

Example:
    >>> transformer = DataTransformer()
    >>> enriched_df = transformer.transform_players(raw_df, teams_df)
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

from utils.error_handling import logger


class DataTransformer:
    """
    Transform and enrich FPL data with derived features.
    
    This class provides:
    - Type conversion from API strings to proper types
    - Derived column creation (price_millions, value_score, etc.)
    - Data enrichment (team names, position names, etc.)
    - Feature engineering for analytics
    
    Example:
        >>> transformer = DataTransformer()
        >>> players = transformer.transform_players(raw_players, teams_df)
    """
    
    # Position mapping
    POSITION_MAP = {
        1: 'GKP',
        2: 'DEF',
        3: 'MID',
        4: 'FWD'
    }
    
    POSITION_NAMES = {
        1: 'Goalkeeper',
        2: 'Defender',
        3: 'Midfielder',
        4: 'Forward'
    }
    
    def __init__(self):
        """Initialize the data transformer."""
        logger.info("Initializing Data Transformer...")
    
    def convert_numeric_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Convert specified columns to numeric type.
        
        Args:
            df: DataFrame to process
            columns: List of column names to convert
        
        Returns:
            DataFrame with converted columns
        
        Example:
            >>> transformer = DataTransformer()
            >>> df = transformer.convert_numeric_columns(df, ['total_points', 'now_cost'])
        """
        logger.info(f"Converting {len(columns)} columns to numeric...")
        
        df_copy = df.copy()
        
        for col in columns:
            if col in df_copy.columns:
                df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
                # Fill NaN with 0 for numeric columns
                df_copy[col] = df_copy[col].fillna(0)
        
        logger.info(f"✓ Converted {len(columns)} columns to numeric")
        return df_copy
    
    def add_price_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price-related derived columns.
        
        Adds:
        - price_millions: Cost in millions (from now_cost / 10)
        - points_per_million: Total points per million cost
        - value_score: Alias for points_per_million
        
        Args:
            df: DataFrame with 'now_cost' column
        
        Returns:
            DataFrame with price columns added
        
        Example:
            >>> transformer = DataTransformer()
            >>> df = transformer.add_price_columns(df)
            >>> best_value = df.nlargest(10, 'points_per_million')
        """
        logger.info("Adding price-related columns...")
        
        df_copy = df.copy()
        
        if 'now_cost' in df_copy.columns:
            # Convert cost from tenths to millions
            df_copy['price_millions'] = df_copy['now_cost'] / 10.0
            
            # Calculate value metrics
            df_copy['points_per_million'] = np.where(
                df_copy['price_millions'] > 0,
                df_copy['total_points'] / df_copy['price_millions'],
                0
            )
            
            # Alias for compatibility
            df_copy['value_score'] = df_copy['points_per_million']
            
            logger.info("✓ Added price columns: price_millions, points_per_million, value_score")
        else:
            logger.warning("'now_cost' column not found, skipping price columns")
        
        return df_copy
    
    def add_position_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add position-related columns.
        
        Adds:
        - position: Short position code (GKP, DEF, MID, FWD)
        - position_name: Full position name
        
        Args:
            df: DataFrame with 'element_type' column
        
        Returns:
            DataFrame with position columns added
        
        Example:
            >>> transformer = DataTransformer()
            >>> df = transformer.add_position_columns(df)
            >>> forwards = df[df['position'] == 'FWD']
        """
        logger.info("Adding position columns...")
        
        df_copy = df.copy()
        
        if 'element_type' in df_copy.columns:
            df_copy['position'] = df_copy['element_type'].map(self.POSITION_MAP)
            df_copy['position_name'] = df_copy['element_type'].map(self.POSITION_NAMES)
            
            logger.info("✓ Added position columns: position, position_name")
        else:
            logger.warning("'element_type' column not found, skipping position columns")
        
        return df_copy
    
    def add_team_names(self, df: pd.DataFrame, teams_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add team name columns by joining with teams data.
        
        Adds:
        - team_name: Full team name
        - team_short_name: Short team code
        
        Args:
            df: DataFrame with 'team' column (team ID)
            teams_df: Teams DataFrame with id, name, short_name
        
        Returns:
            DataFrame with team name columns added
        
        Example:
            >>> transformer = DataTransformer()
            >>> df = transformer.add_team_names(players_df, teams_df)
        """
        logger.info("Adding team names...")
        
        df_copy = df.copy()
        
        if 'team' in df_copy.columns and not teams_df.empty:
            # Create team mapping
            team_map = teams_df.set_index('id')[['name', 'short_name']].to_dict()
            
            df_copy['team_name'] = df_copy['team'].map(team_map['name'])
            df_copy['team_short_name'] = df_copy['team'].map(team_map['short_name'])
            
            # Fill missing with 'Unknown'
            df_copy['team_name'] = df_copy['team_name'].fillna('Unknown')
            df_copy['team_short_name'] = df_copy['team_short_name'].fillna('UNK')
            
            logger.info("✓ Added team name columns")
        else:
            logger.warning("Cannot add team names - missing 'team' column or teams_df empty")
        
        return df_copy
    
    def add_per_90_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add per-90-minutes statistics.
        
        Adds:
        - goals_per_90: Goals scored per 90 minutes
        - assists_per_90: Assists per 90 minutes
        - points_per_90: Points per 90 minutes
        
        Args:
            df: DataFrame with minutes, goals_scored, assists, total_points
        
        Returns:
            DataFrame with per-90 stats added
        
        Example:
            >>> transformer = DataTransformer()
            >>> df = transformer.add_per_90_stats(df)
            >>> top_scorers_per_90 = df.nlargest(10, 'goals_per_90')
        """
        logger.info("Adding per-90 statistics...")
        
        df_copy = df.copy()
        
        if 'minutes' in df_copy.columns:
            # Calculate per-90 stats (avoid division by zero)
            minutes_90 = df_copy['minutes'] / 90.0
            minutes_90 = minutes_90.replace(0, np.nan)  # Avoid division by zero
            
            if 'goals_scored' in df_copy.columns:
                df_copy['goals_per_90'] = (df_copy['goals_scored'] / minutes_90).fillna(0)
            
            if 'assists' in df_copy.columns:
                df_copy['assists_per_90'] = (df_copy['assists'] / minutes_90).fillna(0)
            
            if 'total_points' in df_copy.columns:
                df_copy['points_per_90'] = (df_copy['total_points'] / minutes_90).fillna(0)
            
            logger.info("✓ Added per-90 statistics")
        else:
            logger.warning("'minutes' column not found, skipping per-90 stats")
        
        return df_copy
    
    def add_expected_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add expected stats columns (xG, xA, etc.).
        
        Adds normalized versions of:
        - xG_per_90: Expected goals per 90 minutes
        - xA_per_90: Expected assists per 90 minutes
        
        Args:
            df: DataFrame with expected stats
        
        Returns:
            DataFrame with expected stats per 90
        
        Example:
            >>> transformer = DataTransformer()
            >>> df = transformer.add_expected_stats(df)
        """
        logger.info("Adding expected statistics...")
        
        df_copy = df.copy()
        
        if 'minutes' in df_copy.columns:
            minutes_90 = df_copy['minutes'] / 90.0
            minutes_90 = minutes_90.replace(0, np.nan)
            
            if 'expected_goals' in df_copy.columns:
                df_copy['xG_per_90'] = (df_copy['expected_goals'] / minutes_90).fillna(0)
            
            if 'expected_assists' in df_copy.columns:
                df_copy['xA_per_90'] = (df_copy['expected_assists'] / minutes_90).fillna(0)
            
            logger.info("✓ Added expected statistics")
        
        return df_copy
    
    def add_form_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add form indicator columns.
        
        Adds:
        - form_category: 'Hot', 'Warm', 'Cold' based on form
        - is_inform: Boolean for players in good form
        
        Args:
            df: DataFrame with 'form' column
        
        Returns:
            DataFrame with form indicators
        
        Example:
            >>> transformer = DataTransformer()
            >>> df = transformer.add_form_indicators(df)
            >>> hot_players = df[df['form_category'] == 'Hot']
        """
        logger.info("Adding form indicators...")
        
        df_copy = df.copy()
        
        if 'form' in df_copy.columns:
            # Categorize form
            df_copy['form_category'] = pd.cut(
                df_copy['form'],
                bins=[-np.inf, 3, 6, np.inf],
                labels=['Cold', 'Warm', 'Hot']
            )
            
            # Boolean indicator for in-form players
            df_copy['is_inform'] = df_copy['form'] >= 6.0
            
            logger.info("✓ Added form indicators")
        else:
            logger.warning("'form' column not found, skipping form indicators")
        
        return df_copy
    
    def transform_players(
        self,
        players_df: pd.DataFrame,
        teams_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Complete transformation pipeline for players data.
        
        Applies all transformations:
        1. Numeric conversion
        2. Price columns
        3. Position columns
        4. Team names (if teams_df provided)
        5. Per-90 stats
        6. Expected stats
        7. Form indicators
        
        Args:
            players_df: Raw players DataFrame
            teams_df: Optional teams DataFrame for team names
        
        Returns:
            Fully transformed players DataFrame
        
        Example:
            >>> transformer = DataTransformer()
            >>> transformed = transformer.transform_players(raw_players, teams_df)
        """
        logger.info("Starting complete player transformation pipeline...")
        
        df = players_df.copy()
        
        # 1. Convert numeric columns
        numeric_cols = [
            'total_points', 'now_cost', 'form', 'selected_by_percent',
            'points_per_game', 'minutes', 'goals_scored', 'assists',
            'clean_sheets', 'bonus', 'bps', 'influence', 'creativity',
            'threat', 'ict_index', 'expected_goals', 'expected_assists',
            'expected_goal_involvements', 'expected_goals_conceded'
        ]
        df = self.convert_numeric_columns(df, numeric_cols)
        
        # 2. Add price columns
        df = self.add_price_columns(df)
        
        # 3. Add position columns
        df = self.add_position_columns(df)
        
        # 4. Add team names if teams data provided
        if teams_df is not None and not teams_df.empty:
            df = self.add_team_names(df, teams_df)
        
        # 5. Add per-90 stats
        df = self.add_per_90_stats(df)
        
        # 6. Add expected stats
        df = self.add_expected_stats(df)
        
        # 7. Add form indicators
        df = self.add_form_indicators(df)
        
        logger.info("✓ Player transformation pipeline complete")
        return df
    
    def transform_teams(self, teams_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform teams data.
        
        Args:
            teams_df: Raw teams DataFrame
        
        Returns:
            Transformed teams DataFrame
        
        Example:
            >>> transformer = DataTransformer()
            >>> transformed = transformer.transform_teams(raw_teams)
        """
        logger.info("Transforming teams data...")
        
        df = teams_df.copy()
        
        # Ensure required columns exist
        if 'name' in df.columns:
            df['name'] = df['name'].fillna('')
        
        if 'short_name' not in df.columns and 'name' in df.columns:
            df['short_name'] = df['name'].str[:3].str.upper()
        
        # Alias for compatibility
        if 'short_name' in df.columns:
            df['team_short_name'] = df['short_name']
        
        logger.info("✓ Teams transformation complete")
        return df


# Singleton for global access
_transformer_instance: Optional[DataTransformer] = None


def get_data_transformer() -> DataTransformer:
    """
    Get or create the singleton DataTransformer instance.
    
    Returns:
        DataTransformer instance
    
    Example:
        >>> transformer = get_data_transformer()
        >>> df = transformer.transform_players(raw_df)
    """
    global _transformer_instance
    if _transformer_instance is None:
        _transformer_instance = DataTransformer()
    return _transformer_instance
