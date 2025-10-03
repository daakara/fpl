"""
Advanced Caching Manager for FPL Analytics Dashboard
Provides intelligent caching strategies with performance monitoring
"""
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import hashlib
import json
import time
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import threading
from collections import defaultdict, deque

from utils.enhanced_performance_monitor import monitor_performance
from utils.error_handling import logger


class AdvancedCacheManager:
    """Advanced cache manager with intelligent strategies"""
    
    def __init__(self, cache_dir: str = "cache", max_memory_usage_mb: float = 100):
        """
        Initialize advanced cache manager
        
        Args:
            cache_dir: Directory for persistent cache storage
            max_memory_usage_mb: Maximum memory usage for in-memory cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_memory_usage = max_memory_usage_mb * 1024 * 1024  # Convert to bytes
        self.memory_cache = {}
        self.cache_metadata = {}
        self.access_times = defaultdict(deque)
        self.lock = threading.RLock()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_usage': 0,
            'disk_usage': 0
        }
        
        logger.info(f"Advanced Cache Manager initialized - Max memory: {max_memory_usage_mb}MB")
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate unique cache key for function call"""
        # Create a deterministic hash of function name and arguments
        key_data = {
            'function': func_name,
            'args': str(args),
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _get_memory_usage(self, obj: Any) -> int:
        """Estimate memory usage of an object"""
        try:
            if isinstance(obj, pd.DataFrame):
                return obj.memory_usage(deep=True).sum()
            elif isinstance(obj, np.ndarray):
                return obj.nbytes
            else:
                # Rough estimate using pickle
                return len(pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))
        except:
            return 1024  # Default fallback
    
    def _evict_lru_items(self, required_space: int):
        """Evict least recently used items to free space"""
        with self.lock:
            current_usage = sum(
                self._get_memory_usage(item['data']) 
                for item in self.memory_cache.values()
            )
            
            if current_usage + required_space <= self.max_memory_usage:
                return
            
            # Sort by access time (oldest first)
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]['last_access']
            )
            
            freed_space = 0
            for key, item in sorted_items:
                if freed_space >= required_space:
                    break
                
                item_size = self._get_memory_usage(item['data'])
                
                # Move to disk cache if valuable
                if item['access_count'] > 3:
                    self._save_to_disk(key, item['data'], item['metadata'])
                
                del self.memory_cache[key]
                freed_space += item_size
                self.stats['evictions'] += 1
            
            logger.info(f"Evicted {freed_space} bytes from memory cache")
    
    def _save_to_disk(self, key: str, data: Any, metadata: Dict):
        """Save data to disk cache"""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            metadata_file = self.cache_dir / f"{key}.meta"
            
            # Save data
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Save metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
            
            logger.debug(f"Saved cache key {key} to disk")
            
        except Exception as e:
            logger.error(f"Failed to save cache to disk: {str(e)}")
    
    def _load_from_disk(self, key: str) -> Optional[tuple]:
        """Load data from disk cache"""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            metadata_file = self.cache_dir / f"{key}.meta"
            
            if not (cache_file.exists() and metadata_file.exists()):
                return None
            
            # Load metadata first
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check if expired
            if self._is_expired(metadata):
                cache_file.unlink(missing_ok=True)
                metadata_file.unlink(missing_ok=True)
                return None
            
            # Load data
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"Loaded cache key {key} from disk")
            return data, metadata
            
        except Exception as e:
            logger.error(f"Failed to load cache from disk: {str(e)}")
            return None
    
    def _is_expired(self, metadata: Dict) -> bool:
        """Check if cached item is expired"""
        if 'expires_at' not in metadata:
            return False
        
        expires_at = datetime.fromisoformat(metadata['expires_at'])
        return datetime.now() > expires_at
    
    @monitor_performance()
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            # Try memory cache first
            if key in self.memory_cache:
                item = self.memory_cache[key]
                
                # Check expiration
                if self._is_expired(item['metadata']):
                    del self.memory_cache[key]
                    self.stats['misses'] += 1
                    return None
                
                # Update access info
                item['last_access'] = time.time()
                item['access_count'] += 1
                self.access_times[key].append(time.time())
                
                self.stats['hits'] += 1
                return item['data']
            
            # Try disk cache
            disk_result = self._load_from_disk(key)
            if disk_result:
                data, metadata = disk_result
                
                # Promote to memory cache if frequently accessed
                self._promote_to_memory(key, data, metadata)
                
                self.stats['hits'] += 1
                return data
            
            self.stats['misses'] += 1
            return None
    
    def _promote_to_memory(self, key: str, data: Any, metadata: Dict):
        """Promote disk cache item to memory cache"""
        data_size = self._get_memory_usage(data)
        
        # Check if we have space
        if data_size > self.max_memory_usage * 0.3:  # Don't cache items > 30% of max
            return
        
        # Evict items if needed
        self._evict_lru_items(data_size)
        
        # Add to memory cache
        self.memory_cache[key] = {
            'data': data,
            'metadata': metadata,
            'last_access': time.time(),
            'access_count': 1,
            'size': data_size
        }
    
    @monitor_performance()
    def set(self, key: str, data: Any, ttl_seconds: int = 3600, metadata: Optional[Dict] = None):
        """Set item in cache"""
        with self.lock:
            data_size = self._get_memory_usage(data)
            
            # Prepare metadata
            cache_metadata = metadata or {}
            cache_metadata.update({
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat(),
                'size': data_size,
                'ttl': ttl_seconds
            })
            
            # Decide cache strategy based on size and frequency
            if data_size > self.max_memory_usage * 0.3:
                # Large items go directly to disk
                self._save_to_disk(key, data, cache_metadata)
            else:
                # Try memory cache first
                self._evict_lru_items(data_size)
                
                self.memory_cache[key] = {
                    'data': data,
                    'metadata': cache_metadata,
                    'last_access': time.time(),
                    'access_count': 0,
                    'size': data_size
                }
    
    def smart_caching_decorator(self, ttl_seconds: int = 3600, cache_strategy: str = "adaptive"):
        """
        Smart caching decorator with adaptive strategies
        
        Args:
            ttl_seconds: Time to live in seconds
            cache_strategy: 'memory', 'disk', 'adaptive', or 'hybrid'
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function
                logger.debug(f"Cache miss for {func.__name__} - executing function")
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache result with metadata about execution
                metadata = {
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'args_hash': hashlib.md5(str(args).encode()).hexdigest()[:8],
                    'kwargs_hash': hashlib.md5(str(kwargs).encode()).hexdigest()[:8]
                }
                
                self.set(cache_key, result, ttl_seconds, metadata)
                
                return result
            
            # Add cache management methods to the wrapper
            wrapper.cache_clear = lambda: self.clear_function_cache(func.__name__)
            wrapper.cache_info = lambda: self.get_function_cache_info(func.__name__)
            
            return wrapper
        return decorator
    
    def clear_function_cache(self, func_name: str):
        """Clear cache for a specific function"""
        with self.lock:
            keys_to_remove = []
            
            # Memory cache
            for key, item in self.memory_cache.items():
                if item['metadata'].get('function') == func_name:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.memory_cache[key]
            
            # Disk cache
            for cache_file in self.cache_dir.glob("*.meta"):
                try:
                    with open(cache_file, 'r') as f:
                        metadata = json.load(f)
                    
                    if metadata.get('function') == func_name:
                        key = cache_file.stem
                        (self.cache_dir / f"{key}.pkl").unlink(missing_ok=True)
                        cache_file.unlink(missing_ok=True)
                        
                except Exception as e:
                    logger.error(f"Error clearing disk cache: {str(e)}")
            
            logger.info(f"Cleared cache for function: {func_name}")
    
    def get_function_cache_info(self, func_name: str) -> Dict[str, Any]:
        """Get cache info for a specific function"""
        memory_items = sum(
            1 for item in self.memory_cache.values() 
            if item['metadata'].get('function') == func_name
        )
        
        disk_items = sum(
            1 for meta_file in self.cache_dir.glob("*.meta")
            if self._get_function_from_meta_file(meta_file) == func_name
        )
        
        return {
            'function': func_name,
            'memory_items': memory_items,
            'disk_items': disk_items,
            'total_items': memory_items + disk_items
        }
    
    def _get_function_from_meta_file(self, meta_file: Path) -> Optional[str]:
        """Get function name from metadata file"""
        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            return metadata.get('function')
        except:
            return None
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self.lock:
            memory_usage = sum(
                item['size'] for item in self.memory_cache.values()
            )
            
            disk_usage = sum(
                f.stat().st_size for f in self.cache_dir.glob("*.pkl")
            )
            
            self.stats.update({
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'memory_items': len(self.memory_cache),
                'disk_items': len(list(self.cache_dir.glob("*.pkl"))),
                'hit_rate': self.stats['hits'] / max(1, self.stats['hits'] + self.stats['misses']) * 100
            })
            
            return self.stats.copy()
    
    def cleanup_expired(self):
        """Clean up expired cache items"""
        with self.lock:
            # Memory cache cleanup
            expired_keys = []
            for key, item in self.memory_cache.items():
                if self._is_expired(item['metadata']):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            # Disk cache cleanup
            for meta_file in self.cache_dir.glob("*.meta"):
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    
                    if self._is_expired(metadata):
                        key = meta_file.stem
                        (self.cache_dir / f"{key}.pkl").unlink(missing_ok=True)
                        meta_file.unlink(missing_ok=True)
                        
                except Exception as e:
                    logger.error(f"Error cleaning expired cache: {str(e)}")
            
            logger.info(f"Cleaned up {len(expired_keys)} expired items from memory cache")
    
    def render_streamlit_dashboard(self):
        """Render cache dashboard in Streamlit"""
        st.subheader("🗄️ Cache Management")
        
        stats = self.get_cache_statistics()
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Hit Rate", f"{stats['hit_rate']:.1f}%")
        
        with col2:
            st.metric("Memory Usage", f"{stats['memory_usage'] / 1024 / 1024:.1f} MB")
        
        with col3:
            st.metric("Disk Usage", f"{stats['disk_usage'] / 1024 / 1024:.1f} MB")
        
        with col4:
            st.metric("Total Items", f"{stats['memory_items'] + stats['disk_items']}")
        
        # Detailed metrics
        with st.expander("📊 Detailed Cache Statistics"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Memory Cache**")
                st.write(f"Items: {stats['memory_items']}")
                st.write(f"Usage: {stats['memory_usage'] / 1024 / 1024:.2f} MB")
                st.write(f"Hits: {stats['hits']}")
                st.write(f"Misses: {stats['misses']}")
            
            with col2:
                st.write("**Disk Cache**")
                st.write(f"Items: {stats['disk_items']}")
                st.write(f"Usage: {stats['disk_usage'] / 1024 / 1024:.2f} MB")
                st.write(f"Evictions: {stats['evictions']}")
        
        # Cache management actions
        if st.button("🧹 Clean Expired Items"):
            self.cleanup_expired()
            st.success("Cleaned up expired cache items")
            st.rerun()
        
        if st.button("🗑️ Clear All Cache"):
            self.clear_all_cache()
            st.success("Cleared all cache")
            st.rerun()
    
    def clear_all_cache(self):
        """Clear all cache items"""
        with self.lock:
            self.memory_cache.clear()
            
            # Clear disk cache
            for cache_file in self.cache_dir.glob("*"):
                cache_file.unlink(missing_ok=True)
            
            # Reset stats
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'memory_usage': 0,
                'disk_usage': 0
            }
            
            logger.info("Cleared all cache")


# Global cache manager instance
_cache_manager: Optional[AdvancedCacheManager] = None

def get_cache_manager() -> AdvancedCacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = AdvancedCacheManager()
    return _cache_manager

def smart_cache(ttl_seconds: int = 3600, cache_strategy: str = "adaptive"):
    """Convenience decorator for smart caching"""
    return get_cache_manager().smart_caching_decorator(ttl_seconds, cache_strategy)
