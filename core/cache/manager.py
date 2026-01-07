"""
Unified Cache Manager - Centralized caching strategy

This module provides a single, consistent caching interface for the entire application,
with standardized TTL strategies and cache invalidation.

Classes:
    CacheManager: Central cache management
    CacheTTL: Standard TTL constants

Example:
    >>> from core.cache import get_cache_manager, CacheTTL
    >>> 
    >>> cache = get_cache_manager()
    >>> data = cache.get_or_fetch('players', fetch_func, ttl=CacheTTL.MEDIUM)
"""
import streamlit as st
from typing import Any, Callable, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
import logging

from utils.error_handling import logger


class CacheTTL:
    """
    Standard cache TTL (Time-To-Live) constants in seconds.
    
    Usage:
        >>> @cache_with_ttl(CacheTTL.SHORT)
        >>> def get_live_data():
        ...     return fetch_from_api()
    """
    
    # Live data - updates frequently
    VERY_SHORT = 60       # 1 minute (live scores, price changes)
    SHORT = 300           # 5 minutes (player form, ownership)
    
    # Medium volatility data
    MEDIUM = 900          # 15 minutes (player stats, team data)
    
    # Stable data
    LONG = 3600           # 1 hour (bootstrap data, fixtures)
    VERY_LONG = 7200      # 2 hours (historical data)
    
    # Static data
    PERMANENT = 86400     # 24 hours (teams, positions, constants)


class CacheManager:
    """
    Centralized cache management for FPL data.
    
    This manager provides:
    - Consistent caching strategy across the app
    - TTL-based cache invalidation
    - Manual cache clearing
    - Cache statistics and monitoring
    
    All caching uses Streamlit's built-in cache mechanisms for
    persistence across reruns and sessions.
    
    Example:
        >>> cache = CacheManager()
        >>> data = cache.get_or_compute('key', fetch_func, ttl=CacheTTL.MEDIUM)
    """
    
    def __init__(self):
        """Initialize the cache manager."""
        logger.info("Initializing Unified Cache Manager...")
        
        # Initialize cache stats in session state
        if 'cache_stats' not in st.session_state:
            st.session_state.cache_stats = {
                'hits': 0,
                'misses': 0,
                'invalidations': 0
            }
    
    @staticmethod
    def _generate_cache_key(*args, **kwargs) -> str:
        """
        Generate a consistent cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Hash string suitable for cache key
        
        Example:
            >>> key = CacheManager._generate_cache_key('players', team_id=5)
        """
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def clear_all_caches(self) -> None:
        """
        Clear all Streamlit caches.
        
        This will invalidate all cached data and force fresh fetches.
        Use sparingly as it impacts performance.
        
        Example:
            >>> cache = CacheManager()
            >>> cache.clear_all_caches()
        """
        logger.info("Clearing all caches...")
        
        st.cache_data.clear()
        st.cache_resource.clear()
        
        if 'cache_stats' in st.session_state:
            st.session_state.cache_stats['invalidations'] += 1
        
        logger.info("✓ All caches cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with hits, misses, and invalidations
        
        Example:
            >>> cache = CacheManager()
            >>> stats = cache.get_cache_stats()
            >>> print(f"Hit rate: {stats['hits'] / (stats['hits'] + stats['misses']):.2%}")
        """
        return st.session_state.get('cache_stats', {
            'hits': 0,
            'misses': 0,
            'invalidations': 0
        })
    
    def record_cache_hit(self) -> None:
        """Record a cache hit for statistics."""
        if 'cache_stats' in st.session_state:
            st.session_state.cache_stats['hits'] += 1
    
    def record_cache_miss(self) -> None:
        """Record a cache miss for statistics."""
        if 'cache_stats' in st.session_state:
            st.session_state.cache_stats['misses'] += 1


# Decorator factory for consistent caching
def cache_with_ttl(ttl: int = CacheTTL.MEDIUM, show_spinner: bool = False):
    """
    Decorator to cache function results with specified TTL.
    
    This is a convenience wrapper around Streamlit's @st.cache_data
    that uses our standardized TTL values.
    
    Args:
        ttl: Time-to-live in seconds (use CacheTTL constants)
        show_spinner: Whether to show loading spinner
    
    Returns:
        Decorated function with caching
    
    Example:
        >>> @cache_with_ttl(CacheTTL.SHORT)
        >>> def get_player_data(player_id):
        ...     return fetch_from_api(player_id)
    """
    def decorator(func: Callable) -> Callable:
        @st.cache_data(ttl=ttl, show_spinner=show_spinner)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cache_resource_with_ttl(ttl: int = CacheTTL.PERMANENT):
    """
    Decorator to cache resource objects (models, connections) with TTL.
    
    Use for expensive-to-create objects that should be shared across users:
    - Database connections
    - ML models
    - Service instances
    
    Args:
        ttl: Time-to-live in seconds
    
    Returns:
        Decorated function with resource caching
    
    Example:
        >>> @cache_resource_with_ttl(CacheTTL.PERMANENT)
        >>> def get_ml_model():
        ...     return load_expensive_model()
    """
    def decorator(func: Callable) -> Callable:
        @st.cache_resource(ttl=ttl)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Standard cache decorators for common use cases
cache_5min = cache_with_ttl(CacheTTL.SHORT)
cache_15min = cache_with_ttl(CacheTTL.MEDIUM)
cache_1hour = cache_with_ttl(CacheTTL.LONG)


# Singleton cache manager instance
_cache_manager_instance: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get or create the singleton CacheManager instance.
    
    Returns:
        CacheManager instance
    
    Example:
        >>> cache = get_cache_manager()
        >>> cache.clear_all_caches()
    """
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    return _cache_manager_instance


# Convenience functions for common caching patterns
def get_cached_data(
    key: str,
    fetch_func: Callable,
    ttl: int = CacheTTL.MEDIUM,
    *args,
    **kwargs
) -> Any:
    """
    Get data from cache or fetch if not cached.
    
    This is a functional interface to caching for cases where
    decorators are not convenient.
    
    Args:
        key: Unique identifier for this data
        fetch_func: Function to call if data not in cache
        ttl: Time-to-live in seconds
        *args: Arguments to pass to fetch_func
        **kwargs: Keyword arguments to pass to fetch_func
    
    Returns:
        Cached or freshly fetched data
    
    Example:
        >>> data = get_cached_data(
        ...     'player_123',
        ...     api.get_player,
        ...     CacheTTL.SHORT,
        ...     player_id=123
        ... )
    """
    @st.cache_data(ttl=ttl)
    def _cached_fetch(_key: str, *_args, **_kwargs):
        return fetch_func(*_args, **_kwargs)
    
    return _cached_fetch(key, *args, **kwargs)


def invalidate_cache_for_key(key: str) -> None:
    """
    Invalidate cache for a specific key.
    
    Note: Streamlit doesn't support selective cache invalidation easily,
    so this is a placeholder for future enhancement.
    
    Args:
        key: Cache key to invalidate
    
    Example:
        >>> invalidate_cache_for_key('player_123')
    """
    logger.warning(f"Selective cache invalidation not yet implemented for key: {key}")
    logger.info("Consider using cache_manager.clear_all_caches() instead")
