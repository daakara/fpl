"""
Refactored App Controller with Performance Monitoring and Enhanced Caching
This file contains the refactored version of the large functions from app_controller.py
"""
import streamlit as st
import pandas as pd
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta

from utils.enhanced_performance_monitor import get_performance_monitor, monitor_performance
from utils.error_handling import handle_errors, logger
from config.app_config import config


class PerformanceAwareController:
    """Base controller class with performance monitoring capabilities"""
    
    def __init__(self):
        self.performance_monitor = get_performance_monitor()
        self.performance_monitor.start_monitoring()
        
    @monitor_performance(track_args=True)
    def initialize_services_optimized(self) -> bool:
        """
        Refactored service initialization with performance monitoring
        Breaks down the large initialization into smaller, focused functions
        """
        try:
            logger.info("Starting optimized service initialization...")
            
            # Step 1: Initialize data service
            self._init_data_service()
            
            # Step 2: Test connection with timeout
            self._test_service_connection()
            
            # Step 3: Initialize UI components
            self._init_ui_components()
            
            logger.info("Service initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Service initialization failed: {str(e)}", exc_info=True)
            return False
    
    def _init_data_service(self):
        """Initialize FPL data service"""
        from services.fpl_data_service import FPLDataService
        self.data_service = FPLDataService()
        logger.info("FPL Data Service initialized")
    
    def _test_service_connection(self):
        """Test service connection with proper error handling"""
        try:
            self.data_service.test_connection()
            st.session_state.service_status = "connected"
            logger.info("Service connection test successful")
        except Exception as e:
            st.session_state.service_status = "disconnected"
            logger.warning(f"Service connection test failed: {str(e)}")
    
    def _init_ui_components(self):
        """Initialize UI components"""
        from utils.modern_ui_components import ModernUIComponents
        from components.ui.navigation import UnifiedNavigation
        
        self.ui_components = ModernUIComponents()
        self.navigation = UnifiedNavigation()
        logger.info("UI components initialized")

    @monitor_performance()
    def initialize_session_state_optimized(self):
        """
        Refactored session state initialization with caching
        Uses cached defaults and validates existing state
        """
        # Get cached default state
        default_state = self._get_cached_default_state()
        
        # Initialize only missing keys
        missing_keys = [key for key in default_state.keys() if key not in st.session_state]
        
        for key in missing_keys:
            st.session_state[key] = default_state[key]
            
        # Validate and clean existing state
        self._validate_session_state()
        
        logger.info(f"Session state initialized with {len(missing_keys)} new keys")

    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _get_cached_default_state() -> Dict[str, Any]:
        """Get cached default session state configuration"""
        return {
            'nav_selection': 'dashboard',
            'data_loaded': False,
            'last_update': None,
            'players_df': None,
            'teams_df': None,
            'error_state': None,
            'loading_state': False,
            'fpl_team_loaded': False,
            'fpl_team_id': None,
            'fpl_team_data': None,
            'service_status': 'unknown',
            'feature_flags': {
                'ai_recommendations': True,
                'advanced_analytics': True,
                'real_time_updates': False,
                'export_features': True
            },
            'performance_metrics': {
                'page_loads': 0,
                'data_refreshes': 0,
                'errors': 0,
                'session_start': time.time(),
                'last_performance_check': time.time()
            },
            'cache_metrics': {
                'hits': 0,
                'misses': 0,
                'invalidations': 0
            }
        }
    
    def _validate_session_state(self):
        """Validate and clean session state"""
        # Check for stale data
        if st.session_state.get('last_update'):
            last_update = st.session_state['last_update']
            if isinstance(last_update, str):
                try:
                    last_update = datetime.fromisoformat(last_update)
                except:
                    st.session_state['last_update'] = None
                    
            if last_update and datetime.now() - last_update > timedelta(hours=2):
                st.session_state['data_loaded'] = False
                logger.info("Marked data as stale for refresh")

    @monitor_performance()
    def initialize_pages_optimized(self):
        """
        Refactored page initialization with lazy loading
        Only initializes pages when needed, not all at once
        """
        try:
            # Initialize page registry with lazy loading functions
            self.page_registry = {
                "dashboard": self._lazy_load_dashboard,
                "player_analysis": self._lazy_load_player_analysis,
                "fixture_difficulty": self._lazy_load_fixture_analysis,
                "my_fpl_team": self._lazy_load_my_fpl_team,
                "ai_recommendations": self._lazy_load_ai_recommendations,
                "team_builder": self._lazy_load_team_builder
            }
            
            # Initialize currently selected page only
            current_page = st.session_state.get('nav_selection', 'dashboard')
            if current_page in self.page_registry:
                self.page_registry[current_page]()
            
            logger.info(f"Page registry initialized with {len(self.page_registry)} pages")
            
        except Exception as e:
            logger.error(f"Error initializing pages: {str(e)}", exc_info=True)
            raise

    @staticmethod
    @st.cache_resource
    def _lazy_load_dashboard():
        """Lazy load dashboard page"""
        from views.dashboard_page import DashboardPage
        return DashboardPage()
    
    @staticmethod
    @st.cache_resource  
    def _lazy_load_player_analysis():
        """Lazy load player analysis page"""
        from views.player_analysis_page import PlayerAnalysisPage
        return PlayerAnalysisPage()
    
    @staticmethod
    @st.cache_resource
    def _lazy_load_fixture_analysis():
        """Lazy load fixture analysis page"""
        from views.fixture_analysis_page import FixtureAnalysisPage
        return FixtureAnalysisPage()
    
    @staticmethod
    @st.cache_resource
    def _lazy_load_my_fpl_team():
        """Lazy load My FPL team page"""
        from views.my_team_page import MyTeamPage
        return MyTeamPage()
    
    @staticmethod
    @st.cache_resource
    def _lazy_load_ai_recommendations():
        """Lazy load AI recommendations page"""
        from views.ai_recommendations_page import AIRecommendationsPage
        return AIRecommendationsPage()
    
    @staticmethod
    @st.cache_resource
    def _lazy_load_team_builder():
        """Lazy load team builder page"""
        from views.team_builder_page import TeamBuilderPage
        return TeamBuilderPage()

    @monitor_performance()
    def render_navigation_optimized(self):
        """
        Refactored navigation rendering with caching and performance optimization
        """
        with st.sidebar:
            # Get cached navigation configuration
            nav_config = self._get_cached_navigation_config()
            
            # Render navigation menu
            selected_label = self._render_option_menu(nav_config)
            
            # Handle navigation change
            self._handle_navigation_change(selected_label, nav_config)

    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def _get_cached_navigation_config() -> Dict[str, Any]:
        """Get cached navigation configuration"""
        from components.ui.navigation import UnifiedNavigation
        
        navigation = UnifiedNavigation()
        sorted_nav_items = sorted(
            [item for item in navigation.nav_items.values()],
            key=lambda item: item.order
        )
        
        return {
            'labels': [item.label for item in sorted_nav_items],
            'icons': [item.icon for item in sorted_nav_items],
            'ids': [item.id for item in sorted_nav_items]
        }
    
    def _render_option_menu(self, nav_config: Dict[str, Any]) -> str:
        """Render the option menu with proper state management and fallback"""
        import streamlit as st
        
        current_selection_id = st.session_state.get('nav_selection', 'dashboard')
        current_index = 0
        
        if current_selection_id in nav_config['ids']:
            current_index = nav_config['ids'].index(current_selection_id)
        
        try:
            # Try to use the fancy option menu
            from streamlit_option_menu import option_menu
            
            return option_menu(
                menu_title="FPL Analytics",
                options=nav_config['labels'],
                icons=nav_config['icons'],
                menu_icon="⚽",
                default_index=current_index,
                styles=getattr(config.ui, 'navigation_styles', None)
            )
        except ImportError:
            # Fallback to simple selectbox navigation
            st.sidebar.markdown("## ⚽ FPL Analytics")
            st.sidebar.markdown("---")
            
            selected_label = st.sidebar.selectbox(
                "Navigate to:",
                options=nav_config['labels'],
                index=current_index,
                key="nav_selectbox"
            )
            
            st.sidebar.markdown("---")
            st.sidebar.info("💡 Install `streamlit-option-menu` for enhanced navigation")
            
            return selected_label
    
    def _handle_navigation_change(self, selected_label: str, nav_config: Dict[str, Any]):
        """Handle navigation change with performance tracking"""
        selected_id = nav_config['ids'][nav_config['labels'].index(selected_label)]
        
        if st.session_state.nav_selection != selected_id:
            # Track navigation change
            self._track_navigation_change(selected_id)
            
            # Update session state
            st.session_state.nav_selection = selected_id
            st.session_state.performance_metrics['page_loads'] += 1
            
            # Clear page-specific cache if needed
            if selected_id != st.session_state.get('last_page'):
                self._clear_page_cache(st.session_state.get('last_page'))
                st.session_state.last_page = selected_id
    
    def _track_navigation_change(self, new_page: str):
        """Track navigation changes for analytics"""
        logger.info(f"Navigation changed to: {new_page}")
        
        # Update performance metrics
        if 'navigation_history' not in st.session_state:
            st.session_state.navigation_history = []
        
        st.session_state.navigation_history.append({
            'page': new_page,
            'timestamp': datetime.now().isoformat(),
            'session_time': time.time() - st.session_state.performance_metrics['session_start']
        })
    
    def _clear_page_cache(self, page_id: Optional[str]):
        """Clear page-specific cache when navigating away"""
        if page_id and hasattr(st, 'cache_data'):
            # Clear page-specific cached data
            cache_keys_to_clear = [
                f"{page_id}_data",
                f"{page_id}_analysis",
                f"{page_id}_charts"
            ]
            
            for key in cache_keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring dashboard"""
        system_stats = self.performance_monitor.get_system_stats()
        
        return {
            'system': system_stats,
            'session': st.session_state.get('performance_metrics', {}),
            'cache': st.session_state.get('cache_metrics', {}),
            'recommendations': self.performance_monitor.get_performance_recommendations()
        }


class CachingStrategy:
    """Enhanced caching strategy for FPL data"""
    
    @staticmethod
    @st.cache_data(ttl=1800, show_spinner="Loading FPL data...")  # 30 minutes
    def load_fpl_data_cached() -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load and cache FPL data with automatic refresh"""
        from services.fpl_data_service import FPLDataService
        
        service = FPLDataService()
        try:
            data = service.fetch_fpl_data()
            players_df, teams_df = service.process_fpl_data(data)
            
            # Update cache metrics
            if 'cache_metrics' in st.session_state:
                st.session_state.cache_metrics['misses'] += 1
            
            logger.info(f"Loaded {len(players_df)} players and {len(teams_df)} teams from API")
            return players_df, teams_df
            
        except Exception as e:
            logger.error(f"Failed to load FPL data: {str(e)}")
            raise
    
    @staticmethod
    @st.cache_data(ttl=3600)  # 1 hour
    def get_player_analysis_cached(player_id: int) -> Dict[str, Any]:
        """Cache individual player analysis"""
        # Implementation would go here
        return {"analysis": "cached_data"}
    
    @staticmethod
    @st.cache_data(ttl=7200)  # 2 hours  
    def get_fixture_difficulty_cached() -> Dict[str, Any]:
        """Cache fixture difficulty analysis"""
        # Implementation would go here
        return {"fixtures": "cached_data"}
    
    @staticmethod
    def invalidate_cache(cache_type: str = "all"):
        """Invalidate specific cache types"""
        if cache_type == "all" or cache_type == "fpl_data":
            CachingStrategy.load_fpl_data_cached.clear()
        
        if cache_type == "all" or cache_type == "player_analysis":
            CachingStrategy.get_player_analysis_cached.clear()
        
        if cache_type == "all" or cache_type == "fixture_difficulty":
            CachingStrategy.get_fixture_difficulty_cached.clear()
        
        # Update cache metrics
        if 'cache_metrics' in st.session_state:
            st.session_state.cache_metrics['invalidations'] += 1
        
        logger.info(f"Cache invalidated: {cache_type}")


# Performance monitoring decorators
def track_execution_time(func_name: str):
    """Decorator to track function execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log performance
                logger.info(f"{func_name} executed in {execution_time:.3f}s")
                
                # Update session metrics
                if 'performance_metrics' not in st.session_state:
                    st.session_state.performance_metrics = {}
                
                if 'function_times' not in st.session_state.performance_metrics:
                    st.session_state.performance_metrics['function_times'] = {}
                
                st.session_state.performance_metrics['function_times'][func_name] = execution_time
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func_name} failed after {execution_time:.3f}s: {str(e)}")
                raise
                
        return wrapper
    return decorator
