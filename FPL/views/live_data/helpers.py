"""
Live Data Helpers - Utility functions and helper methods for live data processing.
"""
import pandas as pd
from utils.data_converters import safe_int_convert, safe_float_convert


class LiveDataHelpers:
    """Helper methods for live data page operations."""
    
    @staticmethod
    def safe_get_series_value(series, key, default=None):
        """Safely get a value from a pandas Series with fallback."""
        try:
            if key in series.index:
                return series[key]
            return default
        except (KeyError, AttributeError, TypeError):
            return default
    
    @staticmethod
    def safe_get_numeric(series, key, default=0):
        """Safely get a numeric value from a pandas Series."""
        value = LiveDataHelpers.safe_get_series_value(series, key, default)
        return safe_int_convert(value, default) if isinstance(default, int) else safe_float_convert(value, default)
