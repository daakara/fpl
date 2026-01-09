"""
Safe Data Conversion Utilities for FPL Analytics
Handles data type conversions with error-tolerant fallbacks
"""
import pandas as pd
import numpy as np
from typing import Any, Union, Optional


def safe_int_convert(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to integer with fallback.
    
    Args:
        value: Value to convert (can be string, float, int, or non-numeric)
        default: Default value to return if conversion fails
        
    Returns:
        Integer value or default
        
    Examples:
        >>> safe_int_convert("123")
        123
        >>> safe_int_convert("A")
        0
        >>> safe_int_convert(12.5)
        12
    """
    try:
        if pd.isna(value):
            return default
        numeric_value = pd.to_numeric(value, errors='coerce')
        if pd.isna(numeric_value):
            return default
        return int(numeric_value)
    except (ValueError, TypeError):
        return default


def safe_float_convert(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float with fallback.
    
    Args:
        value: Value to convert
        default: Default value to return if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        if pd.isna(value):
            return default
        numeric_value = pd.to_numeric(value, errors='coerce')
        if pd.isna(numeric_value):
            return default
        return float(numeric_value)
    except (ValueError, TypeError):
        return default


def safe_percentage_convert(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a percentage value (possibly with '%' symbol).
    
    Args:
        value: Value to convert (e.g., "45.2%" or "45.2" or 45.2)
        default: Default value to return if conversion fails
        
    Returns:
        Float percentage value or default
    """
    try:
        if pd.isna(value):
            return default
        
        # Remove % symbol if present
        if isinstance(value, str):
            value = value.strip().replace('%', '')
        
        numeric_value = pd.to_numeric(value, errors='coerce')
        if pd.isna(numeric_value):
            return default
        return float(numeric_value)
    except (ValueError, TypeError):
        return default


def clean_numeric_column(df: pd.DataFrame, column: str, 
                        dtype: str = 'float', 
                        default: Union[int, float] = 0) -> pd.DataFrame:
    """
    Clean and convert a DataFrame column to numeric type safely.
    
    Args:
        df: DataFrame to modify
        column: Column name to clean
        dtype: Target dtype ('int' or 'float')
        default: Default value for invalid entries
        
    Returns:
        DataFrame with cleaned column
    """
    if column not in df.columns:
        return df
    
    df = df.copy()
    df[column] = pd.to_numeric(df[column], errors='coerce').fillna(default)
    
    if dtype == 'int':
        df[column] = df[column].astype(int)
    else:
        df[column] = df[column].astype(float)
    
    return df


def format_price(value: Any, default: str = "£0.0m") -> str:
    """
    Format a price value (usually in tenths of millions).
    
    Args:
        value: Price value (e.g., 125 for £12.5m)
        default: Default string if conversion fails
        
    Returns:
        Formatted price string
    """
    try:
        if pd.isna(value):
            return default
        
        numeric_value = safe_float_convert(value, 0.0)
        price_in_millions = numeric_value / 10
        return f"£{price_in_millions:.1f}m"
    except Exception:
        return default


def format_points(value: Any, default: str = "0") -> str:
    """
    Format points value as string.
    
    Args:
        value: Points value
        default: Default string if conversion fails
        
    Returns:
        Formatted points string
    """
    points = safe_int_convert(value, 0)
    if points > 0:
        return str(points)
    return default


def format_ownership(value: Any, default: str = "0.0%") -> str:
    """
    Format ownership percentage.
    
    Args:
        value: Ownership value
        default: Default string if conversion fails
        
    Returns:
        Formatted ownership string
    """
    ownership = safe_percentage_convert(value, 0.0)
    return f"{ownership:.1f}%"


def validate_numeric_series(series: pd.Series, 
                           allow_negatives: bool = False) -> pd.Series:
    """
    Validate and clean a numeric pandas Series.
    
    Args:
        series: Series to validate
        allow_negatives: Whether to allow negative values
        
    Returns:
        Cleaned Series with invalid values replaced
    """
    # Convert to numeric, coercing errors to NaN
    clean_series = pd.to_numeric(series, errors='coerce')
    
    # Fill NaN with 0
    clean_series = clean_series.fillna(0)
    
    # Remove negatives if not allowed
    if not allow_negatives:
        clean_series = clean_series.clip(lower=0)
    
    return clean_series


def safe_dict_get(dictionary: dict, key: str, 
                  default: Any = None, 
                  convert_type: Optional[type] = None) -> Any:
    """
    Safely get a value from a dictionary with optional type conversion.
    
    Args:
        dictionary: Dictionary to get value from
        key: Key to retrieve
        default: Default value if key not found
        convert_type: Optional type to convert to (int, float, str)
        
    Returns:
        Value from dictionary or default
    """
    value = dictionary.get(key, default)
    
    if value is None or pd.isna(value):
        return default
    
    if convert_type is None:
        return value
    
    try:
        if convert_type == int:
            return safe_int_convert(value, default if isinstance(default, int) else 0)
        elif convert_type == float:
            return safe_float_convert(value, default if isinstance(default, float) else 0.0)
        elif convert_type == str:
            return str(value)
        else:
            return convert_type(value)
    except Exception:
        return default
