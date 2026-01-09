"""
Simplified FPL Team Page - Debug Version
======================================

This is a simplified version of the FPL Team page to debug the blank page issue.
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, Optional

from services.fpl_data_service import FPLDataService
from utils.error_handling import logger, handle_errors


class SimpleFPLTeamPage:
    """Simplified FPL Team page for debugging"""
    
    def __init__(self):
        """Initialize the FPL Team page"""
        self.data_service = FPLDataService()
        self.page_title = "⚽ FPL Team"
        self.base_url = "https://fantasy.premierleague.com/api"
        
    def __call__(self):
        """Make the page callable"""
        self.render()
    
    def render(self):
        """Main render method - simplified for debugging"""
        try:
            # Simple header
            st.title("⚽ My FPL Team")
            st.markdown("Connect your official FPL team and get detailed insights")
            
            # Initialize session state
            self._initialize_session_state()
            
            # Main content
            if not st.session_state.get('fpl_team_loaded', False):
                self._render_team_input_section()
            else:
                self._render_team_dashboard()
                
        except Exception as e:
            st.error(f"Error rendering FPL Team page: {str(e)}")
            logger.error(f"FPL Team page render error: {e}")
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'fpl_team_loaded': False,
            'fpl_team_id': None,
            'fpl_team_data': None,
            'fpl_team_picks': None,
            'fpl_current_gameweek': None,
            'fpl_last_update': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _render_team_input_section(self):
        """Render team ID input section - simplified"""
        st.header("🔗 Connect Your FPL Team")
        
        # Instructions
        with st.expander("📋 How to find your FPL Team ID", expanded=True):
            st.markdown("""
            **Follow these steps to find your FPL Team ID:**
            
            1. 🌐 Go to the [Official FPL Website](https://fantasy.premierleague.com/)
            2. 🔐 Log in to your account
            3. 📊 Navigate to **"Points"** or **"My Team"**
            4. 👀 Look at the URL in your browser
            5. 🔢 Your Team ID is the number after `/entry/`
            
            **Example URL:** `https://fantasy.premierleague.com/entry/1437667/event/8`  
            **Team ID:** `1437667`
            """)
        
        # Input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            team_id = st.text_input(
                "🆔 Enter your FPL Team ID:",
                placeholder="e.g., 1437667",
                help="Your unique FPL Team ID (numbers only)"
            )
        
        with col2:
            st.write("")  # Add spacing
            if st.button("🚀 Load My Team", type="primary", disabled=not team_id):
                if self._validate_team_id(team_id):
                    self._load_team_data(team_id)
                else:
                    st.error("❌ Please enter a valid Team ID (numbers only)")
        
        # Quick test option
        st.markdown("---")
        st.subheader("🧪 Quick Test")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Load Example Team (1437667)", type="secondary"):
                self._load_team_data("1437667")
        
        with col2:
            if st.button("🔄 Load Sample Data", type="secondary"):
                self._load_sample_data()
    
    def _validate_team_id(self, team_id: str) -> bool:
        """Validate team ID format"""
        if not team_id:
            return False
        return team_id.isdigit() and len(team_id) >= 1
    
    def _load_team_data(self, team_id: str):
        """Load team data from FPL API"""
        try:
            with st.spinner(f"🔄 Loading FPL Team {team_id}..."):
                # Fetch team data
                team_data = self._fetch_team_from_api(team_id)
                
                if team_data:
                    # Store in session state
                    st.session_state.fpl_team_id = team_id
                    st.session_state.fpl_team_data = team_data
                    st.session_state.fpl_team_loaded = True
                    st.session_state.fpl_last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    st.success(f"✅ Successfully loaded FPL Team {team_id}!")
                    st.rerun()
                else:
                    st.error("❌ Failed to load team data. Please check your Team ID.")
                    
        except Exception as e:
            logger.error(f"Error loading team {team_id}: {e}")
            st.error(f"❌ Error loading team: {str(e)}")
    
    def _fetch_team_from_api(self, team_id: str) -> Optional[Dict]:
        """Fetch team data from FPL API"""
        try:
            # Fetch basic team info
            response = requests.get(f"{self.base_url}/entry/{team_id}/", timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching team data: {e}")
            return None
    
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        sample_data = {
            'id': 1437667,
            'player_first_name': 'Sample',
            'player_last_name': 'Manager',
            'summary_overall_points': 1247,
            'summary_overall_rank': 456789,
            'summary_event_points': 58,
            'name': 'Sample FPL Team',
            'last_deadline_value': 1003,
        }
        
        st.session_state.fpl_team_id = 'sample'
        st.session_state.fpl_team_data = sample_data
        st.session_state.fpl_team_loaded = True
        st.session_state.fpl_last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        st.success("✅ Sample data loaded!")
        st.rerun()
    
    def _render_team_dashboard(self):
        """Render the main team dashboard - simplified"""
        team_data = st.session_state.fpl_team_data
        
        st.header("📊 Team Dashboard")
        
        # Basic team info
        team_name = team_data.get('name', 'Unknown Team')
        manager_name = f"{team_data.get('player_first_name', 'Unknown')} {team_data.get('player_last_name', 'Manager')}"
        
        st.subheader(f"⚽ {team_name}")
        st.write(f"👤 Manager: {manager_name}")
        st.write(f"🆔 Team ID: {st.session_state.fpl_team_id}")
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_points = team_data.get('summary_overall_points', 0)
            st.metric("Total Points", f"{total_points:,}")
        
        with col2:
            overall_rank = team_data.get('summary_overall_rank', 0)
            st.metric("Overall Rank", f"{overall_rank:,}")
        
        with col3:
            team_value = team_data.get('last_deadline_value', 0) / 10
            st.metric("Team Value", f"£{team_value:.1f}m")
        
        # Actions
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Data"):
                self._load_team_data(st.session_state.fpl_team_id)
        
        with col2:
            if st.button("🏠 New Team"):
                self._reset_team_state()
    
    def _reset_team_state(self):
        """Reset team state"""
        keys_to_reset = [
            'fpl_team_loaded', 'fpl_team_id', 'fpl_team_data', 
            'fpl_team_picks', 'fpl_last_update'
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("✅ Team data cleared!")
        st.rerun()


# Create the page instance
simple_fpl_team_page = SimpleFPLTeamPage()
