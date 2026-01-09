"""
FPL Team Page - Fetch and display user's FPL team data
=====================================================

This page allows users to input their FPL Team ID and fetch their actual team data
from the official FPL API, displaying comprehensive team information and statistics.
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from typing import Dict, Optional, List, Any

from services.fpl_data_service import FPLDataService
from utils.error_handling import logger, handle_errors
from utils.modern_ui_components import ModernUIComponents


class FPLTeamPage:
    """FPL Team page for fetching and displaying user's actual team data"""
    
    def __init__(self):
        """Initialize the FPL Team page"""
        self.data_service = FPLDataService()
        self.page_title = "⚽ FPL Team"
        self.base_url = "https://fantasy.premierleague.com/api"
        
    def __call__(self):
        """Make the page callable"""
        self.render()
    
    @handle_errors("Error rendering FPL Team page")
    def render(self):
        """Main render method for FPL Team page"""
        try:
            # Apply modern styling (with error handling)
            try:
                ModernUIComponents.apply_modern_styling()
            except Exception as style_error:
                logger.warning(f"Failed to apply modern styling: {style_error}")
                # Continue without styling
            
            # Page header
            self._render_header()
            
            # Initialize session state
            self._initialize_session_state()
            
            # Main content
            if not st.session_state.get('fpl_team_loaded', False):
                self._render_team_input_section()
            else:
                self._render_team_dashboard()
                
        except Exception as e:
            st.error(f"Error loading FPL Team page: {str(e)}")
            logger.error(f"FPL Team page render error: {e}")
            # Fallback content
            st.title("⚽ FPL Team")
            st.warning("There was an issue loading the full page. Please try refreshing.")
    
    def _render_header(self):
        """Render page header"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #00ff87 0%, #60efff 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        ">
            <h1>⚽ My FPL Team</h1>
            <p style="font-size: 1.2rem; margin: 0; opacity: 0.9;">
                Connect your official FPL team and get detailed insights
            </p>
        </div>
        """, unsafe_allow_html=True)
    
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
        """Render team ID input section"""
        st.markdown("## 🔗 Connect Your FPL Team")
        
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
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            if st.button("🚀 Load My Team", type="primary", disabled=not team_id):
                if self._validate_team_id(team_id):
                    self._load_team_data(team_id)
                else:
                    st.error("❌ Please enter a valid Team ID (numbers only)")
        
        # Quick test option
        st.markdown("---")
        st.markdown("### 🧪 Quick Test")
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
                    
                    # Fetch current picks
                    picks_data = self._fetch_team_picks(team_id)
                    st.session_state.fpl_team_picks = picks_data
                    
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
            
            team_data = response.json()
            
            # Fetch current gameweek info
            gw_response = requests.get(f"{self.base_url}/bootstrap-static/", timeout=10)
            if gw_response.status_code == 200:
                bootstrap_data = gw_response.json()
                current_gw = next((event['id'] for event in bootstrap_data['events'] if event['is_current']), 1)
                team_data['current_gameweek'] = current_gw
            
            return team_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching team data: {e}")
            return None
    
    def _fetch_team_picks(self, team_id: str) -> Optional[Dict]:
        """Fetch current team picks from FPL API"""
        try:
            # Get current gameweek
            current_gw = st.session_state.fpl_team_data.get('current_gameweek', 1)
            
            # Fetch picks for current gameweek
            response = requests.get(f"{self.base_url}/entry/{team_id}/event/{current_gw}/picks/", timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch team picks: {e}")
            return None
    
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        sample_data = {
            'id': 1437667,
            'joined_time': '2024-07-12T10:30:00Z',
            'started_event': 1,
            'favourite_team': 1,
            'player_first_name': 'Sample',
            'player_last_name': 'Manager',
            'player_region_id': 7,
            'player_region_name': 'England',
            'player_region_iso_code_short': 'EN',
            'summary_overall_points': 1247,
            'summary_overall_rank': 456789,
            'summary_event_points': 58,
            'summary_event_rank': 234567,
            'current_event': 8,
            'leagues': {'classic': [], 'h2h': []},
            'name': 'Sample FPL Team',
            'name_change_blocked': False,
            'kit': {'kit_shirt_type': 'plain', 'kit_shirt_base': '#ff0000'},
            'last_deadline_bank': 7,
            'last_deadline_value': 1003,
            'last_deadline_total_transfers': 5,
            'current_gameweek': 8
        }
        
        sample_picks = {
            'active_chip': None,
            'automatic_subs': [],
            'entry_history': {
                'event': 8,
                'points': 58,
                'total_points': 1247,
                'rank': 234567,
                'overall_rank': 456789,
                'bank': 7,
                'value': 1003,
                'event_transfers': 1,
                'event_transfers_cost': 4,
                'points_on_bench': 12
            },
            'picks': [
                {'element': 1, 'position': 1, 'multiplier': 1, 'is_captain': False, 'is_vice_captain': False},
                {'element': 2, 'position': 2, 'multiplier': 1, 'is_captain': False, 'is_vice_captain': False},
                # Add more sample picks...
            ]
        }
        
        st.session_state.fpl_team_id = 'sample'
        st.session_state.fpl_team_data = sample_data
        st.session_state.fpl_team_picks = sample_picks
        st.session_state.fpl_team_loaded = True
        st.session_state.fpl_last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        st.success("✅ Sample data loaded!")
        st.rerun()
    
    def _render_team_dashboard(self):
        """Render the main team dashboard"""
        team_data = st.session_state.fpl_team_data
        picks_data = st.session_state.fpl_team_picks
        
        # Dashboard header
        self._render_dashboard_header(team_data)
        
        # Quick stats
        self._render_quick_stats(team_data, picks_data)
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "👥 Current Squad", 
            "📊 Performance", 
            "📈 Season History", 
            "⚙️ Team Settings"
        ])
        
        with tab1:
            self._render_current_squad(team_data, picks_data)
        
        with tab2:
            self._render_performance_analysis(team_data, picks_data)
        
        with tab3:
            self._render_season_history(team_data)
        
        with tab4:
            self._render_team_settings()
    
    def _render_dashboard_header(self, team_data: Dict):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            team_name = team_data.get('name', 'Unknown Team')
            manager_name = f"{team_data.get('player_first_name', 'Unknown')} {team_data.get('player_last_name', 'Manager')}"
            
            st.markdown(f"""
            <div style="
                background: white; 
                padding: 1.5rem; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            ">
                <h3 style="margin: 0; color: #333;">👤 {team_name}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Manager: {manager_name}</p>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Team ID: {st.session_state.fpl_team_id}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🔄 Refresh Data"):
                self._load_team_data(st.session_state.fpl_team_id)
        
        with col3:
            if st.button("🏠 New Team"):
                self._reset_team_state()
    
    def _render_quick_stats(self, team_data: Dict, picks_data: Optional[Dict]):
        """Render quick statistics"""
        st.markdown("### 📊 Quick Stats")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Get stats from picks data if available
        if picks_data and 'entry_history' in picks_data:
            history = picks_data['entry_history']
            total_points = history.get('total_points', team_data.get('summary_overall_points', 0))
            overall_rank = history.get('overall_rank', team_data.get('summary_overall_rank', 0))
            gw_points = history.get('points', team_data.get('summary_event_points', 0))
            team_value = history.get('value', team_data.get('last_deadline_value', 0)) / 10
        else:
            total_points = team_data.get('summary_overall_points', 0)
            overall_rank = team_data.get('summary_overall_rank', 0)
            gw_points = team_data.get('summary_event_points', 0)
            team_value = team_data.get('last_deadline_value', 0) / 10
        
        with col1:
            ModernUIComponents.create_metric_card(
                "Total Points", 
                f"{total_points:,}", 
                icon="🎯"
            )
        
        with col2:
            ModernUIComponents.create_metric_card(
                "Overall Rank", 
                f"{overall_rank:,}", 
                icon="🏆"
            )
        
        with col3:
            ModernUIComponents.create_metric_card(
                "Latest GW Points", 
                str(gw_points), 
                icon="⚡"
            )
        
        with col4:
            ModernUIComponents.create_metric_card(
                "Team Value", 
                f"£{team_value:.1f}m", 
                icon="💰"
            )
    
    def _render_current_squad(self, team_data: Dict, picks_data: Optional[Dict]):
        """Render current squad information"""
        st.markdown("### 👥 Current Squad")
        
        if not picks_data or 'picks' not in picks_data:
            st.warning("⚠️ Squad data not available. This might be due to API limitations.")
            return
        
        # Get player data for context
        try:
            players_data = self.data_service.load_fpl_data()
            if isinstance(players_data, tuple):
                players_df = players_data[0]
            else:
                players_df = players_data
        except:
            st.error("❌ Could not load player data for squad details")
            return
        
        picks = picks_data['picks']
        
        # Group picks by position
        formation_counts = {'GKP': 0, 'DEF': 0, 'MID': 0, 'FWD': 0}
        squad_players = []
        
        for pick in picks:
            player_id = pick['element']
            player_info = players_df[players_df['id'] == player_id]
            
            if not player_info.empty:
                player = player_info.iloc[0]
                position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                position = position_map.get(player['element_type'], 'UNK')
                
                squad_players.append({
                    'name': player['web_name'],
                    'team': player.get('team_short_name', 'UNK'),
                    'position': position,
                    'price': player['now_cost'] / 10,
                    'points': player['total_points'],
                    'is_captain': pick.get('is_captain', False),
                    'is_vice_captain': pick.get('is_vice_captain', False),
                    'multiplier': pick.get('multiplier', 1),
                    'position_order': pick['position']
                })
                
                if pick['position'] <= 11:  # Starting XI
                    formation_counts[position] += 1
        
        # Display formation
        playing_formation = f"{formation_counts['DEF']}-{formation_counts['MID']}-{formation_counts['FWD']}"
        st.info(f"⚽ Formation: {playing_formation}")
        
        # Display squad by position
        for position in ['GKP', 'DEF', 'MID', 'FWD']:
            position_players = [p for p in squad_players if p['position'] == position]
            if position_players:
                st.markdown(f"#### {position} ({len(position_players)} players)")
                
                for player in sorted(position_players, key=lambda x: x['position_order']):
                    self._render_player_card(player)
    
    def _render_player_card(self, player: Dict):
        """Render individual player card"""
        # Determine if player is starting (position <= 11)
        is_starting = player['position_order'] <= 11
        border_color = "#00ff87" if is_starting else "#ccc"
        
        # Captain badges
        captain_badge = ""
        if player['is_captain']:
            captain_badge = "🔴 (C)"
        elif player['is_vice_captain']:
            captain_badge = "🟡 (VC)"
        
        card_html = f"""
        <div style="
            background: white;
            border-left: 4px solid {border_color};
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #333;">
                        {player['name']} {captain_badge}
                        {'⭐' if is_starting else '🔄'}
                    </h4>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">
                        {player['team']} | £{player['price']:.1f}m
                    </p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; font-size: 1.2rem; font-weight: bold; color: #333;">
                        {player['points']} pts
                    </p>
                    <p style="margin: 0; font-size: 0.8rem; color: #666;">
                        {'Starting XI' if is_starting else 'Bench'}
                    </p>
                </div>
            </div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    def _render_performance_analysis(self, team_data: Dict, picks_data: Optional[Dict]):
        """Render performance analysis"""
        st.markdown("### 📊 Performance Analysis")
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Season Performance")
            
            total_points = team_data.get('summary_overall_points', 0)
            overall_rank = team_data.get('summary_overall_rank', 0)
            
            # Performance assessment
            if overall_rank <= 100000:
                grade = "🏆 Exceptional"
                color = "#28a745"
            elif overall_rank <= 500000:
                grade = "⭐ Excellent"
                color = "#28a745"
            elif overall_rank <= 1000000:
                grade = "👍 Good"
                color = "#ffc107"
            elif overall_rank <= 2000000:
                grade = "📊 Average"
                color = "#fd7e14"
            else:
                grade = "📈 Needs Improvement"
                color = "#dc3545"
            
            st.markdown(f"""
            <div style="color: {color}; font-weight: bold; font-size: 1.2rem;">
                {grade}
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Total Points", f"{total_points:,}")
            st.metric("Overall Rank", f"{overall_rank:,}")
        
        with col2:
            st.markdown("#### 📈 Recent Form")
            
            if picks_data and 'entry_history' in picks_data:
                history = picks_data['entry_history']
                gw_points = history.get('points', 0)
                gw_rank = history.get('rank', 0)
                
                st.metric("Latest GW Points", gw_points)
                st.metric("Latest GW Rank", f"{gw_rank:,}")
                
                # Form assessment
                if gw_points >= 70:
                    form = "🔥 On Fire!"
                elif gw_points >= 55:
                    form = "📈 Excellent"
                elif gw_points >= 45:
                    form = "👍 Good"
                elif gw_points >= 35:
                    form = "📊 Average"
                else:
                    form = "📉 Poor"
                
                st.markdown(f"**Recent Form:** {form}")
    
    def _render_season_history(self, team_data: Dict):
        """Render season history"""
        st.markdown("### 📈 Season History")
        st.info("📊 Season history data requires additional API calls. Feature coming soon!")
        
        # Show basic season info
        started_event = team_data.get('started_event', 1)
        current_event = team_data.get('current_event', 1)
        
        st.markdown(f"""
        **Season Information:**
        - Started in Gameweek: {started_event}
        - Current Gameweek: {current_event}
        - Gameweeks Played: {current_event - started_event + 1}
        """)
    
    def _render_team_settings(self):
        """Render team settings and actions"""
        st.markdown("### ⚙️ Team Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔄 Data Management")
            
            if st.button("🔄 Refresh Team Data", key="refresh_main"):
                self._load_team_data(st.session_state.fpl_team_id)
            
            if st.button("🗑️ Clear Team Data"):
                self._reset_team_state()
            
            # Last update info
            last_update = st.session_state.get('fpl_last_update', 'Never')
            st.info(f"🕐 Last updated: {last_update}")
        
        with col2:
            st.markdown("#### 📊 Export Options")
            
            if st.button("📥 Export Team Data"):
                st.info("📄 Export functionality coming soon!")
            
            if st.button("📊 Generate Report"):
                st.info("📋 Report generation coming soon!")
    
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
fpl_team_page = FPLTeamPage()
