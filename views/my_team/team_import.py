"""
Team Import Component - Handles team ID input and data loading
"""
import streamlit as st
from .base_component import BaseTeamComponent


class TeamImportComponent(BaseTeamComponent):
    """Component for importing FPL team data"""
    
    def render(self):
        """Render team import interface"""
        self.logger.info("Rendering team import section")
        st.subheader("📥 Import Your FPL Team")
        
        # Add helpful info
        st.info("👋 Enter your FPL Team ID below to analyze your team performance and get AI-powered recommendations!")
        
        # Create columns with error handling
        try:
            col1, col2 = st.columns([2, 1])
        except Exception as e:
            self.logger.error(f"Error creating columns: {str(e)}")
            # Fallback to no columns if there's an issue
            col1 = st.container()
            col2 = st.container()
        
        with col1:
            # Use stored team ID if available
            default_team_id = self.get_session_data('my_team_id', "")
            team_id = st.text_input(
                "Enter your FPL Team ID:",
                value=default_team_id,
                placeholder="e.g., 1234567",
                help="Find your team ID in your FPL team URL"
            )
            
            # Get current gameweek for selection
            selected_gw = self._render_gameweek_selector()
        
        with col2:
            st.write("")  # Add some spacing
            st.write("")  # Add some spacing
            
            if st.button("🔄 Load My Team", type="primary", use_container_width=True):
                if team_id and team_id.strip():
                    self.logger.info(f"User clicked Load Team button with ID: {team_id}")
                    self._load_team_data(team_id.strip(), selected_gw)
                else:
                    st.warning("⚠️ Please enter a valid team ID")
            
            # Add a quick test button
            if st.button("🧪 Quick Test", help="Test with team ID 1437667"):
                self.logger.info("User clicked Quick Test button")
                self._load_team_data("1437667", 7)
        
        # Instructions
        self._render_instructions()
    
    def _render_gameweek_selector(self):
        """Render gameweek selection dropdown"""
        try:
            current_gw = self.data_service.get_current_gameweek()
            if not current_gw or current_gw < 1:
                current_gw = 8  # Default to gameweek 8
            gameweeks = list(range(1, min(current_gw + 1, 39)))
        except Exception as e:
            self.logger.error(f"Error getting current gameweek: {str(e)}")
            current_gw = 8
            gameweeks = list(range(1, 39))
        
        selected_gw = st.selectbox(
            "Select Gameweek:",
            gameweeks,
            index=min(max(current_gw - 1, 0), len(gameweeks) - 1),
            help="Choose which gameweek's team to analyze"
        )
        
        return selected_gw
    
    def _render_instructions(self):
        """Render helpful instructions"""
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
                if not self.get_session_data('data_loaded', False):
                    self.logger.info("Loading player data first...")
                    players_df, teams_df = self.data_service.load_fpl_data()
                    if not players_df.empty:
                        self.set_session_data('players_df', players_df)
                        self.set_session_data('teams_df', teams_df)
                        self.set_session_data('data_loaded', True)
                        self.logger.info("Successfully loaded player data")
                
                # Now load team data
                self.logger.info(f"Loading team data for ID: {team_id}")
                team_data = self.data_service.load_team_data(team_id, gameweek)
                
                if team_data and isinstance(team_data, dict):
                    # Check if picks data is available
                    picks = team_data.get('picks', [])
                    if not picks:
                        # Try previous gameweeks if current one has no picks
                        st.warning(f"No squad data found for gameweek {gameweek}. Trying previous gameweeks...")
                        team_data = self._try_previous_gameweeks(team_id, gameweek)
                    
                    if not team_data or not team_data.get('picks'):
                        raise ValueError("No squad data available for this team in recent gameweeks")
                    
                    self.logger.info("Team data loaded successfully")
                    
                    # Set all session state at once
                    self._update_session_state(team_data, team_id, gameweek)
                    
                    st.success("✅ Team data loaded successfully!")
                    st.rerun()
                    
                else:
                    st.error("❌ Failed to load team data. Please check your team ID and try again.")
                    
        except Exception as e:
            error_msg = f"Error loading team data: {str(e)}"
            self.logger.error(error_msg)
            st.error(f"❌ {error_msg}")
    
    def _try_previous_gameweeks(self, team_id, start_gameweek):
        """Try to load team data from previous gameweeks"""
        for try_gw in range(start_gameweek - 1, max(0, start_gameweek - 5), -1):
            if try_gw < 1:
                break
            st.write(f"Trying gameweek {try_gw}...")
            try:
                alt_team_data = self.data_service.load_team_data(team_id, try_gw)
                if alt_team_data and alt_team_data.get('picks'):
                    st.success(f"Found squad data in gameweek {try_gw}!")
                    return alt_team_data
            except Exception as e:
                st.write(f"GW {try_gw}: {str(e)}")
                continue
        
        return None
    
    def _update_session_state(self, team_data, team_id, gameweek):
        """Update session state with team data"""
        session_updates = {
            'my_team_data': team_data,
            'my_team_id': team_id,
            'my_team_gameweek': gameweek,
            'my_team_loaded': True,
            'current_page': "👤 My FPL Team"
        }
        
        for key, value in session_updates.items():
            self.set_session_data(key, value)
        
        self.logger.info(f"Successfully loaded and stored team data for ID: {team_id}")
        
        # Display quick summary
        entry_name = team_data.get('entry_name', 'Unknown Team')
        overall_points = team_data.get('summary_overall_points', 0)
        overall_rank = team_data.get('summary_overall_rank', 0)
        
        st.info(f"""
        **Team Loaded:** {entry_name}
        **Overall Points:** {overall_points:,}
        **Overall Rank:** {overall_rank:,}
        **Players:** {len(team_data.get('picks', []))}
        """)
        
    def render_debug_section(self):
        """Render debug information section"""
        st.write("🔍 **Debug Info:**")
        st.write(f"- Team loaded: {self.get_session_data('my_team_loaded', False)}")
        st.write(f"- Data loaded: {self.get_session_data('data_loaded', False)}")
        st.write(f"- Team ID: {self.get_session_data('my_team_id', 'None')}")
        st.write(f"- Page render started successfully ✅")
    
    def render_quick_test(self):
        """Render quick test button"""
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
                        self._update_session_state(team_data, test_team_id, gw)
                        st.rerun()
                        break
                    else:
                        st.write(f"❌ GW {gw}: No picks data")
                except Exception as e:
                    st.write(f"❌ GW {gw}: {str(e)}")
