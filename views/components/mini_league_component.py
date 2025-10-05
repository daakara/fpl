"""
Mini-League Performance Component - Compare with friends and mini-leagues
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.error_handling import logger


class MiniLeagueComponent:
    """Handles mini-league analysis and comparisons"""
    
    def __init__(self, data_service=None):
        self.data_service = data_service
    
    def render_mini_league_analysis(self, team_data):
        """Render mini-league analysis"""
        st.header("🏆 Mini-League Performance")
        
        team_name = team_data.get('entry_name', 'Unknown Team')
        st.info(f"📊 Comparing {team_name} with mini-league rivals")
        
        # Create tabs for different league views
        league_tab1, league_tab2, league_tab3, league_tab4 = st.tabs([
            "🏆 League Table", "📊 Head-to-Head", "⚡ Recent Form", "🎯 Captain Analysis"
        ])
        
        with league_tab1:
            self._render_league_table(team_data)
        
        with league_tab2:
            self._render_head_to_head(team_data)
        
        with league_tab3:
            self._render_recent_form(team_data)
        
        with league_tab4:
            self._render_captain_analysis(team_data)
    
    def _render_league_table(self, team_data):
        """Render mini-league table"""
        st.subheader("🏆 League Standings")
        
        # Sample mini-league data
        league_data = [
            {'Rank': 1, 'Manager': 'John Smith', 'Team': 'Arsenal Legends', 'Points': 654, 'GW_Points': 67},
            {'Rank': 2, 'Manager': 'You', 'Team': team_data.get('entry_name', 'Your Team'), 'Points': 641, 'GW_Points': 58},
            {'Rank': 3, 'Manager': 'Sarah Wilson', 'Team': 'City Slickers', 'Points': 635, 'GW_Points': 72},
            {'Rank': 4, 'Manager': 'Mike Johnson', 'Team': 'United Front', 'Points': 612, 'GW_Points': 45},
            {'Rank': 5, 'Manager': 'Lisa Brown', 'Team': 'Spurs Till I Die', 'Points': 598, 'GW_Points': 63},
        ]
        
        df_league = pd.DataFrame(league_data)
        
        # Style the dataframe
        def highlight_user_row(row):
            if row['Manager'] == 'You':
                return ['background-color: #e8f4fd; font-weight: bold'] * len(row)
            return [''] * len(row)
        
        styled_df = df_league.style.apply(highlight_user_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # League metrics
        col1, col2, col3, col4 = st.columns(4)
        
        user_row = df_league[df_league['Manager'] == 'You'].iloc[0]
        
        with col1:
            st.metric("League Position", f"#{user_row['Rank']}")
        
        with col2:
            points_behind = df_league.iloc[0]['Points'] - user_row['Points']
            st.metric("Points Behind Leader", points_behind)
        
        with col3:
            if user_row['Rank'] < len(df_league):
                points_ahead = user_row['Points'] - df_league.iloc[user_row['Rank']]['Points']
                st.metric("Points Ahead", points_ahead)
            else:
                st.metric("Points Ahead", "N/A")
        
        with col4:
            st.metric("League Size", len(df_league))
    
    def _render_head_to_head(self, team_data):
        """Render head-to-head comparisons"""
        st.subheader("📊 Head-to-Head Records")
        
        # Sample H2H data
        h2h_data = [
            {'Opponent': 'John Smith', 'Wins': 3, 'Draws': 1, 'Losses': 4, 'Points_For': 471, 'Points_Against': 523},
            {'Opponent': 'Sarah Wilson', 'Wins': 5, 'Draws': 2, 'Losses': 1, 'Points_For': 512, 'Points_Against': 445},
            {'Opponent': 'Mike Johnson', 'Wins': 6, 'Draws': 0, 'Losses': 2, 'Points_For': 534, 'Points_Against': 398},
            {'Opponent': 'Lisa Brown', 'Wins': 4, 'Draws': 3, 'Losses': 1, 'Points_For': 489, 'Points_Against': 456},
        ]
        
        for h2h in h2h_data:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**vs {h2h['Opponent']}**")
                    record = f"W{h2h['Wins']} D{h2h['Draws']} L{h2h['Losses']}"
                    win_rate = (h2h['Wins'] / (h2h['Wins'] + h2h['Draws'] + h2h['Losses'])) * 100
                    st.write(f"{record} ({win_rate:.1f}% win rate)")
                
                with col2:
                    points_diff = h2h['Points_For'] - h2h['Points_Against']
                    st.write(f"Points: {h2h['Points_For']} - {h2h['Points_Against']}")
                    if points_diff > 0:
                        st.write(f"📈 +{points_diff} advantage")
                    else:
                        st.write(f"📉 {points_diff} behind")
                
                with col3:
                    if win_rate >= 60:
                        st.write("🟢 Dominant")
                    elif win_rate >= 40:
                        st.write("🟡 Competitive")
                    else:
                        st.write("🔴 Struggling")
                
                st.divider()
    
    def _render_recent_form(self, team_data):
        """Render recent form comparison"""
        st.subheader("⚡ Recent Form (Last 5 GWs)")
        
        # Sample form data
        form_data = {
            'Manager': ['You', 'John Smith', 'Sarah Wilson', 'Mike Johnson', 'Lisa Brown'],
            'GW4': [67, 72, 58, 45, 63],
            'GW5': [45, 58, 67, 72, 51],
            'GW6': [72, 45, 63, 58, 67],
            'GW7': [58, 67, 51, 63, 72],
            'GW8': [63, 51, 72, 67, 45]
        }
        
        df_form = pd.DataFrame(form_data)
        
        # Calculate form metrics
        df_form['Total'] = df_form[['GW4', 'GW5', 'GW6', 'GW7', 'GW8']].sum(axis=1)
        df_form['Average'] = df_form['Total'] / 5
        
        # Sort by recent form
        df_form = df_form.sort_values('Total', ascending=False).reset_index(drop=True)
        df_form['Form_Rank'] = range(1, len(df_form) + 1)
        
        # Display form table
        display_cols = ['Form_Rank', 'Manager', 'GW4', 'GW5', 'GW6', 'GW7', 'GW8', 'Total', 'Average']
        st.dataframe(df_form[display_cols], use_container_width=True, hide_index=True)
        
        # Form chart
        fig = go.Figure()
        
        gameweeks = ['GW4', 'GW5', 'GW6', 'GW7', 'GW8']
        colors = ['#1f77b4' if manager == 'You' else '#cccccc' for manager in df_form['Manager']]
        
        for i, (_, row) in enumerate(df_form.iterrows()):
            line_width = 4 if row['Manager'] == 'You' else 2
            fig.add_trace(go.Scatter(
                x=gameweeks,
                y=[row[gw] for gw in gameweeks],
                mode='lines+markers',
                name=row['Manager'],
                line=dict(width=line_width),
                marker=dict(size=8 if row['Manager'] == 'You' else 6)
            ))
        
        fig.update_layout(
            title="Recent Form Comparison",
            xaxis_title="Gameweek",
            yaxis_title="Points",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_captain_analysis(self, team_data):
        """Render captain choice analysis"""
        st.subheader("🎯 Captain Analysis")
        
        # Sample captain data
        captain_data = [
            {'GW': 4, 'Your_Captain': 'Haaland (C)', 'Points': 24, 'League_Popular': 'Salah', 'Success': 'Good'},
            {'GW': 5, 'Your_Captain': 'Salah (C)', 'Points': 4, 'League_Popular': 'Haaland', 'Success': 'Poor'},
            {'GW': 6, 'Your_Captain': 'Son (C)', 'Points': 18, 'League_Popular': 'Haaland', 'Success': 'Excellent'},
            {'GW': 7, 'Your_Captain': 'Haaland (C)', 'Points': 14, 'League_Popular': 'Haaland', 'Success': 'Good'},
            {'GW': 8, 'Your_Captain': 'Palmer (C)', 'Points': 22, 'League_Popular': 'Salah', 'Success': 'Excellent'},
        ]
        
        df_captain = pd.DataFrame(captain_data)
        
        # Captain performance summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_captain_points = df_captain['Points'].sum()
            st.metric("Total Captain Points", total_captain_points)
        
        with col2:
            avg_captain_points = df_captain['Points'].mean()
            st.metric("Avg Captain Points", f"{avg_captain_points:.1f}")
        
        with col3:
            unique_captains = len(df_captain['Your_Captain'].unique())
            st.metric("Different Captains", unique_captains)
        
        with col4:
            differential_picks = len(df_captain[df_captain['Your_Captain'] != df_captain['League_Popular']])
            st.metric("Differential Picks", f"{differential_picks}/{len(df_captain)}")
        
        # Captain history table
        st.subheader("Captain History")
        
        # Color code success
        def color_success(val):
            if val == 'Excellent':
                return 'background-color: #d4edda'
            elif val == 'Good':
                return 'background-color: #fff3cd'
            elif val == 'Poor':
                return 'background-color: #f8d7da'
            return ''
        
        styled_captain = df_captain.style.applymap(color_success, subset=['Success'])
        st.dataframe(styled_captain, use_container_width=True, hide_index=True)
        
        # Captain points chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_captain['GW'],
            y=df_captain['Points'],
            name='Captain Points',
            marker_color=['#2e8b57' if points >= 15 else '#ffa500' if points >= 8 else '#dc143c' 
                         for points in df_captain['Points']]
        ))
        
        fig.update_layout(
            title="Captain Points by Gameweek",
            xaxis_title="Gameweek",
            yaxis_title="Points",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
