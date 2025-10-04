"""
FPL Analytics Application - Enhanced Modular Main Entry Point with Performance Improvements
Integrated with advanced caching, performance monitoring, and refactored components
"""
import streamlit as st
from typing import Optional
import pandas as pd
import time
from datetime import datetime

# Enhanced imports with performance improvements
from core.app_controller import EnhancedFPLAppController
from core.refactored_app_controller import PerformanceAwareController, CachingStrategy

# Enhanced services and utilities
from services.enhanced_fpl_data_service import get_enhanced_fpl_service
from utils.advanced_cache_manager import get_cache_manager, smart_cache
from utils.enhanced_performance_monitor import get_performance_monitor, monitor_performance

# Middleware imports
from middleware import (
    initialize_error_handling,
    initialize_logging,
    configure_container,
    get_error_middleware,
    get_logging_strategy,
    error_handler,
    ErrorCategory,
    ErrorSeverity
)

# Initialize performance monitor instance
performance_monitor = get_performance_monitor()
from utils.enhanced_cache import display_cache_metrics, cache_manager

# Configuration with security enhancements
from config.app_config import config
from config.secure_config import get_secure_config

# UI Components
from components.ui.status_bar import create_default_status_bar
from components.ui.styles import default_style_manager
from components.ui.theme_manager import get_theme_manager
from components.ui.dashboard_exporter import get_dashboard_exporter
from components.ai.player_insights import get_insights_engine
from components.error_handling import default_error_handler


class EnhancedFPLApp(PerformanceAwareController):
    """Enhanced FPL Application with integrated performance improvements"""
    
    def __init__(self):
        """Initialize the enhanced application"""
        super().__init__()
        
        # Initialize middleware
        self.error_middleware = get_error_middleware()
        self.logger = get_logging_strategy()
        
        # Initialize enhanced services
        self.fpl_service = get_enhanced_fpl_service()
        self.cache_manager = get_cache_manager()
        self.secure_config = get_secure_config()
        
        # Initialize new features
        self.theme_manager = get_theme_manager()
        self.dashboard_exporter = get_dashboard_exporter()
        self.insights_engine = get_insights_engine()
        
        # Initialize pages dictionary
        self._initialize_pages()
        
        self.logger.info("Enhanced FPL App initialized with all performance improvements and new features")
    
    def _initialize_pages(self):
        """Initialize the pages dictionary with all available pages"""
        try:
            # Import page classes
            from views.dashboard_page import DashboardPage
            from views.player_analysis_page import PlayerAnalysisPage  
            from views.fixture_analysis_page import FixtureAnalysisPage
            from views.my_team_page import MyTeamPage
            from views.ai_recommendations_page import AIRecommendationsPage
            from views.team_builder_page import TeamBuilderPage
            
            # Create page instances
            self.dashboard = DashboardPage()
            self.player_analysis = PlayerAnalysisPage()
            self.fixture_analysis = FixtureAnalysisPage()
            self.my_team = MyTeamPage()
            self.ai_recommendations = AIRecommendationsPage()
            self.team_builder = TeamBuilderPage()
            
            # Map pages to their render methods (matching navigation configuration)
            self.pages = {
                "dashboard": self.dashboard.render,
                "player_analysis": self.player_analysis.render,
                "fixture_difficulty": self.fixture_analysis.render,
                "my_fpl_team": self.my_team.render,  # Fixed: match navigation key
                "ai_recommendations": self.ai_recommendations.render,
                "team_builder": self.team_builder.render
            }
            
            self.logger.info(f"Successfully initialized {len(self.pages)} pages: {list(self.pages.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error initializing pages: {str(e)}", exc_info=True)
            # Create empty pages dict as fallback
            self.pages = {}

@monitor_performance(track_args=True)
@error_handler(category=ErrorCategory.SYSTEM, severity=ErrorSeverity.HIGH)
def initialize_app() -> Optional[EnhancedFPLApp]:
    """Initialize the application with enhanced performance monitoring"""
    logger = get_logging_strategy()
    
    try:
        with st.spinner("Initializing enhanced application..."):
            logger.info("Starting enhanced application initialization...")
            
            # Initialize performance monitoring
            performance_monitor.start_monitoring()
            
            # Create enhanced controller
            logger.info("Creating Enhanced FPL App Controller...")
            controller = EnhancedFPLApp()
            
            # Initialize optimized services
            if not controller.initialize_services_optimized():
                logger.error("Failed to initialize enhanced services")
                return None
            
            # Initialize optimized session state
            controller.initialize_session_state_optimized()
            
            # Initialize pages with lazy loading
            controller.initialize_pages_optimized()
                
            logger.info("Successfully initialized enhanced application")
            return controller
            
    except Exception as e:
        logger.error(f"Failed to initialize enhanced app: {str(e)}")
        st.error("Failed to initialize enhanced application. Please check the logs.")
        return None


@monitor_performance()
def render_enhanced_status_bar():
    """Render enhanced application status with performance metrics"""
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    
    # Get performance metrics
    cache_manager = get_cache_manager()
    
    cache_stats = cache_manager.get_cache_statistics()
    system_stats = performance_monitor.get_system_stats()
    
    with status_col1:
        data_status = "🟢 Online" if st.session_state.get('data_loaded', False) else "🔴 Offline"
        st.markdown(f"**Data:** {data_status}")
        if st.session_state.get('last_update'):
            last_update = st.session_state.last_update
            if isinstance(last_update, str):
                try:
                    last_update = datetime.fromisoformat(last_update)
                    time_diff = datetime.now() - last_update
                    st.caption(f"Updated {time_diff.seconds // 60}m ago")
                except:
                    pass
    
    with status_col2:
        hit_rate = cache_stats.get('hit_rate', 0)
        cache_color = "🟢" if hit_rate > 80 else "🟡" if hit_rate > 60 else "🔴"
        st.markdown(f"**Cache:** {cache_color} {hit_rate:.1f}%")
        memory_mb = cache_stats.get('memory_usage', 0) / 1024 / 1024
        st.caption(f"Memory: {memory_mb:.1f}MB")
    
    with status_col3:
        cpu_usage = system_stats.get('current_cpu', 0)
        cpu_color = "🟢" if cpu_usage < 50 else "🟡" if cpu_usage < 80 else "🔴"
        st.markdown(f"**CPU:** {cpu_color} {cpu_usage:.1f}%")
        memory_usage = system_stats.get('current_memory', 0)
        st.caption(f"RAM: {memory_usage:.1f}%")
    
    with status_col4:
        monitoring_active = system_stats.get('monitoring_active', False)
        monitor_status = "🟢 Active" if monitoring_active else "🔴 Inactive"
        st.markdown(f"**Monitor:** {monitor_status}")
        if 'performance_metrics' in st.session_state:
            session_start = st.session_state.performance_metrics.get('session_start', time.time())
            uptime = (time.time() - session_start) / 60
            st.caption(f"Uptime: {uptime:.1f}m")


def initialize_data() -> None:
    """Initialize and validate application data"""
    if hasattr(st.session_state, 'players_df') and st.session_state.players_df is not None:
        # Define columns that should be numeric
        numeric_cols = [
            'total_points', 'now_cost', 'form', 'selected_by_percent', 
            'minutes', 'goals_scored', 'assists', 'clean_sheets',
            'bonus', 'bps', 'influence', 'creativity', 'threat', 'ict_index',
            'points_per_game', 'value_form', 'value_season'
        ]
        
        # Convert columns to numeric and handle missing values
        for col in numeric_cols:
            if col in st.session_state.players_df.columns:
                st.session_state.players_df[col] = pd.to_numeric(
                    st.session_state.players_df[col], 
                    errors='coerce'
                ).fillna(0)


@performance_monitor.performance_monitor(track_args=True)
@error_handler(category=ErrorCategory.SYSTEM, severity=ErrorSeverity.CRITICAL)
def main() -> None:
    """Enhanced main application entry point with integrated performance monitoring"""
    # Initialize middleware systems
    error_middleware = initialize_error_handling()
    logger = initialize_logging("fpl_analytics")
    container = configure_container()
    
    try:
        logger.info("Starting enhanced FPL application with performance monitoring...")
        
        # Initialize performance monitoring
        performance_monitor.start_monitoring()
        
        # Clear session state if needed
        if st.runtime.exists():
            for key in ['app_controller', 'nav_selection']:
                if key in st.session_state:
                    del st.session_state[key]
        
        # Apply global styling
        logger.info("Applying global styles...")
        default_style_manager.apply_global_styles()
        
        # Initialize enhanced application with performance monitoring
        if 'app_controller' not in st.session_state:
            logger.info("Initializing enhanced app controller with performance monitoring...")
            st.session_state.app_controller = initialize_app()
            # Set initial navigation
            st.session_state.nav_selection = "dashboard"
            logger.info("Enhanced application initialized successfully")
        
        app = st.session_state.app_controller
        if app is None:
            logger.error("Enhanced app controller initialization failed")
            st.error("❌ Failed to initialize enhanced application. Please check the logs and refresh the page.")
            return
        
        # Render enhanced status bar with performance metrics
        render_enhanced_status_bar()
        
        # Run the enhanced application with monitoring
        logger.info("Starting main application navigation and rendering...")
        
        # Render navigation and handle page routing
        if hasattr(app, 'render_navigation_optimized'):
            # Use the optimized navigation from refactored controller
            app.render_navigation_optimized()
        elif hasattr(app, '_render_navigation'):
            # Fallback to original navigation method
            app._render_navigation()
        
        # Render the current page content
        current_page = st.session_state.get('nav_selection', 'dashboard')
        logger.info(f"Rendering page: {current_page}")
        
        if hasattr(app, 'pages') and current_page in app.pages:
            with st.spinner(f"Loading {current_page}..."):
                try:
                    page_renderer = app.pages[current_page]
                    if callable(page_renderer):
                        logger.info(f"Executing render method for '{current_page}'...")
                        page_renderer()
                    else:
                        logger.error(f"Page {current_page} renderer is not callable")
                        st.error("Page not properly configured")
                except Exception as page_error:
                    logger.error(f"Error rendering page '{current_page}': {str(page_error)}", exc_info=True)
                    st.error(f"An error occurred while loading the {current_page.replace('_', ' ')} page.")
        else:
            st.warning(f"Page '{current_page}' not found. Available pages: {list(getattr(app, 'pages', {}).keys())}")
        
        # Display enhanced features in sidebar
        with st.sidebar:
            st.markdown("---")
            
            # Theme Manager
            st.markdown("### 🎨 Theme Selection")
            theme_manager = get_theme_manager()
            theme_manager.render_theme_selector()
            
            # Dashboard Export
            st.markdown("### 📊 Export Dashboard")
            dashboard_exporter = get_dashboard_exporter()
            
            # Export buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 PDF Report", use_container_width=True):
                    if hasattr(st.session_state, 'players_df') and st.session_state.players_df is not None:
                        with st.spinner("Generating PDF..."):
                            pdf_data = dashboard_exporter.export_pdf_report(st.session_state.players_df)
                            st.download_button(
                                "Download PDF",
                                data=pdf_data,
                                file_name=f"fpl_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.warning("Load FPL data first!")
            
            with col2:
                if st.button("📊 Excel Export", use_container_width=True):
                    if hasattr(st.session_state, 'players_df') and st.session_state.players_df is not None:
                        with st.spinner("Generating Excel..."):
                            excel_data = dashboard_exporter.export_excel_analysis(st.session_state.players_df)
                            st.download_button(
                                "Download Excel",
                                data=excel_data,
                                file_name=f"fpl_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.warning("Load FPL data first!")
            
            st.markdown("---")
            st.markdown("### 📊 Performance Dashboard")
            
            # Cache metrics with advanced manager
            cache_manager.render_streamlit_dashboard()
            
            # Performance monitoring metrics
            if st.checkbox("Show Performance Metrics", value=config.ui.show_debug_info):
                performance_monitor.render_streamlit_dashboard()
            
            # System health indicators
            if st.checkbox("Show System Health", value=False):
                health_metrics = performance_monitor.get_system_health()
                for metric, value in health_metrics.items():
                    if isinstance(value, float):
                        st.metric(metric.replace('_', ' ').title(), f"{value:.1f}%")
                    else:
                        st.metric(metric.replace('_', ' ').title(), str(value))
            
    except Exception as e:
        get_logging_strategy().error(f"Enhanced application error: {str(e)}")
        get_error_middleware().handle_error(e)


if __name__ == "__main__":
    main()