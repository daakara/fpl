"""
Performance Optimization Utilities
Provides caching, lazy loading, and pagination helpers
"""

import streamlit as st
import pandas as pd
from functools import wraps
from typing import Any, Callable, Optional
import time
import hashlib


class PerformanceOptimizer:
    """Utilities for optimizing app performance"""
    
    @staticmethod
    def cache_expensive_calculation(ttl: int = 300, hash_funcs: dict = None):
        """
        Decorator for caching expensive calculations using session state
        Avoids issues with hashing service instances
        
        Args:
            ttl: Time to live in seconds (default: 5 minutes)
            hash_funcs: Ignored, kept for compatibility
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments (excluding unhashable objects)
                try:
                    # Try to create a hash from serializable args
                    serializable_args = []
                    for arg in args:
                        # Skip service instances and other complex objects
                        if hasattr(arg, '__dict__') and hasattr(arg, '__class__'):
                            continue
                        serializable_args.append(str(arg))
                    
                    args_hash = hashlib.md5(str(serializable_args).encode()).hexdigest()
                    cache_key = f"cache_{func.__module__}_{func.__name__}_{args_hash}"
                except:
                    # Fallback to simple cache key
                    cache_key = f"cache_{func.__module__}_{func.__name__}"
                
                # Check cache
                if cache_key in st.session_state:
                    cache_time = st.session_state.get(f'{cache_key}_timestamp', 0)
                    if time.time() - cache_time < ttl:
                        return st.session_state[cache_key]
                
                # Compute and cache
                result = func(*args, **kwargs)
                st.session_state[cache_key] = result
                st.session_state[f'{cache_key}_timestamp'] = time.time()
                return result
                    
            return wrapper
        return decorator
    
    @staticmethod
    def cache_resource(func: Callable) -> Callable:
        """
        Decorator for caching resources (models, connections, etc.)
        Resources are cached for the entire session using session state
        Avoids issues with hashing service instances
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create simple cache key
            cache_key = f"resource_{func.__module__}_{func.__name__}"
            
            if cache_key not in st.session_state:
                st.session_state[cache_key] = func(*args, **kwargs)
            
            return st.session_state[cache_key]
                
        return wrapper
    
    @staticmethod
    def lazy_import(module_name: str, package: Optional[str] = None):
        """
        Lazy import a module only when needed
        
        Args:
            module_name: Name of module to import
            package: Package name for relative imports
            
        Returns:
            Imported module
        """
        import importlib
        return importlib.import_module(module_name, package)
    
    @staticmethod
    def paginate_dataframe(
        df: pd.DataFrame,
        page_size: int = 50,
        page_key: str = "page"
    ) -> pd.DataFrame:
        """
        Paginate a large dataframe
        
        Args:
            df: DataFrame to paginate
            page_size: Number of rows per page
            page_key: Unique key for page number input
            
        Returns:
            Paginated subset of dataframe
        """
        if df.empty:
            return df
        
        total_pages = max(1, (len(df) - 1) // page_size + 1)
        
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col2:
            page = st.number_input(
                f"Page (1-{total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                key=page_key,
                help=f"Showing {page_size} rows per page"
            )
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(df))
        
        # Show pagination info
        with col3:
            st.info(f"Showing {start_idx + 1}-{end_idx} of {len(df)} rows")
        
        return df.iloc[start_idx:end_idx]
    
    @staticmethod
    def measure_performance(func: Callable) -> Callable:
        """
        Decorator to measure and log function performance
        
        Args:
            func: Function to measure
            
        Returns:
            Wrapped function that logs execution time
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Store in session state for monitoring
            if 'performance_metrics' not in st.session_state:
                st.session_state.performance_metrics = {}
            
            st.session_state.performance_metrics[func.__name__] = {
                'execution_time': execution_time,
                'timestamp': time.time()
            }
            
            # Log if slow (> 1 second)
            if execution_time > 1.0:
                st.warning(f"⚠️ Slow operation: {func.__name__} took {execution_time:.2f}s")
            
            return result
        return wrapper
    
    @staticmethod
    def batch_process(
        items: list,
        process_func: Callable,
        batch_size: int = 100,
        show_progress: bool = True
    ) -> list:
        """
        Process items in batches with progress indicator
        
        Args:
            items: List of items to process
            process_func: Function to apply to each item
            batch_size: Number of items per batch
            show_progress: Whether to show progress bar
            
        Returns:
            List of processed results
        """
        results = []
        total_batches = (len(items) - 1) // batch_size + 1
        
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = [process_func(item) for item in batch]
            results.extend(batch_results)
            
            if show_progress:
                progress = (i + batch_size) / len(items)
                progress_bar.progress(min(progress, 1.0))
                status_text.text(f"Processing: {min(i + batch_size, len(items))}/{len(items)} items")
        
        if show_progress:
            progress_bar.empty()
            status_text.empty()
        
        return results
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """
        Generate a unique cache key from arguments
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Unique hash string
        """
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def clear_old_cache_entries(max_age_seconds: int = 3600):
        """
        Clear cache entries older than specified age
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)
        """
        if 'cache_timestamps' not in st.session_state:
            st.session_state.cache_timestamps = {}
        
        current_time = time.time()
        keys_to_remove = []
        
        for key, timestamp in st.session_state.cache_timestamps.items():
            if current_time - timestamp > max_age_seconds:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
            del st.session_state.cache_timestamps[key]
        
        if keys_to_remove:
            st.toast(f"🧹 Cleared {len(keys_to_remove)} old cache entries")


class LazyLoader:
    """Lazy loading manager for heavy libraries and components"""
    
    _loaded_modules = {}
    
    @classmethod
    def load_plotly(cls):
        """Lazy load plotly only when needed for charts"""
        if 'plotly' not in cls._loaded_modules:
            import plotly.graph_objects as go
            import plotly.express as px
            cls._loaded_modules['plotly'] = {'go': go, 'px': px}
        return cls._loaded_modules['plotly']
    
    @classmethod
    def load_sklearn(cls):
        """Lazy load scikit-learn only when needed for ML"""
        if 'sklearn' not in cls._loaded_modules:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler
            cls._loaded_modules['sklearn'] = {
                'RandomForestRegressor': RandomForestRegressor,
                'StandardScaler': StandardScaler
            }
        return cls._loaded_modules['sklearn']
    
    @classmethod
    def load_seaborn(cls):
        """Lazy load seaborn only when needed for advanced plots"""
        if 'seaborn' not in cls._loaded_modules:
            import seaborn as sns
            cls._loaded_modules['seaborn'] = sns
        return cls._loaded_modules['seaborn']


class DataFrameOptimizer:
    """Optimizations specifically for pandas DataFrames"""
    
    @staticmethod
    def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage by converting to appropriate dtypes
        
        Args:
            df: DataFrame to optimize
            
        Returns:
            Optimized DataFrame
        """
        df = df.copy()
        
        # Convert object columns to category if low cardinality
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
        
        # Downcast numeric columns
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    
    @staticmethod
    def filter_columns(df: pd.DataFrame, required_cols: list) -> pd.DataFrame:
        """
        Keep only required columns to reduce memory
        
        Args:
            df: DataFrame to filter
            required_cols: List of column names to keep
            
        Returns:
            Filtered DataFrame
        """
        existing_cols = [col for col in required_cols if col in df.columns]
        return df[existing_cols].copy()
    
    @staticmethod
    def cache_computed_column(
        df: pd.DataFrame,
        col_name: str,
        compute_func: Callable,
        cache_key: str
    ) -> pd.Series:
        """
        Cache a computed column in session state
        
        Args:
            df: Source DataFrame
            col_name: Name for computed column
            compute_func: Function to compute column
            cache_key: Unique cache key
            
        Returns:
            Computed Series
        """
        full_cache_key = f"computed_col_{cache_key}_{col_name}"
        
        if full_cache_key not in st.session_state:
            st.session_state[full_cache_key] = compute_func(df)
            
            # Track cache timestamp
            if 'cache_timestamps' not in st.session_state:
                st.session_state.cache_timestamps = {}
            st.session_state.cache_timestamps[full_cache_key] = time.time()
        
        return st.session_state[full_cache_key]


# Convenience decorators
cache_5min = PerformanceOptimizer.cache_expensive_calculation(ttl=300)
cache_15min = PerformanceOptimizer.cache_expensive_calculation(ttl=900)
cache_1hour = PerformanceOptimizer.cache_expensive_calculation(ttl=3600)
cache_resource = PerformanceOptimizer.cache_resource
measure_perf = PerformanceOptimizer.measure_performance
