"""
Enhanced Dashboard Page - Advanced FPL Analytics Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.modern_ui_components import ModernUIComponents, DataVisualization, render_loading_spinner, create_success_animation
from utils.enhanced_cache import cached_load_fpl_data
from utils.error_handling import logger
from components.ai.player_insights import get_insights_engine

class EnhancedDashboardPage:
    """Advanced dashboard with real-time insights and interactive components."""

    def __init__(self):
        self.ui_components = ModernUIComponents()
        self.refresh_interval = 30 * 60  # 30 minutes in seconds

    def render(self):
        """Render the enhanced dashboard with advanced analytics."""
        
        # Dashboard Header with Auto-refresh
        self._render_dashboard_header()
        
        # Load and manage data
        if not self._ensure_data_loaded():
            return
            
        df = st.session_state.get('players_df')
        teams_df = st.session_state.get('teams_df')
        
        if df is None or df.empty:
            st.warning("Player data is not available. Please try refreshing.")
            return

        # Main Dashboard Content
        self._render_live_updates_section(df)
        self._render_enhanced_metrics(df, teams_df)
        self._render_interactive_charts(df, teams_df)
        self._render_gameweek_insights(df)
        self._render_transfer_market_section(df)
        self._render_ai_recommendations(df)
        self._render_quick_actions()

    def _render_dashboard_header(self):
        """Render dashboard header with live updates info."""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("# 🎯 FPL Analytics Dashboard")
            
        with col2:
            # Auto-refresh toggle
            auto_refresh = st.toggle("🔄 Auto-refresh", value=False, key="auto_refresh")
            if auto_refresh:
                # Placeholder for auto-refresh logic
                st.caption("⚡ Live updates enabled")
                
        with col3:
            # Last updated info
            last_update = st.session_state.get('last_data_update', datetime.now())
            time_diff = datetime.now() - last_update
            st.caption(f"🕒 Updated: {time_diff.seconds//60}m ago")

    def _ensure_data_loaded(self) -> bool:
        """Ensure data is loaded with enhanced loading experience."""
        if not st.session_state.get('data_loaded', False):
            st.markdown("### 🚀 Welcome to FPL Analytics")
            st.markdown("Your comprehensive Fantasy Premier League analysis platform")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔥 Load FPL Data", type="primary", use_container_width=True):
                    with st.spinner("🎯 Loading latest FPL data..."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("📡 Fetching player data...")
                        progress_bar.progress(25)
                        time.sleep(0.5)
                        
                        players_df, teams_df = cached_load_fpl_data()
                        
                        status_text.text("⚽ Processing team information...")
                        progress_bar.progress(50)
                        time.sleep(0.5)
                        
                        status_text.text("🧠 Preparing AI insights...")
                        progress_bar.progress(75)
                        time.sleep(0.5)
                        
                        if not players_df.empty:
                            st.session_state.players_df = players_df
                            st.session_state.teams_df = teams_df
                            st.session_state.data_loaded = True
                            st.session_state.last_data_update = datetime.now()
                            
                            progress_bar.progress(100)
                            status_text.text("✅ Ready!")
                            time.sleep(0.5)
                            
                            create_success_animation("🎉 Data loaded successfully!")
                            st.rerun()
            return False
        return True

    def _render_live_updates_section(self, df: pd.DataFrame):
        """Render live updates and alerts section."""
        st.markdown("### ⚡ Live Updates")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Price Changes
            if 'now_cost' in df.columns:
                # Simulate price changes (in real app, this would be actual data)
                risers = df.nlargest(3, 'form')[['web_name', 'now_cost']].reset_index(drop=True)
                with st.container():
                    st.markdown("**📈 Price Risers**")
                    for _, player in risers.iterrows():
                        st.markdown(f"🔹 {player['web_name']}")
        
        with col2:
            # Form Players
            if 'form' in df.columns:
                hot_players = df.nlargest(3, 'form')[['web_name', 'form']].reset_index(drop=True)
                with st.container():
                    st.markdown("**🔥 Hot Form**")
                    for _, player in hot_players.iterrows():
                        st.markdown(f"🔹 {player['web_name']} ({player['form']})")
        
        with col3:
            # Transfer Trends
            if 'transfers_in_event' in df.columns:
                trending = df.nlargest(3, 'transfers_in_event')[['web_name', 'transfers_in_event']].reset_index(drop=True)
                with st.container():
                    st.markdown("**📊 Trending In**")
                    for _, player in trending.iterrows():
                        transfers = player['transfers_in_event'] if pd.notna(player['transfers_in_event']) else 0
                        st.markdown(f"🔹 {player['web_name']} (+{transfers:,.0f})")
        
        with col4:
            # Gameweek Countdown
            with st.container():
                st.markdown("**⏰ Next Deadline**")
                # In real app, calculate actual deadline
                st.markdown("🔹 **2 days, 14 hours**")
                st.markdown("🔹 **GW 12 Fixtures**")

    def _render_enhanced_metrics(self, df: pd.DataFrame, teams_df: pd.DataFrame):
        """Render enhanced key metrics with more insights."""
        st.markdown("### 📊 Key Performance Indicators")
        
        # Primary Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_players = len(df)
            avg_points = df['total_points'].mean() if 'total_points' in df.columns else 0
            self.ui_components.create_metric_card(
                "Total Players", f"{total_players:,}",
                delta=f"Avg: {avg_points:.1f} pts", icon="👥"
            )

        with col2:
            if 'now_cost' in df.columns:
                avg_price = df['now_cost'].mean() / 10  # Convert to millions
                expensive_players = len(df[df['now_cost'] >= 100])  # £10m+
                self.ui_components.create_metric_card(
                    "Average Price", f"£{avg_price:.1f}m",
                    delta=f"{expensive_players} premium players", icon="💰"
                )

        with col3:
            if 'total_points' in df.columns and len(df) > 0:
                top_scorer = df.loc[df['total_points'].idxmax()]
                points_diff = top_scorer['total_points'] - df['total_points'].quantile(0.75)
                self.ui_components.create_metric_card(
                    "Top Scorer", f"{top_scorer['web_name']}",
                    delta=f"{top_scorer['total_points']} pts (+{points_diff:.0f})", icon="🏆"
                )

        with col4:
            if 'points_per_game' in df.columns and len(df) > 0:
                best_ppg = df.loc[df['points_per_game'].idxmax()]
                self.ui_components.create_metric_card(
                    "Best PPG", f"{best_ppg['web_name']}",
                    delta=f"{best_ppg['points_per_game']:.1f} per game", icon="⭐"
                )

        with col5:
            if 'selected_by_percent' in df.columns:
                most_owned = df.loc[df['selected_by_percent'].idxmax()]
                ownership = float(most_owned['selected_by_percent'])
                self.ui_components.create_metric_card(
                    "Most Owned", f"{most_owned['web_name']}",
                    delta=f"{ownership:.1f}% ownership", icon="👑"
                )

        # Secondary Metrics Row
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'form' in df.columns:
                avg_form = df['form'].mean()
                hot_form_count = len(df[df['form'] >= 7])
                st.metric("Form Index", f"{avg_form:.1f}", f"{hot_form_count} hot players")
        
        with col2:
            if 'minutes' in df.columns:
                avg_minutes = df['minutes'].mean()
                regular_starters = len(df[df['minutes'] >= 900])  # 10+ games worth
                st.metric("Avg Minutes", f"{avg_minutes:.0f}", f"{regular_starters} regulars")
                
        with col3:
            if 'bonus' in df.columns:
                total_bonus = df['bonus'].sum()
                bonus_kings = len(df[df['bonus'] >= 10])
                st.metric("Total Bonus", f"{total_bonus:,}", f"{bonus_kings} bonus kings")
                
        with col4:
            if 'transfers_balance' in df.columns:
                net_transfers = df['transfers_balance'].sum()
                transfer_direction = "📈" if net_transfers > 0 else "📉"
                st.metric("Net Transfers", f"{transfer_direction} {abs(net_transfers):,.0f}")

    def _render_interactive_charts(self, df: pd.DataFrame, teams_df: pd.DataFrame):
        """Render interactive visualizations with advanced filters."""
        st.markdown("### 📈 Interactive Analytics")
        
        # Chart Controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            position_filter = st.selectbox(
                "Position Filter:",
                options=["All Positions", "Goalkeepers", "Defenders", "Midfielders", "Forwards"],
                key="position_filter"
            )
            
        with col2:
            price_range = st.select_slider(
                "Price Range (£m):",
                options=[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                value=(4, 15),
                key="price_range"
            )
            
        with col3:
            min_minutes = st.slider(
                "Min Minutes:",
                min_value=0, max_value=2000, value=300, step=100,
                key="min_minutes"
            )

        # Filter data based on controls
        filtered_df = self._apply_filters(df, position_filter, price_range, min_minutes)
        
        # Charts Row 1
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            self._render_value_scatter_chart(filtered_df)
            
        with chart_col2:
            self._render_form_vs_ownership_chart(filtered_df)
            
        # Charts Row 2
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            self._render_position_performance_chart(filtered_df)
            
        with chart_col4:
            self._render_team_strength_chart(filtered_df, teams_df)

    def _render_gameweek_insights(self, df: pd.DataFrame):
        """Render gameweek-specific insights and predictions."""
        st.markdown("### 🎯 Gameweek Insights")
        
        tab1, tab2, tab3 = st.tabs(["🔮 Predictions", "📊 Form Analysis", "💎 Hidden Gems"])
        
        with tab1:
            self._render_gameweek_predictions(df)
            
        with tab2:
            self._render_form_analysis(df)
            
        with tab3:
            self._render_hidden_gems(df)

    def _render_transfer_market_section(self, df: pd.DataFrame):
        """Render transfer market insights."""
        st.markdown("### 🔄 Transfer Market")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Hot Transfers**")
            if 'transfers_in_event' in df.columns:
                hot_transfers = df.nlargest(10, 'transfers_in_event')[
                    ['web_name', 'now_cost', 'transfers_in_event', 'form']
                ].copy()
                hot_transfers['now_cost'] = hot_transfers['now_cost'] / 10
                hot_transfers.columns = ['Player', 'Price (£m)', 'Transfers In', 'Form']
                st.dataframe(hot_transfers, hide_index=True)
        
        with col2:
            st.markdown("**📉 Transfer Outs**")
            if 'transfers_out_event' in df.columns:
                cold_transfers = df.nlargest(10, 'transfers_out_event')[
                    ['web_name', 'now_cost', 'transfers_out_event', 'form']
                ].copy()
                cold_transfers['now_cost'] = cold_transfers['now_cost'] / 10
                cold_transfers.columns = ['Player', 'Price (£m)', 'Transfers Out', 'Form']
                st.dataframe(cold_transfers, hide_index=True)

    def _render_ai_recommendations(self, df: pd.DataFrame):
        """Render AI-powered recommendations section."""
        if st.session_state.get('feature_flags', {}).get('ai_recommendations', True):
            st.markdown("---")
            st.markdown("### 🤖 AI-Powered Insights")
            
            try:
                insights_engine = get_insights_engine()
                insights_engine.render_insights_dashboard(df)
            except Exception as e:
                st.warning("AI insights temporarily unavailable")
                logger.error(f"AI insights error: {e}")

    def _render_quick_actions(self):
        """Render quick action buttons."""
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Player Search", use_container_width=True):
                st.session_state.nav_selection = "player_analysis"
                st.rerun()
                
        with col2:
            if st.button("🏗️ Team Builder", use_container_width=True):
                st.session_state.nav_selection = "team_builder"
                st.rerun()
                
        with col3:
            if st.button("🤖 AI Recommendations", use_container_width=True):
                st.session_state.nav_selection = "ai_recommendations"
                st.rerun()
                
        with col4:
            if st.button("📊 Advanced Analysis", use_container_width=True):
                st.session_state.nav_selection = "advanced_analysis"
                st.rerun()

    # Helper Methods
    def _apply_filters(self, df: pd.DataFrame, position_filter: str, price_range: Tuple, min_minutes: int) -> pd.DataFrame:
        """Apply dashboard filters to dataframe."""
        filtered_df = df.copy()
        
        # Position filter
        if position_filter != "All Positions":
            position_map = {
                "Goalkeepers": 1, "Defenders": 2, 
                "Midfielders": 3, "Forwards": 4
            }
            if 'element_type' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['element_type'] == position_map[position_filter]]
        
        # Price filter
        if 'now_cost' in filtered_df.columns:
            min_price, max_price = price_range
            filtered_df = filtered_df[
                (filtered_df['now_cost'] >= min_price * 10) & 
                (filtered_df['now_cost'] <= max_price * 10)
            ]
        
        # Minutes filter
        if 'minutes' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['minutes'] >= min_minutes]
            
        return filtered_df

    def _render_value_scatter_chart(self, df: pd.DataFrame):
        """Render value scatter chart."""
        if 'now_cost' in df.columns and 'total_points' in df.columns:
            fig = px.scatter(
                df, 
                x='now_cost', 
                y='total_points',
                color='element_type' if 'element_type' in df.columns else None,
                size='selected_by_percent' if 'selected_by_percent' in df.columns else None,
                hover_name='web_name',
                title="💎 Value Analysis: Price vs Points",
                labels={'now_cost': 'Price (0.1m)', 'total_points': 'Total Points'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    def _render_form_vs_ownership_chart(self, df: pd.DataFrame):
        """Render form vs ownership chart."""
        if 'form' in df.columns and 'selected_by_percent' in df.columns:
            fig = px.scatter(
                df,
                x='selected_by_percent',
                y='form',
                color='element_type' if 'element_type' in df.columns else None,
                size='total_points' if 'total_points' in df.columns else None,
                hover_name='web_name',
                title="🔥 Form vs Ownership",
                labels={'selected_by_percent': 'Ownership %', 'form': 'Form'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    def _render_position_performance_chart(self, df: pd.DataFrame):
        """Render position performance chart."""
        if 'element_type' in df.columns and 'total_points' in df.columns:
            position_names = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
            df_pos = df.copy()
            df_pos['position_name'] = df_pos['element_type'].map(position_names)
            
            fig = px.box(
                df_pos,
                x='position_name',
                y='total_points',
                title="⚽ Performance by Position",
                labels={'position_name': 'Position', 'total_points': 'Total Points'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    def _render_team_strength_chart(self, df: pd.DataFrame, teams_df: pd.DataFrame):
        """Render team strength analysis."""
        if 'team' in df.columns and 'total_points' in df.columns and teams_df is not None:
            team_performance = df.groupby('team')['total_points'].agg(['mean', 'sum', 'count']).reset_index()
            
            if 'name' in teams_df.columns:
                team_performance = team_performance.merge(
                    teams_df[['id', 'name']], 
                    left_on='team', 
                    right_on='id', 
                    how='left'
                )
                
                fig = px.bar(
                    team_performance.nlargest(10, 'sum'),
                    x='name',
                    y='sum',
                    title="🏆 Top Team Performances",
                    labels={'name': 'Team', 'sum': 'Total Points'}
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

    def _render_gameweek_predictions(self, df: pd.DataFrame):
        """Render gameweek predictions."""
        st.markdown("**🔮 Next Gameweek Predictions**")
        
        if 'form' in df.columns and 'total_points' in df.columns:
            # Simple prediction based on form and historical performance
            predictions = df.copy()
            predictions['predicted_points'] = (
                predictions['form'] * 0.6 + 
                (predictions['total_points'] / 11) * 0.4  # Assuming 11 gameweeks
            ).round(1)
            
            top_predictions = predictions.nlargest(10, 'predicted_points')[
                ['web_name', 'predicted_points', 'form', 'now_cost']
            ].copy()
            top_predictions['now_cost'] = top_predictions['now_cost'] / 10
            top_predictions.columns = ['Player', 'Predicted Points', 'Current Form', 'Price (£m)']
            
            st.dataframe(top_predictions, hide_index=True)

    def _render_form_analysis(self, df: pd.DataFrame):
        """Render form analysis."""
        st.markdown("**📊 Form Analysis**")
        
        if 'form' in df.columns:
            form_categories = pd.cut(df['form'], bins=[0, 3, 5, 7, float('inf')], 
                                   labels=['Poor', 'Average', 'Good', 'Excellent'])
            form_dist = form_categories.value_counts()
            
            fig = px.bar(
                x=form_dist.index,
                y=form_dist.values,
                title="Player Form Distribution",
                labels={'x': 'Form Category', 'y': 'Number of Players'}
            )
            st.plotly_chart(fig, use_container_width=True)

    def _render_hidden_gems(self, df: pd.DataFrame):
        """Render hidden gems analysis."""
        st.markdown("**💎 Hidden Gems (Low ownership, high potential)**")
        
        if all(col in df.columns for col in ['selected_by_percent', 'form', 'total_points', 'now_cost']):
            # Find low ownership players with good form and value
            gems = df[
                (df['selected_by_percent'] < 5) &  # Low ownership
                (df['form'] >= 6) &  # Good form
                (df['total_points'] >= df['total_points'].quantile(0.6))  # Above average points
            ].nlargest(10, 'form')[
                ['web_name', 'selected_by_percent', 'form', 'total_points', 'now_cost']
            ].copy()
            
            if not gems.empty:
                gems['now_cost'] = gems['now_cost'] / 10
                gems.columns = ['Player', 'Ownership %', 'Form', 'Total Points', 'Price (£m)']
                st.dataframe(gems, hide_index=True)
            else:
                st.info("No hidden gems found with current criteria")
