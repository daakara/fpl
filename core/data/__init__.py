"""
Core Data Module - Unified FPL Data Management

This module provides the single source of truth for all FPL data operations.

Components:
    - fetcher: API data fetching
    - validator: Data quality validation
    - transformer: Type conversion and enrichment

Example:
    >>> from core.data import get_fpl_data_fetcher, get_data_validator, get_data_transformer
    >>> 
    >>> # Fetch data
    >>> fetcher = get_fpl_data_fetcher()
    >>> players_df = fetcher.get_players_dataframe()
    >>> 
    >>> # Validate data
    >>> validator = get_data_validator()
    >>> clean_df = validator.validate_and_clean(players_df, 'players')
    >>> 
    >>> # Transform data
    >>> transformer = get_data_transformer()
    >>> enriched_df = transformer.transform_players(clean_df)
"""

from .fetcher import FPLDataFetcher, get_fpl_data_fetcher
from .validator import DataValidator, get_data_validator
from .transformer import DataTransformer, get_data_transformer

__all__ = [
    'FPLDataFetcher',
    'get_fpl_data_fetcher',
    'DataValidator',
    'get_data_validator',
    'DataTransformer',
    'get_data_transformer',
]
