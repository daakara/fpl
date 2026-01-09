"""
Page R        self.pages = {
            "🏠 Dashboard": "dashboard",
            "👥 Player Analysis": "player_analysis", 
            "🎯 Fixture Difficulty": "fixture_difficulty",
            "👤 My FPL Team": "my_fpl_team",
            "🤖 AI Recommendations": "ai_recommendations",
            "⚽ Team Builder": "team_builder",
        }Handles navigation and sidebar
"""
import streamlit as st
import pandas as pd


class PageRouter:
    """Handles page routing and navigation"""
    
    def __init__(self):
        self.pages = {
            "🏠 Dashboard": "dashboard",
            "👥 Player Analysis": "player_analysis", 
            "🎯 Fixture Difficulty": "fixture_difficulty",
            "👤 My FPL Team": "my_fpl_team",
            "🤖 AI Recommendations": "ai_recommendations",
            "⚽ Team Builder": "team_builder",
        }
        
    def render_sidebar(self):
        """Render sidebar navigation and data controls"""
        st.sidebar.title("⚽ FPL Analytics")
        st.sidebar.markdown("---")
        
        # Initialize current page in session state if not exists
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "dashboard" # Use the ID, not the label
        
        # Get the list of page names and find the current index
        page_names = list(self.pages.keys())
        current_page = st.session_state.current_page
        current_index = page_names.index(current_page) if current_page in page_names else 0
        
        # Navigation
        selected_page = st.sidebar.selectbox(
            "Navigate to:",
            page_names,
            index=current_index,
            key="page_selector"
        )
        
        # Only update if page actually changed
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
        
        st.sidebar.markdown("---")
        
        # Data status
        self._render_data_status()
        
        # Data controls
        self._render_data_controls()
        
        return self.pages[selected_page]
    
    def _render_data_status(self):
        """Render data loading status"""
        if st.session_state.get('data_loaded', False):
            st.sidebar.success("✅ Data Loaded")
            if not st.session_state.get('players_df', pd.DataFrame()).empty:
                player_count = len(st.session_state.players_df)
                st.sidebar.info(f"📊 {player_count} players loaded")
        else:
            st.sidebar.warning("⚠️ No data loaded")
        

    
    def _render_data_controls(self):
        """Render data loading controls"""
        if st.sidebar.button("🔄 Refresh Data", type="primary"):
            self._load_data()
        
        # Additional controls can be added here
        if st.sidebar.button("🧹 Clear Cache"):
            self._clear_cache()
    
    def _load_data(self):
        """Load FPL data"""
        with st.spinner("Loading FPL data..."):
            try:
                from services.fpl_data_service import FPLDataService
                data_service = FPLDataService()
                players_df, teams_df = data_service.load_fpl_data()
                
                if not players_df.empty:
                    st.session_state.players_df = players_df
                    st.session_state.teams_df = teams_df
                    st.session_state.data_loaded = True
                    st.sidebar.success("✅ Data refreshed successfully!")
                else:
                    st.sidebar.error("❌ Failed to load data")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading data: {str(e)}")
    
    def _clear_cache(self):
        """Clear all cached data"""
        keys_to_clear = [
            'data_loaded', 'players_df', 'teams_df', 
            'fdr_data_loaded', 'fixtures_df'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.sidebar.success("🧹 Cache cleared!")
