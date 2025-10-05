"""
Team Import Component - Handles FPL team import functionality
"""
import streamlit as st
from utils.error_handling import logger


class TeamImportComponent:
    """Handles team import functionality"""
    
    def __init__(self, data_service):
        self.data_service = data_service
    
    def render(self):
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
            default_team_id = st.session_state.get('fpl_team_id', '') or ""
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
                    return self._load_team_data(team_id.strip(), selected_gw)
                else:
                    st.warning("⚠️ Please enter a valid team ID")
            
            # Add a quick test button
            if st.button("🧪 Quick Test", help="Test with team ID 1437667"):
                logger.info("User clicked Quick Test button")
                return self._load_team_data("1437667", 7)
        
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
        
        return False
    
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
