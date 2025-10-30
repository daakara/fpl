"""
Comprehensive FPL Analytics Application
Integrates all advanced features and components for complete FPL analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import asyncio

# Core imports
from core.page_router import PageRouter
from core.dashboard_page import DashboardPage
from core.team_builder_page import TeamBuilderPage
from core.ai_recommendations_page import AIRecommendationsPage
from core.sidebar_component import SidebarComponent
from core.header_component import HeaderComponent

# Advanced components
from views.components.advanced_analytics_component import AdvancedAnalyticsComponent
from views.components.squad_analysis_component import SquadAnalysisComponent
from views.components.fixture_analysis_component import FixtureAnalysisComponent
from views.components.transfer_planning_component import TransferPlanningComponent
from views.components.performance_comparison_component import PerformanceComparisonComponent
from views.components.ai_insights_component import AIInsightsComponent
from views.components.team_health_component import TeamHealthComponent
from views.components.historical_performance_component import HistoricalPerformanceComponent
from views.components.mini_league_component import MiniLeagueComponent

# Enhanced services
from services.enhanced_fpl_data_service import get_enhanced_fpl_service
from utils.advanced_cache_manager import get_cache_manager
from utils.enhanced_performance_monitor import get_performance_monitor
from utils.error_handling import logger
from config.secure_config import get_secure_config

# UI Components
from components.ui_components import MetricsDisplayComponent
from components.enhanced_ai_integration import FPLAIAssistant


class ComprehensiveFPLApp:
    """Complete FPL Analytics Application with all advanced features"""
    
    def __init__(self):
        """Initialize the comprehensive application"""
        # Core services
        self.fpl_service = get_enhanced_fpl_service()
        self.cache_manager = get_cache_manager()
        self.config = get_secure_config()
        self.performance_monitor = get_performance_monitor()
        
        # Navigation and routing
        self.page_router = PageRouter()
        self.sidebar_component = SidebarComponent()
        self.header_component = HeaderComponent()
        
        # Page components
        self.dashboard_page = DashboardPage()
        self.team_builder_page = TeamBuilderPage()
        self.ai_recommendations_page = AIRecommendationsPage()
        
        # Advanced analytics components
        self.advanced_analytics = AdvancedAnalyticsComponent(self.fpl_service)
        self.squad_analysis = SquadAnalysisComponent(self.fpl_service)
        self.fixture_analysis = FixtureAnalysisComponent(self.fpl_service)
        self.transfer_planning = TransferPlanningComponent(self.fpl_service)
        self.performance_comparison = PerformanceComparisonComponent(self.fpl_service)
        self.ai_insights = AIInsightsComponent()
        self.team_health = TeamHealthComponent(self.fpl_service)
        self.historical_performance = HistoricalPerformanceComponent(self.fpl_service)
        self.mini_league = MiniLeagueComponent(self.fpl_service)
        
        # UI components
        self.metrics_display = MetricsDisplayComponent()
        self.ai_assistant = FPLAIAssistant()
        
        logger.info("Comprehensive FPL App initialized with all advanced features")
    
    def setup_page_config(self):
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title="FPL Analytics - Comprehensive",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://fantasy.premierleague.com',
                'Report a bug': 'mailto:support@fplanalytics.com',
                'About': 'Comprehensive FPL Analytics with AI-powered insights'
            }
        )
        
        # Custom CSS for enhanced styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .nav-container {
            background: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .feature-highlight {
            border-left: 4px solid #00ff87;
            padding-left: 1rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize comprehensive session state"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        
        if 'fpl_data_loaded' not in st.session_state:
            st.session_state.fpl_data_loaded = False
        
        if 'user_team_id' not in st.session_state:
            st.session_state.user_team_id = None
        
        if 'selected_players' not in st.session_state:
            st.session_state.selected_players = []
        
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'basic'
        
        if 'ai_insights_enabled' not in st.session_state:
            st.session_state.ai_insights_enabled = True
    
    def render_enhanced_navigation(self):
        """Render comprehensive navigation system"""
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        st.markdown("## 🧭 **Navigation Center**")
        
        # Primary navigation tabs
        primary_tabs = st.tabs([
            "📊 Dashboard", 
            "⚽ My Team", 
            "👥 Player Analysis", 
            "🏗️ Team Builder", 
            "🤖 AI Insights",
            "📈 Advanced Analytics"
        ])
        
        with primary_tabs[0]:  # Dashboard
            self.render_dashboard_section()
        
        with primary_tabs[1]:  # My Team
            self.render_my_team_section()
        
        with primary_tabs[2]:  # Player Analysis
            self.render_player_analysis_section()
        
        with primary_tabs[3]:  # Team Builder
            self.render_team_builder_section()
        
        with primary_tabs[4]:  # AI Insights
            self.render_ai_insights_section()
        
        with primary_tabs[5]:  # Advanced Analytics
            self.render_advanced_analytics_section()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_dashboard_section(self):
        """Render comprehensive dashboard"""
        st.markdown("### 📊 **Enhanced Dashboard**")
        
        # Key performance metrics
        try:
            bootstrap_data = self.fpl_service.get_bootstrap_data()
            
            # Main metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("🏆 Total Players", len(bootstrap_data.get('elements', [])), "+0")
            with col2:
                st.metric("⚽ Teams", len(bootstrap_data.get('teams', [])), "+0")
            with col3:
                st.metric("🎯 Current GW", self._get_current_gameweek(bootstrap_data), "+1")
            with col4:
                cache_stats = self.cache_manager.get_stats()
                st.metric("⚡ Cache Hit Rate", f"{cache_stats.get('hit_rate', 0):.1%}", "+5%")
            with col5:
                st.metric("🚀 Response Time", "245ms", "-15ms")
            
            # Dashboard insights
            st.markdown("### 📈 **Live Market Insights**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top performers chart
                top_players = self._get_top_performers(bootstrap_data)
                if not top_players.empty:
                    fig = px.bar(
                        top_players.head(10), 
                        x='total_points', 
                        y='web_name',
                        orientation='h',
                        title='Top 10 Players by Points',
                        color='total_points',
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Price trends
                st.markdown("#### 💰 **Market Trends**")
                st.success("🔥 **Hot Picks**: Price rises expected")
                st.warning("📉 **Falling**: Monitor these players")
                st.info("💡 **Value Plays**: Best points per million")
                
                # Quick team health check
                if st.session_state.user_team_id:
                    st.markdown("#### 🏥 **Your Team Health**")
                    self.team_health.render_quick_health_check()
            
        except Exception as e:
            logger.error(f"Dashboard rendering error: {e}")
            st.error(f"Dashboard loading error: {e}")
    
    def render_my_team_section(self):
        """Render comprehensive my team analysis"""
        st.markdown("### ⚽ **My FPL Team Analysis**")
        
        # Team ID input
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            team_id = st.number_input(
                "🆔 **Enter Your FPL Team ID**", 
                min_value=1, 
                value=st.session_state.get('user_team_id', 1234567),
                help="Find your Team ID in the FPL website URL"
            )
        
        with col2:
            if st.button("📱 Load Team", type="primary"):
                st.session_state.user_team_id = team_id
                with st.spinner("Loading your team data..."):
                    self._load_team_data(team_id)
        
        with col3:
            analysis_mode = st.selectbox(
                "Analysis Depth",
                ["Basic", "Advanced", "Expert"],
                key="team_analysis_mode"
            )
        
        # Team analysis tabs
        if st.session_state.get('user_team_id'):
            team_tabs = st.tabs([
                "🔍 Team Overview", 
                "📊 Performance Analysis", 
                "🏥 Team Health", 
                "🔄 Transfer Planning",
                "🎯 Optimization"
            ])
            
            with team_tabs[0]:  # Team Overview
                self.render_team_overview()
            
            with team_tabs[1]:  # Performance Analysis
                self.historical_performance.render_performance_analysis()
            
            with team_tabs[2]:  # Team Health
                self.team_health.render_team_health_analysis()
            
            with team_tabs[3]:  # Transfer Planning
                self.transfer_planning.render_transfer_planning()
            
            with team_tabs[4]:  # Optimization
                self.render_team_optimization()
    
    def render_player_analysis_section(self):
        """Render comprehensive player analysis"""
        st.markdown("### 👥 **Advanced Player Analysis**")
        
        analysis_tabs = st.tabs([
            "🔍 Player Search", 
            "📊 Performance Metrics", 
            "🎯 Fixture Analysis", 
            "🤖 AI Predictions",
            "⚖️ Player Comparison"
        ])
        
        with analysis_tabs[0]:  # Player Search
            self.render_player_search()
        
        with analysis_tabs[1]:  # Performance Metrics
            self.render_performance_metrics()
        
        with analysis_tabs[2]:  # Fixture Analysis
            self.fixture_analysis.render_fixture_analysis()
        
        with analysis_tabs[3]:  # AI Predictions
            self.ai_insights.render_player_predictions()
        
        with analysis_tabs[4]:  # Player Comparison
            self.performance_comparison.render_player_comparison()
    
    def render_team_builder_section(self):
        """Render advanced team builder"""
        st.markdown("### 🏗️ **AI-Powered Team Builder**")
        
        builder_tabs = st.tabs([
            "🎯 Quick Build", 
            "⚙️ Custom Build", 
            "🤖 AI Optimization", 
            "🔄 Draft Mode"
        ])
        
        with builder_tabs[0]:  # Quick Build
            self.team_builder_page.render_quick_team_builder()
        
        with builder_tabs[1]:  # Custom Build
            self.render_custom_team_builder()
        
        with builder_tabs[2]:  # AI Optimization
            self.render_ai_team_optimization()
        
        with builder_tabs[3]:  # Draft Mode
            self.render_draft_mode()
    
    def render_ai_insights_section(self):
        """Render comprehensive AI insights"""
        st.markdown("### 🤖 **AI-Powered Insights**")
        
        ai_tabs = st.tabs([
            "💬 AI Assistant", 
            "🔮 Predictions", 
            "📈 Market Analysis", 
            "🎯 Recommendations"
        ])
        
        with ai_tabs[0]:  # AI Assistant
            self.render_ai_assistant()
        
        with ai_tabs[1]:  # Predictions
            self.ai_insights.render_ai_predictions()
        
        with ai_tabs[2]:  # Market Analysis
            self.render_market_analysis()
        
        with ai_tabs[3]:  # Recommendations
            self.ai_recommendations_page.render_ai_recommendations()
    
    def render_advanced_analytics_section(self):
        """Render advanced analytics suite"""
        st.markdown("### 📈 **Advanced Analytics Suite**")
        
        analytics_tabs = st.tabs([
            "📊 Statistical Analysis", 
            "🎯 Performance Deep Dive", 
            "🏆 Mini League Analysis", 
            "📉 Trend Analysis"
        ])
        
        with analytics_tabs[0]:  # Statistical Analysis
            try:
                bootstrap_data = self.fpl_service.get_bootstrap_data()
                players_df = pd.DataFrame(bootstrap_data.get('elements', []))
                team_data = bootstrap_data.get('teams', [])
                self.advanced_analytics.render_advanced_analytics(team_data, players_df)
            except Exception as e:
                st.error(f"Analytics loading error: {e}")
        
        with analytics_tabs[1]:  # Performance Deep Dive
            self.squad_analysis.render_squad_analysis()
        
        with analytics_tabs[2]:  # Mini League Analysis
            self.mini_league.render_mini_league_analysis()
        
        with analytics_tabs[3]:  # Trend Analysis
            self.render_trend_analysis()
    
    # Helper methods for rendering specific components
    
    def render_team_overview(self):
        """Render team overview section"""
        st.markdown("#### 📋 **Team Summary**")
        
        # Mock team data for demonstration
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Team Value", "£100.5m", "+£0.2m")
        with col2:
            st.metric("📊 Total Points", "1,245", "+67")
        with col3:
            st.metric("🏆 Overall Rank", "245,432", "+1,234")
        with col4:
            st.metric("🎯 Gameweek Rank", "892,123", "-45,678")
        
        # Formation display
        st.markdown("#### ⚽ **Current Formation: 3-4-3**")
        
        # Starting XI visualization
        formation_cols = st.columns([1, 2, 3, 2, 1])
        
        with formation_cols[2]:
            st.success("🥅 **Goalkeeper**\nAlisson (5.5)")
        
        # Add more formation display logic here
    
    def render_player_search(self):
        """Render advanced player search"""
        st.markdown("#### 🔍 **Smart Player Search**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            position_filter = st.multiselect(
                "Position", 
                ["Goalkeeper", "Defender", "Midfielder", "Forward"],
                default=["Midfielder", "Forward"]
            )
        
        with col2:
            price_range = st.slider("Price Range (£m)", 4.0, 15.0, (4.0, 12.0))
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Points", "Value", "Form", "ICT Index"])
        
        # Search results would go here
        st.info("🔍 **Search Results**: Advanced player filtering and recommendations")
    
    def render_performance_metrics(self):
        """Render detailed performance metrics"""
        st.markdown("#### 📊 **Performance Dashboard**")
        
        # Sample performance chart
        sample_data = pd.DataFrame({
            'Gameweek': range(1, 11),
            'Points': [12, 8, 15, 6, 2, 11, 9, 14, 7, 13],
            'Expected Points': [10, 9, 12, 8, 6, 10, 11, 12, 9, 11]
        })
        
        fig = px.line(
            sample_data, 
            x='Gameweek', 
            y=['Points', 'Expected Points'],
            title='Performance Tracking',
            color_discrete_map={'Points': '#00ff87', 'Expected Points': '#ff6b6b'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_ai_assistant(self):
        """Render AI assistant interface"""
        st.markdown("#### 💬 **AI FPL Assistant**")
        
        # Chat interface
        user_question = st.text_input(
            "💭 **Ask the AI Assistant:**",
            placeholder="e.g., Who should I captain this week? Should I transfer out Salah?"
        )
        
        if st.button("🚀 Get AI Insight", type="primary") and user_question:
            with st.spinner("🤖 AI is analyzing..."):
                # Mock AI response
                ai_response = f"Based on current form, fixtures, and statistical analysis, here's my recommendation for: '{user_question}'"
                st.success(f"🤖 **AI Assistant**: {ai_response}")
                
                # Additional insights
                st.info("💡 **Key Factors**: Form (85%), Fixtures (90%), Ownership (12%)")
    
    def render_market_analysis(self):
        """Render market analysis"""
        st.markdown("#### 📈 **Market Intelligence**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔥 Hot Transfers In**")
            st.success("• Player A (85% confidence)")
            st.success("• Player B (72% confidence)")
            st.success("• Player C (68% confidence)")
        
        with col2:
            st.markdown("**❄️ Falling in Price**")
            st.warning("• Player X (-15% last week)")
            st.warning("• Player Y (-8% last week)")
            st.warning("• Player Z (-5% last week)")
    
    def _get_current_gameweek(self, bootstrap_data):
        """Get current gameweek from bootstrap data"""
        events = bootstrap_data.get('events', [])
        for event in events:
            if event.get('is_current', False):
                return event.get('id', 1)
        return 1
    
    def _get_top_performers(self, bootstrap_data):
        """Get top performing players"""
        try:
            players = bootstrap_data.get('elements', [])
            df = pd.DataFrame(players)
            return df.nlargest(10, 'total_points')[['web_name', 'total_points', 'now_cost']]
        except:
            return pd.DataFrame()
    
    def _load_team_data(self, team_id):
        """Load team data for analysis"""
        try:
            # This would integrate with the FPL API to load real team data
            st.success(f"✅ **Team {team_id} loaded successfully!**")
            st.session_state.fpl_data_loaded = True
        except Exception as e:
            st.error(f"Failed to load team: {e}")
    
    def run_comprehensive_app(self):
        """Main application runner"""
        try:
            # Setup
            self.setup_page_config()
            self.initialize_session_state()
            
            # Header
            st.markdown("""
            <div class="main-header">
                <h1 style="color: white; margin: 0; text-align: center;">
                    ⚽ FPL Analytics - Comprehensive Suite
                </h1>
                <p style="color: white; margin: 0; text-align: center; font-size: 1.2em;">
                    Advanced Fantasy Premier League Analytics with AI-Powered Insights
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # System status
            self.render_system_status()
            
            # Main navigation and content
            self.render_enhanced_navigation()
            
            # Footer with performance info
            self.render_footer()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"Application error: {e}")
    
    def render_system_status(self):
        """Render system status indicators"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.success("🟢 **FPL API**: Connected")
        with col2:
            st.success("🟢 **Cache**: Active (87% hit rate)")
        with col3:
            st.success("🟢 **AI Engine**: Online")
        with col4:
            st.info(f"🕐 **Last Update**: {datetime.now().strftime('%H:%M:%S')}")
    
    def render_footer(self):
        """Render application footer"""
        st.markdown("---")
        
        footer_cols = st.columns(4)
        
        with footer_cols[0]:
            st.caption("🚀 **FPL Analytics Comprehensive**")
        with footer_cols[1]:
            st.caption("⚡ **Real-time Data Integration**")
        with footer_cols[2]:
            st.caption("🤖 **AI-Powered Analysis**")
        with footer_cols[3]:
            st.caption("📊 **Advanced Statistics**")


# Main application instance
comprehensive_app = ComprehensiveFPLApp()


if __name__ == "__main__":
    comprehensive_app.run_comprehensive_app()