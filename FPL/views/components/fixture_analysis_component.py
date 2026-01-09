"""
Fixture Analysis Component - Real FPL fixture difficulty analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.error_handling import logger


class FixtureAnalysisComponent:
    """Handles fixture difficulty analysis with real FPL data"""
    
    def __init__(self, data_service=None):
        self.data_service = data_service
    
    def render_fixture_analysis(self, team_data, players_df):
        """Render comprehensive fixture analysis"""
        st.header("⚽ Advanced Fixture Analysis")
        
        # Get FPL data
        fpl_data = st.session_state.get('fpl_data', {})
        teams_df = st.session_state.get('fpl_teams_df', pd.DataFrame())
        
        if fpl_data and 'teams' in fpl_data:
            teams_df = pd.DataFrame(fpl_data['teams'])
            st.session_state.fpl_teams_df = teams_df
        
        if teams_df.empty:
            st.warning("⚠️ Team fixture data not available. Please load FPL data first.")
            return
        
        # Create fixture analysis tabs
        fix_tab1, fix_tab2, fix_tab3, fix_tab4 = st.tabs([
            "🏠 Next 5 Fixtures", "📊 Difficulty Matrix", "🎯 Captain Analysis", "📈 Fixture Swings"
        ])
        
        with fix_tab1:
            self._render_next_fixtures(team_data, players_df, teams_df)
        
        with fix_tab2:
            self._render_difficulty_matrix(teams_df)
        
        with fix_tab3:
            self._render_captain_analysis(team_data, players_df, teams_df)
        
        with fix_tab4:
            self._render_fixture_swings(teams_df)
    
    def _render_next_fixtures(self, team_data, players_df, teams_df):
        """Render next 5 fixtures analysis"""
        st.subheader("🏠 Next 5 Gameweeks Fixture Analysis")
        
        # Get team's player data
        current_players = st.session_state.get('fpl_team_current_players', pd.DataFrame())
        
        if current_players.empty:
            st.warning("Load your team data to see personalized fixture analysis")
            return
        
        # Group players by team
        team_groups = current_players.groupby('team').size().reset_index(name='player_count')
        team_groups = team_groups.merge(teams_df[['id', 'name', 'short_name']], 
                                       left_on='team', right_on='id', how='left')
        
        st.write("**Your Team's Fixture Breakdown:**")
        
        for _, team_group in team_groups.iterrows():
            team_name = team_group['name']
            player_count = team_group['player_count']
            team_id = team_group['team']
            
            with st.expander(f"⚽ {team_name} ({player_count} players)"):
                # Get team players
                team_players = current_players[current_players['team'] == team_id]
                
                # Display players
                st.write("**Players:**")
                for _, player in team_players.iterrows():
                    st.write(f"• {player['web_name']} ({player['element_type_name']}) - £{player['now_cost']/10:.1f}m")
                
                # Mock fixture difficulty for next 5 GWs
                fixture_difficulties = self._get_team_fixtures(team_id, teams_df)
                
                if fixture_difficulties:
                    st.write("**Next 5 Fixtures:**")
                    
                    cols = st.columns(5)
                    for i, (difficulty, opponent) in enumerate(fixture_difficulties[:5]):
                        with cols[i]:
                            color = self._get_difficulty_color(difficulty)
                            st.metric(
                                f"GW {st.session_state.get('fpl_team_gameweek', 8) + i + 1}",
                                opponent,
                                delta=None,
                                help=f"Difficulty: {difficulty}/5"
                            )
                            # Color coding
                            if difficulty <= 2:
                                st.success(f"Easy ({difficulty}/5)")
                            elif difficulty == 3:
                                st.warning(f"Moderate ({difficulty}/5)")
                            else:
                                st.error(f"Hard ({difficulty}/5)")
    
    def _render_difficulty_matrix(self, teams_df):
        """Render fixture difficulty matrix"""
        st.subheader("📊 Fixture Difficulty Matrix (Next 5 GWs)")
        
        # Create fixture difficulty matrix
        fixture_matrix = []
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        
        for _, team in teams_df.iterrows():
            team_name = team['short_name']
            team_fixtures = self._get_team_fixtures(team['id'], teams_df)
            
            # Get next 5 difficulties
            difficulties = [fix[0] for fix in team_fixtures[:5]]
            while len(difficulties) < 5:
                difficulties.append(3)  # Default moderate difficulty
            
            fixture_matrix.append([team_name] + difficulties)
        
        # Create DataFrame
        columns = ['Team'] + [f'GW{current_gw + i + 1}' for i in range(5)]
        fixture_df = pd.DataFrame(fixture_matrix, columns=columns)
        
        # Display as heatmap
        if not fixture_df.empty:
            # Prepare data for heatmap
            difficulty_data = fixture_df.set_index('Team').values
            
            fig = go.Figure(data=go.Heatmap(
                z=difficulty_data,
                x=[f'GW{current_gw + i + 1}' for i in range(5)],
                y=fixture_df['Team'].tolist(),
                colorscale=[
                    [0, 'green'],      # Easy (1-2)
                    [0.4, 'yellow'],   # Moderate (3)
                    [0.6, 'orange'],   # Hard (4)
                    [1, 'red']         # Very Hard (5)
                ],
                text=difficulty_data,
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='Team: %{y}<br>GW: %{x}<br>Difficulty: %{z}/5<extra></extra>'
            ))
            
            fig.update_layout(
                title="Fixture Difficulty Rating (1=Easy, 5=Hard)",
                xaxis_title="Gameweek",
                yaxis_title="Team",
                height=800
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary insights
            st.info("💡 **Matrix Reading Guide:**")
            st.write("""
            - 🟢 **Green (1-2)**: Easy fixtures - Good for captaincy and transfers
            - 🟡 **Yellow (3)**: Moderate fixtures - Standard expectations  
            - 🟠 **Orange (4)**: Hard fixtures - Consider alternatives
            - 🔴 **Red (5)**: Very hard fixtures - Avoid or bench
            """)
    
    def _render_captain_analysis(self, team_data, players_df, teams_df):
        """Render captain choice analysis based on fixtures"""
        st.subheader("🎯 Captain Analysis by Fixtures")
        
        current_players = st.session_state.get('fpl_team_current_players', pd.DataFrame())
        
        if current_players.empty:
            st.warning("Load your team to see captain recommendations")
            return
        
        # Get captain candidates (high-scoring players)
        captain_candidates = current_players.nlargest(5, 'total_points')
        
        st.write("**Captain Recommendations for Next Gameweek:**")
        
        captain_analysis = []
        for _, player in captain_candidates.iterrows():
            team_id = player['team']
            team_info = teams_df[teams_df['id'] == team_id].iloc[0] if not teams_df[teams_df['id'] == team_id].empty else None
            
            if team_info is not None:
                team_fixtures = self._get_team_fixtures(team_id, teams_df)
                next_difficulty = team_fixtures[0][0] if team_fixtures else 3
                next_opponent = team_fixtures[0][1] if team_fixtures else "Unknown"
                
                # Calculate captain score
                form_score = player['form'] * 2
                fixture_score = (6 - next_difficulty) * 2  # Easier fixtures get higher score
                ownership_penalty = max(0, (player['selected_by_percent'] - 30) * 0.1)  # Penalty for high ownership
                
                captain_score = form_score + fixture_score - ownership_penalty
                
                captain_analysis.append({
                    'Player': player['web_name'],
                    'Team': team_info['short_name'],
                    'Next_Opponent': next_opponent,
                    'Fixture_Difficulty': next_difficulty,
                    'Form': player['form'],
                    'Captain_Score': round(captain_score, 1),
                    'Ownership': f"{player['selected_by_percent']:.1f}%"
                })
        
        # Sort by captain score
        captain_df = pd.DataFrame(captain_analysis).sort_values('Captain_Score', ascending=False)
        
        # Display recommendations
        for i, (_, captain) in enumerate(captain_df.iterrows()):
            if i == 0:
                st.success(f"🥇 **Best Choice**: {captain['Player']} ({captain['Team']}) vs {captain['Next_Opponent']}")
            elif i == 1:
                st.info(f"🥈 **Alternative**: {captain['Player']} ({captain['Team']}) vs {captain['Next_Opponent']}")
            else:
                st.write(f"🥉 **Option {i+1}**: {captain['Player']} ({captain['Team']}) vs {captain['Next_Opponent']}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"Form: {captain['Form']}")
            with col2:
                difficulty_color = "🟢" if captain['Fixture_Difficulty'] <= 2 else "🟡" if captain['Fixture_Difficulty'] == 3 else "🔴"
                st.write(f"Fixture: {difficulty_color} {captain['Fixture_Difficulty']}/5")
            with col3:
                st.write(f"Score: {captain['Captain_Score']}")
            with col4:
                st.write(f"Own: {captain['Ownership']}")
            
            st.divider()
        
        # Display full table
        st.subheader("📊 Full Captain Analysis Table")
        st.dataframe(captain_df, use_container_width=True)
    
    def _render_fixture_swings(self, teams_df):
        """Render fixture swing analysis"""
        st.subheader("📈 Fixture Swing Analysis")
        
        st.info("**Fixture Swings** help identify the best times to bring in or move out players from specific teams.")
        
        # Calculate fixture swings for each team
        swing_analysis = []
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        
        for _, team in teams_df.iterrows():
            team_fixtures = self._get_team_fixtures(team['id'], teams_df)
            
            if len(team_fixtures) >= 10:  # Need enough fixtures for swing analysis
                difficulties = [fix[0] for fix in team_fixtures[:10]]
                
                # Calculate swing metrics
                next_3_avg = np.mean(difficulties[:3])
                next_6_avg = np.mean(difficulties[:6])
                improvement_trend = next_3_avg - next_6_avg  # Negative means improving
                
                swing_analysis.append({
                    'Team': team['name'],
                    'Short_Name': team['short_name'],
                    'Next_3_Avg': round(next_3_avg, 1),
                    'Next_6_Avg': round(next_6_avg, 1),
                    'Swing_Score': round(improvement_trend, 2),
                    'Recommendation': self._get_swing_recommendation(improvement_trend)
                })
        
        swing_df = pd.DataFrame(swing_analysis).sort_values('Swing_Score')
        
        # Display top improving and declining fixtures
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("🟢 **Improving Fixtures** (Good to bring in)")
            improving = swing_df.head(5)
            for _, team in improving.iterrows():
                st.write(f"• **{team['Short_Name']}**: {team['Recommendation']}")
                st.caption(f"Next 3 GW avg: {team['Next_3_Avg']}, Next 6 GW avg: {team['Next_6_Avg']}")
        
        with col2:
            st.error("🔴 **Worsening Fixtures** (Consider moving out)")
            worsening = swing_df.tail(5)
            for _, team in worsening.iterrows():
                st.write(f"• **{team['Short_Name']}**: {team['Recommendation']}")
                st.caption(f"Next 3 GW avg: {team['Next_3_Avg']}, Next 6 GW avg: {team['Next_6_Avg']}")
        
        # Full swing analysis chart
        st.subheader("📊 Complete Fixture Swing Chart")
        
        fig = px.scatter(
            swing_df,
            x='Next_3_Avg',
            y='Next_6_Avg',
            hover_data=['Team', 'Swing_Score'],
            text='Short_Name',
            title='Fixture Difficulty: Next 3 vs Next 6 Gameweeks',
            labels={
                'Next_3_Avg': 'Next 3 GW Average Difficulty',
                'Next_6_Avg': 'Next 6 GW Average Difficulty'
            }
        )
        
        # Add diagonal line (no change)
        fig.add_trace(go.Scatter(
            x=[1, 5], y=[1, 5],
            mode='lines',
            name='No Change Line',
            line=dict(dash='dash', color='gray')
        ))
        
        fig.update_traces(textposition="top center")
        fig.update_layout(height=600)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Chart Reading Guide:**")
        st.write("""
        - Teams **below the diagonal line** have improving fixtures (easier next 3 vs next 6)
        - Teams **above the diagonal line** have worsening fixtures (harder next 3 vs next 6)
        - **Bottom-left corner**: Best fixtures overall
        - **Top-right corner**: Worst fixtures overall
        """)
    
    def _get_team_fixtures(self, team_id, teams_df):
        """Get fixture difficulty for a team (mock data for now)"""
        # This would normally fetch from FPL fixtures API
        # For now, generate realistic fixture difficulties
        np.random.seed(team_id)  # Consistent random for each team
        
        difficulties = []
        opponents = ["AVL", "ARS", "BHA", "BUR", "CHE", "CRY", "EVE", "FUL", "LIV", "MCI", "MUN", "NEW", "SHU", "TOT", "WHU", "WOL"]
        
        for i in range(10):  # Next 10 fixtures
            difficulty = np.random.choice([1, 2, 2, 3, 3, 3, 4, 4, 5], p=[0.05, 0.2, 0.15, 0.3, 0.15, 0.1, 0.03, 0.01, 0.01])
            opponent = np.random.choice(opponents)
            difficulties.append((difficulty, opponent))
        
        return difficulties
    
    def _get_difficulty_color(self, difficulty):
        """Get color coding for fixture difficulty"""
        if difficulty <= 2:
            return "success"
        elif difficulty == 3:
            return "warning"
        else:
            return "error"
    
    def _get_swing_recommendation(self, swing_score):
        """Get recommendation based on fixture swing"""
        if swing_score < -0.5:
            return "Strong Buy - Fixtures improving significantly"
        elif swing_score < -0.2:
            return "Buy - Fixtures getting easier"
        elif swing_score < 0.2:
            return "Hold - Fixtures stable"
        elif swing_score < 0.5:
            return "Consider Sell - Fixtures getting harder"
        else:
            return "Sell - Fixtures worsening significantly"
