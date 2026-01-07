"""
Data Quality Validator - Ensures data integrity and type safety

This module provides comprehensive data validation for FPL data,
ensuring consistency, type safety, and data quality throughout the application.

Classes:
    DataValidator: Main validation class for all FPL data

Example:
    >>> validator = DataValidator()
    >>> validated_df = validator.validate_players_dataframe(raw_df)
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

from utils.error_handling import logger
from middleware.error_handling import FPLError, ErrorCategory, ErrorSeverity


class DataValidator:
    """
    Comprehensive data quality validation for FPL data.
    
    This class provides:
    - Schema validation
    - Type checking and enforcement
    - Missing value detection and handling
    - Outlier detection
    - Data consistency checks
    
    Example:
        >>> validator = DataValidator()
        >>> clean_df = validator.validate_and_clean(raw_df, 'players')
    """
    
    # Required columns for each data type
    REQUIRED_COLUMNS = {
        'players': [
            'id', 'web_name', 'team', 'element_type',
            'now_cost', 'total_points', 'form'
        ],
        'teams': [
            'id', 'name', 'short_name'
        ],
        'fixtures': [
            'id', 'event', 'team_h', 'team_a'
        ]
    }
    
    # Expected data types for columns
    COLUMN_TYPES = {
        'players': {
            'id': 'int',
            'web_name': 'str',
            'team': 'int',
            'element_type': 'int',
            'now_cost': 'numeric',
            'total_points': 'numeric',
            'form': 'numeric',
            'selected_by_percent': 'numeric',
            'minutes': 'numeric',
            'goals_scored': 'numeric',
            'assists': 'numeric',
            'clean_sheets': 'numeric',
            'bonus': 'numeric',
            'bps': 'numeric',
            'influence': 'numeric',
            'creativity': 'numeric',
            'threat': 'numeric',
            'ict_index': 'numeric'
        },
        'teams': {
            'id': 'int',
            'name': 'str',
            'short_name': 'str',
            'strength': 'int'
        }
    }
    
    # Valid ranges for numeric columns
    VALID_RANGES = {
        'total_points': (0, 500),
        'now_cost': (30, 150),  # £3.0m to £15.0m
        'form': (-10, 20),
        'selected_by_percent': (0, 100),
        'minutes': (0, 3420),  # Max minutes in a season
        'goals_scored': (0, 50),
        'assists': (0, 50),
        'clean_sheets': (0, 38),
        'ict_index': (0, 500)
    }
    
    def __init__(self):
        """Initialize the data validator."""
        logger.info("Initializing Data Validator...")
    
    def validate_schema(self, df: pd.DataFrame, data_type: str) -> Tuple[bool, List[str]]:
        """
        Validate that DataFrame has required columns.
        
        Args:
            df: DataFrame to validate
            data_type: Type of data ('players', 'teams', 'fixtures')
        
        Returns:
            Tuple of (is_valid, missing_columns)
        
        Example:
            >>> validator = DataValidator()
            >>> is_valid, missing = validator.validate_schema(df, 'players')
            >>> if not is_valid:
            ...     print(f"Missing columns: {missing}")
        """
        required = self.REQUIRED_COLUMNS.get(data_type, [])
        missing = [col for col in required if col not in df.columns]
        
        is_valid = len(missing) == 0
        
        if not is_valid:
            logger.warning(f"Schema validation failed for {data_type}: Missing columns {missing}")
        else:
            logger.info(f"✓ Schema validation passed for {data_type}")
        
        return is_valid, missing
    
    def enforce_types(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        Enforce correct data types for columns.
        
        Args:
            df: DataFrame to process
            data_type: Type of data ('players', 'teams')
        
        Returns:
            DataFrame with corrected types
        
        Example:
            >>> validator = DataValidator()
            >>> typed_df = validator.enforce_types(df, 'players')
        """
        logger.info(f"Enforcing data types for {data_type}...")
        
        df_copy = df.copy()
        type_spec = self.COLUMN_TYPES.get(data_type, {})
        
        for col, dtype in type_spec.items():
            if col not in df_copy.columns:
                continue
            
            try:
                if dtype == 'int':
                    df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce').fillna(0).astype(int)
                elif dtype == 'numeric':
                    df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce').fillna(0)
                elif dtype == 'str':
                    df_copy[col] = df_copy[col].astype(str).fillna('')
            except Exception as e:
                logger.warning(f"Failed to convert {col} to {dtype}: {str(e)}")
        
        logger.info(f"✓ Type enforcement complete for {data_type}")
        return df_copy
    
    def detect_outliers(self, df: pd.DataFrame, column: str) -> pd.Series:
        """
        Detect outliers in a numeric column using IQR method.
        
        Args:
            df: DataFrame containing the column
            column: Column name to check
        
        Returns:
            Boolean Series indicating outliers
        
        Example:
            >>> validator = DataValidator()
            >>> outliers = validator.detect_outliers(df, 'total_points')
            >>> outlier_count = outliers.sum()
        """
        if column not in df.columns:
            return pd.Series([False] * len(df))
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        
        if outliers.sum() > 0:
            logger.info(f"Detected {outliers.sum()} outliers in {column}")
        
        return outliers
    
    def validate_ranges(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Validate that numeric columns are within expected ranges.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Dictionary of {column: count_of_invalid_values}
        
        Example:
            >>> validator = DataValidator()
            >>> invalid = validator.validate_ranges(df)
            >>> if invalid:
            ...     print(f"Found invalid values: {invalid}")
        """
        logger.info("Validating numeric ranges...")
        
        invalid_counts = {}
        
        for col, (min_val, max_val) in self.VALID_RANGES.items():
            if col not in df.columns:
                continue
            
            invalid_mask = (df[col] < min_val) | (df[col] > max_val)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                invalid_counts[col] = invalid_count
                logger.warning(f"Found {invalid_count} invalid values in {col} (expected {min_val}-{max_val})")
        
        if not invalid_counts:
            logger.info("✓ All numeric ranges valid")
        
        return invalid_counts
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'smart') -> pd.DataFrame:
        """
        Handle missing values using specified strategy.
        
        Args:
            df: DataFrame to process
            strategy: 'zero', 'mean', 'median', or 'smart'
        
        Returns:
            DataFrame with missing values handled
        
        Example:
            >>> validator = DataValidator()
            >>> clean_df = validator.handle_missing_values(df, strategy='smart')
        """
        logger.info(f"Handling missing values (strategy={strategy})...")
        
        df_copy = df.copy()
        missing_before = df_copy.isnull().sum().sum()
        
        if strategy == 'zero':
            df_copy = df_copy.fillna(0)
        elif strategy == 'mean':
            df_copy = df_copy.fillna(df_copy.mean(numeric_only=True))
        elif strategy == 'median':
            df_copy = df_copy.fillna(df_copy.median(numeric_only=True))
        elif strategy == 'smart':
            # Smart strategy: use 0 for counts, mean for rates
            count_columns = [
                'total_points', 'minutes', 'goals_scored', 'assists',
                'clean_sheets', 'bonus', 'bps'
            ]
            rate_columns = [
                'form', 'selected_by_percent', 'points_per_game',
                'influence', 'creativity', 'threat', 'ict_index'
            ]
            
            for col in count_columns:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col].fillna(0)
            
            for col in rate_columns:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col].fillna(df_copy[col].mean())
            
            # Fill remaining with 0
            df_copy = df_copy.fillna(0)
        
        missing_after = df_copy.isnull().sum().sum()
        logger.info(f"✓ Handled {missing_before - missing_after} missing values")
        
        return df_copy
    
    def validate_and_clean(
        self,
        df: pd.DataFrame,
        data_type: str,
        enforce_schema: bool = True,
        handle_missing: bool = True
    ) -> pd.DataFrame:
        """
        Complete validation and cleaning pipeline.
        
        Args:
            df: DataFrame to validate and clean
            data_type: Type of data ('players', 'teams', 'fixtures')
            enforce_schema: Whether to enforce required columns
            handle_missing: Whether to handle missing values
        
        Returns:
            Validated and cleaned DataFrame
        
        Raises:
            FPLError: If validation fails critically
        
        Example:
            >>> validator = DataValidator()
            >>> clean_df = validator.validate_and_clean(raw_df, 'players')
        """
        logger.info(f"Starting validation pipeline for {data_type}...")
        
        df_clean = df.copy()
        
        # 1. Schema validation
        if enforce_schema:
            is_valid, missing = self.validate_schema(df_clean, data_type)
            if not is_valid:
                raise FPLError(
                    f"Schema validation failed: Missing columns {missing}",
                    category=ErrorCategory.DATA,
                    severity=ErrorSeverity.HIGH
                )
        
        # 2. Type enforcement
        df_clean = self.enforce_types(df_clean, data_type)
        
        # 3. Handle missing values
        if handle_missing:
            df_clean = self.handle_missing_values(df_clean, strategy='smart')
        
        # 4. Validate ranges
        invalid_ranges = self.validate_ranges(df_clean)
        if invalid_ranges:
            logger.warning(f"Found invalid ranges in: {list(invalid_ranges.keys())}")
            # Cap values at valid ranges
            for col, (min_val, max_val) in self.VALID_RANGES.items():
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].clip(lower=min_val, upper=max_val)
        
        logger.info(f"✓ Validation pipeline complete for {data_type}")
        return df_clean
    
    def validate_consistency(self, players_df: pd.DataFrame, teams_df: pd.DataFrame) -> bool:
        """
        Validate consistency between players and teams data.
        
        Args:
            players_df: Players DataFrame
            teams_df: Teams DataFrame
        
        Returns:
            True if data is consistent
        
        Example:
            >>> validator = DataValidator()
            >>> is_consistent = validator.validate_consistency(players, teams)
        """
        logger.info("Validating data consistency...")
        
        # Check that all player team IDs exist in teams
        if 'team' in players_df.columns and 'id' in teams_df.columns:
            valid_team_ids = set(teams_df['id'].unique())
            player_team_ids = set(players_df['team'].unique())
            
            invalid_teams = player_team_ids - valid_team_ids
            if invalid_teams:
                logger.warning(f"Found players with invalid team IDs: {invalid_teams}")
                return False
        
        logger.info("✓ Data consistency validated")
        return True


# Singleton for global access
_validator_instance: Optional[DataValidator] = None


def get_data_validator() -> DataValidator:
    """
    Get or create the singleton DataValidator instance.
    
    Returns:
        DataValidator instance
    
    Example:
        >>> validator = get_data_validator()
        >>> clean_df = validator.validate_and_clean(df, 'players')
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = DataValidator()
    return _validator_instance
