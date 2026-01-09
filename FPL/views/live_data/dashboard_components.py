"""
Live Dashboard Components - Header, alerts, and real-time monitoring components.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import pandas as pd
from utils.enhanced_cache import cached_load_fpl_data
from utils.error_handling import logger
from utils.modern_ui_components import ModernUIComponents


class LiveDashboardComponents:
    """Components for the live data dashboard header and real-time features."""
    
    def __init__(self):
        self.ui_components = ModernUIComponents()
        self.auto_refresh_interval = 30
        self.last_refresh = datetime.now()
    
    def render_live_header(self):
        """Render live data header with real-time controls."""
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.markdown("# ⚡ Live Data Dashboard")
            st.caption("Real-time FPL monitoring and alerts")
            
        with col2:
            auto_refresh = st.toggle("🔄 Auto-refresh", value=False, key="live_auto_refresh")
            if auto_refresh:
                st.caption("⚡ Live updates ON")
                
        with col3:
            if st.button("🔄 Refresh Now", type="secondary"):
                self.refresh_data()
        
        with col4:
            if self.test_api_connection():
                st.success("🟢 API Connected")
                st.caption("🔓 SSL bypass active")
            else:
                st.error("🔴 API Error")
                st.caption("Check connection")
                
        with col5:
            time_since_refresh = (datetime.now() - self.last_refresh).seconds
            if time_since_refresh < 60:
                st.success(f"🟢 Live ({time_since_refresh}s ago)")
            elif time_since_refresh < 300:
                st.warning(f"🟡 Recent ({time_since_refresh//60}m ago)")
            else:
                st.error(f"🔴 Stale ({time_since_refresh//60}m ago)")
    
    def handle_auto_refresh(self):
        """Handle automatic data refresh."""
        if st.session_state.get('live_auto_refresh', False):
            time_since_last = (datetime.now() - self.last_refresh).seconds
            
            if time_since_last >= self.auto_refresh_interval:
                with st.spinner("🔄 Auto-refreshing data..."):
                    self.refresh_data()
                    st.rerun()
                    
            next_refresh_in = self.auto_refresh_interval - time_since_last
            if next_refresh_in > 0:
                st.caption(f"Next refresh in: {next_refresh_in}s")
    
    def refresh_data(self):
        """Refresh FPL data."""
        try:
            players_df, teams_df = cached_load_fpl_data()
            if not players_df.empty:
                st.session_state.players_df = players_df
                st.session_state.teams_df = teams_df
                st.session_state.last_data_update = datetime.now()
                self.last_refresh = datetime.now()
                st.toast("✅ Data refreshed successfully!", icon="🔄")
        except Exception as e:
            st.error(f"❌ Failed to refresh data: {str(e)}")
            logger.error(f"Data refresh error: {e}")
    
    def test_api_connection(self) -> bool:
        """Test API connection status."""
        try:
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/", timeout=5, verify=False)
            return response.status_code == 200
        except:
            return False
    
    def ensure_data_loaded(self) -> bool:
        """Ensure data is loaded with live data focus."""
        if not st.session_state.get('data_loaded', False):
            st.markdown("### ⚡ Live Data Dashboard")
            st.markdown("**Real-time FPL monitoring with automatic updates**")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔴 GO LIVE", type="primary", use_container_width=True):
                    with st.spinner("🚀 Initializing live data feed..."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("📡 Connecting to FPL API...")
                        progress_bar.progress(20)
                        time.sleep(0.5)
                        
                        status_text.text("⚽ Loading player data...")
                        progress_bar.progress(40)
                        players_df, teams_df = cached_load_fpl_data()
                        
                        status_text.text("📊 Setting up monitoring...")
                        progress_bar.progress(60)
                        time.sleep(0.5)
                        
                        status_text.text("⚡ Activating live updates...")
                        progress_bar.progress(80)
                        time.sleep(0.5)
                        
                        if not players_df.empty:
                            if 'element_type' in players_df.columns and 'position' not in players_df.columns:
                                position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                                players_df['position'] = players_df['element_type'].map(position_map)
                            
                            st.session_state.players_df = players_df
                            st.session_state.teams_df = teams_df
                            st.session_state.data_loaded = True
                            st.session_state.last_data_update = datetime.now()
                            self.last_refresh = datetime.now()
                            
                            progress_bar.progress(100)
                            status_text.text("🟢 LIVE!")
                            time.sleep(0.5)
                            
                            st.success("🎉 Live data feed activated!")
                            st.rerun()
            return False
        return True
