"""
Squad Analysis Component - Handles current squad display and analysis
"""
import streamlit as st
import pandas as pd
from utils.error_handling import logger


class SquadAnalysisComponent:
    """Handles squad analysis and display"""
    
    def render_current_squad(self, team_data, players_df):
        """Display current squad with player details"""
        st.subheader("👥 Current Squad")
        
        picks = team_data.get('picks', [])
        if not picks:
            st.warning("No squad data available")
            return
        
        # Match picks with player data
        squad_data = []
        formation_counts = {'Goalkeeper': 0, 'Defender': 0, 'Midfielder': 0, 'Forward': 0}
        
        for pick in picks:
            player_info = players_df[players_df['id'] == pick['element']]
            if not player_info.empty:
                player = player_info.iloc[0]
                position = player.get('position_name', 'Unknown')
                
                # Count for formation
                if position in formation_counts:
                    formation_counts[position] += 1
                
                squad_data.append({
                    'Player': player.get('web_name', 'Unknown'),
                    'Position': position,
                    'Team': player.get('team_short_name', 'UNK'),
                    'Price': f"£{player.get('cost_millions', 0):.1f}m",
                    'Points': player.get('total_points', 0),
                    'Form': f"{player.get('form', 0):.1f}",
                    'Status': '(C)' if pick.get('is_captain') else '(VC)' if pick.get('is_vice_captain') else '',
                    'Playing': '✅' if pick.get('position', 12) <= 11 else '🪑'
                })
        
        if squad_data:
            # Formation display
            formation_str = f"{formation_counts['Goalkeeper']}-{formation_counts['Defender']}-{formation_counts['Midfielder']}-{formation_counts['Forward']}"
            st.info(f"**Formation:** {formation_str}")
            
            # Squad table
            squad_df = pd.DataFrame(squad_data)
            st.dataframe(
                squad_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Price": st.column_config.TextColumn("Price"),
                    "Points": st.column_config.NumberColumn("Points"),
                    "Form": st.column_config.TextColumn("Form"),
                    "Playing": st.column_config.TextColumn("Starting?")
                }
            )
            
            # Squad statistics
            self._display_squad_statistics(squad_data)
    
    def _display_squad_statistics(self, squad_data):
        """Display squad statistics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value = sum([float(row['Price'].replace('£', '').replace('m', '')) for row in squad_data])
            st.metric("Squad Value", f"£{total_value:.1f}m")
        
        with col2:
            total_points = sum([row['Points'] for row in squad_data])
            st.metric("Total Points", f"{total_points:,}")
        
        with col3:
            avg_form = sum([float(row['Form']) for row in squad_data]) / len(squad_data)
            st.metric("Average Form", f"{avg_form:.1f}")
        
        with col4:
            starting_players = len([row for row in squad_data if row['Playing'] == '✅'])
            st.metric("Starting XI", f"{starting_players}/11")
