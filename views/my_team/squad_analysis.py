"""
Squad Analysis Component - Displays current squad details and analysis
"""
import streamlit as st
import pandas as pd
from .base_component import BaseTeamComponent


class SquadAnalysisComponent(BaseTeamComponent):
    """Component for analyzing current squad"""
    
    def render(self, team_data):
        """Render current squad analysis"""
        if not self.validate_team_data(team_data):
            st.error("❌ Invalid team data")
            return
        
        if not self.validate_player_data():
            st.warning("⚠️ Player data not available. Please ensure data is loaded.")
            return
        
        try:
            st.subheader("👥 Current Squad Analysis")
            
            # Get squad data
            squad_data = self._get_squad_data(team_data)
            if squad_data.empty:
                st.warning("No squad data available")
                return
            
            # Display squad overview
            self._render_squad_overview(squad_data, team_data)
            
            # Display detailed squad table
            self._render_squad_table(squad_data)
            
            # Squad insights
            self._render_squad_insights(squad_data)
            
        except Exception as e:
            self.handle_error(e, "Squad Analysis")
    
    def _get_squad_data(self, team_data):
        """Get squad data with player details"""
        try:
            picks = team_data.get('picks', [])
            players_df = self.get_session_data('players_df')
            
            if not picks or players_df is None:
                return pd.DataFrame()
            
            # Create squad dataframe
            squad_list = []
            for pick in picks:
                player_id = pick.get('element')
                player = players_df[players_df['id'] == player_id]
                
                if not player.empty:
                    player_data = player.iloc[0].to_dict()
                    player_data.update({
                        'position_in_squad': pick.get('position'),
                        'is_captain': pick.get('is_captain', False),
                        'is_vice_captain': pick.get('is_vice_captain', False),
                        'multiplier': pick.get('multiplier', 1)
                    })
                    squad_list.append(player_data)
            
            return pd.DataFrame(squad_list)
            
        except Exception as e:
            self.logger.error(f"Error getting squad data: {str(e)}")
            return pd.DataFrame()
    
    def _render_squad_overview(self, squad_data, team_data):
        """Render squad overview metrics"""
        try:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_value = squad_data['now_cost'].sum() / 10
                st.metric("Squad Value", f"£{total_value:.1f}M")
            
            with col2:
                total_points = squad_data['total_points'].sum()
                st.metric("Total Points", f"{total_points:,}")
            
            with col3:
                avg_form = squad_data['form'].astype(float).mean()
                st.metric("Avg Form", f"{avg_form:.1f}")
            
            with col4:
                bank = team_data.get('bank', 0) / 10
                st.metric("Bank", f"£{bank:.1f}M")
                
        except Exception as e:
            self.logger.error(f"Error rendering squad overview: {str(e)}")
    
    def _render_squad_table(self, squad_data):
        """Render detailed squad table"""
        try:
            st.subheader("📋 Squad Details")
            
            # Prepare display data
            display_data = squad_data.copy()
            
            # Format key columns
            display_data['Cost'] = display_data['now_cost'].apply(lambda x: f"£{x/10:.1f}M")
            display_data['Points'] = display_data['total_points']
            display_data['Form'] = display_data['form'].astype(float).round(1)
            display_data['Selected %'] = display_data['selected_by_percent'].astype(float).round(1)
            
            # Add captain indicators
            display_data['Role'] = display_data.apply(self._get_player_role, axis=1)
            
            # Select columns to display
            columns_to_show = [
                'web_name', 'position_name', 'team_short_name', 
                'Cost', 'Points', 'Form', 'Selected %', 'Role'
            ]
            
            # Filter and display
            table_data = display_data[columns_to_show].copy()
            table_data.columns = ['Player', 'Position', 'Team', 'Cost', 'Points', 'Form', 'Owned %', 'Role']
            
            # Sort by position
            position_order = {'Goalkeeper': 1, 'Defender': 2, 'Midfielder': 3, 'Forward': 4}
            table_data['pos_order'] = table_data['Position'].map(position_order)
            table_data = table_data.sort_values('pos_order').drop('pos_order', axis=1)
            
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            self.logger.error(f"Error rendering squad table: {str(e)}")
            st.error("Error displaying squad table")
    
    def _get_player_role(self, row):
        """Get player role (Captain, Vice-Captain, or blank)"""
        if row.get('is_captain'):
            return "🔥 Captain"
        elif row.get('is_vice_captain'):
            return "⚡ Vice-Captain"
        else:
            return ""
    
    def _render_squad_insights(self, squad_data):
        """Render squad insights and analysis"""
        try:
            st.subheader("🔍 Squad Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Position Breakdown:**")
                position_counts = squad_data['position_name'].value_counts()
                for position, count in position_counts.items():
                    st.write(f"• {position}: {count} players")
                
                # Team distribution
                st.write("**Team Distribution:**")
                team_counts = squad_data['team_short_name'].value_counts()
                top_teams = team_counts.head(5)
                for team, count in top_teams.items():
                    st.write(f"• {team}: {count} players")
            
            with col2:
                st.write("**Performance Insights:**")
                
                # Top performers
                top_scorer = squad_data.loc[squad_data['total_points'].idxmax()]
                st.write(f"• Top Scorer: {top_scorer['web_name']} ({top_scorer['total_points']} pts)")
                
                # Best form
                best_form = squad_data.loc[squad_data['form'].astype(float).idxmax()]
                st.write(f"• Best Form: {best_form['web_name']} ({best_form['form']})")
                
                # Most valuable
                most_expensive = squad_data.loc[squad_data['now_cost'].idxmax()]
                st.write(f"• Most Expensive: {most_expensive['web_name']} (£{most_expensive['now_cost']/10:.1f}M)")
                
                # Captain choice analysis
                captain = squad_data[squad_data['is_captain'] == True]
                if not captain.empty:
                    cap_points = captain.iloc[0]['total_points']
                    st.write(f"• Captain Points: {cap_points} pts")
                
        except Exception as e:
            self.logger.error(f"Error rendering squad insights: {str(e)}")
            st.warning("Some insights could not be displayed")
