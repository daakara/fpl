"""
Enhanced Application Controller with Modern Features
Clean Application Controller - Focuses on state management and routing.
"""
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime
from utils.modern_ui_components import ModernUIComponents, DataVisualization, render_loading_spinner, create_success_animation
from components.ui.navigation import UnifiedNavigation, navigation
import time

from views.player_analysis_page import PlayerAnalysisPage
from views.fixture_analysis_page import FixtureAnalysisPage
from views.dashboard_page import DashboardPage
from views.my_team_page import MyTeamPage
from views.team_builder_page import TeamBuilderPage
from components.ui.navigation import UnifiedNavigation
from utils.enhanced_cache import display_cache_metrics, cached_load_fpl_data
from utils.error_handling import handle_errors, logger, perf_monitor
from config.app_config import config

# New page imports
from views.ai_recommendations_page import AIRecommendationsPage
from services.fpl_data_service import FPLDataService

import time


class EnhancedFPLAppController:
    """Enhanced application controller with modern features and performance monitoring"""
    

    def __init__(self):
        """Initialize the application controller."""
        logger.info("Setting up page configuration...")
        self.setup_page_config()        

        logger.info("Initializing core services...")
        self.initialize_services()
        
        logger.info("Setting up UI components...")
        self.ui_components = ModernUIComponents()        

        logger.info("Initializing navigation...")
        self.navigation = UnifiedNavigation()
        
        logger.info("Initializing session state...")
        self.initialize_session_state()        
        
        # Initialize pages after navigation
        logger.info("Initializing pages...")
        self.initialize_pages()
        logger.info("Application controller initialization complete")
            

    def initialize_pages(self):
        """Initialize page components"""
        try:
            # Get data from session state to pass to pages
            players_df = st.session_state.get('players_df')
            teams_df = st.session_state.get('teams_df')
            
            # Pre-initialize page instances
            # We now pass the dataframes to each page during initialization.
            # This makes the pages more self-contained and easier to test.
            self.player_analysis = PlayerAnalysisPage()
            self.fixture_analysis = FixtureAnalysisPage()
            self.dashboard = DashboardPage()
            self.my_team = MyTeamPage()
            self.ai_recommendations = AIRecommendationsPage()
            self.team_builder = TeamBuilderPage()
            
            # Map pages to their render methods
            self.pages = {
                "dashboard": self.dashboard.render,
                "player_analysis": self.player_analysis.render,
                "fixture_difficulty": self.fixture_analysis.render,
                "my_fpl_team": self.my_team.render,
                "ai_recommendations": self.ai_recommendations.render,
                "team_builder": self.team_builder.render
            }
            
            logger.info(f"Successfully initialized {len(self.pages)} pages")
            
        except Exception as e:
            logger.error(f"Error initializing pages: {str(e)}", exc_info=True)
            raise

    def initialize_services(self):
        """Initialize core services with proper error handling"""
        try:
            from services.fpl_data_service import FPLDataService
            
            logger.info("Creating FPL Data Service instance...")
            self.data_service = FPLDataService()
            
            logger.info("Testing data service connection...")
            # Try to make a simple API call to test connection
            try:
                self.data_service.test_connection()
                logger.info("Data service connection test successful")
            except Exception as conn_err:
                logger.warning(f"Initial data service connection test failed: {str(conn_err)}. The app will continue to load.")
                # Don't raise an error, allow the app to start.
                # The user can try to refresh data from the UI.
                
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}", exc_info=True)
            raise
    
    def setup_page_config(self):
        """Setup enhanced Streamlit page configuration"""
        st.set_page_config(
            page_title=config.ui.page_title,
            page_icon=config.ui.page_icon,
            layout=config.ui.layout,
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': None
            }
        )
        
        # Global styles are now applied once in main_modular.py
        pass
    
    def initialize_session_state(self):
        """Initialize session state with default values"""
        try:
            default_state = {
                'nav_selection': 'dashboard',
                'data_loaded': False,
                'last_update': None,
                'players_df': None,
                'teams_df': None,
                'error_state': None,
                'loading_state': False,

                'feature_flags': {
                    'ai_recommendations': True,
                    'advanced_analytics': True,
                    'real_time_updates': False,
                    'export_features': True
                },
                'performance_metrics': {
                    'page_loads': 0,
                    'data_refreshes': 0,
                    'errors': 0,
                    'session_start': time.time()
                }
            }
            
            # Set any uninitialized state values
            for key, default_value in default_state.items():
                if key not in st.session_state:
                    st.session_state[key] = default_value
            if 'current_page' not in st.session_state: # This was incorrectly placed in initialize_pages
                st.session_state.current_page = "🏠 Dashboard"
            
        except Exception as e:
            logger.error(f"Failed to initialize session state: {str(e)}", exc_info=True)
            raise

    def _render_navigation(self):
        """Renders the sidebar navigation using a selectbox for stable page routing."""
        """Renders a modern, icon-based sidebar navigation using streamlit-option-menu."""
        with st.sidebar:
            # Prepare items for the option_menu
            sorted_nav_items = sorted(
                [item for item in self.navigation.nav_items.values() if item.id in self.pages],
                key=lambda item: item.order
            )
            
            nav_labels = [item.label for item in sorted_nav_items]
            nav_icons = [item.icon for item in sorted_nav_items]
            nav_ids = [item.id for item in sorted_nav_items]

            # Determine the default index based on the current session state
            current_selection_id = st.session_state.get('nav_selection', 'dashboard')
            current_index = nav_ids.index(current_selection_id) if current_selection_id in nav_ids else 0

            # Create the new navigation menu
            selected_label = option_menu(
                menu_title="FPL Analytics",
                options=nav_labels,
                icons=nav_icons,
                menu_icon="⚽",
                default_index=current_index,
                # Safely get styles from config, provide None as a default
                # to prevent AttributeError if it's not defined.
                styles=getattr(config.ui, 'navigation_styles', None)
            )
            
            # Update session state based on the menu selection.
            # The component handles the click state, so we just need to sync our app state.
            selected_id = nav_ids[nav_labels.index(selected_label)]
            if st.session_state.nav_selection != selected_id:
                st.session_state.nav_selection = selected_id
                st.rerun()

            st.markdown("---")

            # Render data status and controls, similar to the old PageRouter
            self._render_data_status()
            self._render_data_controls()            

    def _render_data_status(self):
        """Render data loading status in the sidebar."""
        if st.session_state.get('data_loaded', False):
            st.sidebar.success("✅ Data Loaded")
            if st.session_state.get('players_df') is not None and not st.session_state.get('players_df').empty:
                player_count = len(st.session_state.players_df)
                st.sidebar.info(f"📊 {player_count} players loaded")
        else:
            st.sidebar.warning("⚠️ No data loaded")



    def _render_data_controls(self):
        """Render data loading controls in the sidebar."""
        if st.sidebar.button("🔄 Refresh Data", type="primary", use_container_width=True):
            self.handle_quick_action("refresh_data")

    def run(self):
        """Run the application with enhanced features and monitoring"""
        try:
            if 'page_loads' in st.session_state.performance_metrics:
                st.session_state.performance_metrics['page_loads'] += 1

            logger.debug(f"App run started. Current nav_selection: {st.session_state.get('nav_selection', 'dashboard')}")
            
            # Render navigation first
            logger.info("Rendering navigation...")
            self._render_navigation()
            
            # Get and validate current page
            current_page = st.session_state.get('nav_selection', 'dashboard')
            logger.info(f"Rendering page: {current_page}")
            
            # Render the selected page
            logger.debug(f"Attempting to render page '{current_page}' from self.pages.")
            if current_page in self.pages:
                with st.spinner(f"Loading {current_page}..."):
                    try:
                        page_renderer = self.pages[current_page]
                        if callable(page_renderer):
                            logger.info(f"Executing render method for '{current_page}'...")
                            page_renderer()  # Execute the render method
                        else:
                            logger.error(f"Page {current_page} renderer is not callable")
                            st.error("Page not properly configured")
                    except Exception as e: # This will now catch errors inside the page render methods
                        logger.error(f"Error rendering page '{current_page}': {str(e)}", exc_info=True)
                        st.error(f"An error occurred while loading the {current_page.replace('_', ' ')} page.")
            else:
                st.error(f"Page not found: {current_page}")            
                
        except Exception as e:
            logger.error(f"Error running application: {str(e)}", exc_info=True)
            st.error("An error occurred while running the application. Please check the logs.")
    
    def _create_placeholder_page(self, page_id: str):
        """Create a placeholder for unimplemented pages"""
        def placeholder():
            st.info(f"🚧 The {page_id} page is under construction. Check back soon!")
        return placeholder

    def handle_quick_action(self, action: str):
        """Handle quick action buttons"""
        if action == "refresh_data":
            with st.spinner("Refreshing data..."):
                try:
                    # Clear cache and reload
                    from utils.enhanced_cache import cache_manager
                    cache_manager.clear_cache()
                    players_df, teams_df = cached_load_fpl_data()
                    
                    if not players_df.empty:
                        st.session_state.players_df = players_df
                        st.session_state.teams_df = teams_df
                        st.session_state.data_loaded = True
                        st.session_state.performance_metrics['data_refreshes'] += 1
                        
                        logger.log_user_action("data_refresh", {"success": True})
                    else:
                        st.error("Failed to refresh data")
                        logger.log_user_action("data_refresh", {"success": False})
                except Exception as e:
                    st.error(f"Error refreshing data: {str(e)}")
                    logger.log_error(e, "data_refresh")
        elif action == "export_data":
            self.export_current_data()
        
        elif action == "settings":
            st.switch_page("settings")
    
    def display_debug_info(self):
        """Display debug information"""
        with st.sidebar.expander("🔧 Debug Info"):
            st.write("**Performance Metrics:**")
            st.json(self.performance_metrics)
            
            st.write("**Session State Keys:**")
            st.write(list(st.session_state.keys()))
            
            st.write("**Feature Flags:**")
            st.json(st.session_state.feature_flags)
    
    def render_footer(self):
        """Render application footer"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 20px;">
            <p>FPL Analytics Dashboard v2.0 | Built with ❤️ for FPL managers</p>
        </div>    
        """)
