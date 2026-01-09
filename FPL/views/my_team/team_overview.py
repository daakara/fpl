"""
Team Overview Component - Displays team summary and key metrics
"""
import streamlit as st
from .base_component import BaseTeamComponent


class TeamOverviewComponent(BaseTeamComponent):
    """Component for displaying team overview"""
    
    def render(self, team_data: dict):
        """Render team overview section"""
        if not self.validate_team_data(team_data):
            st.error("❌ Invalid team data provided")
            return
        
        try:
            st.subheader("📊 Team Overview")
            
            # Team basic info
            entry_name = team_data.get('entry_name', 'Unknown Team')
            st.write(f"**Team Name:** {entry_name}")
            
            # Key metrics in columns
            self._render_key_metrics(team_data)
            
            # Additional team info
            self._render_additional_info(team_data)
            
        except Exception as e:
            self.handle_error(e, "Team Overview")
    
    def _render_key_metrics(self, team_data):
        """Render key performance metrics"""
        try:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                overall_points = team_data.get('summary_overall_points', 0)
                st.metric(
                    label="Overall Points",
                    value=f"{overall_points:,}",
                    help="Total points accumulated this season"
                )
            
            with col2:
                overall_rank = team_data.get('summary_overall_rank', 0)
                st.metric(
                    label="Overall Rank",
                    value=f"{overall_rank:,}",
                    help="Current position among all FPL managers"
                )
            
            with col3:
                event_points = team_data.get('summary_event_points', 0)
                event_rank = team_data.get('summary_event_rank', 0)
                st.metric(
                    label="GW Points",
                    value=f"{event_points}",
                    help=f"Points from latest gameweek (Rank: {event_rank:,})"
                )
            
            with col4:
                team_value = team_data.get('value', 0) / 10  # Convert to millions
                bank = team_data.get('bank', 0) / 10  # Convert to millions
                st.metric(
                    label="Team Value",
                    value=f"£{team_value:.1f}M",
                    help=f"Squad value (Bank: £{bank:.1f}M)"
                )
                
        except Exception as e:
            self.logger.error(f"Error rendering key metrics: {str(e)}")
            st.error("Error displaying team metrics")
    
    def _render_additional_info(self, team_data):
        """Render additional team information"""
        try:
            st.divider()
            
            # Team composition
            picks = team_data.get('picks', [])
            if picks:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Squad Information:**")
                    st.write(f"• Total Players: {len(picks)}")
                    
                    # Captain info
                    captain = next((p for p in picks if p.get('is_captain')), None)
                    vice_captain = next((p for p in picks if p.get('is_vice_captain')), None)
                    
                    if captain:
                        st.write(f"• Captain: Player ID {captain.get('element')}")
                    if vice_captain:
                        st.write(f"• Vice Captain: Player ID {vice_captain.get('element')}")
                
                with col2:
                    st.write("**Latest Gameweek:**")
                    gameweek = team_data.get('gameweek', self.get_session_data('my_team_gameweek', 'Unknown'))
                    st.write(f"• Gameweek: {gameweek}")
                    
                    # Transfers info if available
                    if 'event_transfers' in team_data:
                        transfers = team_data.get('event_transfers', 0)
                        st.write(f"• Transfers Made: {transfers}")
                    
                    if 'event_transfers_cost' in team_data:
                        transfer_cost = team_data.get('event_transfers_cost', 0)
                        st.write(f"• Transfer Cost: {transfer_cost} pts")
        
        except Exception as e:
            self.logger.error(f"Error rendering additional info: {str(e)}")
            st.warning("Some team information could not be displayed")
    
    def render_team_status(self, team_data):
        """Render team loading status"""
        if not team_data:
            st.info("👋 Welcome! Import your FPL team to get started with detailed analysis.")
            return False
        
        if not self.validate_team_data(team_data):
            st.warning("⚠️ Team data is incomplete. Try reloading your team.")
            return False
        
        return True
