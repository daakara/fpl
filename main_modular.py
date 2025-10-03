"""
FPL Analytics Application - Enhanced Modular Main Entry Point
"""
import streamlit as st
from typing import Optional
import pandas as pd

from core.app_controller import EnhancedFPLAppController
from utils.enhanced_cache import display_cache_metrics, cache_manager
from utils.error_handling import logger
from config.app_config import config

from components.ui.status_bar import create_default_status_bar
from components.ui.styles import default_style_manager
from components.error_handling import default_error_handler


def initialize_app() -> Optional[EnhancedFPLAppController]:
    """Initialize the application with proper error handling"""
    try:
        with st.spinner("Initializing application..."):
            logger.info("Starting application initialization...")
            
            # Step 1: Create controller
            logger.info("Creating FPL App Controller...")
            controller = EnhancedFPLAppController()
            if controller is None:
                logger.error("Failed to create controller instance")
                return None
                
            logger.info("Successfully initialized application")
            return controller
            
    except Exception as e:
        logger.error(f"Failed to initialize app: {str(e)}", exc_info=True)
        st.error("Failed to initialize application. Please check the logs.")
        return None


def render_app_status_bar():
    """Render application status and health indicators"""
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    
    with status_col1:
        data_status = "🟢 Online" if st.session_state.get('data_loaded', False) else "🔴 Offline"
        st.markdown(f"**Data:** {data_status}")
    
    with status_col2:
        cache_hit_rate = 85  # Would get from actual cache metrics
        cache_color = "🟢" if cache_hit_rate > 80 else "🟡" if cache_hit_rate > 60 else "🔴"
        st.markdown(f"**Cache:** {cache_color} {cache_hit_rate}%")
    
    with status_col3:
        ai_status = "🤖 Ready" if st.session_state.get('ai_enabled', True) else "🤖 Disabled"
        st.markdown(f"**AI:** {ai_status}")
    
    with status_col4:
        user_count = len(st.session_state.get('users', [1]))  # Placeholder
        st.markdown(f"**Users:** 👥 {user_count}")


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


def main() -> None:
    """Enhanced main application entry point with modular components"""
    try:
        logger.info("Starting main application...")
        
        # Clear session state if needed
        if st.runtime.exists():
            for key in ['app_controller', 'nav_selection']:
                if key in st.session_state:
                    del st.session_state[key]
        
        # Apply global styling
        logger.info("Applying global styles...")
        default_style_manager.apply_global_styles()
        
        # Initialize application
        if 'app_controller' not in st.session_state:
            logger.info("Initializing new app controller...")
            st.session_state.app_controller = initialize_app()
            # Set initial navigation
            st.session_state.nav_selection = "dashboard"
            logger.info("Initial navigation set to dashboard")
        
        app = st.session_state.app_controller
        if app is None:
            logger.error("App controller initialization failed")
            st.error("❌ Failed to initialize application. Please check the logs and refresh the page.")
            return
        
        # Render status bar
        status_bar = create_default_status_bar(st.session_state)
        status_bar.render()
        
        # Run the enhanced application
        app.run()
        
        # Display cache metrics in sidebar if enabled
        if config.ui.show_debug_info:
            with st.sidebar:
                display_cache_metrics()
            
    except Exception as e:
        default_error_handler.handle(e)


if __name__ == "__main__":
    main()