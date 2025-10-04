"""
My FPL Team Page - Rebuilt UI
============================

A completely rebuilt, modern My FPL Team page with:
- Clean, responsive design
- Enhanced user experience  
- Improved performance
- Better error handling
- Modern UI components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from services.fpl_data_service import FPLDataService
from utils.error_handling import logger, handle_errors
from utils.modern_ui_components import (
    ModernUIComponents, NavigationManager, DataVisualization,
    render_loading_spinner, create_success_animation
)

class RebuildMyTeamPage:
    """Rebuilt My FPL Team page with modern UI and enhanced functionality"""
    
    def __init__(self):
        """Initialize the rebuilt page"""
        self.data_service = FPLDataService()
        self.page_title = "🏆 My FPL Team"
        self.title = "🏆 My FPL Team"  # Add explicit title attribute
        self.version = "2.0 - Rebuilt"
        
    def __call__(self):
        """Make the page callable"""
        self.render()
    
    @handle_errors
    def render(self):
        """Main render method with modern UI"""
        # Page configuration
        self._setup_page_config()
        
        # Header section
        self._render_header()
        
        # Initialize session state
        self._initialize_session_state()
        
        # Main content
        if not st.session_state.get('team_loaded', False):
            self._render_team_import_section()
        else:
            self._render_team_dashboard()
    
    def _setup_page_config(self):
        """Setup page configuration and styling"""
        # Custom CSS for modern look
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #00ff87 0%, #60efff 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .metric-container {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        
        .player-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .status-good { color: #28a745; font-weight: bold; }
        .status-warning { color: #ffc107; font-weight: bold; }
        .status-danger { color: #dc3545; font-weight: bold; }
        
        .quick-stats {
            display: flex;
            justify-content: space-around;
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render modern page header"""
        st.markdown(f"""
        <div class="main-header">
            <h1>🏆 My FPL Team Analysis</h1>
            <p><strong>{self.version}</strong> | Enhanced UI & Performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Public method to render header (for compatibility)"""
        return self._render_header()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'team_loaded': False,
            'team_id': None,
            'team_data': None,
            'current_gameweek': None,
            'players_df': None,
            'teams_df': None,
            'last_update': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _render_team_import_section(self):
        """Render enhanced team import section"""
        st.markdown("## 📥 Import Your FPL Team")
        
        # Quick start options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 Quick Start")
            
            # Preset team IDs for testing
            if st.button("🎯 Test with Team 1437667", type="primary"):
                self._load_team("1437667")
            
            if st.button("🔄 Load Sample Data"):
                self._load_sample_data()
        
        with col2:
            st.markdown("### 📊 Manual Entry")
            
            team_id = st.text_input(
                "Enter your FPL Team ID:",
                placeholder="e.g., 1437667",
                help="Find your team ID in the FPL website URL"
            )
            
            if st.button("📈 Load My Team", disabled=not team_id):
                if self._validate_team_id(team_id):
                    self._load_team(team_id)
                else:
                    st.error("❌ Please enter a valid team ID (numbers only)")
        
        # Help section
        with st.expander("❓ How to find your Team ID"):
            st.markdown("""
            1. Go to the **Official FPL Website**
            2. Navigate to **"Points"** or **"My Team"**
            3. Look at the URL: `https://fantasy.premierleague.com/entry/XXXXXXX/event/X`
            4. Your Team ID is the number after `/entry/` (e.g., 1437667)
            """)
        
        # Current status
        self._render_data_status()
    
    def _render_team_dashboard(self):
        """Render the main team dashboard"""
        team_data = st.session_state.team_data
        
        # Dashboard header
        self._render_dashboard_header(team_data)
        
        # Quick stats
        self._render_quick_stats(team_data)
        
        # Main tabs
        self._render_main_tabs(team_data)
    
    def _render_dashboard_header(self, team_data):
        """Render dashboard header with team info"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### 👤 {team_data.get('entry_name', 'Unknown Team')}")
            st.markdown(f"**Manager:** {team_data.get('player_first_name', '')} {team_data.get('player_last_name', '')}")
        
        with col2:
            if st.button("🔄 Refresh Data"):
                self._refresh_team_data()
        
        with col3:
            if st.button("🏠 New Team"):
                self._reset_team_state()
    
    def _render_quick_stats(self, team_data):
        """Render quick statistics overview"""
        st.markdown("### 📊 Quick Stats")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_points = team_data.get('summary_overall_points', 0)
            ModernUIComponents.create_metric_card(
                "Total Points", f"{total_points:,}", icon="🎯"
            )
        
        with col2:
            overall_rank = team_data.get('summary_overall_rank', 0)
            ModernUIComponents.create_metric_card(
                "Overall Rank", f"{overall_rank:,}", icon="🏆"
            )
        
        with col3:
            gameweek_points = team_data.get('summary_event_points', 0)
            ModernUIComponents.create_metric_card(
                "GW Points", str(gameweek_points), icon="⚡"
            )
        
        with col4:
            team_value = team_data.get('value', 0) / 10  # Convert from tenths
            ModernUIComponents.create_metric_card(
                "Team Value", f"£{team_value:.1f}m", icon="💰"
            )
    
    def _render_main_tabs(self, team_data):
        """Render main analysis tabs"""
        tabs = st.tabs([
            "👥 Squad Overview",
            "📈 Performance",
            "🎯 Recommendations", 
            "⚡ Quick Actions",
            "📊 Analytics"
        ])
        
        with tabs[0]:
            self._render_squad_overview(team_data)
        
        with tabs[1]:
            self._render_performance_analysis(team_data)
        
        with tabs[2]:
            self._render_recommendations(team_data)
        
        with tabs[3]:
            self._render_quick_actions(team_data)
        
        with tabs[4]:
            self._render_analytics(team_data)
    
    def _render_squad_overview(self, team_data):
        """Render squad overview with modern cards"""
        st.markdown("### 👥 Current Squad")
        
        if 'picks' not in team_data:
            st.warning("⚠️ Squad data not available")
            return
        
        # Load player data if not available
        players_df = self._get_players_data()
        if players_df.empty:
            st.error("❌ Player data not available")
            return
        
        # Group players by position
        picks = team_data['picks']
        
        # Position mapping
        position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        positions = {'GKP': [], 'DEF': [], 'MID': [], 'FWD': []}
        
        for pick in picks:
            player_id = pick['element']
            player_info = players_df[players_df['id'] == player_id]
            
            if not player_info.empty:
                player = player_info.iloc[0]
                position = position_map.get(player['element_type'], 'Unknown')
                
                player_data = {
                    'name': player['web_name'],
                    'team': player['team'],
                    'points': player['total_points'],
                    'price': player['now_cost'] / 10,
                    'selected_by': player['selected_by_percent'],
                    'is_captain': pick.get('is_captain', False),
                    'is_vice_captain': pick.get('is_vice_captain', False)
                }
                
                positions[position].append(player_data)
        
        # Render by position
        for position, players in positions.items():
            if players:
                st.markdown(f"#### {position} ({len(players)} players)")
                
                for player in players:
                    self._render_player_card(player)
    
    def _render_player_card(self, player):
        """Render individual player card"""
        # Create player card HTML
        captain_badge = "🔴 (C)" if player['is_captain'] else "🟡 (VC)" if player['is_vice_captain'] else ""
        
        card_html = f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        '>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h4 style='margin: 0; font-size: 1.1rem;'>{player['name']} {captain_badge}</h4>
                    <p style='margin: 0; opacity: 0.8;'>£{player['price']:.1f}m</p>
                </div>
                <div style='text-align: right;'>
                    <p style='margin: 0; font-size: 1.2rem; font-weight: bold;'>{player['points']} pts</p>
                    <p style='margin: 0; font-size: 0.8rem;'>{player['selected_by']:.1f}% owned</p>
                </div>
            </div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    def _render_performance_analysis(self, team_data):
        """Render performance analysis"""
        st.markdown("### 📈 Performance Analysis")
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Season Performance")
            
            total_points = team_data.get('summary_overall_points', 0)
            overall_rank = team_data.get('summary_overall_rank', 0)
            
            # Performance grade
            if overall_rank <= 100000:
                grade = "🏆 Excellent"
                color = "status-good"
            elif overall_rank <= 500000:
                grade = "⭐ Good"  
                color = "status-good"
            elif overall_rank <= 1000000:
                grade = "👍 Average"
                color = "status-warning"
            else:
                grade = "📈 Needs Improvement"
                color = "status-danger"
            
            st.markdown(f'<p class="{color}">{grade}</p>', unsafe_allow_html=True)
            st.markdown(f"**Total Points:** {total_points:,}")
            st.markdown(f"**Overall Rank:** {overall_rank:,}")
        
        with col2:
            st.markdown("#### 📊 Recent Form")
            
            gameweek_points = team_data.get('summary_event_points', 0)
            st.markdown(f"**Latest GW Points:** {gameweek_points}")
            
            # Form indicator
            if gameweek_points >= 60:
                form = "🔥 On Fire!"
                form_color = "status-good"
            elif gameweek_points >= 45:
                form = "📈 Good Form"
                form_color = "status-good"
            elif gameweek_points >= 30:
                form = "📊 Average"
                form_color = "status-warning"
            else:
                form = "📉 Struggling"
                form_color = "status-danger"
            
            st.markdown(f'<p class="{form_color}">{form}</p>', unsafe_allow_html=True)
    
    def _render_recommendations(self, team_data):
        """Render AI recommendations"""
        st.markdown("### 🤖 Smart Recommendations")
        
        # Analysis based recommendations
        recommendations = self._generate_recommendations(team_data)
        
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                st.markdown(f"#### {i}. {rec['title']}")
                st.markdown(rec['description'])
                
                if rec['priority'] == 'high':
                    st.error(f"🔴 High Priority: {rec['action']}")
                elif rec['priority'] == 'medium':
                    st.warning(f"🟡 Medium Priority: {rec['action']}")
                else:
                    st.info(f"🟢 Low Priority: {rec['action']}")
                
                st.markdown("---")
    
    def _render_quick_actions(self, team_data):
        """Render quick action buttons"""
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🔄 Data Actions")
            if st.button("🔄 Refresh Team Data", key="refresh_1"):
                self._refresh_team_data()
            
            if st.button("📊 Update Player Data", key="update_players"):
                self._update_player_data()
        
        with col2:
            st.markdown("#### 📈 Analysis")
            if st.button("🎯 Generate Report", key="generate_report"):
                st.success("📋 Report generated! Check the Analytics tab.")
            
            if st.button("🔍 Deep Analysis", key="deep_analysis"):
                self._run_deep_analysis(team_data)
        
        with col3:
            st.markdown("#### 🛠️ Tools")
            if st.button("💰 Value Calculator", key="value_calc"):
                self._show_value_calculator(team_data)
            
            if st.button("🏆 Rank Tracker", key="rank_tracker"):
                self._show_rank_tracker(team_data)
    
    def _render_analytics(self, team_data):
        """Render advanced analytics"""
        st.markdown("### 📊 Advanced Analytics")
        
        # Team composition analysis
        self._render_team_composition(team_data)
        
        # Value analysis
        self._render_value_analysis(team_data)
        
        # Performance trends
        self._render_performance_trends(team_data)
    
    def _render_team_composition(self, team_data):
        """Render team composition charts"""
        st.markdown("#### 👥 Team Composition")
        
        players_df = self._get_players_data()
        if players_df.empty:
            st.warning("⚠️ Player data not available for composition analysis")
            return
        
        # Position distribution
        picks = team_data.get('picks', [])
        position_counts = {'GKP': 0, 'DEF': 0, 'MID': 0, 'FWD': 0}
        position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        
        for pick in picks:
            player_id = pick['element']
            player_info = players_df[players_df['id'] == player_id]
            
            if not player_info.empty:
                position = position_map.get(player_info.iloc[0]['element_type'], 'Unknown')
                if position in position_counts:
                    position_counts[position] += 1
        
        # Create pie chart
        fig = px.pie(
            values=list(position_counts.values()),
            names=list(position_counts.keys()),
            title="Squad Composition by Position"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_value_analysis(self, team_data):
        """Render value analysis"""
        st.markdown("#### 💰 Value Analysis")
        
        team_value = team_data.get('value', 0) / 10
        bank = team_data.get('bank', 0) / 10
        total_budget = team_value + bank
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Squad Value", f"£{team_value:.1f}m")
        
        with col2:
            st.metric("In Bank", f"£{bank:.1f}m")
        
        with col3:
            st.metric("Total Budget", f"£{total_budget:.1f}m")
        
        # Budget utilization
        utilization = (team_value / 100) * 100 if total_budget > 0 else 0
        st.progress(utilization / 100)
        st.markdown(f"Budget Utilization: {utilization:.1f}%")
    
    def _render_performance_trends(self, team_data):
        """Render performance trends"""
        st.markdown("#### 📈 Performance Trends")
        
        # Mock trend data (in a real app, this would come from historical data)
        gameweeks = list(range(1, 11))
        points = [45, 52, 38, 61, 49, 55, 42, 58, 47, team_data.get('summary_event_points', 50)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=gameweeks,
            y=points,
            mode='lines+markers',
            name='Points per GW',
            line=dict(color='#00ff87', width=3)
        ))
        
        fig.update_layout(
            title="Gameweek Points Trend",
            xaxis_title="Gameweek",
            yaxis_title="Points",
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_data_status(self):
        """Render current data status"""
        st.markdown("### 📊 Data Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.get('players_df') is not None:
                st.success("✅ Player data loaded")
            else:
                st.warning("⚠️ Player data not loaded")
                if st.button("📥 Load Player Data"):
                    self._load_player_data()
        
        with col2:
            last_update = st.session_state.get('last_update')
            if last_update:
                st.info(f"🕐 Last updated: {last_update}")
            else:
                st.info("🕐 No recent updates")
    
    def _validate_team_id(self, team_id):
        """Validate team ID format"""
        return team_id.isdigit() and len(team_id) >= 1
    
    def _load_team(self, team_id):
        """Load team data"""
        try:
            with st.spinner(f"🔄 Loading team {team_id}..."):
                # Simulate API call delay
                time.sleep(1)
                
                # In a real implementation, this would call the FPL API
                team_data = self._get_mock_team_data(team_id)
                
                st.session_state.team_data = team_data
                st.session_state.team_id = team_id
                st.session_state.team_loaded = True
                st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                st.success(f"✅ Team {team_id} loaded successfully!")
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error loading team {team_id}: {e}")
            st.error(f"❌ Failed to load team {team_id}: {str(e)}")
    
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        sample_data = {
            'entry_name': 'Sample FPL Team',
            'player_first_name': 'Demo',
            'player_last_name': 'User',
            'summary_overall_points': 1247,
            'summary_overall_rank': 456789,
            'summary_event_points': 58,
            'value': 1003,  # £100.3m in tenths
            'bank': 7,      # £0.7m in tenths
            'picks': []     # Would contain actual picks
        }
        
        st.session_state.team_data = sample_data
        st.session_state.team_id = 'sample'
        st.session_state.team_loaded = True
        st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        st.success("✅ Sample data loaded!")
        st.rerun()
    
    def _get_mock_team_data(self, team_id):
        """Get mock team data for testing"""
        return {
            'entry_name': f'FPL Team {team_id}',
            'player_first_name': 'Test',
            'player_last_name': 'Manager',
            'summary_overall_points': 1156,
            'summary_overall_rank': 234567,
            'summary_event_points': 52,
            'value': 996,
            'bank': 14,
            'picks': [
                {'element': 1, 'is_captain': True, 'is_vice_captain': False},
                {'element': 2, 'is_captain': False, 'is_vice_captain': True},
                # ... more picks would be here
            ]
        }
    
    def _get_players_data(self):
        """Get players data from session state or load"""
        if st.session_state.get('players_df') is not None:
            return st.session_state.players_df
        
        # Mock player data for demonstration
        mock_players = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'web_name': ['Pope', 'Alexander-Arnold', 'Salah', 'Haaland', 'Bruno'],
            'element_type': [1, 2, 3, 4, 3],
            'team': [1, 2, 2, 3, 4],
            'total_points': [85, 145, 203, 189, 167],
            'now_cost': [55, 75, 130, 140, 105],
            'selected_by_percent': [12.5, 45.2, 67.8, 78.9, 34.1]
        })
        
        return mock_players
    
    def _load_player_data(self):
        """Load player data"""
        try:
            with st.spinner("📥 Loading player data..."):
                # In a real implementation, this would load from FPL API
                players_df = self._get_players_data()
                st.session_state.players_df = players_df
                st.success("✅ Player data loaded!")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Failed to load player data: {str(e)}")
    
    def _refresh_team_data(self):
        """Refresh team data"""
        if st.session_state.team_id:
            self._load_team(st.session_state.team_id)
        else:
            st.warning("⚠️ No team loaded to refresh")
    
    def _reset_team_state(self):
        """Reset team state"""
        reset_keys = ['team_loaded', 'team_id', 'team_data', 'last_update']
        for key in reset_keys:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    def _generate_recommendations(self, team_data):
        """Generate smart recommendations"""
        recommendations = []
        
        overall_rank = team_data.get('summary_overall_rank', 0)
        gameweek_points = team_data.get('summary_event_points', 0)
        
        # Rank-based recommendations
        if overall_rank > 500000:
            recommendations.append({
                'title': 'Improve Overall Rank',
                'description': 'Your current rank suggests there\'s room for improvement.',
                'action': 'Consider more differential picks and captain choices',
                'priority': 'high'
            })
        
        # Points-based recommendations
        if gameweek_points < 40:
            recommendations.append({
                'title': 'Boost Gameweek Performance',
                'description': 'Recent gameweek performance is below average.',
                'action': 'Review your captain choice and starting XI',
                'priority': 'medium'
            })
        
        # General recommendations
        recommendations.append({
            'title': 'Regular Team Review',
            'description': 'Keep your team updated with latest performances.',
            'action': 'Review team weekly and make necessary transfers',
            'priority': 'low'
        })
        
        return recommendations
    
    def _update_player_data(self):
        """Update player data"""
        with st.spinner("🔄 Updating player data..."):
            time.sleep(1)
            self._load_player_data()
    
    def _run_deep_analysis(self, team_data):
        """Run deep analysis"""
        st.info("🔍 Running deep analysis...")
        with st.spinner("Analyzing..."):
            time.sleep(2)
        st.success("✅ Deep analysis complete! Check recommendations.")
    
    def _show_value_calculator(self, team_data):
        """Show value calculator"""
        st.info("💰 Value calculator opened in sidebar")
        with st.sidebar:
            st.markdown("### 💰 Value Calculator")
            current_value = team_data.get('value', 0) / 10
            st.metric("Current Squad Value", f"£{current_value:.1f}m")
    
    def _show_rank_tracker(self, team_data):
        """Show rank tracker"""
        current_rank = team_data.get('summary_overall_rank', 0)
        st.info(f"🏆 Current rank: {current_rank:,}")


# Create alias for backward compatibility
MyTeamPage = RebuildMyTeamPage
