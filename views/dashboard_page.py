"""
Dashboard Page - Displays the main dashboard with key metrics and features.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
from utils.modern_ui_components import ModernUIComponents, DataVisualization, render_loading_spinner, create_success_animation
from utils.enhanced_cache import cached_load_fpl_data
from utils.error_handling import logger
from utils.performance_optimizer import PerformanceOptimizer, LazyLoader, cache_5min
from components.ai.player_insights import get_insights_engine
from utils.mobile_responsive import (
    is_mobile, 
    is_desktop,
    responsive_columns,
    responsive_metric,
    responsive_dataframe
)
from services.price_change_predictor import PriceChangePredictor

class DashboardPage:
    """Handles the rendering of the main dashboard."""

    def __init__(self):
        self.ui_components = ModernUIComponents()

    def render(self):
        """Render the main dashboard with key FPL insights."""
        
        # Enhanced Header with Live Updates Info - Responsive
        if is_mobile():
            # Mobile layout - stack vertically
            st.markdown("# 🎯 FPL Dashboard")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", type="secondary", use_container_width=True):
                    with st.spinner("Refreshing..."):
                        players_df, teams_df = cached_load_fpl_data()
                        if not players_df.empty:
                            st.session_state.players_df = players_df
                            st.session_state.teams_df = teams_df
                            st.session_state.last_data_update = datetime.now()
                            st.success("✅ Refreshed!")
                            st.rerun()
            
            with col2:
                last_update = st.session_state.get('last_data_update', None)
                if last_update:
                    time_diff = datetime.now() - last_update
                    minutes_ago = time_diff.seconds // 60
                    st.caption(f"🕒 {minutes_ago}m ago")
        else:
            # Desktop layout - three columns
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown("# 🎯 FPL Analytics Dashboard")
                
            with col2:
                # Data refresh button
                if st.button("🔄 Refresh Data", type="secondary"):
                    with st.spinner("Refreshing FPL data..."):
                        players_df, teams_df = cached_load_fpl_data()
                        if not players_df.empty:
                            st.session_state.players_df = players_df
                            st.session_state.teams_df = teams_df
                            st.session_state.last_data_update = datetime.now()
                            st.success("✅ Data refreshed!")
                            st.rerun()
                            
            with col3:
                # Last updated info
                last_update = st.session_state.get('last_data_update', None)
                if last_update:
                    time_diff = datetime.now() - last_update
                    minutes_ago = time_diff.seconds // 60
                    st.caption(f"🕒 Updated: {minutes_ago}m ago")
                else:
                    st.caption(f"🕒 Initializing...")

        if not st.session_state.get('data_loaded', False):
            st.markdown("### 🚀 Welcome to Advanced FPL Analytics")
            st.markdown("Your comprehensive Fantasy Premier League analysis platform with AI-powered insights")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                # Show loading message in fallback mode
                if st.session_state.get('data_source') == 'fallback':
                    st.info("📦 Running in fallback mode - using sample data")
                    # Trigger data load by setting flag
                    st.session_state.data_loaded = True
                    st.rerun()
                elif st.button("🔥 Load FPL Data", type="primary", use_container_width=True):
                    with st.spinner("Loading FPL data..."):
                        render_loading_spinner("Fetching latest player data...")
                        players_df, teams_df = cached_load_fpl_data()

                        if not players_df.empty:
                            st.session_state.players_df = players_df
                            st.session_state.teams_df = teams_df
                            st.session_state.data_loaded = True
                            st.session_state.last_data_update = datetime.now()
                            create_success_animation("Data loaded successfully!")
                            st.rerun()
            return

        df = st.session_state.get('players_df')
        if df is None or df.empty:
            st.warning("⚠️ Player data is not available. Please try refreshing the page.")
            st.info(f"Data source: {st.session_state.get('data_source', 'unknown')}")
            return

            return

        # Live Updates Section
        self._render_live_updates_section(df)
        
        # Price Change Predictions (NEW FEATURE)
        self._render_price_changes_section(df)
        
        # Enhanced key metrics with modern cards
        st.markdown("### 📊 Key Performance Indicators")

        # Position filter for metrics - Responsive
        if is_mobile():
            position_filter = st.selectbox(
                "Position Filter:",
                options=["All Positions", "Goalkeepers (GK)", "Defenders (DEF)", "Midfielders (MID)", "Forwards (FWD)"],
                key="dashboard_position_filter"
            )
        else:
            col_filter1, col_filter2, col_filter3 = st.columns([1, 1, 2])
            with col_filter1:
                position_filter = st.selectbox(
                    "Position Filter:",
                    options=["All Positions", "Goalkeepers (GK)", "Defenders (DEF)", "Midfielders (MID)", "Forwards (FWD)"],
                    key="dashboard_position_filter"
                )
        
        # Apply position filter
        filtered_df = self._apply_position_filter(df, position_filter)

        # Responsive metric cards
        if is_mobile():
            # Mobile: 2 columns
            cols = st.columns(2)
            metrics = [
                ("Active Players", len(filtered_df), f"Avg: {filtered_df['total_points'].mean():.1f} pts" if 'total_points' in filtered_df.columns else "", "👥"),
                ("Average Price", f"£{(filtered_df['now_cost'].mean() / 10 if 'now_cost' in filtered_df.columns else filtered_df.get('cost_millions', pd.Series([0])).mean()):.1f}m", "Market", "💰"),
                ("Top Scorer", filtered_df.loc[filtered_df['total_points'].idxmax()]['web_name'] if 'total_points' in filtered_df.columns and len(filtered_df) > 0 else "N/A", f"{filtered_df['total_points'].max():.0f} pts" if 'total_points' in filtered_df.columns else "", "🏆"),
                ("Best Form", filtered_df.loc[filtered_df['form'].idxmax()]['web_name'] if 'form' in filtered_df.columns and len(filtered_df) > 0 else "N/A", f"{filtered_df['form'].max():.1f}" if 'form' in filtered_df.columns else "", "🔥"),
            ]
            
            for idx, (label, value, delta, icon) in enumerate(metrics):
                with cols[idx % 2]:
                    self.ui_components.create_metric_card(label, str(value), delta=delta, icon=icon)
        else:
            # Desktop: 5 columns
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                total_players = len(filtered_df)
                avg_points = filtered_df['total_points'].mean() if 'total_points' in filtered_df.columns else 0
                self.ui_components.create_metric_card(
                    "Active Players", f"{total_players:,}",
                    delta=f"Avg: {avg_points:.1f} pts", icon="👥"
                )

            with col2:
                if 'now_cost' in filtered_df.columns:
                    avg_price = filtered_df['now_cost'].mean() / 10  # Convert to millions
                    expensive_players = len(filtered_df[filtered_df['now_cost'] >= 100])  # £10m+
                    self.ui_components.create_metric_card(
                        "Average Price", f"£{avg_price:.1f}m",
                        delta=f"{expensive_players} premium players", icon="💰"
                    )
                elif 'cost_millions' in filtered_df.columns:
                    avg_price = filtered_df['cost_millions'].mean()
                    self.ui_components.create_metric_card(
                        "Average Price", f"£{avg_price:.1f}m",
                        delta="Market stable", icon="💰"
                    )

            with col3:
                if 'total_points' in filtered_df.columns and len(filtered_df) > 0:
                    top_scorer = filtered_df.loc[filtered_df['total_points'].idxmax()]
                    points_gap = top_scorer['total_points'] - filtered_df['total_points'].quantile(0.75)
                    self.ui_components.create_metric_card(
                        "Top Scorer", f"{top_scorer['web_name']}",
                        delta=f"{top_scorer['total_points']} pts (+{points_gap:.0f})", icon="🏆"
                    )

            with col4:
                if 'form' in filtered_df.columns and len(filtered_df) > 0:
                    best_form = filtered_df.loc[filtered_df['form'].idxmax()]
                    hot_form_count = len(filtered_df[filtered_df['form'] >= 7])
                    self.ui_components.create_metric_card(
                        "Best Form", f"{best_form['web_name']}",
                        delta=f"{best_form['form']} form ({hot_form_count} hot)", icon="🔥"
                    )
                elif 'points_per_million' in filtered_df.columns and len(filtered_df) > 0:
                    best_value = filtered_df.loc[filtered_df['points_per_million'].idxmax()]
                    self.ui_components.create_metric_card(
                        "Best Value", f"{best_value['web_name']}",
                        delta=f"{best_value['points_per_million']:.1f} pts/£m", icon="💎"
                    )

            with col5:
                if 'selected_by_percent' in filtered_df.columns and len(filtered_df) > 0:
                    most_owned = filtered_df.loc[filtered_df['selected_by_percent'].idxmax()]
                    ownership = float(most_owned['selected_by_percent'])
                    self.ui_components.create_metric_card(
                        "Most Owned", f"{most_owned['web_name']}",
                        delta=f"{ownership:.1f}% ownership", icon="👑"
                    )

        # Interactive visualizations
        st.markdown("### 📈 Performance Insights")

        if len(filtered_df) > 0:
            # Responsive visualization layout
            if is_mobile():
                # Mobile: stack vertically
                viz_col1 = st.container()
                viz_col2 = st.container()
            else:
                # Desktop: side by side
                viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                # Enhanced price vs performance chart
                if 'total_points' in filtered_df.columns:
                    if 'cost_millions' in filtered_df.columns:
                        DataVisualization.create_performance_chart(
                            filtered_df, 'cost_millions', 'total_points',
                            "💎 Price vs Performance Analysis"
                        )
                    elif 'now_cost' in filtered_df.columns:
                        # Create price in millions column
                        chart_df = filtered_df.copy()
                        chart_df['price_millions'] = chart_df['now_cost'] / 10
                        DataVisualization.create_performance_chart(
                            chart_df, 'price_millions', 'total_points',
                            "💎 Price vs Performance Analysis"
                        )

            with viz_col2:
                if 'element_type' in filtered_df.columns:
                    position_counts = filtered_df['element_type'].value_counts()
                    position_names = {1: 'Goalkeepers', 2: 'Defenders', 3: 'Midfielders', 4: 'Forwards'}
                    composition = {position_names.get(k, f'Position {k}'): v for k, v in position_counts.items()}
                    DataVisualization.create_team_balance_chart(composition)

            # Additional charts row
            viz_col3, viz_col4 = st.columns(2)
            
            with viz_col3:
                # Form vs Ownership scatter
                if 'form' in filtered_df.columns and 'selected_by_percent' in filtered_df.columns:
                    fig = px.scatter(
                        filtered_df.head(100),  # Limit for performance
                        x='selected_by_percent',
                        y='form',
                        hover_name='web_name',
                        color='element_type',
                        title="🔥 Form vs Ownership",
                        labels={'selected_by_percent': 'Ownership %', 'form': 'Current Form'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with viz_col4:
                # Minutes distribution by position
                if 'minutes' in filtered_df.columns and 'element_type' in filtered_df.columns:
                    position_names = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                    chart_df = filtered_df.copy()
                    chart_df['position_name'] = chart_df['element_type'].map(position_names)
                    
                    fig = px.box(
                        chart_df,
                        x='position_name',
                        y='minutes',
                        title="⏱️ Playing Time by Position",
                        labels={'position_name': 'Position', 'minutes': 'Minutes Played'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

        # AI-Powered Insights Section
        if st.session_state.get('feature_flags', {}).get('ai_recommendations', True):
            st.markdown("---")
            insights_engine = get_insights_engine()
            insights_engine.render_insights_dashboard(df)

        # Quick Actions Section
        self._render_quick_actions()

        # Feature highlights
        st.markdown("### ✨ Available Features")

        feature_col1, feature_col2 = st.columns(2)

        with feature_col1:
            ai_enabled = self.ui_components.create_feature_card(
                "AI Recommendations",
                "Get personalized player suggestions powered by machine learning",
                "🤖",
                enabled=st.session_state.get('feature_flags', {}).get('ai_recommendations', True)
            )
            if 'feature_flags' in st.session_state:
                st.session_state.feature_flags['ai_recommendations'] = ai_enabled

            analytics_enabled = self.ui_components.create_feature_card(
                "Advanced Analytics",
                "Deep performance insights and statistical analysis",
                "📊",
                enabled=st.session_state.get('feature_flags', {}).get('advanced_analytics', True)
            )
            if 'feature_flags' in st.session_state:
                st.session_state.feature_flags['advanced_analytics'] = analytics_enabled

        with feature_col2:
            realtime_enabled = self.ui_components.create_feature_card(
                "Real-time Updates",
                "Live data updates and price change monitoring",
                "⚡",
                enabled=st.session_state.get('feature_flags', {}).get('real_time_updates', False),
                beta=True
            )
            if 'feature_flags' in st.session_state:
                st.session_state.feature_flags['real_time_updates'] = realtime_enabled

            export_enabled = self.ui_components.create_feature_card(
                "Data Export",
                "Export analysis results and custom reports",
                "💾",
                enabled=st.session_state.get('feature_flags', {}).get('export_features', True)
            )
            if 'feature_flags' in st.session_state:
                st.session_state.feature_flags['export_features'] = export_enabled

    def _render_live_updates_section(self, df):
        """Render live updates and trending information."""
        st.markdown("### ⚡ Live Updates & Trends")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**🔥 Hot Form**")
            if 'form' in df.columns:
                hot_players = df.nlargest(3, 'form')[['web_name', 'form']].reset_index(drop=True)
                for _, player in hot_players.iterrows():
                    form_value = float(player['form']) if pd.notna(player['form']) else 0
                    st.markdown(f"🔹 {player['web_name']} ({form_value:.1f})")
            else:
                st.markdown("🔹 Form data loading...")
        
        with col2:
            st.markdown("**📈 Most Owned**")
            if 'selected_by_percent' in df.columns:
                popular = df.nlargest(3, 'selected_by_percent')[['web_name', 'selected_by_percent']].reset_index(drop=True)
                for _, player in popular.iterrows():
                    ownership = float(player['selected_by_percent']) if pd.notna(player['selected_by_percent']) else 0
                    st.markdown(f"🔹 {player['web_name']} ({ownership:.1f}%)")
            else:
                st.markdown("🔹 Ownership data loading...")
        
        with col3:
            st.markdown("**💎 Best Value**")
            if 'total_points' in df.columns and 'now_cost' in df.columns:
                df_value = df.copy()
                df_value['value_score'] = df_value['total_points'] / (df_value['now_cost'] / 10)
                best_value = df_value.nlargest(3, 'value_score')[['web_name', 'value_score']].reset_index(drop=True)
                for _, player in best_value.iterrows():
                    value = player['value_score'] if pd.notna(player['value_score']) else 0
                    st.markdown(f"🔹 {player['web_name']} ({value:.1f})")
            else:
                st.markdown("🔹 Value data loading...")
        
        with col4:
            st.markdown("**⏰ Next Deadline**")
            st.markdown("🔹 **2 days, 14 hours**")
            st.markdown("🔹 **GW 12 Fixtures**")
            st.markdown("🔹 **Plan your transfers**")

    def _render_price_changes_section(self, df):
        """Render price change predictions."""
        st.markdown("### 💰 Price Change Predictions")
        
        try:
            predictor = PriceChangePredictor()
            predictions = predictor.predict_price_changes(df, include_probable=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🔥 Likely Risers**")
                if predictions['risers']:
                    for riser in predictions['risers'][:5]:
                        st.markdown(
                            f"{riser['emoji']} **{riser['name']}** - "
                            f"{riser['net_transfers']//1000}K net "
                            f"({riser['confidence']})"
                        )
                else:
                    st.info("No significant risers detected")
            
            with col2:
                st.markdown("**🔻 Likely Fallers**")
                if predictions['fallers']:
                    for faller in predictions['fallers'][:5]:
                        st.markdown(
                            f"{faller['emoji']} **{faller['name']}** - "
                            f"{abs(faller['net_transfers'])//1000}K net "
                            f"({faller['confidence']})"
                        )
                else:
                    st.info("No significant fallers detected")
            
            with col3:
                st.markdown("**⚠️ Watchlist**")
                if predictions['watchlist']:
                    for player in predictions['watchlist'][:5]:
                        st.markdown(
                            f"⚠️ **{player['name']}** - "
                            f"{abs(player['net_transfers'])//1000}K "
                            f"({player['direction']})"
                        )
                else:
                    st.info("No players on the edge")
            
            # Summary statistics
            with st.expander("📊 Price Change Statistics"):
                stats = predictions['stats']
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Likely Risers", stats['likely_risers'])
                with col_stat2:
                    st.metric("Likely Fallers", stats['likely_fallers'])
                with col_stat3:
                    st.metric("Total Transfers In", f"{stats['total_transfers_in']//1000}K")
        
        except Exception as e:
            logger.error(f"Error rendering price changes: {e}")
            st.info("💰 Price change predictions will appear here")

    def _apply_position_filter(self, df, position_filter):
        """Apply position filter to dataframe."""
        if position_filter == "All Positions":
            return df
        
        position_map = {
            "Goalkeepers (GK)": 1,
            "Defenders (DEF)": 2, 
            "Midfielders (MID)": 3,
            "Forwards (FWD)": 4
        }
        
        if 'element_type' in df.columns:
            return df[df['element_type'] == position_map[position_filter]]
        
        return df

    def _render_quick_actions(self):
        """Render quick action buttons for navigation."""
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