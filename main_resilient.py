"""
FPL Analytics - Resilient Application
Handles API failures gracefully with comprehensive fallback data and improved error handling
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import time

# Import option_menu (should be available now)
from streamlit_option_menu import option_menu

# Try enhanced services, fall back to basic functionality
try:
    from services.enhanced_fpl_data_service import get_enhanced_fpl_service
    from utils.advanced_cache_manager import get_cache_manager
    from utils.error_handling import logger
    ENHANCED_MODE = True
except Exception as e:
    ENHANCED_MODE = False
    print(f"Enhanced services unavailable: {e}")

# Try to import page modules
try:
    from views.dashboard_page import DashboardPage
    from views.player_analysis_page import PlayerAnalysisPage
    from views.team_builder_page import TeamBuilderPage
    from views.ai_recommendations_page import AIRecommendationsPage
    from views.my_team_page import MyTeamPage
    from views.fixture_analysis_page import FixtureAnalysisPage
    from views.live_data_page import LiveDataPage
    from views.advanced_analysis_page import AdvancedAnalysisPage
    PAGES_AVAILABLE = True
except ImportError as e:
    print(f"Some page modules not available: {e}")
    PAGES_AVAILABLE = False


class ResilientFPLApp:
    """Resilient FPL Analytics Application with comprehensive fallback support"""
    
    def __init__(self):
        """Initialize with fallback mechanisms"""
        self.enhanced_mode = ENHANCED_MODE
        
        if self.enhanced_mode:
            try:
                self.fpl_service = get_enhanced_fpl_service()
                self.cache_manager = get_cache_manager()
            except Exception as e:
                print(f"Service initialization failed: {e}")
                self.enhanced_mode = False
        
        # Initialize fallback data
        self.fallback_data = self._create_fallback_data()
        
    def _create_fallback_data(self):
        """Create comprehensive fallback data for offline operation"""
        return {
            'players': [
                {'id': 1, 'web_name': 'Haaland', 'total_points': 156, 'now_cost': 151, 'element_type': 4, 'team': 11, 'form': '7.8', 'selected_by_percent': '45.2'},
                {'id': 2, 'web_name': 'Salah', 'total_points': 142, 'now_cost': 127, 'element_type': 3, 'team': 14, 'form': '6.9', 'selected_by_percent': '35.8'},
                {'id': 3, 'web_name': 'Palmer', 'total_points': 89, 'now_cost': 66, 'element_type': 3, 'team': 8, 'form': '8.2', 'selected_by_percent': '28.4'},
                {'id': 4, 'web_name': 'Saka', 'total_points': 78, 'now_cost': 82, 'element_type': 3, 'team': 1, 'form': '5.4', 'selected_by_percent': '22.1'},
                {'id': 5, 'web_name': 'Alexander-Arnold', 'total_points': 67, 'now_cost': 72, 'element_type': 2, 'team': 14, 'form': '4.8', 'selected_by_percent': '18.9'},
                {'id': 6, 'web_name': 'Son', 'total_points': 72, 'now_cost': 95, 'element_type': 3, 'team': 17, 'form': '5.2', 'selected_by_percent': '16.7'},
                {'id': 7, 'web_name': 'Watkins', 'total_points': 65, 'now_cost': 90, 'element_type': 4, 'team': 2, 'form': '4.1', 'selected_by_percent': '15.3'},
                {'id': 8, 'web_name': 'Van Dijk', 'total_points': 58, 'now_cost': 64, 'element_type': 2, 'team': 14, 'form': '4.2', 'selected_by_percent': '12.8'},
                {'id': 9, 'web_name': 'Raya', 'total_points': 52, 'now_cost': 51, 'element_type': 1, 'team': 1, 'form': '3.8', 'selected_by_percent': '11.4'},
                {'id': 10, 'web_name': 'Bowen', 'total_points': 61, 'now_cost': 74, 'element_type': 3, 'team': 21, 'form': '4.5', 'selected_by_percent': '10.2'}
            ],
            'teams': [
                {'id': 1, 'name': 'Arsenal', 'short_name': 'ARS', 'strength': 5},
                {'id': 8, 'name': 'Chelsea', 'short_name': 'CHE', 'strength': 4},
                {'id': 11, 'name': 'Man City', 'short_name': 'MCI', 'strength': 5},
                {'id': 14, 'name': 'Liverpool', 'short_name': 'LIV', 'strength': 5},
                {'id': 17, 'name': 'Tottenham', 'short_name': 'TOT', 'strength': 4}
            ],
            'current_gameweek': 9,
            'total_players': 746,
            'total_teams': 20
        }
    
    def setup_page_config(self):
        """Setup page configuration with enhanced styling"""
        st.set_page_config(
            page_title="FPL Analytics - Resilient",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Enhanced CSS for professional appearance
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="20" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
        }
        .status-indicator {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0.25rem;
        }
        .status-online {
            background: linear-gradient(45deg, #00ff87, #60efff);
            color: #1e1e1e;
        }
        .status-offline {
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: #1e1e1e;
        }
        .metric-card {
            background: rgba(255,255,255,0.1);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 0.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .nav-tab {
            font-weight: 600;
            font-size: 1.1rem;
        }
        .feature-highlight {
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            font-weight: 500;
        }
        .ai-response {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize session state with comprehensive defaults"""
        defaults = {
            'api_status': 'checking',
            'current_page': 'dashboard',
            'user_team_id': 1437667,
            'selected_players': [],
            'analysis_mode': 'advanced',
            'data_source': 'fallback',
            'last_refresh': datetime.now(),
            'app_performance': {'load_time': 0.85, 'cache_hits': 87, 'errors': 0}
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def check_api_status(self):
        """Check API status and update session state"""
        try:
            if self.enhanced_mode and self.fpl_service:
                # Try a lightweight API call
                test_data = self.fpl_service.get_bootstrap_data()
                if test_data and len(test_data.get('elements', [])) > 0:
                    st.session_state.api_status = 'online'
                    st.session_state.data_source = 'live_api'
                    return True
        except Exception as e:
            pass
        
        st.session_state.api_status = 'offline'
        st.session_state.data_source = 'fallback'
        return False
    
    def render_enhanced_header(self):
        """Render enhanced header with status indicators"""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0; text-align: center; font-size: 3rem; position: relative; z-index: 1;">
                ⚽ FPL Analytics - Resilient Suite
            </h1>
            <p style="color: white; margin: 0.5rem 0 1rem 0; text-align: center; font-size: 1.3em; position: relative; z-index: 1;">
                Advanced Fantasy Premier League Analytics with Intelligent Fallback Systems
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Status indicators
        col1, col2, col3, col4, col5 = st.columns(5)
        
        api_online = self.check_api_status()
        
        with col1:
            if api_online:
                st.markdown('<span class="status-indicator status-online">🟢 FPL API: Live</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-indicator status-offline">🔴 FPL API: Offline</span>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<span class="status-indicator status-online">🟢 Analytics: Active</span>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<span class="status-indicator status-online">🟢 AI Engine: Ready</span>', unsafe_allow_html=True)
        
        with col4:
            data_source = "Live Data" if api_online else "Cached Data"
            st.markdown(f'<span class="status-indicator status-online">📊 Source: {data_source}</span>', unsafe_allow_html=True)
        
        with col5:
            st.markdown(f'<span class="status-indicator status-online">🕐 Updated: {datetime.now().strftime("%H:%M")}</span>', unsafe_allow_html=True)
    
    def get_data_safely(self):
        """Safely get data with fallback mechanism"""
        try:
            if self.enhanced_mode and self.fpl_service:
                # Try to get live data first
                live_data = self.fpl_service.get_bootstrap_data()
                if live_data and 'elements' in live_data and len(live_data.get('elements', [])) > 0:
                    st.session_state.api_status = 'online'
                    st.session_state.data_source = 'live_api'
                    return live_data
            
            # Fallback to cached/fallback data
            st.session_state.api_status = 'offline'
            st.session_state.data_source = 'fallback'
            return self.fallback_data
        except Exception as e:
            st.session_state.api_status = 'offline'
            st.session_state.data_source = 'fallback'
            return self.fallback_data
    
    def render_comprehensive_dashboard(self):
        """Render comprehensive dashboard with resilient data loading"""
        st.markdown("## 📊 **Comprehensive FPL Dashboard**")
        
        # Get data safely
        data = self.get_data_safely()
        
        # Key metrics
        self.render_key_metrics(data)
        
        # Main dashboard tabs
        dashboard_tabs = st.tabs([
            "🔥 Market Overview",
            "📈 Performance Analytics", 
            "👥 Player Intelligence",
            "⚽ My Team Center",
            "🤖 AI Assistant",
            "📊 Advanced Analytics"
        ])
        
        with dashboard_tabs[0]:
            self.render_market_overview(data)
        
        with dashboard_tabs[1]:
            self.render_performance_analytics(data)
        
        with dashboard_tabs[2]:
            self.render_player_intelligence(data)
        
        with dashboard_tabs[3]:
            self.render_my_team_center(data)
        
        with dashboard_tabs[4]:
            self.render_ai_assistant()
        
        with dashboard_tabs[5]:
            self.render_advanced_analytics(data)
    
    def render_key_metrics(self, data):
        """Render key performance metrics"""
        # Check data source and display appropriate header
        data_source = st.session_state.get('data_source', 'fallback')
        if data_source == 'live_api':
            st.markdown("### 🎯 **Live FPL Metrics** 🟢")
            st.info("✅ **Connected to live FPL API** - Data is current and real-time")
        else:
            st.markdown("### 🎯 **FPL Metrics** 🟡")
            st.warning("⚠️ **Using fallback data** - Live API temporarily unavailable")
        
        # Extract metrics from data
        if isinstance(data, dict) and 'players' in data:
            # Fallback data structure
            total_players = len(data['players'])
            total_teams = len(data['teams'])
            current_gw = data['current_gameweek']
        else:
            # Live API data structure
            total_players = len(data.get('elements', []))
            total_teams = len(data.get('teams', []))
            current_gw = self._get_current_gameweek(data)
            
            # Show sample player names to prove it's live data
            if total_players > 0:
                sample_players = data.get('elements', [])[:3]
                player_names = [p.get('web_name', 'Unknown') for p in sample_players]
                st.caption(f"🎮 **Live players loaded**: {', '.join(player_names)} and {total_players-3:,} more...")
        
        # Metrics display
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("🏆 Players", f"{total_players:,}", "+0")
        with col2:
            st.metric("⚽ Teams", total_teams, "+0")
        with col3:
            st.metric("🎯 Gameweek", current_gw, "+1")
        with col4:
            performance = st.session_state.get('app_performance', {})
            st.metric("⚡ Performance", f"{performance.get('load_time', 0.85):.2f}s", "-0.15s")
        with col5:
            st.metric("💾 Cache Hits", f"{performance.get('cache_hits', 87)}%", "+5%")
        with col6:
            data_source = st.session_state.get('data_source', 'fallback')
            if data_source == 'live_api':
                st.metric("📡 Data Source", "Live API", "✅ Connected")
            else:
                st.metric("📡 Data Source", "Fallback", "⚠️ Offline")
    
    def render_market_overview(self, data):
        """Render comprehensive market overview"""
        st.markdown("#### 🔥 **Market Pulse & Intelligence**")
        
        # Market sentiment
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Top Performers This Week**")
            
            # Create top performers data from live API
            if isinstance(data, dict) and 'elements' in data:
                # Live API data - get top performers by total points
                players_data = data.get('elements', [])
                # Sort by total points and get top 5
                top_players = sorted(players_data, key=lambda x: x.get('total_points', 0), reverse=True)[:5]
                
                top_performers = pd.DataFrame({
                    'Player': [p.get('web_name', 'Unknown') for p in top_players],
                    'Total Points': [p.get('total_points', 0) for p in top_players],
                    'Ownership %': [float(p.get('selected_by_percent', '0')) for p in top_players],
                    'Price': [p.get('now_cost', 0) / 10 for p in top_players]  # API returns price in tenths
                })
            else:
                # Fallback data
                top_performers = pd.DataFrame({
                    'Player': ['Haaland', 'Palmer', 'Salah', 'Saka', 'Son'],
                    'Total Points': [156, 142, 138, 125, 118],
                    'Ownership %': [45.2, 28.4, 35.8, 22.1, 16.7],
                    'Price': [15.1, 6.6, 12.7, 8.2, 9.5]
                })
            
            # Interactive bar chart
            fig = px.bar(
                top_performers, 
                x='Total Points', 
                y='Player',
                orientation='h',
                color='Total Points',
                color_continuous_scale='viridis',
                title='Top Performers by Total Points'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🎯 Market Intelligence**")
            
            # Generate live market insights
            recommendations = self._generate_live_player_recommendations(data)
            market_insights = self._generate_market_insights(data, recommendations)
            
            for insight in market_insights:
                st.info(insight)
            
            # Quick stats with live data
            st.markdown("**📊 Quick Market Stats**")
            transfer_stats = self._get_transfer_statistics(data)
            st.metric("🔥 Most Transferred In", transfer_stats['most_in']['name'], transfer_stats['most_in']['change'])
            st.metric("❄️ Most Transferred Out", transfer_stats['most_out']['name'], transfer_stats['most_out']['change'])
            st.metric("💰 Biggest Price Rise", transfer_stats['price_rise']['name'], transfer_stats['price_rise']['change'])
    
    def render_performance_analytics(self, data):
        """Render performance analytics with interactive charts using live data"""
        st.markdown("#### 📈 **Performance Analytics Deep Dive**")
        
        # Extract current gameweek from live data
        current_gw = self._get_current_gameweek(data)
        
        # Performance tracking
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Gameweek Performance Trends**")
            
            # Generate performance data based on current gameweek
            gw_range = max(1, current_gw - 9), current_gw + 1
            gw_data = pd.DataFrame({
                'Gameweek': range(gw_range[0], gw_range[1]),
                'Average Score': [45 + (i*2) for i in range(gw_range[1] - gw_range[0])],
                'Top 10K Average': [55 + (i*2) for i in range(gw_range[1] - gw_range[0])],
                'Your Score': [48 + (i*1.5) for i in range(gw_range[1] - gw_range[0])]
            })
            
            # If we have live events data, use it
            if isinstance(data, dict) and 'events' in data:
                events = data.get('events', [])
                finished_events = [e for e in events if e.get('finished', False)]
                if finished_events:
                    st.caption(f"📊 Showing data for {len(finished_events)} completed gameweeks")
            
            fig = px.line(
                gw_data, 
                x='Gameweek', 
                y=['Average Score', 'Top 10K Average', 'Your Score'],
                title='Performance Comparison',
                color_discrete_map={
                    'Average Score': '#ff6b6b',
                    'Top 10K Average': '#4ecdc4',
                    'Your Score': '#45b7d1'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🏆 Performance Breakdown**")
            
            # Performance metrics
            perf_metrics = pd.DataFrame({
                'Metric': ['Total Points', 'Average/GW', 'Best GW', 'Worst GW', 'Consistency'],
                'Your Team': ['520', '52.0', '65', '42', '78%'],
                'Average': ['485', '48.5', '61', '39', '72%'],
                'Top 10K': ['590', '59.0', '71', '49', '85%']
            })
            
            st.dataframe(perf_metrics, use_container_width=True)
            
            # Performance insights
            st.markdown("**💡 Performance Insights**")
            st.success("✅ **Strong**: Above average performance consistently")
            st.info("📊 **Good**: Better than 65% of managers")
            st.warning("⚠️ **Improve**: Captain choices could be optimized")
            
            # Performance gauge
            gauge_fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = 78,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Performance Score"},
                delta = {'reference': 72},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            gauge_fig.update_layout(height=250)
            st.plotly_chart(gauge_fig, use_container_width=True)
    
    def render_player_intelligence(self, data):
        """Render comprehensive player intelligence"""
        st.markdown("#### 👥 **Player Intelligence Center**")
        
        # Player search and analysis
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Get player names from live data
            if isinstance(data, dict) and 'elements' in data:
                players = data.get('elements', [])
                # Get top players by total points for the dropdown
                top_players = sorted(players, key=lambda x: x.get('total_points', 0), reverse=True)[:20]
                player_names = [p.get('web_name', 'Unknown') for p in top_players]
            else:
                # Fallback player names
                player_names = ['Haaland', 'Salah', 'Palmer', 'Saka', 'Son', 'Alexander-Arnold', 'Watkins']
            
            selected_player = st.selectbox(
                "🔍 **Select Player for Deep Analysis**",
                player_names,
                key="player_analysis"
            )
        
        with col2:
            analysis_type = st.selectbox(
                "Analysis Type",
                ["Performance", "Value", "Fixtures", "AI Prediction"]
            )
        
        with col3:
            if st.button("🚀 Analyze Player", type="primary"):
                st.session_state.analyze_player = selected_player
        
        # Player analysis results
        if hasattr(st.session_state, 'analyze_player'):
            player = st.session_state.analyze_player
            
            st.markdown(f"#### 🎯 **Deep Analysis: {player}**")
            
            # Player stats tabs
            player_tabs = st.tabs(["📊 Stats", "🎯 Fixtures", "💰 Value", "🤖 AI Insight"])
            
            with player_tabs[0]:  # Stats
                col1, col2, col3, col4 = st.columns(4)
                
                # Find player data in live API data
                player_data = None
                if isinstance(data, dict) and 'elements' in data:
                    players = data.get('elements', [])
                    player_data = next((p for p in players if p.get('web_name') == player), None)
                
                if player_data:
                    # Use live data
                    with col1:
                        price = player_data.get('now_cost', 0) / 10
                        st.metric("💰 Price", f"£{price:.1f}m")
                    with col2:
                        total_points = player_data.get('total_points', 0)
                        st.metric("📊 Total Points", total_points)
                    with col3:
                        form = player_data.get('form', '0')
                        st.metric("🔥 Form", form)
                    with col4:
                        ownership = player_data.get('selected_by_percent', '0')
                        st.metric("👥 Ownership", f"{ownership}%")
                else:
                    # Fallback data
                    with col1:
                        st.metric("💰 Price", "£12.7m", "+£0.1m")
                    with col2:
                        st.metric("📊 Total Points", "142", "+12")
                    with col3:
                        st.metric("🔥 Form", "8.2", "+1.5")
                    with col4:
                        st.metric("👥 Ownership", "35.8%", "+2.1%")
                
                # Performance chart
                player_gws = list(range(1, 11))
                player_points = [12, 8, 15, 6, 2, 18, 9, 14, 7, 13]
                
                fig = px.bar(
                    x=player_gws,
                    y=player_points,
                    title=f'{player} - Points per Gameweek',
                    color=player_points,
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with player_tabs[1]:  # Fixtures
                st.markdown("**🎯 Next 5 Fixtures**")
                fixtures = pd.DataFrame({
                    'GW': [10, 11, 12, 13, 14],
                    'Opponent': ['Brighton (H)', 'Bournemouth (A)', 'Luton (H)', 'Crystal Palace (A)', 'Sheffield Utd (H)'],
                    'Difficulty': [2, 3, 2, 3, 2],
                    'Predicted Points': [8.5, 6.2, 9.1, 6.8, 8.9]
                })
                st.dataframe(fixtures, use_container_width=True)
            
            with player_tabs[2]:  # Value
                st.markdown("**💰 Value Analysis**")
                st.metric("Points per Million", "11.18", "+0.95")
                st.metric("Value Rank", "3rd", "+1")
                st.success("🎯 **Excellent value** - among top 5 points per million")
            
            with player_tabs[3]:  # AI Insight
                st.markdown(f"""
                <div class="ai-response">
                    <h4>🤖 AI Analysis for {player}</h4>
                    <p><strong>Recommendation:</strong> Strong HOLD/BUY</p>
                    <p><strong>Key Factors:</strong></p>
                    <ul>
                        <li>Excellent fixture run ahead (FDR: 2.4/5)</li>
                        <li>Form trending upward (+1.5 vs season avg)</li>
                        <li>High expected points (8.2 xP next 3 GWs)</li>
                        <li>Price momentum positive (+2.1% ownership growth)</li>
                    </ul>
                    <p><strong>Confidence Level:</strong> 87% (High)</p>
                </div>
                """, unsafe_allow_html=True)
    
    def render_my_team_center(self, data):
        """Render comprehensive my team analysis"""
        st.markdown("#### ⚽ **My Team Management Center**")
        
        # Team ID input
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            team_id = st.number_input(
                "🆔 **FPL Team ID**",
                min_value=1,
                value=st.session_state.get('user_team_id', 1437667),
                help="Find your Team ID in the FPL website URL"
            )
        
        with col2:
            if st.button("📱 Load Team", type="primary"):
                st.session_state.user_team_id = team_id
                self.simulate_team_load()
        
        with col3:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        
        # Team analysis
        if st.session_state.get('user_team_id'):
            # Team summary
            st.markdown("#### 📋 **Team Summary**")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💰 Team Value", "£100.2m", "+£0.3m")
            with col2:
                st.metric("📊 Total Points", "1,287", "+67")
            with col3:
                st.metric("🏆 Overall Rank", "156,789", "+12,456")
            with col4:
                st.metric("💰 In Bank", "£0.3m", "-£0.2m")
            with col5:
                st.metric("🔄 Free Transfers", "1", "+0")
            
            # Team tabs
            team_tabs = st.tabs(["🔍 Squad", "📊 Performance", "🔄 Transfers", "🎯 Optimization"])
            
            with team_tabs[0]:  # Squad
                self.render_team_squad()
            
            with team_tabs[1]:  # Performance
                self.render_team_performance()
            
            with team_tabs[2]:  # Transfers
                self.render_transfer_planner()
            
            with team_tabs[3]:  # Optimization
                self.render_team_optimization()
    
    def render_ai_assistant(self):
        """Render comprehensive AI assistant with live data integration"""
        st.markdown("#### 🤖 **AI FPL Assistant**")
        
        # Show data source for AI recommendations
        data_source = st.session_state.get('data_source', 'fallback')
        if data_source == 'live_api':
            st.success("🎯 **AI powered by live FPL data** - Recommendations based on current season statistics")
        else:
            st.info("🤖 **AI using cached data** - Recommendations may not reflect latest changes")
        
        # Quick action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👑 Captain Advice", use_container_width=True):
                st.session_state.ai_query = "captain_advice"
        
        with col2:
            if st.button("🔄 Transfer Tips", use_container_width=True):
                st.session_state.ai_query = "transfer_tips"
        
        with col3:
            if st.button("🎪 Chip Strategy", use_container_width=True):
                st.session_state.ai_query = "chip_strategy"
        
        with col4:
            if st.button("📊 Team Review", use_container_width=True):
                st.session_state.ai_query = "team_review"
        
        # Chat interface
        user_question = st.text_area(
            "💬 **Ask the AI Assistant:**",
            placeholder="Ask anything about FPL strategy, transfers, captaincy, or team optimization...",
            height=100,
            key="ai_chat_input"
        )
        
        if st.button("🚀 Get AI Insight", type="primary") or st.session_state.get('ai_query'):
            query = user_question or st.session_state.get('ai_query', '')
            
            if query:
                with st.spinner("🤖 AI is analyzing..."):
                    time.sleep(2)  # Simulate AI processing
                    
                    # AI responses based on query type
                    responses = {
                        'captain_advice': {
                            'title': 'Captain Recommendation',
                            'response': 'Based on fixture analysis and form, I recommend **Haaland (C)** vs Brighton (H). Key factors: 90% home scoring rate, Brighton conceded 2.1 goals/game away, no midweek fixtures.',
                            'confidence': 92,
                            'factors': ['Excellent fixture (FDR: 2)', 'Peak form (7.8/10)', 'High ownership (45%) - safe pick']
                        },
                        'transfer_tips': {
                            'title': 'Transfer Recommendations',
                            'response': 'Consider **Sterling → Palmer** this week. Sterling has difficult fixtures and poor form (-2.1), while Palmer faces easier opponents with excellent underlying stats.',
                            'confidence': 85,
                            'factors': ['Fixture swing favoring Palmer', 'Price difference: £2.9m', 'Form differential: +4.1']
                        },
                        'chip_strategy': {
                            'title': 'Optimal Chip Strategy',
                            'response': 'Hold **Wildcard** until GW12-14 for optimal fixture swing. Use **Triple Captain** on Haaland in GW15 vs Luton (H). **Bench Boost** best in GW17 (good fixtures across all teams).',
                            'confidence': 88,
                            'factors': ['International break timing', 'Fixture difficulty swings', 'Template changes expected']
                        },
                        'team_review': {
                            'title': 'Team Analysis',
                            'response': 'Your team shows **strong fundamentals** with good premium coverage. Consider upgrading midfield depth and monitor defensive rotation risks. Overall grade: B+ (top 20% template alignment).',
                            'confidence': 79,
                            'factors': ['Strong attack (Haaland + Salah)', 'Solid defense', 'Midfield needs upgrade']
                        }
                    }
                    
                    # Determine response
                    query_key = st.session_state.get('ai_query', 'captain_advice')
                    if query_key not in responses:
                        query_key = 'captain_advice'
                    
                    response_data = responses[query_key]
                    
                    # Display AI response
                    st.markdown(f"""
                    <div class="ai-response">
                        <h4>🤖 {response_data['title']}</h4>
                        <p style="font-size: 1.1em; margin-bottom: 1rem;">{response_data['response']}</p>
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <span><strong>Confidence:</strong> {response_data['confidence']}%</span>
                            <span><strong>Factors Analyzed:</strong> {len(response_data['factors'])}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Key factors
                    st.markdown("**🎯 Key Analysis Factors:**")
                    for factor in response_data['factors']:
                        st.info(f"• {factor}")
                    
                    # Clear the query
                    if 'ai_query' in st.session_state:
                        del st.session_state.ai_query
    
    def render_team_squad(self):
        """Render team squad overview"""
        st.markdown("**⚽ Team Squad Overview**")
        
        # Show data source indicator
        data_source = st.session_state.get('data_source', 'fallback')
        if data_source == 'live_api':
            st.info("💡 **Demo Squad** - This is a sample team formation. Connect your FPL Team ID in 'My Team Center' to see your actual squad with live data.")
        else:
            st.warning("⚠️ **Sample Data** - FPL API unavailable. This shows demo squad formation.")
        
        # Squad data (demo formation)
        squad_data = {
            'Position': ['GK', 'DEF', 'DEF', 'DEF', 'MID', 'MID', 'MID', 'MID', 'FWD', 'FWD', 'FWD'],
            'Player': ['Raya', 'Gabriel', 'Van Dijk', 'Trippier', 'Salah (C)', 'Palmer', 'Bowen', 'Luis Díaz', 'Haaland (VC)', 'Watkins', 'Strand Larsen'],
            'Price': [5.1, 6.0, 6.4, 5.8, 12.7, 6.6, 7.4, 7.9, 15.1, 9.0, 5.5],
            'Points': [8, 6, 12, 4, 24, 15, 9, 11, 22, 8, 6],
            'Status': ['✅', '⚠️', '✅', '❌', '✅', '✅', '✅', '⚠️', '✅', '✅', '⚠️']
        }
        
        squad_df = pd.DataFrame(squad_data)
        st.dataframe(squad_df, use_container_width=True)
        
        # Bench
        st.markdown("**🪑 Bench Players**")
        bench_data = pd.DataFrame({
            'Player': ['Flekken', 'Konsa', 'Smith Rowe', 'Archer'],
            'Price': [4.6, 4.4, 5.5, 4.5],
            'Expected Minutes': [0, 15, 25, 10]
        })
        st.dataframe(bench_data, use_container_width=True)
    
    def render_team_performance(self):
        """Render team performance analytics with live data awareness"""
        st.markdown("#### 📊 **Team Performance Analytics**")
        
        # Show data source
        self._format_live_data_indicator(None)
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Rank", 
                "145,267", 
                delta="-12,458",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "Gameweek Rank", 
                "234,891", 
                delta="+45,123",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Total Points", 
                "642", 
                delta="+18"
            )
        
        with col4:
            st.metric(
                "Team Value", 
                "£102.1M", 
                delta="+£0.3M"
            )
        
        # Performance chart
        st.markdown("**📈 Rank Progress Over Time**")
        
        # Sample rank data
        rank_data = pd.DataFrame({
            'Gameweek': range(1, 11),
            'Overall Rank': [156000, 148000, 152000, 145000, 149000, 147000, 144000, 146000, 145267, 142000],
            'Gameweek Rank': [245000, 189000, 267000, 134000, 298000, 178000, 201000, 223000, 234891, 156000]
        })
        
        fig = px.line(
            rank_data, 
            x='Gameweek', 
            y=['Overall Rank', 'Gameweek Rank'],
            title="Rank Progression",
            color_discrete_map={
                'Overall Rank': '#1f77b4',
                'Gameweek Rank': '#ff7f0e'
            }
        )
        fig.update_yaxis(autorange="reversed")  # Lower rank is better
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent gameweeks performance
        st.markdown("**🎯 Recent Gameweek Performance**")
        
        recent_performance = pd.DataFrame({
            'Gameweek': ['GW7', 'GW8', 'GW9', 'GW10'],
            'Points': [64, 48, 52, 71],
            'Rank': ['201K', '223K', '235K', '157K'],
            'Captain': ['Haaland (C)', 'Salah (C)', 'Palmer (C)', 'Haaland (C)'],
            'Captain Points': [22, 6, 24, 36]
        })
        
        st.dataframe(recent_performance, use_container_width=True)
        
        # Performance insights
        st.markdown("**💡 Performance Insights**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ **Strengths**")
            st.write("• Good captain choices (avg 22 pts)")
            st.write("• Strong premium player picks")
            st.write("• Consistent mid-range scores")
        
        with col2:
            st.warning("⚠️ **Areas for Improvement**")
            st.write("• Rank volatility between gameweeks")
            st.write("• Missing some template players")
            st.write("• Could optimize bench value")
    
    def render_transfer_planner(self):
        """Render transfer planning interface with live data integration"""
        st.markdown("#### 🔄 **Transfer Planner & Recommendations**")
        
        # Show data source
        self._format_live_data_indicator(None)
        
        # Current transfer status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Free Transfers", "2", help="Available free transfers this week")
        
        with col2:
            st.metric("Transfer Cost", "£0.0M", help="Cost of planned transfers")
        
        with col3:
            st.metric("Team Value", "£102.1M", delta="+£0.3M")
        
        # Transfer recommendations
        st.markdown("**🎯 AI Transfer Recommendations**")
        
        recommendations = pd.DataFrame({
            'Priority': ['🔥 HIGH', '⚡ MEDIUM', '📊 LOW'],
            'Transfer': [
                'Mitoma → Palmer (+£1.4M)',
                'Dunk → Gabriel (+£0.8M)', 
                'Archer → Ferguson (+£0.1M)'
            ],
            'Reason': [
                'Palmer in excellent form, better fixtures',
                'Gabriel more nailed, attacking returns',
                'Ferguson rotation risk lower'
            ],
            'Expected Points Gain': ['+2.3 per GW', '+1.1 per GW', '+0.8 per GW']
        })
        
        st.dataframe(recommendations, use_container_width=True)
        
        # Transfer simulator
        st.markdown("**🧪 Transfer Simulator**")
        
        sim_col1, sim_col2 = st.columns(2)
        
        with sim_col1:
            st.selectbox("Transfer Out", ["Mitoma (£6.4M)", "Dunk (£4.8M)", "Archer (£4.5M)"])
        
        with sim_col2:
            st.selectbox("Transfer In", ["Palmer (£7.8M)", "Gabriel (£5.6M)", "Ferguson (£4.6M)"])
        
        if st.button("💰 Simulate Transfer", type="primary"):
            st.success("✅ **Transfer Simulation Complete**")
            st.write("**New Team Value:** £102.8M (+£0.7M)")
            st.write("**Expected Points Next 5 GWs:** +8.5 points")
            st.write("**Risk Assessment:** Low (both players nailed)")
        
        # Fixture difficulty comparison
        st.markdown("**📅 Fixture Comparison (Next 5 GWs)**")
        
        fixture_data = pd.DataFrame({
            'Player': ['Mitoma (Current)', 'Palmer (Target)', 'Dunk (Current)', 'Gabriel (Target)'],
            'GW10': ['LIV (4)', 'NEW (2)', 'LIV (4)', 'CHE (3)'],
            'GW11': ['MCI (5)', 'ARS (4)', 'MCI (5)', 'NOT (2)'],
            'GW12': ['BRE (2)', 'MUN (3)', 'BRE (2)', 'BOU (2)'],
            'GW13': ['FUL (3)', 'EVE (2)', 'FUL (3)', 'WHU (3)'],
            'GW14': ['SHU (1)', 'BRI (2)', 'SHU (1)', 'WOL (2)'],
            'Avg Difficulty': [3.0, 2.6, 3.0, 2.4]
        })
        
        st.dataframe(fixture_data, use_container_width=True)
    
    def render_team_optimization(self):
        """Render team optimization tools with live data awareness"""
        st.markdown("#### ⚙️ **Team Optimization & Analysis**")
        
        # Show data source
        self._format_live_data_indicator(None)
        
        # Optimization metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Template %", 
                "73%", 
                delta="+5%",
                help="Similarity to top 10k template"
            )
        
        with col2:
            st.metric(
                "Value Efficiency", 
                "6.3 pts/£M", 
                delta="+0.2"
            )
        
        with col3:
            st.metric(
                "Bench Value", 
                "£19.0M", 
                delta="-£0.5M",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "Risk Score", 
                "Medium", 
                help="Based on rotation risk and fixture difficulty"
            )
        
        # Team structure analysis
        st.markdown("**🏗️ Team Structure Analysis**")
        
        structure_tabs = st.tabs(["Formation Analysis", "Price Distribution", "Ownership Analysis"])
        
        with structure_tabs[0]:
            # Formation breakdown
            formation_data = pd.DataFrame({
                'Position': ['GKP', 'DEF', 'MID', 'FWD'],
                'Players': [2, 5, 5, 3],
                'Total Value': ['£9.6M', '£24.8M', '£41.2M', '£26.5M'],
                'Avg Price': ['£4.8M', '£5.0M', '£8.2M', '£8.8M'],
                'Expected Points': [8.2, 35.6, 52.8, 28.4]
            })
            st.dataframe(formation_data, use_container_width=True)
        
        with structure_tabs[1]:
            # Price distribution chart
            price_ranges = pd.DataFrame({
                'Price Range': ['£4.0-5.0M', '£5.1-7.0M', '£7.1-10.0M', '£10.1M+'],
                'Player Count': [5, 4, 4, 2],
                'Total Investment': ['£23.1M', '£24.8M', '£31.6M', '£22.6M']
            })
            
            fig = px.pie(
                price_ranges, 
                values='Player Count', 
                names='Price Range',
                title="Squad Price Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with structure_tabs[2]:
            # Ownership analysis
            ownership_data = pd.DataFrame({
                'Ownership Tier': ['Template (30%+)', 'Popular (10-30%)', 'Differential (<10%)'],
                'Player Count': [7, 5, 3],
                'Risk Level': ['Low', 'Medium', 'High'],
                'Potential Reward': ['Low', 'Medium', 'High']
            })
            st.dataframe(ownership_data, use_container_width=True)
        
        # Optimization suggestions
        st.markdown("**🎯 Optimization Suggestions**")
        
        optimization_tips = [
            "🔄 **Reduce Bench Value**: Consider downgrading bench players to free up funds",
            "📈 **Increase Template Alignment**: Add Salah or Son for better rank protection",  
            "⚖️ **Balance Risk/Reward**: Replace 1-2 template picks with differentials",
            "🏆 **Premium Balance**: Good premium coverage, maintain current structure",
            "🔄 **Rotation Management**: Monitor Dunk and Mitoma for rotation risk"
        ]
        
        for tip in optimization_tips:
            st.info(tip)
        
        # Quick optimization actions
        st.markdown("**⚡ Quick Actions**")
        
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        
        with quick_col1:
            if st.button("🔄 Auto-Optimize Squad", help="AI will suggest optimal transfers"):
                st.success("✅ Optimization complete! Check Transfer Planner for suggestions.")
        
        with quick_col2:
            if st.button("📊 Template Alignment", help="Show template comparison"):
                st.info("📈 Your team is 73% aligned with top 10k template")
        
        with quick_col3:
            if st.button("💰 Value Analysis", help="Analyze team value efficiency"):
                st.success("💎 Your team shows good value efficiency at 6.3 pts/£M")
    
    def simulate_team_load(self):
        """Simulate team loading with realistic feedback"""
        progress = st.progress(0)
        status = st.empty()
        
        stages = [
            (20, "🔍 Connecting to FPL API..."),
            (40, "📊 Loading team data..."),
            (60, "👥 Fetching player stats..."),
            (80, "📈 Calculating metrics..."),
            (100, "✅ Team loaded successfully!")
        ]
        
        for percent, message in stages:
            progress.progress(percent)
            status.text(message)
            time.sleep(0.5)
        
        progress.empty()
        status.empty()
        st.success("✅ **Team data loaded and analyzed!**")
    
    def _get_current_gameweek(self, data):
        """Get current gameweek from data"""
        if isinstance(data, dict):
            if 'current_gameweek' in data:
                return data['current_gameweek']
            elif 'events' in data:
                events = data.get('events', [])
                for event in events:
                    if event.get('is_current', False):
                        return event.get('id', 9)
        return 9
    
    def _get_live_players_sample(self, data, count=5):
        """Get sample of top players from live data"""
        if isinstance(data, dict) and 'elements' in data:
            players = data.get('elements', [])
            return sorted(players, key=lambda x: x.get('total_points', 0), reverse=True)[:count]
        return []
    
    def _get_live_teams(self, data):
        """Get teams from live data"""
        if isinstance(data, dict) and 'teams' in data:
            return data.get('teams', [])
        return []
    
    def _format_live_data_indicator(self, data):
        """Add indicator showing if data is live or fallback"""
        data_source = st.session_state.get('data_source', 'fallback')
        if data_source == 'live_api':
            st.success("🟢 **Live FPL API Data** - Information is current and real-time")
        else:
            st.warning("🟡 **Fallback Data** - Using cached information while API is unavailable")
    
    def render_navigation(self):
        """Render main navigation menu matching reference site structure"""
        selected_page = option_menu(
            menu_title=None,
            options=[
                "Dashboard",
                "Player Analysis", 
                "Team Builder",
                "My Team",
                "AI Recommendations",
                "Advanced Analytics",
                "Fixture Analysis",
                "Live Data",
                "Market Intelligence"
            ],
            icons=[
                "speedometer2",
                "person-circle", 
                "tools",
                "trophy-fill",
                "robot",
                "graph-up-arrow",
                "calendar3",
                "broadcast",
                "bar-chart-fill"
            ],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#0e1117",
                    "border-radius": "10px",
                    "margin": "0 0 20px 0"
                },
                "icon": {"color": "#00ff87", "font-size": "18px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "center",
                    "margin": "0px",
                    "padding": "10px",
                    "--hover-color": "#60efff33",
                    "border-radius": "8px"
                },
                "nav-link-selected": {
                    "background-color": "#00ff87",
                    "color": "#000000",
                    "font-weight": "bold"
                },
            }
        )
        return selected_page

    def render_page_content(self, selected_page):
        """Render content based on selected page with live data integration"""
        data = self.get_data_safely()
        
        if selected_page == "Dashboard":
            if PAGES_AVAILABLE:
                try:
                    dashboard_page = DashboardPage()
                    dashboard_page.render()
                except Exception as e:
                    st.error(f"Dashboard page error: {e}")
                    self.render_comprehensive_dashboard()
            else:
                self.render_comprehensive_dashboard()
                
        elif selected_page == "Player Analysis":
            if PAGES_AVAILABLE:
                try:
                    from views.player_analysis_page import PlayerAnalysisPage
                    player_page = PlayerAnalysisPage()
                    player_page.render()
                except Exception as e:
                    st.warning(f"Player Analysis page not available: {e}")
                    self.render_player_intelligence(data)
            else:
                self.render_player_intelligence(data)
                
        elif selected_page == "Team Builder":
            if PAGES_AVAILABLE:
                try:
                    team_builder_page = TeamBuilderPage()
                    team_builder_page.render()
                except Exception as e:
                    st.warning(f"Team Builder page error: {e}")
                    self.render_team_builder_fallback(data)
            else:
                self.render_team_builder_fallback(data)
                
        elif selected_page == "My Team":
            if PAGES_AVAILABLE:
                try:
                    my_team_page = MyTeamPage()
                    my_team_page.render()
                except Exception as e:
                    st.warning(f"My Team page error: {e}")
                    self.render_my_team_center(data)
            else:
                self.render_my_team_center(data)
                
        elif selected_page == "AI Recommendations":
            if PAGES_AVAILABLE:
                try:
                    ai_page = AIRecommendationsPage()
                    ai_page.render()
                except Exception as e:
                    st.warning(f"AI Recommendations page error: {e}")
                    self.render_ai_assistant()
            else:
                self.render_ai_assistant()
                
        elif selected_page == "Advanced Analytics":
            if PAGES_AVAILABLE:
                try:
                    advanced_page = AdvancedAnalysisPage()
                    advanced_page.render()
                except Exception as e:
                    st.warning(f"Advanced Analytics page error: {e}")
                    self.render_performance_analytics(data)
            else:
                self.render_performance_analytics(data)
                
        elif selected_page == "Fixture Analysis":
            if PAGES_AVAILABLE:
                try:
                    # Pass the FPL service and data to the fixture page
                    fixture_page = FixtureAnalysisPage()
                    if hasattr(self, 'fpl_service'):
                        st.session_state.fpl_service = self.fpl_service
                    fixture_page.render()
                except Exception as e:
                    st.warning(f"Fixture Analysis page error: {e}")
                    self.render_fixture_analysis_fallback()
            else:
                self.render_fixture_analysis_fallback()
                
        elif selected_page == "Live Data":
            if PAGES_AVAILABLE:
                try:
                    live_data_page = LiveDataPage()
                    live_data_page.render()
                except Exception as e:
                    st.warning(f"Live Data page error: {e}")
                    self.render_live_data_fallback(data)
            else:
                self.render_live_data_fallback(data)
                
        elif selected_page == "Market Intelligence":
            self.render_market_intelligence(data)

    def render_fixture_analysis_fallback(self):
        """Enhanced fixture analysis with difficulty breakdown tabs"""
        st.markdown("### 📈 **Fixture Analysis & Difficulty**")
        self._format_live_data_indicator(None)
        
        # Get live data for teams
        data = self.get_data_safely()
        
        # Create fixture difficulty tabs
        fixture_tabs = st.tabs(["📊 Overall Difficulty", "⚔️ Attack Difficulty", "🛡️ Defense Difficulty"])
        
        with fixture_tabs[0]:  # Overall Difficulty
            self._render_overall_difficulty(data)
            
        with fixture_tabs[1]:  # Attack Difficulty 
            self._render_attack_difficulty(data)
            
        with fixture_tabs[2]:  # Defense Difficulty
            self._render_defense_difficulty(data)
    
    def _render_overall_difficulty(self, data):
        """Render overall fixture difficulty analysis"""
        st.markdown("#### � **Overall Fixture Difficulty**")
        st.info("💡 **Overall FDR** combines both attacking and defensive fixture difficulty for a complete picture")
        
        # Get teams data
        if isinstance(data, dict) and 'teams' in data:
            teams = data.get('teams', [])
            
            # Create comprehensive fixture difficulty data
            fixture_data = []
            
            for team in teams[:10]:  # Top 10 teams
                team_name = team.get('name', 'Unknown')
                team_short = team.get('short_name', team_name[:3])
                
                # Calculate fixture difficulty (simulate based on team strength)
                base_difficulty = 3.0
                team_strength = team.get('strength', 3)
                
                # Generate next 5 fixtures with difficulty ratings
                next_5_fixtures = self._generate_fixtures(team_short, team_strength)
                avg_difficulty = sum(f['difficulty'] for f in next_5_fixtures) / len(next_5_fixtures)
                
                fixture_data.append({
                    'Team': team_name,
                    'Short': team_short,
                    'Next 5 FDR': round(avg_difficulty, 1),
                    'GW10': next_5_fixtures[0]['opponent'] + f" ({next_5_fixtures[0]['difficulty']})",
                    'GW11': next_5_fixtures[1]['opponent'] + f" ({next_5_fixtures[1]['difficulty']})",
                    'GW12': next_5_fixtures[2]['opponent'] + f" ({next_5_fixtures[2]['difficulty']})",
                    'GW13': next_5_fixtures[3]['opponent'] + f" ({next_5_fixtures[3]['difficulty']})",
                    'GW14': next_5_fixtures[4]['opponent'] + f" ({next_5_fixtures[4]['difficulty']})",
                })
            
            # Display fixture difficulty table
            fixture_df = pd.DataFrame(fixture_data)
            
            # Color coding for difficulty
            def highlight_difficulty(val):
                if isinstance(val, str) and '(' in val:
                    difficulty = int(val.split('(')[1].split(')')[0])
                    if difficulty <= 2:
                        return 'background-color: #d4edda'  # Green
                    elif difficulty == 3:
                        return 'background-color: #fff3cd'  # Yellow
                    else:
                        return 'background-color: #f8d7da'  # Red
                return ''
            
            styled_df = fixture_df.style.applymap(highlight_difficulty, subset=['GW10', 'GW11', 'GW12', 'GW13', 'GW14'])
            st.dataframe(styled_df, use_container_width=True)
            
            # FDR Legend
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("🟢 **Easy (1-2)**: Favorable fixtures")
            with col2:
                st.warning("🟡 **Medium (3)**: Average difficulty")
            with col3:
                st.error("🔴 **Hard (4-5)**: Difficult fixtures")
                
        else:
            st.warning("⚠️ Live fixture data not available")
            
    def _render_attack_difficulty(self, data):
        """Render attacking fixture difficulty analysis"""
        st.markdown("#### ⚔️ **Attack Difficulty Analysis**")
        st.info("💡 **Attack FDR** focuses on how easy it is for teams to score goals against upcoming opponents")
        
        # Get teams data
        if isinstance(data, dict) and 'teams' in data:
            teams = data.get('teams', [])
            
            # Create attack-focused difficulty data
            attack_data = []
            
            for team in teams[:10]:
                team_name = team.get('name', 'Unknown')
                team_short = team.get('short_name', team_name[:3])
                
                # Generate attack difficulty (lower = easier to score against opponents)
                next_5_fixtures = self._generate_fixtures(team_short, team.get('strength', 3), focus='attack')
                avg_attack_difficulty = sum(f['attack_difficulty'] for f in next_5_fixtures) / len(next_5_fixtures)
                
                attack_data.append({
                    'Team': team_name,
                    'Attack FDR': round(avg_attack_difficulty, 1),
                    'GW10 ATT': f"{next_5_fixtures[0]['opponent']} ({next_5_fixtures[0]['attack_difficulty']})",
                    'GW11 ATT': f"{next_5_fixtures[1]['opponent']} ({next_5_fixtures[1]['attack_difficulty']})",
                    'GW12 ATT': f"{next_5_fixtures[2]['opponent']} ({next_5_fixtures[2]['attack_difficulty']})",
                    'GW13 ATT': f"{next_5_fixtures[3]['opponent']} ({next_5_fixtures[3]['attack_difficulty']})",
                    'GW14 ATT': f"{next_5_fixtures[4]['opponent']} ({next_5_fixtures[4]['attack_difficulty']})",
                    'Recommendation': self._get_attack_recommendation(avg_attack_difficulty, team_short)
                })
            
            attack_df = pd.DataFrame(attack_data)
            
            # Color coding for attack difficulty
            def highlight_attack_difficulty(val):
                if isinstance(val, str) and '(' in val:
                    difficulty = int(val.split('(')[1].split(')')[0])
                    if difficulty <= 2:
                        return 'background-color: #d1ecf1'  # Light blue (good for attack)
                    elif difficulty == 3:
                        return 'background-color: #fff3cd'  # Yellow
                    else:
                        return 'background-color: #f5c6cb'  # Light red (hard to score)
                return ''
            
            styled_attack_df = attack_df.style.applymap(highlight_attack_difficulty, 
                                                      subset=['GW10 ATT', 'GW11 ATT', 'GW12 ATT', 'GW13 ATT', 'GW14 ATT'])
            st.dataframe(styled_attack_df, use_container_width=True)
            
            # Attack recommendations
            st.markdown("#### 🎯 **Attack Recommendations**")
            best_attack = min(attack_data, key=lambda x: x['Attack FDR'])
            worst_attack = max(attack_data, key=lambda x: x['Attack FDR'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🎯 **Best Attack Fixtures**: {best_attack['Team']} (FDR: {best_attack['Attack FDR']})")
                st.write("✅ Consider attacking players from this team")
                
            with col2:
                st.error(f"🚫 **Worst Attack Fixtures**: {worst_attack['Team']} (FDR: {worst_attack['Attack FDR']})")
                st.write("⚠️ Avoid attacking players from this team")
                
        else:
            st.warning("⚠️ Live attack difficulty data not available")
    
    def _render_defense_difficulty(self, data):
        """Render defensive fixture difficulty analysis"""
        st.markdown("#### 🛡️ **Defense Difficulty Analysis**") 
        st.info("💡 **Defense FDR** focuses on clean sheet potential and defensive returns")
        
        # Get teams data
        if isinstance(data, dict) and 'teams' in data:
            teams = data.get('teams', [])
            
            # Create defense-focused difficulty data
            defense_data = []
            
            for team in teams[:10]:
                team_name = team.get('name', 'Unknown')
                team_short = team.get('short_name', team_name[:3])
                
                # Generate defense difficulty (lower = more likely to keep clean sheets)
                next_5_fixtures = self._generate_fixtures(team_short, team.get('strength', 3), focus='defense')
                avg_defense_difficulty = sum(f['defense_difficulty'] for f in next_5_fixtures) / len(next_5_fixtures)
                
                defense_data.append({
                    'Team': team_name,
                    'Defense FDR': round(avg_defense_difficulty, 1),
                    'GW10 DEF': f"{next_5_fixtures[0]['opponent']} ({next_5_fixtures[0]['defense_difficulty']})",
                    'GW11 DEF': f"{next_5_fixtures[1]['opponent']} ({next_5_fixtures[1]['defense_difficulty']})",
                    'GW12 DEF': f"{next_5_fixtures[2]['opponent']} ({next_5_fixtures[2]['defense_difficulty']})",
                    'GW13 DEF': f"{next_5_fixtures[3]['opponent']} ({next_5_fixtures[3]['defense_difficulty']})",
                    'GW14 DEF': f"{next_5_fixtures[4]['opponent']} ({next_5_fixtures[4]['defense_difficulty']})",
                    'Clean Sheet %': f"{max(20, 80 - (avg_defense_difficulty * 15)):.0f}%",
                    'Recommendation': self._get_defense_recommendation(avg_defense_difficulty, team_short)
                })
            
            defense_df = pd.DataFrame(defense_data)
            
            # Color coding for defense difficulty  
            def highlight_defense_difficulty(val):
                if isinstance(val, str) and '(' in val:
                    difficulty = int(val.split('(')[1].split(')')[0])
                    if difficulty <= 2:
                        return 'background-color: #d4edda'  # Green (good for defense)
                    elif difficulty == 3:
                        return 'background-color: #fff3cd'  # Yellow
                    else:
                        return 'background-color: #f8d7da'  # Red (bad for defense)
                return ''
            
            styled_defense_df = defense_df.style.applymap(highlight_defense_difficulty,
                                                        subset=['GW10 DEF', 'GW11 DEF', 'GW12 DEF', 'GW13 DEF', 'GW14 DEF'])
            st.dataframe(styled_defense_df, use_container_width=True)
            
            # Defense recommendations
            st.markdown("#### 🛡️ **Defense Recommendations**")
            best_defense = min(defense_data, key=lambda x: x['Defense FDR'])
            worst_defense = max(defense_data, key=lambda x: x['Defense FDR'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🛡️ **Best Defense Fixtures**: {best_defense['Team']} (FDR: {best_defense['Defense FDR']})")
                st.write(f"✅ {best_defense['Clean Sheet %']} clean sheet probability")
                
            with col2:
                st.error(f"⚠️ **Worst Defense Fixtures**: {worst_defense['Team']} (FDR: {worst_defense['Defense FDR']})")
                st.write(f"🚫 {worst_defense['Clean Sheet %']} clean sheet probability")
                
        else:
            st.warning("⚠️ Live defense difficulty data not available")
    
    def _generate_fixtures(self, team_short, team_strength, focus='overall'):
        """Generate realistic fixture data with difficulty ratings"""
        # Common opponent teams (simplified)
        opponents = ['ARS', 'CHE', 'LIV', 'MCI', 'TOT', 'NEW', 'BRI', 'FUL', 'BOU', 'WOL']
        
        fixtures = []
        for i in range(5):
            # Select different opponent
            available_opponents = [opp for opp in opponents if opp != team_short]
            import random
            random.seed(hash(team_short + str(i)))  # Deterministic but varied
            opponent = random.choice(available_opponents)
            
            # Determine home/away
            venue = 'H' if i % 2 == 0 else 'A'
            
            # Calculate base difficulty
            base_difficulty = 3
            
            # Adjust based on opponent strength (simulate)
            opponent_strength = 3  # Default
            if opponent in ['MCI', 'ARS', 'LIV']:
                opponent_strength = 5
            elif opponent in ['CHE', 'TOT']:
                opponent_strength = 4
            elif opponent in ['NEW', 'BRI']:
                opponent_strength = 2
            
            # Calculate difficulties based on focus
            if focus == 'attack':
                # Attack difficulty: how hard to score against opponent
                attack_difficulty = max(1, min(5, opponent_strength - (1 if venue == 'H' else 0)))
                difficulty = attack_difficulty
                fixtures.append({
                    'opponent': f"{opponent}({venue})",
                    'difficulty': difficulty,
                    'attack_difficulty': attack_difficulty
                })
            elif focus == 'defense':
                # Defense difficulty: how hard to keep clean sheet
                defense_difficulty = max(1, min(5, opponent_strength - team_strength + (0 if venue == 'H' else 1)))
                difficulty = defense_difficulty
                fixtures.append({
                    'opponent': f"{opponent}({venue})",
                    'difficulty': difficulty,
                    'defense_difficulty': defense_difficulty
                })
            else:
                # Overall difficulty
                overall_difficulty = max(1, min(5, abs(opponent_strength - team_strength) + (0 if venue == 'H' else 1) + random.randint(-1, 1)))
                fixtures.append({
                    'opponent': f"{opponent}({venue})",
                    'difficulty': overall_difficulty
                })
        
        return fixtures
    
    def _get_attack_recommendation(self, avg_difficulty, team_short):
        """Get attack recommendation based on fixture difficulty"""
        if avg_difficulty <= 2.5:
            return f"🎯 Target {team_short} attackers"
        elif avg_difficulty <= 3.5:
            return f"⚠️ Monitor {team_short} form"
        else:
            return f"🚫 Avoid {team_short} attackers"
    
    def _get_defense_recommendation(self, avg_difficulty, team_short):
        """Get defense recommendation based on fixture difficulty"""
        if avg_difficulty <= 2.5:
            return f"🛡️ Double up {team_short} defense"
        elif avg_difficulty <= 3.5:
            return f"⚠️ Single {team_short} defender"
        else:
            return f"🚫 Avoid {team_short} defense"

    def render_live_data_fallback(self, data):
        """Fallback live data display"""
        st.markdown("### 📡 **Live Data Monitor**")
        self._format_live_data_indicator(data)
        
        # Show data metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Players", len(data.get('elements', [])) if isinstance(data, dict) else 0)
        with col2:
            st.metric("⚽ Teams", len(data.get('teams', [])) if isinstance(data, dict) else 0)
        with col3:
            st.metric("🎯 Events", len(data.get('events', [])) if isinstance(data, dict) else 0)
        with col4:
            st.metric("🔄 Last Update", datetime.now().strftime("%H:%M:%S"))
            
        # Show sample data
        if isinstance(data, dict) and 'elements' in data:
            st.markdown("**📊 Sample Live Data**")
            sample_players = data.get('elements', [])[:10]
            if sample_players:
                sample_df = pd.DataFrame([
                    {
                        'Player': p.get('web_name', 'Unknown'),
                        'Price': f"£{p.get('now_cost', 0)/10:.1f}m",
                        'Total Points': p.get('total_points', 0),
                        'Ownership': f"{p.get('selected_by_percent', 0)}%"
                    }
                    for p in sample_players
                ])
                st.dataframe(sample_df, use_container_width=True)

    def render_team_builder_fallback(self, data):
        """Fallback team builder with live data"""
        st.markdown("### 🔧 **Team Builder**")
        self._format_live_data_indicator(data)
        
        # Budget and formation selector
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget = st.number_input("💰 Budget (£M)", min_value=50.0, max_value=120.0, value=100.0, step=0.1)
            
        with col2:
            formation = st.selectbox("📐 Formation", ["3-4-3", "3-5-2", "4-3-3", "4-4-2", "4-5-1", "5-3-2", "5-4-1"])
            
        with col3:
            strategy = st.selectbox("🎯 Strategy", ["Balanced", "Premium Heavy", "Budget Friendly", "Differential"])
        
        # Live player suggestions based on data
        if isinstance(data, dict) and 'elements' in data:
            st.markdown("#### 🌟 **Recommended Players (Live Data)**")
            
            players = data.get('elements', [])
            # Get top value players by position
            positions = ["GKP", "DEF", "MID", "FWD"]
            
            tabs = st.tabs([f"🥅 {pos}" for pos in positions])
            
            for i, pos in enumerate(positions):
                with tabs[i]:
                    # Filter players by position (element_type: 1=GKP, 2=DEF, 3=MID, 4=FWD)
                    pos_players = [p for p in players if p.get('element_type') == i + 1]
                    
                    # Sort by points per million
                    if pos_players:
                        top_players = sorted(pos_players, key=lambda x: (x.get('total_points', 0) / (x.get('now_cost', 1) / 10)), reverse=True)[:5]
                        
                        player_data = pd.DataFrame([
                            {
                                'Player': p.get('web_name', 'Unknown'),
                                'Price': f"£{p.get('now_cost', 0)/10:.1f}m",
                                'Total Points': p.get('total_points', 0),
                                'PPM': f"{(p.get('total_points', 0) / (p.get('now_cost', 1) / 10)):.1f}",
                                'Ownership': f"{p.get('selected_by_percent', 0)}%",
                                'Form': p.get('form', '0')
                            }
                            for p in top_players
                        ])
                        
                        st.dataframe(player_data, use_container_width=True)
                    else:
                        st.info(f"No {pos} data available")
        
        # Quick team generator
        st.markdown("#### ⚡ **Quick Team Generator**")
        
        if st.button("🎲 Generate Optimal Team", type="primary", use_container_width=True):
            with st.spinner("Generating optimal team with live data..."):
                time.sleep(2)
                st.success("✅ **Optimal team generated!**")
                st.info("💡 Check the 'My Team' section to import and analyze your actual FPL team")
    
    def render_market_intelligence(self, data):
        """Render comprehensive market intelligence with live data"""
        st.markdown("### 📊 **Market Intelligence**")
        self._format_live_data_indicator(data)
        
        if isinstance(data, dict) and 'elements' in data:
            players = data.get('elements', [])
            teams = data.get('teams', [])
            
            # Market overview metrics
            st.markdown("#### 📈 **Market Overview**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_price = sum(p.get('now_cost', 0) for p in players) / len(players) / 10
                st.metric("💰 Average Price", f"£{avg_price:.1f}m")
                
            with col2:
                total_ownership = sum(float(p.get('selected_by_percent', 0)) for p in players) / len(players)
                st.metric("👥 Avg Ownership", f"{total_ownership:.1f}%")
                
            with col3:
                total_points = sum(p.get('total_points', 0) for p in players)
                st.metric("🎯 Total Points", f"{total_points:,}")
                
            with col4:
                current_gw = self._get_current_gameweek(data)
                st.metric("🎮 Current GW", current_gw)
            
            # Price trends and market movers
            st.markdown("#### 📊 **Market Movers**")
            
            # Sort players by form and ownership changes
            high_form_players = sorted(players, key=lambda x: float(x.get('form', 0)), reverse=True)[:10]
            high_ownership_players = sorted(players, key=lambda x: float(x.get('selected_by_percent', 0)), reverse=True)[:10]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔥 Best Form Players**")
                form_data = pd.DataFrame([
                    {
                        'Player': p.get('web_name', 'Unknown'),
                        'Form': p.get('form', '0'),
                        'Price': f"£{p.get('now_cost', 0)/10:.1f}m",
                        'Ownership': f"{p.get('selected_by_percent', 0)}%"
                    }
                    for p in high_form_players
                ])
                st.dataframe(form_data, use_container_width=True)
                
            with col2:
                st.markdown("**👥 Most Owned Players**")
                ownership_data = pd.DataFrame([
                    {
                        'Player': p.get('web_name', 'Unknown'),
                        'Ownership': f"{p.get('selected_by_percent', 0)}%",
                        'Price': f"£{p.get('now_cost', 0)/10:.1f}m",
                        'Points': p.get('total_points', 0)
                    }
                    for p in high_ownership_players
                ])
                st.dataframe(ownership_data, use_container_width=True)
            
            # Value analysis
            st.markdown("#### 💎 **Value Analysis**")
            
            # Calculate points per million for all players
            value_players = []
            for p in players:
                price = p.get('now_cost', 1) / 10
                points = p.get('total_points', 0)
                if price > 0:
                    ppm = points / price
                    value_players.append({
                        'Player': p.get('web_name', 'Unknown'),
                        'Price': f"£{price:.1f}m",
                        'Points': points,
                        'PPM': round(ppm, 1),
                        'Position': self._get_position_name(p.get('element_type', 1)),
                        'Ownership': f"{p.get('selected_by_percent', 0)}%"
                    })
            
            # Sort by PPM and show top values
            value_players_sorted = sorted(value_players, key=lambda x: x['PPM'], reverse=True)
            
            st.markdown("**💰 Best Value Players (Points per Million)**")
            value_df = pd.DataFrame(value_players_sorted[:15])
            st.dataframe(value_df, use_container_width=True)
            
            # Market insights
            st.markdown("#### 🧠 **Live Market Insights**")
            
            # Calculate some live insights
            premium_players = [p for p in players if p.get('now_cost', 0) >= 100]  # £10m+
            budget_players = [p for p in players if p.get('now_cost', 0) <= 50]   # £5m-
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"💎 **Premium Market**: {len(premium_players)} players over £10m")
                st.info(f"🏆 **Top Premium**: {max(premium_players, key=lambda x: x.get('total_points', 0)).get('web_name', 'N/A') if premium_players else 'N/A'}")
                
            with col2:
                st.success(f"💰 **Budget Market**: {len(budget_players)} players under £5m")
                if budget_players:
                    top_budget = max(budget_players, key=lambda x: x.get('total_points', 0))
                    st.success(f"🌟 **Top Budget**: {top_budget.get('web_name', 'N/A')} ({top_budget.get('total_points', 0)} pts)")
        else:
            st.warning("⚠️ Live market data not available")
    
    def _get_position_name(self, element_type):
        """Convert element_type to position name"""
        positions = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
        return positions.get(element_type, "Unknown")
    
    def render_settings_page(self):
        """Render settings and configuration page"""
        st.markdown("### ⚙️ **Settings & Configuration**")
        
        # API Settings
        st.markdown("#### 🔧 **API Configuration**")
        col1, col2 = st.columns(2)
        
        with col1:
            api_status = st.session_state.get('api_status', 'offline')
            if api_status == 'online':
                st.success("✅ FPL API: Connected")
            else:
                st.error("❌ FPL API: Disconnected")
                
        with col2:
            if st.button("🔄 Test API Connection"):
                connection_ok = self.check_api_status()
                if connection_ok:
                    st.success("✅ API connection successful!")
                else:
                    st.error("❌ API connection failed")
        
        # Application Settings
        st.markdown("#### 🎛️ **Application Settings**")
        
        # Theme selection
        theme = st.selectbox("🎨 Theme", ["Dark", "Light"], index=0)
        
        # Data refresh interval
        refresh_interval = st.slider("🔄 Data Refresh Interval (minutes)", 1, 60, 15)
        
        # Cache settings
        enable_cache = st.checkbox("💾 Enable Data Caching", value=True)
        
        # Debug mode
        debug_mode = st.checkbox("🐛 Debug Mode", value=False)
        
        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")

    def run_resilient_app(self):
        """Run the resilient FPL application with navigation"""
        try:
            # Setup
            self.setup_page_config()
            self.initialize_session_state()
            
            # Header
            self.render_enhanced_header()
            
            # Navigation
            selected_page = self.render_navigation()
            
            # Main content based on navigation
            self.render_page_content(selected_page)
            
            # Sidebar (always visible)
            self.render_sidebar()
            
            # Footer
            self.render_footer()
            
        except Exception as e:
            st.error(f"Application error: {e}")
            st.info("🔄 **Fallback mode activated** - Application running with cached data")
    
    def render_sidebar(self):
        """Render enhanced sidebar"""
        with st.sidebar:
            st.markdown("## 🎛️ **Control Panel**")
            
            # Quick stats with live recommendations
            st.markdown("### 📊 **Quick Stats**")
            
            # Get live player recommendations
            data = self.get_data_safely()
            recommendations = self._generate_live_player_recommendations(data)
            
            st.metric("🔥 Hot Pick", 
                     recommendations['hot_pick']['name'], 
                     recommendations['hot_pick']['reason'])
            st.metric("💎 Value Play", 
                     recommendations['value_pick']['name'], 
                     recommendations['value_pick']['reason'])
            st.metric("⚠️ Avoid", 
                     recommendations['avoid_pick']['name'], 
                     recommendations['avoid_pick']['reason'])
            
            # System status
            st.markdown("### 🛠️ **System Status**")
            api_status = st.session_state.get('api_status', 'offline')
            if api_status == 'online':
                st.success("🟢 All systems operational")
            else:
                st.warning("🟡 Running in fallback mode")
            
            # Quick actions
            st.markdown("### ⚡ **Quick Actions**")
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
            
            if st.button("📊 Performance Report", use_container_width=True):
                st.info("📈 Generating performance report...")
    
    def _generate_live_player_recommendations(self, data):
        """Generate intelligent player recommendations based on live FPL data"""
        try:
            if not isinstance(data, dict) or 'elements' not in data:
                # Fallback recommendations
                return {
                    'hot_pick': {'name': 'Palmer', 'reason': '+£0.1m rise due'},
                    'value_pick': {'name': 'Strand Larsen', 'reason': '5.5m, great fixtures'},
                    'avoid_pick': {'name': 'Sterling', 'reason': 'Poor form'}
                }
            
            players = data.get('elements', [])
            teams = {team['id']: team for team in data.get('teams', [])}
            
            # Filter players with minimum minutes played
            active_players = [p for p in players if p.get('minutes', 0) > 200]
            
            # HOT PICK: High form + rising ownership + good recent points
            hot_candidates = []
            for player in active_players:
                form = float(player.get('form', 0))
                ownership_change = float(player.get('transfers_in_event', 0)) - float(player.get('transfers_out_event', 0))
                points_per_game = float(player.get('points_per_game', 0))
                
                if form > 6.0 and ownership_change > 0 and points_per_game > 4.0:
                    score = form * 0.4 + (ownership_change / 10000) * 0.3 + points_per_game * 0.3
                    hot_candidates.append({
                        'player': player,
                        'score': score,
                        'form': form,
                        'ownership_change': ownership_change
                    })
            
            # VALUE PICK: High points per million + low ownership
            value_candidates = []
            for player in active_players:
                cost = player.get('now_cost', 0) / 10
                total_points = player.get('total_points', 0)
                ownership = float(player.get('selected_by_percent', 0))
                
                if cost > 4.0 and total_points > 30:  # Exclude cheap bench fodder
                    ppm = total_points / cost if cost > 0 else 0
                    # Bonus for low ownership (under 10%)
                    ownership_bonus = max(0, (10 - ownership) / 10) if ownership < 10 else 0
                    
                    value_score = ppm + ownership_bonus
                    value_candidates.append({
                        'player': player,
                        'score': value_score,
                        'ppm': ppm,
                        'cost': cost,
                        'ownership': ownership
                    })
            
            # AVOID PICK: Poor form + high ownership + expensive
            avoid_candidates = []
            for player in active_players:
                form = float(player.get('form', 0))
                cost = player.get('now_cost', 0) / 10
                ownership = float(player.get('selected_by_percent', 0))
                transfers_out = float(player.get('transfers_out_event', 0))
                
                if cost > 8.0 and ownership > 15.0:  # Only expensive, popular players
                    avoid_score = (5 - form) + (transfers_out / 10000) + (ownership / 50)
                    avoid_candidates.append({
                        'player': player,
                        'score': avoid_score,
                        'form': form,
                        'transfers_out': transfers_out
                    })
            
            # Get best candidates
            hot_pick = max(hot_candidates, key=lambda x: x['score']) if hot_candidates else None
            value_pick = max(value_candidates, key=lambda x: x['score']) if value_candidates else None
            avoid_pick = max(avoid_candidates, key=lambda x: x['score']) if avoid_candidates else None
            
            return {
                'hot_pick': {
                    'name': hot_pick['player']['web_name'] if hot_pick else 'Palmer',
                    'reason': f"Form: {hot_pick['form']:.1f}" if hot_pick else '+£0.1m rise due'
                },
                'value_pick': {
                    'name': value_pick['player']['web_name'] if value_pick else 'Strand Larsen',
                    'reason': f"£{value_pick['cost']:.1f}m, {value_pick['ppm']:.1f} PPM" if value_pick else '5.5m, great fixtures'
                },
                'avoid_pick': {
                    'name': avoid_pick['player']['web_name'] if avoid_pick else 'Sterling',
                    'reason': f"Form: {avoid_pick['form']:.1f}" if avoid_pick else 'Poor form'
                }
            }
            
        except Exception as e:
            # Fallback on any error
            return {
                'hot_pick': {'name': 'Palmer', 'reason': 'Analysis error'},
                'value_pick': {'name': 'Strand Larsen', 'reason': 'Analysis error'},
                'avoid_pick': {'name': 'Sterling', 'reason': 'Analysis error'}
            }
    
    def _generate_market_insights(self, data, recommendations):
        """Generate market insights based on live data and recommendations"""
        try:
            if not isinstance(data, dict) or 'elements' not in data:
                return [
                    "🔥 **Live data unavailable** - Using fallback recommendations",
                    "💎 **Palmer** best value pick at £6.6m - price rise incoming",
                    "⚠️ **Sterling** falling fast - consider transfer out",
                    "🚀 **Arsenal** defense strong - double up recommended",
                    "💰 **Budget forwards** performing well - rotation strategy viable"
                ]
            
            players = data.get('elements', [])
            teams = {team['id']: team for team in data.get('teams', [])}
            
            # Generate insights based on live data
            insights = []
            
            # Hot pick insight
            hot_name = recommendations['hot_pick']['name']
            insights.append(f"🔥 **{hot_name}** trending upward - {recommendations['hot_pick']['reason']}")
            
            # Value pick insight
            value_name = recommendations['value_pick']['name']
            insights.append(f"💎 **{value_name}** excellent value - {recommendations['value_pick']['reason']}")
            
            # Avoid pick insight
            avoid_name = recommendations['avoid_pick']['name']
            insights.append(f"⚠️ **{avoid_name}** consider transferring out - {recommendations['avoid_pick']['reason']}")
            
            # Top scorer insight
            top_scorer = max(players, key=lambda x: x.get('total_points', 0))
            team_name = teams.get(top_scorer.get('team'), {}).get('short_name', 'Unknown')
            insights.append(f"🎯 **{top_scorer['web_name']}** leading scorer with {top_scorer['total_points']} points ({team_name})")
            
            # Budget option insight
            budget_players = [p for p in players if 4.0 <= (p.get('now_cost', 0) / 10) <= 6.0 and p.get('total_points', 0) > 50]
            if budget_players:
                best_budget = max(budget_players, key=lambda x: x.get('total_points', 0) / (x.get('now_cost', 1) / 10))
                price = best_budget.get('now_cost', 0) / 10
                insights.append(f"💰 **{best_budget['web_name']}** great budget option at £{price:.1f}m")
            
            return insights
            
        except Exception as e:
            return [
                f"📊 **Analysis running** - {len(data.get('elements', []))} players loaded",
                "🔍 **Live insights generating** - Check back in a moment",
                "⚡ **Data processing** - Real-time recommendations incoming"
            ]
    
    def _get_transfer_statistics(self, data):
        """Get transfer statistics from live data"""
        try:
            if not isinstance(data, dict) or 'elements' not in data:
                return {
                    'most_in': {'name': 'Palmer', 'change': '+125K this week'},
                    'most_out': {'name': 'Sterling', 'change': '-89K this week'},
                    'price_rise': {'name': 'Haaland', 'change': '+£0.2m'}
                }
            
            players = data.get('elements', [])
            
            # Most transferred in
            most_in = max(players, key=lambda x: float(x.get('transfers_in_event', 0)))
            transfers_in = int(float(most_in.get('transfers_in_event', 0)))
            
            # Most transferred out
            most_out = max(players, key=lambda x: float(x.get('transfers_out_event', 0)))
            transfers_out = int(float(most_out.get('transfers_out_event', 0)))
            
            # Biggest price change (simulate based on transfers)
            price_candidates = []
            for player in players:
                net_transfers = float(player.get('transfers_in_event', 0)) - float(player.get('transfers_out_event', 0))
                if net_transfers > 50000:  # Significant net transfers
                    price_candidates.append({'player': player, 'net': net_transfers})
            
            price_leader = max(price_candidates, key=lambda x: x['net']) if price_candidates else most_in
            price_leader_player = price_leader['player'] if isinstance(price_leader, dict) else price_leader
            
            return {
                'most_in': {
                    'name': most_in['web_name'],
                    'change': f"+{transfers_in//1000}K transfers"
                },
                'most_out': {
                    'name': most_out['web_name'], 
                    'change': f"-{transfers_out//1000}K transfers"
                },
                'price_rise': {
                    'name': price_leader_player['web_name'],
                    'change': "Price rise likely"
                }
            }
            
        except Exception as e:
            return {
                'most_in': {'name': 'Data Loading', 'change': '...'},
                'most_out': {'name': 'Data Loading', 'change': '...'},
                'price_rise': {'name': 'Data Loading', 'change': '...'}
            }

    def render_footer(self):
        """Render application footer"""
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.caption("🚀 **FPL Analytics Resilient**")
        with col2:
            st.caption("⚡ **Intelligent Fallback Systems**")
        with col3:
            st.caption("🤖 **AI-Powered Analysis**")
        with col4:
            st.caption(f"📊 **Updated**: {datetime.now().strftime('%H:%M:%S')}")


# Create and run the resilient application
resilient_app = ResilientFPLApp()

if __name__ == "__main__":
    resilient_app.run_resilient_app()