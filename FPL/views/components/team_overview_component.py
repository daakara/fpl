"""
Team Overview Component - Displays team basic information and metrics
"""
import streamlit as st
from utils.error_handling import logger


class TeamOverviewComponent:
    """Handles team overview display"""
    
    def render(self, team_data: dict):
        """Render the team overview section"""
        try:
            # Team header with name and ID
            team_name = team_data.get('entry_name', 'Your Team')
            team_id = st.session_state.my_team_id
            st.subheader(f"🏆 {team_name} (ID: {team_id})")
            
            # Key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                rank = team_data.get('summary_overall_rank', 'N/A')
                if isinstance(rank, (int, float)):
                    st.metric("Overall Rank", f"{rank:,}")
                else:
                    st.metric("Overall Rank", "N/A")
            
            with col2:
                points = team_data.get('summary_overall_points', 'N/A')
                if isinstance(points, (int, float)):
                    st.metric("Total Points", f"{points:,}")
                else:
                    st.metric("Total Points", "N/A")
            
            with col3:
                gw_rank = team_data.get('summary_event_rank', 'N/A')
                if isinstance(gw_rank, (int, float)):
                    st.metric("Gameweek Rank", f"{gw_rank:,}")
                else:
                    st.metric("Gameweek Rank", "N/A")
            
            with col4:
                value = team_data.get('value', 1000)
                st.metric("Team Value", f"£{value/10:.1f}m")
            
            st.divider()
            
        except Exception as e:
            logger.error(f"Error rendering team overview: {str(e)}")
            st.error("Error displaying team overview")
