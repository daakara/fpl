"""
Modular My Team Page - Uses component-based architecture
"""
import streamlit as st
from services.fpl_data_service import FPLDataService
from utils.error_handling import logger, handle_errors

# Import modular components
from .my_team.team_import import TeamImportComponent
from .my_team.team_overview import TeamOverviewComponent
from .my_team.squad_analysis import SquadAnalysisComponent
from .my_team.performance_analysis import PerformanceAnalysisComponent
from .my_team.recommendations import RecommendationsComponent
from .my_team.optimizer import StartingXIOptimizerComponent
from .my_team.swot_analysis import SWOTAnalysisComponent
from .my_team.advanced_analytics import AdvancedAnalyticsComponent
from .my_team.transfer_planning import TransferPlanningComponent
from .my_team.performance_comparison import PerformanceComparisonComponent
from .my_team.fixture_analysis import FixtureAnalysisComponent


class ModularMyTeamPage:
    """Modular My FPL Team page using component architecture"""
    
    def __init__(self):
        """Initialize the modular page with components"""
        self.data_service = FPLDataService()
        
        # Initialize components
        self.team_import = TeamImportComponent(self.data_service)
        self.team_overview = TeamOverviewComponent(self.data_service)
        self.squad_analysis = SquadAnalysisComponent(self.data_service)
        self.performance_analysis = PerformanceAnalysisComponent(self.data_service)
        self.recommendations = RecommendationsComponent(self.data_service)
        self.optimizer = StartingXIOptimizerComponent(self.data_service)
        self.swot_analysis = SWOTAnalysisComponent(self.data_service)
        self.advanced_analytics = AdvancedAnalyticsComponent(self.data_service)
        self.transfer_planning = TransferPlanningComponent(self.data_service)
        self.performance_comparison = PerformanceComparisonComponent(self.data_service)
        self.fixture_analysis = FixtureAnalysisComponent(self.data_service)
    
    def __call__(self):
        """Make the class callable"""
        self.render()
    
    @handle_errors("Error rendering My Team page")
    def render(self):
        """Main render method using modular components"""
        logger.info("Starting Modular My Team page render")
        st.header("👤 My FPL Team (Modular)")
        
        # Initialize session state
        self._initialize_session_state()
        
        # Debug information (optional - can be disabled in production)
        if st.checkbox("Show Debug Info", value=False):
            self.team_import.render_debug_section()
        
        # Quick test button
        self.team_import.render_quick_test()
        
        st.divider()
        
        try:
            # Check if team is loaded
            if not st.session_state.get('my_team_loaded', False):
                logger.info("No team loaded, showing import section")
                self._handle_data_loading()
                self.team_import.render()
                return
            
            # Get team data from session state
            team_data = st.session_state.get('my_team_data')
            
            if not self._validate_team_data(team_data):
                logger.error("Invalid team data in session state")
                st.error("❌ Error: Invalid team data. Please try loading your team again.")
                self._reset_team_state()
                return
            
            # Display team overview
            self.team_overview.render(team_data)
            
            # Create main analysis tabs
            self._render_analysis_tabs(team_data)
            
        except Exception as e:
            logger.error(f"Error in main render: {str(e)}")
            st.error(f"❌ Unexpected error: {str(e)}")
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'my_team_loaded': False,
            'my_team_id': None,
            'my_team_data': None,
            'my_team_gameweek': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _handle_data_loading(self):
        """Handle background data loading"""
        if not st.session_state.get('data_loaded', False):
            logger.info("Attempting to load player data in background...")
            try:
                with st.spinner("⚡ Loading FPL data..."):
                    players_df, teams_df = self.data_service.load_fpl_data()
                    if not players_df.empty:
                        st.session_state.players_df = players_df
                        st.session_state.teams_df = teams_df
                        st.session_state.data_loaded = True
                        logger.info("Successfully loaded player data")
            except Exception as e:
                logger.error(f"Error loading player data: {str(e)}")
                st.warning("⚠️ Could not load player data in background, but you can still import your team.")
    
    def _validate_team_data(self, team_data):
        """Validate team data structure"""
        if not team_data or not isinstance(team_data, dict):
            return False
        
        required_fields = ['picks', 'entry_name']
        return all(field in team_data for field in required_fields)
    
    def _reset_team_state(self):
        """Reset team-related session state"""
        reset_keys = ['my_team_loaded', 'my_team_id', 'my_team_data', 'my_team_gameweek']
        for key in reset_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    def _render_analysis_tabs(self, team_data):
        """Render main analysis tabs using components"""
        tab_names = [
            "👥 Current Squad",
            "📊 Performance Analysis",
            "💡 Recommendations",
            "⭐ Starting XI Optimizer",
            "🎯 SWOT Analysis",
            "📈 Advanced Analytics",
            "🔄 Transfer Planning",
            "📊 Performance Comparison",
            "⚽ Fixture Analysis"
        ]
        
        tabs = st.tabs(tab_names)
        
        # Map tabs to components with error handling
        tab_components = [
            (tabs[0], self.squad_analysis, "Current Squad"),
            (tabs[1], self.performance_analysis, "Performance Analysis"),
            (tabs[2], self.recommendations, "Recommendations"),
            (tabs[3], self.optimizer, "Starting XI Optimizer"),
            (tabs[4], self.swot_analysis, "SWOT Analysis"),
            (tabs[5], self.advanced_analytics, "Advanced Analytics"),
            (tabs[6], self.transfer_planning, "Transfer Planning"),
            (tabs[7], self.performance_comparison, "Performance Comparison"),
            (tabs[8], self.fixture_analysis, "Fixture Analysis")
        ]
        
        # Render each tab with error boundary
        for tab, component, tab_name in tab_components:
            with tab:
                try:
                    component.render(team_data)
                except Exception as e:
                    logger.error(f"Error in {tab_name} tab: {str(e)}")
                    st.error(f"❌ Error loading {tab_name}")
                    st.info("This component is being updated. Please try again later.")

    # Component method access for backward compatibility
    def render_team_import(self):
        """Render team import component"""
        return self.team_import.render()
    
    def render_team_overview(self, team_data=None):
        """Render team overview component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.team_overview.render(team_data)
    
    def render_squad_analysis(self, team_data=None):
        """Render squad analysis component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.squad_analysis.render(team_data)
    
    def render_performance_analysis(self, team_data=None):
        """Render performance analysis component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.performance_analysis.render(team_data)
    
    def render_recommendations(self, team_data=None):
        """Render AI recommendations component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.recommendations.render(team_data)
    
    def render_optimizer(self, team_data=None):
        """Render Starting XI optimizer component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.optimizer.render(team_data)
    
    def render_swot_analysis(self, team_data=None):
        """Render SWOT analysis component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.swot_analysis.render(team_data)
    
    def render_advanced_analytics(self, team_data=None):
        """Render advanced analytics component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.advanced_analytics.render(team_data)
    
    def render_transfer_planning(self, team_data=None):
        """Render transfer planning component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.transfer_planning.render(team_data)
    
    def render_performance_comparison(self, team_data=None):
        """Render performance comparison component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.performance_comparison.render(team_data)
    
    def render_fixture_analysis(self, team_data=None):
        """Render fixture analysis component"""
        if team_data is None:
            team_data = st.session_state.get('my_team_data')
        return self.fixture_analysis.render(team_data)


# For backward compatibility, create an alias
MyTeamPage = ModularMyTeamPage
