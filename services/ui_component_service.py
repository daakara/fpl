"""
UI Component Service
Handles rendering of common UI components and layouts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


class UIComponentService:
    """Service for rendering common UI components"""
    
    def __init__(self):
        """Initialize the UI component service"""
        pass
    
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
        
        api_online = st.session_state.get('api_status', 'offline') == 'online'
        
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
    
    def render_top_performers_chart(self, data):
        """Render top performers chart"""
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
        st.plotly_chart(fig, width='stretch')
        
        return top_performers
    
    def render_performance_gauge(self, score=78, reference=72):
        """Render performance gauge"""
        gauge_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Performance Score"},
            delta = {'reference': reference},
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
        st.plotly_chart(gauge_fig, width='stretch')
    
    def render_live_data_indicator(self, data):
        """Format and display live data connection indicator"""
        data_source = st.session_state.get('data_source', 'fallback')
        if data_source == 'live_api':
            st.success("🟢 **Live FPL API Data** - Information is current and real-time")
        else:
            st.warning("🟡 **Fallback Data** - Using cached information while API is unavailable")
    
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
    
    def _get_current_gameweek(self, data):
        """Extract current gameweek from FPL data"""
        if isinstance(data, dict) and 'events' in data:
            events = data.get('events', [])
            for event in events:
                if event.get('is_current', False):
                    return event.get('id', 1)
        return 10  # Fallback to GW 10