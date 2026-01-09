"""
FPL Analytics - Refactored Resilient Application
Clean, modular architecture with separated concerns
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import refactored services
from services.navigation_service import NavigationService
from services.ui_component_service import UIComponentService
from services.player_recommendation_service import PlayerRecommendationService
from services.data_utilities_service import DataUtilitiesService
from controllers.dashboard_controller import DashboardController

# Import critical services
from services.data_quality_service import DataQualityService
from services.price_change_predictor_service import PriceChangePredictorService
from services.external_data_integrator_service import ExternalDataIntegratorService

# Import mobile responsiveness
from utils.mobile_responsive import (
    MobileResponsive, 
    is_mobile, 
    is_tablet, 
    is_desktop,
    responsive_columns,
    responsive_metric,
    responsive_dataframe,
    add_responsive_css
)

# Import theme manager and fixture ticker
from utils.theme_manager import get_theme_manager, inject_theme, render_theme_toggle
from components.fixture_ticker import FixtureTicker

# Try enhanced services, fall back to basic functionality
try:
    from services.enhanced_fpl_data_service import get_enhanced_fpl_service
    from utils.advanced_cache_manager import get_cache_manager
    from utils.error_handling import logger
    ENHANCED_MODE = True
except Exception as e:
    ENHANCED_MODE = False
    print(f"Enhanced services unavailable: {e}")
    # Create a simple logger fallback
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

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
    from views.advanced_analytics_page_enhanced import AdvancedAnalyticsPage as EnhancedAnalyticsPage
    from views.learning_resources_page import LearningResourcesPage
    from views.injury_transfer_page import InjuryTransferPage
    PAGES_AVAILABLE = True
except ImportError as e:
    print(f"Some page modules not available: {e}")
    PAGES_AVAILABLE = False


class RefactoredFPLApp:
    """Refactored FPL Analytics Application with clean architecture"""
    
    def __init__(self):
        """Initialize with dependency injection"""
        self.enhanced_mode = ENHANCED_MODE
        
        # Initialize services
        self.navigation_service = NavigationService()
        self.ui_service = UIComponentService()
        self.recommendation_service = PlayerRecommendationService()
        self.data_service = DataUtilitiesService()
        self.dashboard_controller = DashboardController()
        
        # Initialize critical services
        self.data_quality_service = DataQualityService()
        self.price_predictor = PriceChangePredictorService()
        self.external_data_service = ExternalDataIntegratorService()
        
        # Initialize enhanced services if available
        if self.enhanced_mode:
            try:
                self.fpl_service = get_enhanced_fpl_service()
                self.cache_manager = get_cache_manager()
            except Exception as e:
                self.enhanced_mode = False
                print(f"Enhanced services initialization failed: {e}")
        
        # Create fallback data
        self.fallback_data = self.data_service.create_fallback_data()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="FPL Analytics - Resilient Suite",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/yourusername/fpl-analytics',
                'Report a bug': "https://github.com/yourusername/fpl-analytics/issues",
                'About': "# FPL Analytics Resilient Suite\n**Advanced Fantasy Premier League Analytics**"
            }
        )
        
        # Add responsive CSS for mobile optimization
        add_responsive_css()
        
        # Inject theme CSS (NEW FEATURE: Dark Mode)
        inject_theme()
        
        # Custom CSS for enhanced UI
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
        .ai-response {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize session state with default values"""
        import pandas as pd
        
        defaults = {
            'app_initialized': True,
            'api_status': 'checking',
            'data_source': 'initializing',
            'app_performance': {
                'load_time': 0.85,
                'cache_hits': 87,
                'api_calls': 12
            },
            'current_page': 'Dashboard',
            'data_loaded': False,
            'players_df': pd.DataFrame(),
            'teams_df': pd.DataFrame(),
            'last_data_update': None,
            'fpl_team_loaded': False,
            'fpl_team_data': None,
            'fpl_team_id': None,
            'fpl_team_gameweek': None,
            'ai_rec_pos_filter': 'All',
            'ai_rec_budget_filter': 100.0
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _ensure_numeric_types(self, df):
        """Convert string columns to proper numeric types for FPL data"""
        numeric_columns = ['form', 'selected_by_percent', 'total_points', 'now_cost', 
                          'points_per_game', 'minutes', 'goals_scored', 'assists', 
                          'clean_sheets', 'goals_conceded', 'bonus', 'bps', 
                          'ict_index', 'influence', 'creativity', 'threat']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    
    def check_api_status(self):
        """Check FPL API status with enhanced error handling"""
        try:
            if self.enhanced_mode and hasattr(self, 'fpl_service'):
                # Test API connection
                test_data = self.fpl_service.get_bootstrap_data()
                if test_data and len(test_data.get('elements', [])) > 0:
                    st.session_state.api_status = 'online'
                    st.session_state.data_source = 'live_api'
                    return True
        except Exception as e:
            if self.enhanced_mode and hasattr(self, 'fpl_service'):
                logger.warning(f"API check failed: {e}")
        
        st.session_state.api_status = 'offline'
        st.session_state.data_source = 'fallback'
        return False
    
    def get_data_safely(self):
        """Safely get data with comprehensive fallback mechanism and data quality validation"""
        # Use session state to cache data and avoid re-fetching
        import pandas as pd
        from datetime import datetime
        
        # Check if data is already cached in session state
        if st.session_state.get('data_cached', False) and st.session_state.get('cached_data'):
            return st.session_state.cached_data
        
        try:
            if self.enhanced_mode and hasattr(self, 'fpl_service'):
                # Try to get live data first
                live_data = self.fpl_service.get_bootstrap_data()
                if live_data and self.data_service.validate_data_structure(live_data):
                    st.session_state.api_status = 'online'
                    st.session_state.data_source = 'live_api'
                    
                    # Populate session state with loaded data
                    if 'elements' in live_data:
                        df = pd.DataFrame(live_data['elements'])
                        # Use DataQualityService for comprehensive validation and cleaning
                        df = self.data_quality_service.validate_and_clean_players(df)
                        # Add price change predictions
                        df = self.price_predictor.predict_price_changes(df)
                        # Add injury/fitness data
                        df = self.external_data_service.get_injury_news(df)
                        
                        st.session_state.players_df = df
                        st.session_state.data_loaded = True
                        st.session_state.last_data_update = datetime.now()
                        logger.info(f"✅ Live data loaded and validated: {len(st.session_state.players_df)} players")
                    
                    if 'teams' in live_data:
                        teams_df = pd.DataFrame(live_data['teams'])
                        teams_df = self.data_quality_service.validate_and_clean_teams(teams_df)
                        st.session_state.teams_df = teams_df
                    
                    # Cache the data in session state
                    st.session_state.cached_data = live_data
                    st.session_state.data_cached = True
                    return live_data
            
            # Fallback to cached/default data
            st.session_state.api_status = 'offline'
            st.session_state.data_source = 'fallback'
            
            # Populate session state with fallback data
            if 'elements' in self.fallback_data:
                df = pd.DataFrame(self.fallback_data['elements'])
                # Use DataQualityService for comprehensive validation and cleaning
                df = self.data_quality_service.validate_and_clean_players(df)
                # Add price change predictions
                df = self.price_predictor.predict_price_changes(df)
                # Add injury/fitness data
                df = self.external_data_service.get_injury_news(df)
                
                st.session_state.players_df = df
                st.session_state.data_loaded = True
                st.session_state.last_data_update = datetime.now()
                logger.info(f"⚠️ Using fallback data (validated): {len(st.session_state.players_df)} players")
            
            if 'teams' in self.fallback_data:
                teams_df = pd.DataFrame(self.fallback_data['teams'])
                teams_df = self.data_quality_service.validate_and_clean_teams(teams_df)
                st.session_state.teams_df = teams_df
            
            # Cache the fallback data in session state
            st.session_state.cached_data = self.fallback_data
            st.session_state.data_cached = True
            return self.fallback_data
            
        except Exception as e:
            if self.enhanced_mode:
                logger.error(f"Data retrieval failed: {e}")
            
            st.session_state.api_status = 'offline'
            st.session_state.data_source = 'fallback'
            
            # Ensure minimal session state even on error
            if not st.session_state.get('data_loaded', False):
                st.session_state.players_df = pd.DataFrame()
                st.session_state.teams_df = pd.DataFrame()
                st.session_state.data_loaded = False
            
            return self.fallback_data
    
    def render_page_content(self, selected_page):
        """Render content based on selected page with clean separation"""
        data = self.get_data_safely()
        
        if selected_page == "Dashboard":
            if PAGES_AVAILABLE:
                try:
                    dashboard_page = DashboardPage()
                    dashboard_page.render()
                except Exception as e:
                    st.error(f"Dashboard page error: {e}")
                    self.dashboard_controller.render_comprehensive_dashboard(data)
            else:
                self.dashboard_controller.render_comprehensive_dashboard(data)
                
        elif selected_page == "Player Analysis":
            if PAGES_AVAILABLE:
                try:
                    from views.player_analysis_page import PlayerAnalysisPage
                    player_page = PlayerAnalysisPage()
                    player_page.render()
                except Exception as e:
                    st.warning(f"Player Analysis page not available: {e}")
                    self.dashboard_controller.render_player_intelligence(data)
            else:
                self.dashboard_controller.render_player_intelligence(data)
                
        elif selected_page == "Team Builder":
            self._render_fallback_page("Team Builder", "🛠️ **Team Builder**", 
                                     "Build and optimize your FPL squad")
                
        elif selected_page == "My Team":
            if PAGES_AVAILABLE:
                try:
                    my_team_page = MyTeamPage()
                    my_team_page.render()
                except Exception as e:
                    st.warning(f"My Team page error: {e}")
                    self.dashboard_controller.render_my_team_center(data)
            else:
                self.dashboard_controller.render_my_team_center(data)
                
        elif selected_page == "AI Recommendations":
            if PAGES_AVAILABLE:
                try:
                    ai_page = AIRecommendationsPage()
                    ai_page.render()
                except Exception as e:
                    st.warning(f"AI Recommendations page error: {e}")
                    self.dashboard_controller.render_ai_assistant()
            else:
                self.dashboard_controller.render_ai_assistant()
                
        elif selected_page == "Advanced Analytics":
            if PAGES_AVAILABLE:
                try:
                    # Use the enhanced analytics page
                    enhanced_analytics = EnhancedAnalyticsPage()
                    enhanced_analytics.render()
                except Exception as e:
                    st.warning(f"Enhanced analytics not available: {e}")
                    # Fallback to original
                    self.dashboard_controller.render_advanced_analytics(data)
            else:
                self.dashboard_controller.render_advanced_analytics(data)
                
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
                    self._render_fallback_page("Fixture Analysis", "📅 **Fixture Analysis**",
                                             "Comprehensive fixture difficulty analysis")
            else:
                self._render_fallback_page("Fixture Analysis", "📅 **Fixture Analysis**",
                                         "Comprehensive fixture difficulty analysis")
                
        elif selected_page == "Price Changes":
            try:
                from views.price_changes_page import PriceChangesPage
                price_page = PriceChangesPage()
                price_page.render()
            except Exception as e:
                st.warning(f"Price Changes page error: {e}")
                self._render_fallback_page("Price Changes", "💰 **Price Changes**",
                                         "Track price rises and falls")
                
        elif selected_page == "Live Data":
            self._render_live_data_page(data)
                
        elif selected_page == "Market Intelligence":
            self._render_market_intelligence_page(data)
        
        elif selected_page == "Injury & Transfers":
            if PAGES_AVAILABLE:
                try:
                    injury_transfer_page = InjuryTransferPage()
                    injury_transfer_page.render()
                except Exception as e:
                    st.warning(f"Injury & Transfers page error: {e}")
                    self._render_fallback_page("Injury & Transfers", "⚕️ **Injury & Transfer Centre**",
                                             "Latest injury news and transfer updates from Premier League")
            else:
                self._render_fallback_page("Injury & Transfers", "⚕️ **Injury & Transfer Centre**",
                                         "Latest injury news and transfer updates from Premier League")
        
        elif selected_page == "Learning Resources":
            if PAGES_AVAILABLE:
                try:
                    learning_page = LearningResourcesPage()
                    learning_page.render()
                except Exception as e:
                    st.warning(f"Learning Resources page error: {e}")
                    self._render_fallback_page("Learning Resources", "🎓 **Learning Resources**",
                                             "FPL glossary, strategy guides, and tutorials")
            else:
                self._render_fallback_page("Learning Resources", "🎓 **Learning Resources**",
                                         "FPL glossary, strategy guides, and tutorials")
    
    def _render_fallback_page(self, page_name, title, description):
        """Render a fallback page when specific page module isn't available"""
        st.markdown(f"### {title}")
        st.info(f"📋 {description}")
        
        page_info = self.navigation_service.get_page_info(page_name)
        st.markdown(f"**Features coming soon:**")
        
        for feature in page_info['features']:
            st.markdown(f"- {feature}")
        
        st.warning("🚧 This page is under development. Using fallback functionality.")
    
    def _render_live_data_page(self, data):
        """Render comprehensive live data dashboard with enhanced tabs"""
        try:
            # Use the comprehensive LiveDataPage class
            if PAGES_AVAILABLE:
                live_data_page = LiveDataPage()
                live_data_page.render()
            else:
                # Fallback to basic live data display
                st.markdown("### 📡 **Live Data Monitoring**")
                
                self.ui_service.render_live_data_indicator(data)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Players Loaded", len(data.get('elements', [])))
                
                with col2:
                    st.metric("⚽ Teams", len(data.get('teams', [])))
                
                with col3:
                    freshness = self.data_service.get_data_freshness(data)
                    st.metric("🕐 Data Freshness", freshness)
                
                # Sample data preview
                if isinstance(data, dict) and 'elements' in data:
                    st.markdown("#### 👥 **Sample Players**")
                    sample_players = self.data_service.get_live_players_sample(data, 10)
                    st.write(", ".join(sample_players))
                    
        except Exception as e:
            st.error(f"❌ Error loading Live Data page: {str(e)}")
            st.info("🔄 Please try refreshing the page or check your connection.")
    
    def _render_market_intelligence_page(self, data):
        """Render market intelligence page"""
        st.markdown("### 📈 **Market Intelligence**")
        
        # Get recommendations and insights
        recommendations = self.recommendation_service.generate_live_player_recommendations(data)
        transfer_stats = self.recommendation_service.get_transfer_statistics(data)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🔥 **Hot Pick**")
            st.success(f"**{recommendations['hot_pick']['name']}**")
            st.caption(recommendations['hot_pick']['reason'])
        
        with col2:
            st.markdown("#### 💎 **Value Pick**")
            st.info(f"**{recommendations['value_pick']['name']}**")
            st.caption(recommendations['value_pick']['reason'])
        
        with col3:
            st.markdown("#### ⚠️ **Avoid Pick**")
            st.error(f"**{recommendations['avoid_pick']['name']}**")
            st.caption(recommendations['avoid_pick']['reason'])
        
        # Transfer statistics
        st.markdown("#### 📊 **Transfer Statistics**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔥 Most Transferred In", 
                     transfer_stats['most_in']['name'], 
                     transfer_stats['most_in']['change'])
        
        with col2:
            st.metric("❄️ Most Transferred Out", 
                     transfer_stats['most_out']['name'], 
                     transfer_stats['most_out']['change'])
        
        with col3:
            st.metric("💰 Price Rise Candidate", 
                     transfer_stats['price_rise']['name'], 
                     transfer_stats['price_rise']['change'])
    
    def render_sidebar(self):
        """Render enhanced sidebar with live recommendations"""
        with st.sidebar:
            st.markdown("## 🎛️ **Control Panel**")
            
            # NEW FEATURE: Dark Mode Toggle
            st.markdown("### 🎨 **Theme**")
            render_theme_toggle(position='sidebar')
            
            st.markdown("---")
            
            # Quick stats with live recommendations
            st.markdown("### 📊 **Quick Stats**")
            
            # Get live player recommendations
            data = self.get_data_safely()
            recommendations = self.recommendation_service.generate_live_player_recommendations(data)
            
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
            
            if st.button("🔄 Refresh Data", width='stretch'):
                st.rerun()
            
            if st.button("📊 Performance Report", width='stretch'):
                st.info("📈 Generating performance report...")
    
    def render_fixture_ticker(self):
        """Render scrolling fixture ticker (NEW FEATURE)"""
        try:
            # Get fixtures and teams data
            data = self.get_data_safely()
            fixtures_df = data.get('fixtures', pd.DataFrame())
            teams_df = data.get('teams', pd.DataFrame())
            
            if not fixtures_df.empty and not teams_df.empty:
                ticker = FixtureTicker()
                ticker.render(fixtures_df, teams_df, num_gameweeks=5, speed='medium')
        except Exception as e:
            logger.debug(f"Fixture ticker not available: {e}")
            # Silently skip if fixtures not available
            pass
    
    def run_refactored_app(self):
        """Run the refactored FPL application"""
        try:
            # Setup
            self.setup_page_config()
            self.initialize_session_state()
            
            # Header
            self.ui_service.render_enhanced_header()
            
            # NEW FEATURE: Fixture Ticker
            self.render_fixture_ticker()
            
            # Navigation
            selected_page = self.navigation_service.render_navigation()
            
            # Main content based on navigation
            self.render_page_content(selected_page)
            
            # Sidebar (always visible)
            self.render_sidebar()
            
            # Footer
            self.ui_service.render_footer()
            
        except Exception as e:
            st.error(f"Application error: {e}")
            st.info("🔄 **Fallback mode activated** - Application running with cached data")


# Create and run the refactored application
refactored_app = RefactoredFPLApp()

if __name__ == "__main__":
    refactored_app.run_refactored_app()