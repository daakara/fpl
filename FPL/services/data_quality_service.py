"""
Data Quality Service - Systematic validation and type enforcement
Prevents data type errors and ensures data consistency across the application
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DataQualityService:
    """
    Comprehensive data quality validation and transformation service
    Ensures data integrity throughout the application
    """
    
    # Expected schema for player data
    PLAYER_SCHEMA = {
        # Numeric fields that should be float
        'float_fields': [
            'form', 'points_per_game', 'selected_by_percent', 
            'value_form', 'value_season', 'influence', 'creativity', 
            'threat', 'ict_index', 'expected_goals', 'expected_assists',
            'expected_goal_involvements', 'expected_goals_conceded'
        ],
        # Numeric fields that should be int
        'int_fields': [
            'id', 'team', 'total_points', 'now_cost', 'minutes',
            'goals_scored', 'assists', 'clean_sheets', 'goals_conceded',
            'own_goals', 'penalties_saved', 'penalties_missed', 'yellow_cards',
            'red_cards', 'saves', 'bonus', 'bps', 'transfers_in', 
            'transfers_out', 'transfers_in_event', 'transfers_out_event',
            'event_points', 'code'
        ],
        # String fields
        'string_fields': [
            'first_name', 'second_name', 'web_name', 'news', 'status'
        ],
        # Boolean fields
        'bool_fields': [
            'in_dreamteam', 'special'
        ]
    }
    
    # Expected schema for team data
    TEAM_SCHEMA = {
        'int_fields': ['id', 'code', 'position', 'played', 'win', 'draw', 'loss', 'points'],
        'string_fields': ['name', 'short_name'],
        'float_fields': ['strength', 'strength_overall_home', 'strength_overall_away',
                        'strength_attack_home', 'strength_attack_away',
                        'strength_defence_home', 'strength_defence_away']
    }
    
    def __init__(self):
        """Initialize the data quality service"""
        self.validation_errors = []
        self.transformations_applied = []
    
    def validate_and_clean_players(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive validation and cleaning of player data
        
        Args:
            df: Raw player dataframe
            
        Returns:
            Cleaned and validated dataframe
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to validate_and_clean_players")
            return df
        
        logger.info(f"Starting data quality validation for {len(df)} players")
        self.validation_errors = []
        self.transformations_applied = []
        
        # 1. Type enforcement
        df = self._enforce_types(df, self.PLAYER_SCHEMA)
        
        # 2. Handle missing values
        df = self._handle_missing_values(df)
        
        # 3. Outlier detection and handling
        df = self._handle_outliers(df)
        
        # 4. Data consistency checks
        df = self._ensure_consistency(df)
        
        # 5. Add derived fields
        df = self._add_derived_fields(df)
        
        logger.info(f"Data quality validation complete. Applied {len(self.transformations_applied)} transformations")
        if self.validation_errors:
            logger.warning(f"Found {len(self.validation_errors)} validation issues")
        
        return df
    
    def validate_and_clean_teams(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive validation and cleaning of team data
        
        Args:
            df: Raw team dataframe
            
        Returns:
            Cleaned and validated dataframe
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to validate_and_clean_teams")
            return df
        
        logger.info(f"Starting data quality validation for {len(df)} teams")
        
        # Type enforcement for teams
        df = self._enforce_types(df, self.TEAM_SCHEMA)
        
        # Handle missing values
        df = self._handle_missing_values(df, is_team_data=True)
        
        return df
    
    def _enforce_types(self, df: pd.DataFrame, schema: Dict) -> pd.DataFrame:
        """
        Enforce correct data types according to schema
        
        Args:
            df: DataFrame to process
            schema: Schema definition with field types
            
        Returns:
            DataFrame with correct types
        """
        df = df.copy()
        
        # Convert float fields
        for field in schema.get('float_fields', []):
            if field in df.columns:
                try:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    # Replace NaN with 0.0 for numeric fields
                    df[field] = df[field].fillna(0.0)
                    self.transformations_applied.append(f"Converted {field} to float")
                except Exception as e:
                    self.validation_errors.append(f"Failed to convert {field} to float: {e}")
        
        # Convert int fields
        for field in schema.get('int_fields', []):
            if field in df.columns:
                try:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    df[field] = df[field].fillna(0).astype(int)
                    self.transformations_applied.append(f"Converted {field} to int")
                except Exception as e:
                    self.validation_errors.append(f"Failed to convert {field} to int: {e}")
        
        # Convert string fields
        for field in schema.get('string_fields', []):
            if field in df.columns:
                try:
                    df[field] = df[field].astype(str).fillna('')
                    self.transformations_applied.append(f"Converted {field} to string")
                except Exception as e:
                    self.validation_errors.append(f"Failed to convert {field} to string: {e}")
        
        # Convert boolean fields
        for field in schema.get('bool_fields', []):
            if field in df.columns:
                try:
                    df[field] = df[field].astype(bool)
                    self.transformations_applied.append(f"Converted {field} to bool")
                except Exception as e:
                    self.validation_errors.append(f"Failed to convert {field} to bool: {e}")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame, is_team_data: bool = False) -> pd.DataFrame:
        """
        Handle missing values with appropriate strategies
        
        Args:
            df: DataFrame to process
            is_team_data: Whether this is team data (different handling)
            
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        if not is_team_data:
            # For player data
            # Fill missing form/points with 0
            for col in ['form', 'points_per_game', 'total_points', 'event_points']:
                if col in df.columns:
                    df[col] = df[col].fillna(0)
            
            # Fill missing player names with placeholder
            for col in ['first_name', 'second_name', 'web_name']:
                if col in df.columns:
                    df[col] = df[col].fillna('Unknown')
            
            # Fill missing news with empty string
            if 'news' in df.columns:
                df['news'] = df['news'].fillna('')
            
            # Fill missing status with 'a' (available)
            if 'status' in df.columns:
                df['status'] = df['status'].fillna('a')
            
            # Fill missing chance_of_playing with 100
            if 'chance_of_playing_next_round' in df.columns:
                df['chance_of_playing_next_round'] = df['chance_of_playing_next_round'].fillna(100)
            
            self.transformations_applied.append("Filled missing values in player data")
        else:
            # For team data
            for col in ['strength', 'strength_overall_home', 'strength_overall_away']:
                if col in df.columns:
                    df[col] = df[col].fillna(3)  # Default strength
            
            self.transformations_applied.append("Filled missing values in team data")
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect and handle outliers in numeric fields
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with outliers handled
        """
        df = df.copy()
        
        # Cap form at reasonable values (0-10 scale)
        if 'form' in df.columns:
            df['form'] = df['form'].clip(0, 10)
        
        # Cap selected_by_percent at 0-100
        if 'selected_by_percent' in df.columns:
            df['selected_by_percent'] = df['selected_by_percent'].clip(0, 100)
        
        # Cap ICT index at reasonable max (usually < 100)
        if 'ict_index' in df.columns:
            df['ict_index'] = df['ict_index'].clip(0, 150)
        
        # Ensure now_cost is positive
        if 'now_cost' in df.columns:
            df['now_cost'] = df['now_cost'].clip(lower=0)
        
        self.transformations_applied.append("Applied outlier handling")
        
        return df
    
    def _ensure_consistency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure data consistency (e.g., derived fields match)
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with consistency ensured
        """
        df = df.copy()
        
        # Ensure transfers_in >= transfers_in_event
        if 'transfers_in' in df.columns and 'transfers_in_event' in df.columns:
            df.loc[df['transfers_in_event'] > df['transfers_in'], 'transfers_in'] = \
                df.loc[df['transfers_in_event'] > df['transfers_in'], 'transfers_in_event']
        
        # Ensure transfers_out >= transfers_out_event
        if 'transfers_out' in df.columns and 'transfers_out_event' in df.columns:
            df.loc[df['transfers_out_event'] > df['transfers_out'], 'transfers_out'] = \
                df.loc[df['transfers_out_event'] > df['transfers_out'], 'transfers_out_event']
        
        # Ensure minutes <= 90 * games_played (approximate check)
        # This is a soft check since players can play extra time
        
        self.transformations_applied.append("Applied consistency checks")
        
        return df
    
    def _add_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add useful derived fields for analysis
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with derived fields added
        """
        df = df.copy()
        
        # Add net transfers
        if 'transfers_in' in df.columns and 'transfers_out' in df.columns:
            df['net_transfers'] = df['transfers_in'] - df['transfers_out']
        
        # Add net transfers this gameweek
        if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
            df['net_transfers_event'] = df['transfers_in_event'] - df['transfers_out_event']
        
        # Add value score (total_points per million)
        if 'total_points' in df.columns and 'now_cost' in df.columns:
            df['value_score'] = df.apply(
                lambda row: row['total_points'] / (row['now_cost'] / 10) if row['now_cost'] > 0 else 0,
                axis=1
            )
        
        # Add minutes per game
        if 'minutes' in df.columns:
            # Approximate: assuming ~10 games played (adjust based on gameweek)
            df['minutes_per_game'] = df['minutes'] / (df['minutes'] / 90).clip(lower=1)
        
        # Add price in £ format
        if 'now_cost' in df.columns:
            df['price'] = df['now_cost'] / 10
        
        self.transformations_applied.append("Added derived fields")
        
        return df
    
    def get_quality_report(self) -> Dict:
        """
        Generate a data quality report
        
        Returns:
            Dictionary with quality metrics
        """
        return {
            'transformations_applied': len(self.transformations_applied),
            'validation_errors': len(self.validation_errors),
            'transformations_list': self.transformations_applied,
            'errors_list': self.validation_errors
        }
    
    def validate_dataframe_schema(self, df: pd.DataFrame, expected_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that dataframe has expected columns
        
        Args:
            df: DataFrame to validate
            expected_columns: List of expected column names
            
        Returns:
            Tuple of (is_valid, missing_columns)
        """
        if df is None or df.empty:
            return False, expected_columns
        
        missing = [col for col in expected_columns if col not in df.columns]
        return len(missing) == 0, missing
