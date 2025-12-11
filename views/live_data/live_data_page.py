"""
Live Data Page - Refactored main controller using modular components.

This file has been refactored from a 1789-line monolith into a modular structure:
- dashboard_components.py: Header, auto-refresh, data loading
- hidden_gems_renderer.py: Hidden Gems discovery module
- helpers.py: Utility functions for data access

The main LiveDataPage class now orchestrates these components.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# Modular component imports
from .dashboard_components import LiveDashboardComponents
from .hidden_gems_renderer import HiddenGemsRenderer
from .helpers import LiveDataHelpers

# Legacy/shared component imports
from utils.modern_ui_components import ModernUIComponents
from utils.enhanced_cache import cached_load_fpl_data
from utils.error_handling import logger
from utils.data_converters import safe_int_convert, safe_float_convert


class LiveDataPage(LiveDataHelpers):
    """
    Refactored Live Data Dashboard - Main controller class.
    
    This class has been refactored to delegate rendering to specialized modules:
    - Dashboard components for header/alerts
    - Hidden Gems renderer for discovery features
    - Individual page renderers for each tab
    """

    def __init__(self):
        self.ui_components = ModernUIComponents()
        self.dashboard = LiveDashboardComponents()
        self.hidden_gems = HiddenGemsRenderer()
        self.auto_refresh_interval = 30
        self.last_refresh = datetime.now()

    def render(self):
        """Render the live data dashboard with real-time FPL insights."""
        
        try:
            # Use modular dashboard components
            self.dashboard.render_live_header()
            self.dashboard.handle_auto_refresh()
            
            # Load and manage data
            if not self.dashboard.ensure_data_loaded():
                return
                
            df = st.session_state.get('players_df')
            teams_df = st.session_state.get('teams_df')
            
            if df is None or df.empty:
                st.warning("Player data is not available. Please try refreshing.")
                return
            
            # Ensure position column exists
            if 'element_type' in df.columns and 'position' not in df.columns:
                position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                df['position'] = df['element_type'].map(position_map)
                st.session_state.players_df = df

            # Enhanced FPL Analysis Tabs
            self._render_tab_interface(df, teams_df)
                
        except ValueError as e:
            self._handle_value_error(e)
        except Exception as e:
            self._handle_general_error(e)

    def _render_tab_interface(self, df, teams_df):
        """Render the main tab interface."""
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
            "🎯 Live Overview", 
            "📊 Player Analytics",
            "🏆 Squad Builder",
            "💰 Transfer Intelligence",
            "👑 Captain Selector",
            "📅 Fixture Analysis",
            "📈 Performance Tracker",
            "🚨 Live Alerts",
            "💎 Hidden Gems",
            "👤 My Team Hub"
        ])
        
        # Check for Phase 2 components
        try:
            from views.phase2_subpages import Phase2SubPagesManager
            phase2_manager = Phase2SubPagesManager()
            st.success("🚀 Phase 2: AI-Powered Intelligence Active!")
        except ImportError:
            st.warning("Phase 2 AI components not available. Some features may be limited.")
        
        with tab1:
            self._render_live_overview_dashboard(df, teams_df)
        with tab2:
            self._render_player_analytics_page(df, teams_df)
        with tab3:
            self._render_squad_builder_page(df, teams_df)
        with tab4:
            self._render_transfer_intelligence_page(df, teams_df)
        with tab5:
            self._render_captain_selector_page(df, teams_df)
        with tab6:
            self._render_fixture_analysis_page(df, teams_df)
        with tab7:
            self._render_performance_tracker_page(df, teams_df)
        with tab8:
            self._render_live_alerts_page(df, teams_df)
        with tab9:
            # Use modular Hidden Gems renderer
            self.hidden_gems.render(df, teams_df)
        with tab10:
            self._render_my_team_hub_page(df, teams_df)
    
    def _handle_value_error(self, e):
        """Handle ValueError exceptions."""
        if "invalid literal for int()" in str(e):
            st.error("⚠️ **Data Conversion Error**: Some player data contains invalid values. Please refresh the data.")
            logger.error(f"Integer conversion error in Live Data page: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            if st.button("🔄 Reload Data"):
                st.session_state.pop('players_df', None)
                st.session_state.pop('teams_df', None)
                st.rerun()
        else:
            st.error(f"⚠️ **Error loading Live Data page**: {str(e)}")
            logger.error(f"ValueError in Live Data page: {e}")
    
    def _handle_general_error(self, e):
        """Handle general exceptions."""
        st.error(f"⚠️ **Error loading Live Data page**: {str(e)}")
        logger.error(f"Error in Live Data page render: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        if st.button("🔄 Try Again"):
            st.rerun()
    
    # NOTE: The following methods are placeholders that delegate to the original
    # implementations. These can be further refactored into separate modules.
    
    def _render_live_overview_dashboard(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_live_overview_dashboard(df, teams_df)
    
    def _render_player_analytics_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_player_analytics_page(df, teams_df)
    
    def _render_squad_builder_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_squad_builder_page(df, teams_df)
    
    def _render_transfer_intelligence_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_transfer_intelligence_page(df, teams_df)
    
    def _render_captain_selector_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_captain_selector_page(df, teams_df)
    
    def _render_fixture_analysis_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_fixture_analysis_page(df, teams_df)
    
    def _render_performance_tracker_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_performance_tracker_page(df, teams_df)
    
    def _render_live_alerts_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_live_alerts_page(df, teams_df)
    
    def _render_my_team_hub_page(self, df, teams_df):
        """Placeholder - delegates to original implementation."""
        from views.live_data_page_legacy import LiveDataPageLegacy
        legacy = LiveDataPageLegacy()
        legacy._render_my_team_hub_page(df, teams_df)
