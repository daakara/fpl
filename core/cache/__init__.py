"""
Core Cache Module - Unified Caching Strategy

This module provides centralized cache management with consistent TTL strategies.

Components:
    - manager: Central cache manager
    - CacheTTL: Standard TTL constants
    - Decorators: Convenience decorators for caching

Example:
    >>> from core.cache import get_cache_manager, CacheTTL, cache_5min
    >>> 
    >>> # Using decorators
    >>> @cache_5min
    >>> def get_data():
    ...     return expensive_operation()
    >>> 
    >>> # Using cache manager
    >>> cache = get_cache_manager()
    >>> cache.clear_all_caches()
"""

from .manager import (
    CacheManager,
    CacheTTL,
    get_cache_manager,
    cache_with_ttl,
    cache_resource_with_ttl,
    cache_5min,
    cache_15min,
    cache_1hour,
    get_cached_data,
    invalidate_cache_for_key
)

__all__ = [
    'CacheManager',
    'CacheTTL',
    'get_cache_manager',
    'cache_with_ttl',
    'cache_resource_with_ttl',
    'cache_5min',
    'cache_15min',
    'cache_1hour',
    'get_cached_data',
    'invalidate_cache_for_key',
]
