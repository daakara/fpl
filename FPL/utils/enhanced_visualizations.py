"""
Enhanced Visualization Utilities
Advanced interactive visualizations for FPL Analytics
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class EnhancedVisualizations:
    """Advanced visualization tools for FPL Analytics"""
    
    @staticmethod
    def player_comparison_radar(
        df: pd.DataFrame,
        player_ids: List[int] = None,
        player_names: List[str] = None,
        metrics: List[str] = None
    ) -> go.Figure:
        """
        Create multi-dimensional radar chart for player comparison
        
        Args:
            df: DataFrame with player data
            player_ids: List of player IDs to compare (optional)
            player_names: List of player names to compare (optional)
            metrics: List of metrics to compare (optional, uses defaults if None)
        
        Returns:
            Plotly Figure object
        """
        # Default metrics if none provided
        if metrics is None:
            metrics = [
                'goals_scored_per_90',
                'assists_per_90', 
                'expected_goals_per_90',
                'expected_assists_per_90',
                'bonus',
                'ict_index'
            ]
        
        # Filter for selected players
        if player_names:
            comparison_df = df[df['web_name'].isin(player_names)].copy()
        elif player_ids:
            comparison_df = df[df['id'].isin(player_ids)].copy()
        else:
            # Default to top 3 by total points
            comparison_df = df.nlargest(3, 'total_points').copy()
        
        if comparison_df.empty:
            st.warning("No players found for comparison")
            return go.Figure()
        
        # Normalize metrics to 0-100 scale for better visualization
        normalized_df = comparison_df.copy()
        for metric in metrics:
            if metric in normalized_df.columns:
                max_val = df[metric].max()
                min_val = df[metric].min()
                if max_val > min_val:
                    normalized_df[f'{metric}_norm'] = (
                        (normalized_df[metric] - min_val) / (max_val - min_val) * 100
                    )
                else:
                    normalized_df[f'{metric}_norm'] = 50
        
        # Create radar chart
        fig = go.Figure()
        
        # Clean metric labels
        metric_labels = {
            'goals_scored_per_90': 'Goals/90',
            'assists_per_90': 'Assists/90',
            'expected_goals_per_90': 'xG/90',
            'expected_assists_per_90': 'xA/90',
            'bonus': 'Bonus Points',
            'ict_index': 'ICT Index'
        }
        
        # Add trace for each player
        colors = px.colors.qualitative.Set2
        for idx, (_, player) in enumerate(normalized_df.iterrows()):
            player_name = player.get('web_name', f"Player {idx+1}")
            
            # Get normalized values
            values = []
            labels = []
            for metric in metrics:
                if f'{metric}_norm' in player.index:
                    values.append(player[f'{metric}_norm'])
                    labels.append(metric_labels.get(metric, metric))
            
            # Close the radar by repeating first value
            values.append(values[0])
            labels.append(labels[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                name=player_name,
                line=dict(color=colors[idx % len(colors)]),
                fillcolor=colors[idx % len(colors)],
                opacity=0.6,
                hovertemplate=(
                    f"<b>{player_name}</b><br>"
                    "%{theta}: %{r:.1f}<br>"
                    "<extra></extra>"
                )
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=True,
                    ticks='',
                    gridcolor='rgba(128, 128, 128, 0.2)'
                ),
                angularaxis=dict(
                    gridcolor='rgba(128, 128, 128, 0.2)'
                )
            ),
            showlegend=True,
            title={
                'text': "⚖️ Multi-Dimensional Player Comparison",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=500,
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    
    @staticmethod
    def form_heatmap(
        df: pd.DataFrame,
        last_n_gameweeks: int = 5,
        min_minutes: int = 100
    ) -> go.Figure:
        """
        Create color-coded heatmap of player form across last N gameweeks
        
        Args:
            df: DataFrame with player data
            last_n_gameweeks: Number of recent gameweeks to display
            min_minutes: Minimum minutes to include player
        
        Returns:
            Plotly Figure object
        """
        # Filter active players
        active_df = df[df.get('minutes', 0) >= min_minutes].copy()
        
        if active_df.empty:
            st.warning("No active players found")
            return go.Figure()
        
        # Simulate form data (in real app, this would come from gameweek history)
        # For now, use form score as proxy
        form_data = []
        
        # Get top 20 players by total points
        top_players = active_df.nlargest(20, 'total_points')
        
        for _, player in top_players.iterrows():
            player_name = player.get('web_name', 'Unknown')
            form_score = float(player.get('form', 0))
            
            # Simulate gameweek scores based on form
            # In production, replace with actual gameweek data
            base_points = form_score
            gw_scores = []
            for i in range(last_n_gameweeks):
                # Add variation
                variation = np.random.normal(0, 2)
                gw_score = max(0, base_points + variation)
                gw_scores.append(round(gw_score, 1))
            
            form_data.append({
                'player': player_name,
                'team': player.get('team_short_name', 'UNK'),
                'scores': gw_scores
            })
        
        # Create matrix for heatmap
        players = [d['player'] for d in form_data]
        scores_matrix = [d['scores'] for d in form_data]
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=scores_matrix,
            x=[f'GW-{i}' for i in range(last_n_gameweeks, 0, -1)],
            y=players,
            colorscale=[
                [0, '#FF4136'],      # Red for 0
                [0.2, '#FF851B'],    # Orange
                [0.4, '#FFDC00'],    # Yellow
                [0.6, '#01FF70'],    # Light green
                [0.8, '#00FF87'],    # Green
                [1.0, '#2ECC40']     # Dark green
            ],
            text=scores_matrix,
            texttemplate='%{z:.1f}',
            textfont={"size": 10},
            colorbar=dict(
                title="Points",
                titleside="right"
            ),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x}: %{z:.1f} pts<br>"
                "<extra></extra>"
            )
        ))
        
        fig.update_layout(
            title={
                'text': f"📊 Player Form Heatmap (Last {last_n_gameweeks} Gameweeks)",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="Gameweek",
            yaxis_title="Player",
            height=600,
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def fixture_difficulty_matrix(
        teams_df: pd.DataFrame,
        fixtures_df: pd.DataFrame = None,
        next_n_fixtures: int = 5
    ) -> go.Figure:
        """
        Create matrix showing all teams' next N fixtures with color-coded difficulty
        
        Args:
            teams_df: DataFrame with team data
            fixtures_df: DataFrame with fixture data (optional)
            next_n_fixtures: Number of upcoming fixtures to show
        
        Returns:
            Plotly Figure object
        """
        # If no fixtures provided, create mock data
        if fixtures_df is None or fixtures_df.empty:
            teams = teams_df['short_name'].tolist()[:20]  # Limit to 20 teams
            
            # Create simulated fixture difficulty
            fixture_data = []
            opponents = teams.copy()
            
            for team in teams:
                team_fixtures = []
                available_opponents = [t for t in opponents if t != team]
                
                for i in range(next_n_fixtures):
                    if available_opponents:
                        opponent = np.random.choice(available_opponents)
                        difficulty = np.random.randint(1, 6)  # FDR 1-5
                        is_home = np.random.choice([True, False])
                        
                        team_fixtures.append({
                            'opponent': opponent,
                            'difficulty': difficulty,
                            'home': is_home
                        })
                
                fixture_data.append({
                    'team': team,
                    'fixtures': team_fixtures
                })
        else:
            # Use actual fixture data
            fixture_data = []
            # Process fixtures_df here
            # This would be implemented based on actual fixture data structure
        
        # Create matrix data
        teams = [d['team'] for d in fixture_data]
        difficulty_matrix = []
        text_matrix = []
        
        for team_data in fixture_data:
            team_difficulties = []
            team_texts = []
            
            for fixture in team_data['fixtures']:
                team_difficulties.append(fixture['difficulty'])
                location = '(H)' if fixture['home'] else '(A)'
                team_texts.append(f"{fixture['opponent']} {location}")
            
            difficulty_matrix.append(team_difficulties)
            text_matrix.append(team_texts)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=difficulty_matrix,
            x=[f'Fixture {i+1}' for i in range(next_n_fixtures)],
            y=teams,
            text=text_matrix,
            texttemplate='%{text}',
            textfont={"size": 9},
            colorscale=[
                [0, '#00FF87'],      # FDR 1 - Very Easy (Green)
                [0.25, '#01FF70'],   # FDR 2 - Easy (Light Green)
                [0.5, '#FFDC00'],    # FDR 3 - Average (Yellow)
                [0.75, '#FF851B'],   # FDR 4 - Hard (Orange)
                [1.0, '#FF4136']     # FDR 5 - Very Hard (Red)
            ],
            colorbar=dict(
                title="FDR",
                titleside="right",
                tickmode='array',
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Very Easy', 'Easy', 'Average', 'Hard', 'Very Hard']
            ),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x}: %{text}<br>"
                "Difficulty: %{z}<br>"
                "<extra></extra>"
            ),
            zmin=1,
            zmax=5
        ))
        
        fig.update_layout(
            title={
                'text': f"🗓️ Fixture Difficulty Matrix (Next {next_n_fixtures} Fixtures)",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="Upcoming Fixtures",
            yaxis_title="Team",
            height=700,
            template='plotly_white',
            xaxis=dict(side='top')
        )
        
        return fig
    
    @staticmethod
    def interactive_scatter_with_filters(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        color_col: str = None,
        size_col: str = None,
        hover_data: List[str] = None
    ) -> go.Figure:
        """
        Create interactive scatter plot with dynamic filtering
        
        Args:
            df: DataFrame with player data
            x_col: Column for x-axis
            y_col: Column for y-axis
            color_col: Column for color coding (optional)
            size_col: Column for bubble size (optional)
            hover_data: Additional columns to show on hover
        
        Returns:
            Plotly Figure object
        """
        if hover_data is None:
            hover_data = ['web_name', 'team_short_name']
        
        # Ensure required columns exist
        if x_col not in df.columns or y_col not in df.columns:
            st.error(f"Required columns not found: {x_col}, {y_col}")
            return go.Figure()
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in df.columns else None,
            size=size_col if size_col and size_col in df.columns else None,
            hover_data=[col for col in hover_data if col in df.columns],
            title=f"{y_col} vs {x_col}",
            template="plotly_white"
        )
        
        fig.update_layout(
            title_x=0.5,
            height=500,
            hovermode='closest'
        )
        
        fig.update_traces(
            marker=dict(
                line=dict(width=1, color='DarkSlateGrey'),
                opacity=0.7
            )
        )
        
        return fig
    
    @staticmethod
    def points_trend_line_chart(
        df: pd.DataFrame,
        player_names: List[str],
        gameweeks: int = 10
    ) -> go.Figure:
        """
        Create line chart showing points trend for selected players
        
        Args:
            df: DataFrame with player data
            player_names: List of player names to plot
            gameweeks: Number of gameweeks to show
        
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set2
        
        for idx, player_name in enumerate(player_names):
            player_data = df[df['web_name'] == player_name]
            
            if not player_data.empty:
                # Simulate gameweek data (replace with actual data)
                form = float(player_data.iloc[0].get('form', 5))
                gw_points = []
                
                for i in range(gameweeks):
                    # Simulate points with variation
                    points = max(0, form + np.random.normal(0, 3))
                    gw_points.append(round(points, 1))
                
                fig.add_trace(go.Scatter(
                    x=list(range(1, gameweeks + 1)),
                    y=gw_points,
                    mode='lines+markers',
                    name=player_name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    marker=dict(size=8),
                    hovertemplate=(
                        f"<b>{player_name}</b><br>"
                        "GW %{x}: %{y:.1f} pts<br>"
                        "<extra></extra>"
                    )
                ))
        
        fig.update_layout(
            title={
                'text': "📈 Points Trend Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="Gameweek",
            yaxis_title="Points",
            height=400,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
