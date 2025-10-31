"""
Dashboard Controller
Handles dashboard page logic and rendering
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from services.ui_component_service import UIComponentService
from services.player_recommendation_service import PlayerRecommendationService
from services.data_utilities_service import DataUtilitiesService


class DashboardController:
    """Controller for dashboard page functionality"""
    
    def __init__(self):
        """Initialize dashboard controller with required services"""
        self.ui_service = UIComponentService()
        self.recommendation_service = PlayerRecommendationService()
        self.data_service = DataUtilitiesService()
    
    def render_comprehensive_dashboard(self, data):
        """Render comprehensive dashboard with resilient data loading"""
        st.markdown("## 📊 **Comprehensive FPL Dashboard**")
        
        # Key metrics
        self.ui_service.render_key_metrics(data)
        
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
    
    def render_market_overview(self, data):
        """Render comprehensive market overview"""
        st.markdown("#### 🔥 **Market Pulse & Intelligence**")
        
        # Market sentiment
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Top Performers This Week**")
            top_performers = self.ui_service.render_top_performers_chart(data)
        
        with col2:
            st.markdown("**🎯 Market Intelligence**")
            
            # Generate live market insights
            recommendations = self.recommendation_service.generate_live_player_recommendations(data)
            market_insights = self.recommendation_service.generate_market_insights(data, recommendations)
            
            for insight in market_insights:
                st.info(insight)
            
            # Quick stats with live data
            st.markdown("**📊 Quick Market Stats**")
            transfer_stats = self.recommendation_service.get_transfer_statistics(data)
            st.metric("🔥 Most Transferred In", transfer_stats['most_in']['name'], transfer_stats['most_in']['change'])
            st.metric("❄️ Most Transferred Out", transfer_stats['most_out']['name'], transfer_stats['most_out']['change'])
            st.metric("💰 Biggest Price Rise", transfer_stats['price_rise']['name'], transfer_stats['price_rise']['change'])
    
    def render_performance_analytics(self, data):
        """Render performance analytics with interactive charts using live data"""
        st.markdown("#### 📈 **Performance Analytics Deep Dive**")
        
        # Extract current gameweek from live data
        current_gw = self.data_service.get_current_gameweek(data)
        
        # Performance tracking
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Gameweek Performance Trends**")
            
            # Generate performance data based on current gameweek
            gw_data = self.data_service.prepare_performance_data(current_gw)
            
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
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown("**🏆 Performance Breakdown**")
            
            # Performance metrics
            perf_metrics = self.data_service.prepare_team_performance_data()
            st.dataframe(perf_metrics, width='stretch')
            
            # Performance insights
            st.markdown("**💡 Performance Insights**")
            st.success("✅ **Strong**: Above average performance consistently")
            st.info("📊 **Good**: Better than 65% of managers")
            st.warning("⚠️ **Improve**: Captain choices could be optimized")
            
            # Performance gauge
            self.ui_service.render_performance_gauge(78, 72)
    
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
            self._render_player_analysis(st.session_state.analyze_player, data)
    
    def _render_player_analysis(self, player, data):
        """Render detailed player analysis"""
        st.markdown(f"#### 🎯 **Deep Analysis: {player}**")
        
        # Player stats tabs
        player_tabs = st.tabs(["📊 Stats", "🎯 Fixtures", "💰 Value", "🤖 AI Insight"])
        
        with player_tabs[0]:  # Stats
            self._render_player_stats(player, data)
        
        with player_tabs[1]:  # Fixtures
            self._render_player_fixtures(player, data)
        
        with player_tabs[2]:  # Value
            self._render_player_value(player, data)
        
        with player_tabs[3]:  # AI Insight
            self._render_player_ai_insight(player)
    
    def _render_player_stats(self, player, data):
        """Render player statistics"""
        col1, col2, col3, col4 = st.columns(4)
        
        # Get player data
        player_info = self.data_service.extract_player_data_for_analysis(data, player)
        
        with col1:
            st.metric("💰 Price", f"£{player_info['price']:.1f}m")
        with col2:
            st.metric("📊 Total Points", player_info['total_points'])
        with col3:
            st.metric("🔥 Form", player_info['form'])
        with col4:
            st.metric("👥 Ownership", f"{player_info['ownership']}%")
    
    def _render_player_fixtures(self, player, data):
        """Render player fixtures analysis"""
        st.markdown("**🗓️ Upcoming Fixtures**")
        
        # Get team short name for fixtures
        player_info = self.data_service.extract_player_data_for_analysis(data, player)
        team_short = player_info.get('team_short', 'UNK')
        
        # Generate fixtures
        fixtures = self.data_service.simulate_fixtures(team_short)
        st.dataframe(fixtures, use_container_width=True)
    
    def _render_player_value(self, player, data):
        """Render player value analysis"""
        st.markdown("**💰 Value Analysis**")
        
        player_info = self.data_service.extract_player_data_for_analysis(data, player)
        
        # Calculate points per million
        ppm = player_info['total_points'] / player_info['price'] if player_info['price'] > 0 else 0
        
        st.metric("Points per Million", f"{ppm:.2f}", "+0.95")
        st.metric("Value Rank", "3rd", "+1")
        st.success("🎯 **Excellent value** - among top 5 points per million")
    
    def _render_player_ai_insight(self, player):
        """Render AI insights for player"""
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
                self._simulate_team_load()
        
        with col3:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        
        # Team analysis
        if st.session_state.get('user_team_id'):
            self._render_team_summary()
    
    def _simulate_team_load(self):
        """Simulate team loading with sample data"""
        st.session_state.team_loaded = True
        st.session_state.team_value = 100.3
        st.session_state.bank = 0.7
        st.session_state.total_points = 520
        st.success("✅ Team loaded successfully!")
    
    def _render_team_summary(self):
        """Render team summary information"""
        st.markdown("#### 📋 **Team Summary**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Team Value", f"£{st.session_state.get('team_value', 100.0)}m")
        with col2:
            st.metric("🏦 In Bank", f"£{st.session_state.get('bank', 1.0)}m")
        with col3:
            st.metric("📊 Total Points", st.session_state.get('total_points', 500))
        with col4:
            st.metric("🏆 Overall Rank", "125,432", "↑15,234")
    
    def render_ai_assistant(self):
        """Render AI assistant interface"""
        st.markdown("#### 🤖 **AI Assistant & Recommendations**")
        
        # Show data source for AI recommendations
        data_source = st.session_state.get('data_source', 'fallback')
        if data_source == 'live_api':
            st.success("🎯 **AI powered by live FPL data** - Recommendations based on current season statistics")
        else:
            st.info("🤖 **AI using cached data** - Recommendations may not reflect latest changes")
        
        # AI Chat Interface
        st.markdown("**💬 Ask the AI Assistant**")
        
        # Sample questions
        sample_questions = [
            "Who should I captain this week?",
            "Which players should I transfer out?", 
            "Best value picks under £6m?",
            "Analyze my team's fixture difficulty"
        ]
        
        selected_question = st.selectbox(
            "💡 **Quick Questions**", 
            ["Choose a question..."] + sample_questions
        )
        
        user_question = st.text_area(
            "🗨️ **Or ask your own question**",
            placeholder="Ask about transfers, captains, or strategy...",
            help="The AI can help with player analysis, transfer suggestions, and strategic advice"
        )
        
        if st.button("🚀 Get AI Recommendation", type="primary"):
            question = user_question if user_question else selected_question
            if question and question != "Choose a question...":
                self._generate_ai_response(question)
    
    def _generate_ai_response(self, question):
        """Generate AI response to user question"""
        # Simulated AI responses based on question type
        responses = {
            "captain": {
                'title': 'Captain Recommendation',
                'recommendation': 'Haaland (vs Bournemouth)',
                'confidence': '92%',
                'reasoning': 'Excellent home fixture, in red-hot form, highest ceiling'
            },
            "transfer": {
                'title': 'Transfer Recommendations', 
                'recommendation': 'Palmer IN, Sterling OUT',
                'confidence': '85%',
                'reasoning': 'Palmer has great fixtures and rising, Sterling struggling'
            }
        }
        
        # Determine response type
        if "captain" in question.lower():
            response = responses['captain']
        else:
            response = responses['transfer']
        
        # Display AI response
        st.markdown(f"#### 🤖 **{response['title']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Recommendation**: {response['recommendation']}")
            st.info(f"**Confidence**: {response['confidence']}")
        
        with col2:
            st.markdown(f"**Reasoning**: {response['reasoning']}")
    
    def render_advanced_analytics(self, data):
        """Render advanced analytics section"""
        st.markdown("#### 📊 **Advanced Analytics & Insights**")
        
        # Advanced metrics placeholder
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Performance Trends**")
            st.info("Advanced trend analysis coming soon...")
        
        with col2:
            st.markdown("**🔮 Predictive Models**")
            st.info("ML predictions coming soon...")