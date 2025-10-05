"""
Modular My Team Page - Refactored with component-based architecture
"""
import streamlit as st
import pandas as pd
import numpy as np
import time
from services.fpl_data_service import FPLDataService
from utils.error_handling import logger, handle_errors

# Import components
from .components.team_import_component import TeamImportComponent
from .components.team_overview_component import TeamOverviewComponent
from .components.squad_analysis_component import SquadAnalysisComponent
from .components.performance_analysis_component import PerformanceAnalysisComponent
from .components.team_recommendations_component import TeamRecommendationsComponent
from .components.starting_xi_optimizer_component import StartingXIOptimizerComponent
from .components.advanced_analytics_factory import AdvancedAnalyticsComponentFactory
from .components.historical_performance_component import HistoricalPerformanceComponent
from .components.mini_league_component import MiniLeagueComponent
from .components.team_health_component import TeamHealthComponent
from .components.ai_insights_component import AIInsightsComponent


class MyTeamPage:
    """Modular My FPL Team functionality with component-based architecture"""
    
    def __init__(self):
        self.data_service = FPLDataService()
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all page components"""
        self.team_import = TeamImportComponent(self.data_service)
        self.team_overview = TeamOverviewComponent()
        self.squad_analysis = SquadAnalysisComponent()
        self.performance_analysis = PerformanceAnalysisComponent()
        self.team_recommendations = TeamRecommendationsComponent()
        self.starting_xi_optimizer = StartingXIOptimizerComponent()
        
        # Advanced components (with fallbacks)
        factory = AdvancedAnalyticsComponentFactory()
        self.swot_analysis = factory.create_swot_analysis_component()
        self.advanced_analytics = factory.create_advanced_analytics_component()
        self.transfer_planning = factory.create_transfer_planning_component()
        self.performance_comparison = factory.create_performance_comparison_component()
        self.fixture_analysis = factory.create_fixture_analysis_component()
        
        # New enhanced components
        self.historical_performance = HistoricalPerformanceComponent(self.data_service)
        self.mini_league = MiniLeagueComponent(self.data_service)
        self.team_health = TeamHealthComponent(self.data_service)
        self.ai_insights = AIInsightsComponent(self.data_service)
    
    def __call__(self):
        """Make the class callable for compatibility"""
        self.render()
    
    def render(self):
        """Main render method for My Team page"""
        try:
            self._render_team_page()
        except Exception as e:
            self._render_error_state(e)
    
    def _render_error_state(self, error):
        """Render error state with helpful information"""
        st.error(f"❌ Error in My Team page: {str(error)}")
        st.write("📍 Please try refreshing the page or contact support if the issue persists.")
        st.write("🔍 **Troubleshooting:**") 
        st.write("1. Check your internet connection")
        st.write("2. Try refreshing the browser page")
        
        import traceback
        with st.expander("🔧 Technical Details"):
            st.code(traceback.format_exc())
    
    def _render_team_page(self):
        """Internal render method with all the page content"""
        try:
            logger.info("Starting My Team page render")
        except:
            # If logger fails, continue anyway
            pass
        
        st.header("👤 My FPL Team")
        st.success("✅ My FPL Team page is loading successfully!")
        
        # Debug information
        self._render_debug_info()
        
        # Add test button
        self._render_test_button()
        
        st.divider()
        st.info("🔄 Initializing team data...")
        
        # Initialize session state
        self._initialize_session_state()
        
        # Check if team is loaded
        if not st.session_state.get('fpl_team_loaded', False):
            logger.info("No team loaded, showing import section")
            self._ensure_player_data_loaded()
            self.team_import.render()
            return
        
        # Get and validate team data
        team_data = st.session_state.fpl_team_data
        if not self._validate_team_data(team_data):
            return
        
        # Display team overview
        self.team_overview.render(team_data)
        
        # Render main content tabs
        self._render_main_tabs(team_data)
        
        # Add reload option
        self._render_reload_option()
    
    def _render_team_import_section(self):
        """Render team import interface"""
        logger.info("Rendering team import section")
        st.subheader("📥 Import Your FPL Team")
        
        # Add some helpful info
        st.info("👋 Enter your FPL Team ID below to analyze your team performance and get AI-powered recommendations!")
        
        try:
            col1, col2 = st.columns([2, 1])
        except Exception as e:
            logger.error(f"Error creating columns: {str(e)}")
            # Fallback to no columns if there's an issue
            col1 = st.container()
            col2 = st.container()
        
        with col1:
            # Use stored team ID if available
            default_team_id = st.session_state.fpl_team_id if st.session_state.fpl_team_id else ""
            team_id = st.text_input(
                "Enter your FPL Team ID:",
                value=default_team_id,
                placeholder="e.g., 1234567",
                help="Find your team ID in your FPL team URL"
            )
            
            # Get current gameweek for selection
            try:
                current_gw = self.data_service.get_current_gameweek()
                if not current_gw or current_gw < 1:
                    current_gw = 8  # Default to gameweek 8
                gameweeks = list(range(1, min(current_gw + 1, 39)))
            except Exception as e:
                logger.error(f"Error getting current gameweek: {str(e)}")
                current_gw = 8
                gameweeks = list(range(1, 39))
            
            selected_gw = st.selectbox(
                "Select Gameweek:",
                gameweeks,
                index=min(max(current_gw - 1, 0), len(gameweeks) - 1),
                help="Choose which gameweek's team to analyze"
            )
        
        with col2:
            st.write("")  # Add some spacing
            st.write("")  # Add some spacing
            
            if st.button("🔄 Load My Team", type="primary", use_container_width=True):
                if team_id and team_id.strip():
                    logger.info(f"User clicked Load Team button with ID: {team_id}")
                    self._load_team_data(team_id.strip(), selected_gw)
                else:
                    st.warning("⚠️ Please enter a valid team ID")
            
            # Add a quick test button
            if st.button("🧪 Quick Test", help="Test with team ID 1437667"):
                logger.info("User clicked Quick Test button")
                self._load_team_data("1437667", 7)
        
        # Instructions
        with st.expander("💡 How to find your Team ID", expanded=False):
            st.markdown("""
            **Step 1:** Go to the official FPL website and log in
            
            **Step 2:** Navigate to your team page
            
            **Step 3:** Look at the URL - it will look like:
            `https://fantasy.premierleague.com/entry/1234567/event/15`
            
            **Step 4:** Your Team ID is the number after `/entry/` (in this example: 1234567)
            
            **Note:** Your team must be public for this to work. You can change this in your FPL account settings.
            """)
    
    def _load_team_data(self, team_id, gameweek):
        """Load team data from FPL API"""
        try:
            # Create a loading container
            with st.spinner("🔄 Loading team data..."):
                # First ensure we have player data
                if not st.session_state.get('data_loaded', False):
                    logger.info("Loading player data first...")
                    players_df, teams_df = self.data_service.load_fpl_data()
                    if not players_df.empty:
                        st.session_state.players_df = players_df
                        st.session_state.teams_df = teams_df
                        st.session_state.data_loaded = True
                        logger.info("Successfully loaded player data")
                
                # Now load team data
                logger.info(f"Loading team data for ID: {team_id}")
                team_data = self.data_service.load_team_data(team_id, gameweek)
                
                if team_data and isinstance(team_data, dict):
                    # Check if picks data is available
                    picks = team_data.get('picks', [])
                    if not picks:
                        # Try previous gameweeks if current one has no picks
                        st.warning(f"No squad data found for gameweek {gameweek}. Trying previous gameweeks...")
                        for try_gw in range(gameweek - 1, max(0, gameweek - 5), -1):
                            if try_gw < 1:
                                break
                            st.write(f"Trying gameweek {try_gw}...")
                            try:
                                alt_team_data = self.data_service.load_team_data(team_id, try_gw)
                                if alt_team_data and alt_team_data.get('picks'):
                                    team_data = alt_team_data
                                    gameweek = try_gw
                                    st.success(f"Found squad data in gameweek {try_gw}!")
                                    break
                            except Exception as e:
                                st.write(f"GW {try_gw}: {str(e)}")
                                continue
                    
                    if not team_data.get('picks'):
                        raise ValueError("No squad data available for this team in recent gameweeks")
                    
                    logger.info("Team data loaded successfully")
                    
                    # Set all session state at once
                    session_updates = {
                        'fpl_team_data': team_data,
                        'fpl_team_id': team_id,
                        'fpl_team_gameweek': gameweek,
                        'fpl_team_loaded': True,
                        'current_page': "👤 My FPL Team"
                    }
                    
                    for key, value in session_updates.items():
                        st.session_state[key] = value
                    
                    # Show success message
                    picks_count = len(team_data.get('picks', []))
                    st.success(f"✅ Team loaded successfully! Found {picks_count} players for gameweek {gameweek}")
                    logger.info(f"Successfully loaded and stored team data for ID: {team_id}")
                    
                    # Force the page to use the new state
                    st.rerun()
                    
                else:
                    raise ValueError("Invalid or empty team data received")
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error loading team: {error_msg}")
            
            # Clear session state
            keys_to_clear = ['fpl_team_loaded', 'fpl_team_id', 'fpl_team_data', 'fpl_team_gameweek']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Show error with guidance
            st.error(f"""
            ❌ Error loading team: {error_msg}
            
            Please ensure:
            1. The team ID is correct
            2. Your FPL team is set to public
            3. The FPL servers are responsive
            """)
            
            return False
            
        return True
    
    def _render_debug_info(self):
        """Render debug information"""
        try:
            st.write("🔍 **Debug Info:**")
            st.write(f"- Team loaded: {st.session_state.get('fpl_team_loaded', False)}")
            st.write(f"- Data loaded: {st.session_state.get('data_loaded', False)}")
            st.write(f"- Team ID: {st.session_state.get('fpl_team_id', 'None')}")
            st.write(f"- Page render started successfully ✅")
        except Exception as e:
            st.error(f"Debug info failed: {e}")
    
    def _render_test_button(self):
        """Render test button for quick testing"""
        if st.button("🧪 Test with Team ID 1437667"):
            st.write("**Testing with your team ID...**")
            test_team_id = "1437667"
            # Try multiple gameweeks to find one that works
            for gw in [8, 7, 6, 5, 4, 3, 2, 1]:
                try:
                    st.write(f"Trying gameweek {gw}...")
                    team_data = self.data_service.load_team_data(test_team_id, gw)
                    if team_data and team_data.get('picks'):
                        st.success(f"✅ Successfully loaded team data for GW {gw}!")
                        st.write(f"Team: {team_data.get('entry_name', 'Unknown')}")
                        st.write(f"Squad size: {len(team_data.get('picks', []))}")
                        # Set the data in session state
                        self._set_team_session_state(team_data, test_team_id, gw)
                        st.rerun()
                        break
                    else:
                        st.write(f"❌ GW {gw}: No picks data")
                except Exception as e:
                    st.write(f"❌ GW {gw}: {str(e)}")
    
    def _initialize_session_state(self):
        """Initialize session state for team data"""
        if 'fpl_team_loaded' not in st.session_state:
            st.session_state.fpl_team_loaded = False
            
        if 'fpl_team_id' not in st.session_state:
            st.session_state.fpl_team_id = None
            
        if 'fpl_team_data' not in st.session_state:
            st.session_state.fpl_team_data = None
    
    def _ensure_player_data_loaded(self):
        """Ensure player data is loaded in the background"""
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
        """Validate team data"""
        if not team_data or not isinstance(team_data, dict):
            logger.error("Invalid team data in session state")
            st.error("❌ Error: Invalid team data. Please try loading your team again.")
            st.session_state.fpl_team_loaded = False
            return False
        return True
    
    def _set_team_session_state(self, team_data, team_id, gameweek):
        """Set team data in session state"""
        session_updates = {
            'fpl_team_data': team_data,
            'fpl_team_id': team_id,
            'fpl_team_gameweek': gameweek,
            'fpl_team_loaded': True,
            'current_page': "👤 My FPL Team"
        }
        
        for key, value in session_updates.items():
            st.session_state[key] = value
    
    def _render_main_tabs(self, team_data):
        """Render the main content tabs"""
        tab_names = [
            "👥 Current Squad",
            "📊 Performance Analysis", 
            "💡 Recommendations",
            "⭐ Starting XI Optimizer",
            "🤖 AI Insights",
            "📈 Historical Performance",
            "🏆 Mini-League",
            "🏥 Team Health",
            "🎯 SWOT Analysis",
            "📊 Advanced Analytics",
            "🔄 Transfer Planning",
            "📋 Performance Comparison",
            "⚽ Fixture Analysis"
        ]
        
        tabs = st.tabs(tab_names)
        
        # Render each tab with error handling
        tab_handlers = [
            lambda: self._render_squad_tab(team_data),
            lambda: self._render_performance_tab(team_data),
            lambda: self._render_recommendations_tab(team_data),
            lambda: self._render_optimizer_tab(team_data),
            lambda: self._render_ai_insights_tab(team_data),
            lambda: self._render_historical_performance_tab(team_data),
            lambda: self._render_mini_league_tab(team_data),
            lambda: self._render_team_health_tab(team_data),
            lambda: self._render_swot_tab(team_data),
            lambda: self._render_advanced_analytics_tab(team_data),
            lambda: self._render_transfer_planning_tab(team_data),
            lambda: self._render_performance_comparison_tab(team_data),
            lambda: self._render_fixture_analysis_tab(team_data)
        ]
        
        for i, (tab, handler) in enumerate(zip(tabs, tab_handlers)):
            with tab:
                try:
                    handler()
                except Exception as e:
                    logger.error(f"Error in tab {i}: {str(e)}")
                    st.error(f"Error loading tab content: {str(e)}")
    
    def _render_squad_tab(self, team_data):
        """Render current squad tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Loading player data to display squad details...")
            return
        
        players_df = st.session_state.players_df
        self.squad_analysis.render_current_squad(team_data, players_df)
    
    def _render_performance_tab(self, team_data):
        """Render performance analysis tab"""
        self.performance_analysis.render_performance_analysis(team_data)
    
    def _render_recommendations_tab(self, team_data):
        """Render recommendations tab"""
        self.team_recommendations.render_recommendations(team_data)
    
    def _render_optimizer_tab(self, team_data):
        """Render Starting XI optimizer tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("⚠️ Please load FPL player data first to enable the Starting XI Optimizer")
            return
        
        players_df = st.session_state.players_df
        self.starting_xi_optimizer.render_optimizer(team_data, players_df)
    
    def _render_swot_tab(self, team_data):
        """Render SWOT analysis tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Load player data to enable detailed SWOT analysis")
            return
        
        players_df = st.session_state.players_df
        self.swot_analysis.render_swot_analysis(team_data, players_df)
    
    def _render_advanced_analytics_tab(self, team_data):
        """Render advanced analytics tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Load player data to enable advanced analytics")
            return
        
        players_df = st.session_state.players_df
        self.advanced_analytics.render_advanced_analytics(team_data, players_df)
    
    def _render_transfer_planning_tab(self, team_data):
        """Render transfer planning tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Load player data to enable transfer planning")
            return
        
        players_df = st.session_state.players_df
        self.transfer_planning.render_transfer_planning(team_data, players_df)
    
    def _render_performance_comparison_tab(self, team_data):
        """Render performance comparison tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Load player data to enable performance comparison")
            return
        
        players_df = st.session_state.players_df
        self.performance_comparison.render_performance_comparison(team_data, players_df)
    
    def _render_fixture_analysis_tab(self, team_data):
        """Render fixture analysis tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Load player data to enable detailed fixture analysis")
            return
        
        players_df = st.session_state.players_df
        self.fixture_analysis.render_fixture_analysis(team_data, players_df)
    
    def _render_historical_performance_tab(self, team_data):
        """Render historical performance analysis tab"""
        try:
            self.historical_performance.render_historical_analysis(team_data)
        except Exception as e:
            logger.error(f"Error in historical performance tab: {str(e)}")
            st.error("⚠️ Historical performance analysis unavailable. This feature requires extended team data.")
            st.info("💡 This tab will show points trends, value changes, transfer history, and league position tracking once more data is available.")
    
    def _render_mini_league_tab(self, team_data):
        """Render mini-league analysis tab"""
        try:
            self.mini_league.render_mini_league_analysis(team_data)
        except Exception as e:
            logger.error(f"Error in mini-league tab: {str(e)}")
            st.error("⚠️ Mini-league analysis unavailable. This feature requires league data.")
            st.info("💡 This tab will show league standings, head-to-head records, recent form comparison, and captain analysis once league data is connected.")
    
    def _render_team_health_tab(self, team_data):
        """Render team health analysis tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Load player data to enable team health analysis")
            return
        
        try:
            players_df = st.session_state.players_df
            self.team_health.render_team_health(team_data, players_df)
        except Exception as e:
            logger.error(f"Error in team health tab: {str(e)}")
            st.error("⚠️ Team health analysis encountered an error.")
            st.info("💡 This tab provides player fitness status, financial health, strategy analysis, and risk assessment.")
    
    def _render_ai_insights_tab(self, team_data):
        """Render AI insights analysis tab"""
        if not st.session_state.get('data_loaded', False):
            st.warning("Load player data to enable AI insights")
            return
        
        try:
            players_df = st.session_state.players_df
            self.ai_insights.render_ai_insights(team_data, players_df)
        except Exception as e:
            logger.error(f"Error in AI insights tab: {str(e)}")
            st.error("⚠️ AI insights analysis encountered an error.")
            st.info("💡 This tab provides smart recommendations, predictive analysis, success probability, and pattern recognition.")
    
    def _render_reload_option(self):
        """Render reload option in sidebar"""
        st.sidebar.button(
            "🔄 Load Different Team",
            on_click=self._reset_team_state,
            help="Clear current team data and load a different team"
        )
    
    def _reset_team_state(self):
        """Reset all team-related session state"""
        keys_to_clear = [
            'fpl_team_loaded', 'fpl_team_id', 'fpl_team_data', 
            'fpl_team_gameweek'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
