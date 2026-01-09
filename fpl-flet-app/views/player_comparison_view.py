import flet as ft
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import List, Any

from services.fpl_api_service import FPLDataService

# --- Helper functions for Plotly charts (adapted from EnhancedVisualizations) ---

def _normalize_metrics(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Normalize metrics to a 0-100 scale for better radar chart visualization."""
    normalized_df = df.copy()
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
        else:
            normalized_df[f'{metric}_norm'] = 0 # If metric not available, default to 0
    return normalized_df

def _create_player_comparison_radar(
    df: pd.DataFrame, # df is already comparison_df
    player_names: List[str]
) -> go.Figure:
    """
    Create multi-dimensional radar chart for player comparison.
    """
    metrics = [
        'total_points', 'form', 'points_per_game', 'value_score',
        'goals_scored', 'assists', 'clean_sheets', 'ict_index'
    ]

    if df.empty:
        return go.Figure()

    normalized_df = _normalize_metrics(df, metrics)

    fig = go.Figure()

    metric_labels = {
        'total_points': 'Total Points',
        'form': 'Form',
        'points_per_game': 'PPG',
        'value_score': 'Value Score',
        'goals_scored': 'Goals',
        'assists': 'Assists',
        'clean_sheets': 'Clean Sheets',
        'ict_index': 'ICT Index'
    }
    
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA'] # Plotly default colors

    for idx, (_, player) in enumerate(normalized_df.iterrows()):
        player_name = player.get('web_name', f"Player {idx+1}")
        
        values = []
        labels = []
        for metric in metrics:
            if f'{metric}_norm' in player.index:
                values.append(player[f'{metric}_norm'])
                labels.append(metric_labels.get(metric, metric))
        
        if not values: # Skip if no valid metrics found for player
            continue

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
                "%{{theta}}: %{{r:.1f}}<br>"
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

def _create_points_trend_line_chart(
    df: pd.DataFrame,
    player_names: List[str],
    gameweeks: int = 10
) -> go.Figure:
    """
    Create line chart showing points trend for selected players (simulated data).
    """
    fig = go.Figure()
    
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']

    for idx, player_name in enumerate(player_names):
        # Access the single row for the current player directly from the filtered df
        player_row = df[df['web_name'] == player_name].iloc[0]
        
        if not player_row.empty:
            form = float(player_row.get('form', 5))
            gw_points = []
            
            # Simulate points with variation based on form
            for i in range(gameweeks):
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
                    "GW %{{x}}: %{{y:.1f}} pts<br>"
                    "<extra></extra>"
                )
            ))
    
    fig.update_layout(
        title={
            'text': "📈 Points Trend Analysis (Simulated)",
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

# --- Flet View Implementation ---

async def build_player_comparison(data_service: FPLDataService, page_session: Any):
    """
    Builds the Flet UI for the Player Comparison tool.
    """
    players_df = await data_service.get_players()
    
    if players_df.empty:
        return ft.Column([
            ft.Text("No player data available. Please ensure data is loaded."),
            ft.ProgressRing()
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    player_options = [ft.dropdown.Option(p) for p in players_df['web_name'].unique().tolist()]

    # State for selected players and visualization type
    selected_player_names = ft.Ref[ft.Column]()
    comparison_type_radio_group = ft.Ref[ft.RadioGroup]()
    
    # Store selected player names for dynamic updates
    selected_players_state = [ft.Ref[ft.Dropdown]() for _ in range(4)]
    
    # Content area for charts/tables
    content_area = ft.Ref[ft.Column]()

    def update_comparison_content():
        """Updates the content area based on selected players and visualization type."""
        selected_names = []
        for i, dp_ref in enumerate(selected_players_state):
            if dp_ref.current and dp_ref.current.value:
                selected_names.append(dp_ref.current.value)
                page_session[f"pc_player_{i}"] = dp_ref.current.value
            else:
                if f"pc_player_{i}" in page_session:
                    del page_session[f"pc_player_{i}"]

        if len(selected_names) < 2:
            content_area.current.controls = [
                ft.Text("Please select at least two players to compare.", size=16, text_align=ft.TextAlign.CENTER)
            ]
            content_area.current.update()
            return

        comparison_df = players_df[players_df['web_name'].isin(selected_names)].copy()
        
        # Calculate derived metrics needed for comparison table/radar
        comparison_df['cost_millions'] = comparison_df['now_cost'] / 10
        comparison_df['points_per_million'] = (comparison_df['total_points'] / comparison_df['cost_millions']).fillna(0)
        
        current_comparison_type = comparison_type_radio_group.current.value
        page_session["pc_comparison_type"] = current_comparison_type
        
        new_content_controls = []

        # Always show detailed comparison table
        new_content_controls.append(ft.Container(height=20)) # Spacer
        new_content_controls.append(
            ft.Text("📋 Detailed Comparison Table", size=18, weight=ft.FontWeight.BOLD)
        )
        
        # Ensure all columns exist, handle potential missing ones gracefully for display
        display_cols = ['web_name', 'position', 'team_short_name', 'cost_millions', 
                        'total_points', 'form', 'points_per_million', 'selected_by_percent', 'minutes']
        
        # Map element_type to position name if 'position' is not directly available
        if 'element_type' in comparison_df.columns and 'position' not in comparison_df.columns:
            pos_map = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
            comparison_df['position'] = comparison_df['element_type'].map(pos_map)
        elif 'position_name' in comparison_df.columns:
            comparison_df['position'] = comparison_df['position_name']
        else:
            comparison_df['position'] = 'N/A' # Fallback
            
        # Map team_code to team_short_name if available in data_service
        if 'team' in comparison_df.columns:
            teams_df = data_service.get_teams()
            if not teams_df.empty:
                team_name_map = dict(zip(teams_df['id'], teams_df['short_name']))
                comparison_df['team_short_name'] = comparison_df['team'].map(team_name_map)
            else:
                comparison_df['team_short_name'] = 'N/A'
        else:
            comparison_df['team_short_name'] = 'N/A'

        
        data_rows = []
        for index, row in comparison_df.iterrows():
            cells = []
            for col in display_cols:
                # Format specific columns
                if col == 'cost_millions':
                    cells.append(ft.DataCell(ft.Text(f"£{row.get(col, 0):.1f}m")))
                elif col == 'points_per_million':
                    cells.append(ft.DataCell(ft.Text(f"{row.get(col, 0):.1f}")))
                elif col == 'selected_by_percent':
                    cells.append(ft.DataCell(ft.Text(f"{row.get(col, 0):.1f}%")))
                elif col == 'form':
                    cells.append(ft.DataCell(ft.Text(f"{row.get(col, 0):.1f}")))
                else:
                    cells.append(ft.DataCell(ft.Text(str(row.get(col, 'N/A')))))
            data_rows.append(ft.DataRow(cells=cells))

        new_content_controls.append(
            ft.SingleChildScrollView(
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True,
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Player")),
                        ft.DataColumn(ft.Text("Pos")),
                        ft.DataColumn(ft.Text("Team")),
                        ft.DataColumn(ft.Text("Price")),
                        ft.DataColumn(ft.Text("Points")),
                        ft.DataColumn(ft.Text("Form")),
                        ft.DataColumn(ft.Text("PPM")),
                        ft.DataColumn(ft.Text("Own%")),
                        ft.DataColumn(ft.Text("Mins")),
                    ],
                    rows=data_rows,
                    width=float('inf') # Use available width
                )
            )
        )
        
        if current_comparison_type == "Radar Chart":
            radar_chart_fig = _create_player_comparison_radar(comparison_df, selected_names)
            new_content_controls.append(ft.Container(height=20)) # Spacer
            new_content_controls.append(
                ft.Text("📊 Multi-Dimensional Radar Comparison", size=18, weight=ft.FontWeight.BOLD)
            )
            new_content_controls.append(ft.plotly_chart.PlotlyChart(radar_chart_fig, expand=True, is_isolated=True))
        elif current_comparison_type == "Trend Lines":
            trend_chart_fig = _create_points_trend_line_chart(comparison_df, selected_names)
            new_content_controls.append(ft.Container(height=20)) # Spacer
            new_content_controls.append(
                ft.Text("📈 Points Trend Comparison (Simulated)", size=18, weight=ft.FontWeight.BOLD)
            )
            new_content_controls.append(ft.plotly_chart.PlotlyChart(trend_chart_fig, expand=True, is_isolated=True))
        
        # Add quick insights
        if not comparison_df.empty:
            new_content_controls.append(ft.Container(height=20)) # Spacer
            new_content_controls.append(
                ft.Text("✨ Quick Insights", size=18, weight=ft.FontWeight.BOLD)
            )
            
            insights_column = []
            if 'total_points' in comparison_df.columns:
                best_points = comparison_df.loc[comparison_df['total_points'].idxmax()]
                insights_column.append(ft.Text(f"🏆 Highest Points: {best_points['web_name']} ({best_points['total_points']} pts)", color=ft.colors.GREEN_ACCENT_700))
            
            if 'points_per_million' in comparison_df.columns:
                best_value = comparison_df.loc[comparison_df['points_per_million'].idxmax()]
                insights_column.append(ft.Text(f"💎 Best Value: {best_value['web_name']} ({best_value['points_per_million']:.1f} PPM)", color=ft.colors.BLUE_ACCENT_200))
            
            if 'form' in comparison_df.columns:
                best_form = comparison_df.loc[comparison_df['form'].idxmax()]
                insights_column.append(ft.Text(f"🔥 Best Form: {best_form['web_name']} ({best_form['form']:.1f})", color=ft.colors.ORANGE_ACCENT_200))
            
            new_content_controls.append(ft.Column(insights_column))

        content_area.current.controls = new_content_controls
        content_area.current.update()
        content_area.current.page.update() # Update the page to reflect changes


    player_selector_cols = []
    for i in range(4):
        session_player_key = f"pc_player_{i}"
        initial_player_selection = page_session.get(session_player_key)
        player_selector_cols.append(
            ft.Dropdown(
                ref=selected_players_state[i],
                label=f"Player {i+1}",
                options=player_options,
                value=initial_player_selection,
                on_change=lambda e: update_comparison_content(),
                expand=True
            )
        )

    initial_comparison_type = page_session.get("pc_comparison_type", "Radar Chart")
    return ft.Column(
        [
            ft.Text("⚖️ Player Comparison", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(player_selector_cols, spacing=10),
            ft.Container(height=20), # Spacer
            ft.Text("Choose Visualization Type:", size=16),
            ft.RadioGroup(
                ref=comparison_type_radio_group,
                content=ft.Row([
                    ft.Radio(value="Radar Chart", label="Radar Chart"),
                    ft.Radio(value="Table", label="Table"),
                    ft.Radio(value="Trend Lines", label="Trend Lines"),
                ]),
                value=initial_comparison_type, # Default selection from session
                on_change=lambda e: update_comparison_content()
            ),
            ft.Container(height=20), # Spacer
            ft.Column(ref=content_area, expand=True) # Dynamic content area
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        on_ready=lambda e: update_comparison_content() # Initial content load
    )
