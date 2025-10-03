"""
Dashboard Page - Displays the main dashboard with key metrics and features.
"""
import streamlit as st
import time
from utils.modern_ui_components import ModernUIComponents, DataVisualization, render_loading_spinner, create_success_animation
from utils.enhanced_cache import cached_load_fpl_data
from utils.error_handling import logger

class DashboardPage:
    """Handles the rendering of the main dashboard."""

    def __init__(self):
        self.ui_components = ModernUIComponents()

    def render(self):
        """Render the main dashboard with key FPL insights."""
        st.markdown("### 🎯 Dashboard Overview")

        if not st.session_state.get('data_loaded', False):
            if st.button("🚀 Get Started - Load FPL Data", type="primary"):
                with st.spinner("Loading FPL data..."):
                    render_loading_spinner("Fetching latest player data...")
                    players_df, teams_df = cached_load_fpl_data()

                    if not players_df.empty:
                        st.session_state.players_df = players_df
                        st.session_state.teams_df = teams_df
                        st.session_state.data_loaded = True
                        create_success_animation("Data loaded successfully!")
                        st.rerun()
            return

        df = st.session_state.get('players_df')
        if df is None or df.empty:
            st.warning("Player data is not available. Please try refreshing.")
            return

        # Enhanced key metrics with modern cards
        st.markdown("### 📊 Key Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            self.ui_components.create_metric_card(
                "Total Players", f"{len(df):,}",
                delta=f"+{len(df)-500} from last season", icon="👥"
            )

        with col2:
            if 'cost_millions' in df.columns:
                avg_price = df['cost_millions'].mean()
                self.ui_components.create_metric_card(
                    "Average Price", f"£{avg_price:.1f}m",
                    delta="Market stable", icon="💰"
                )

        with col3:
            if 'total_points' in df.columns and len(df) > 0:
                top_scorer = df.loc[df['total_points'].idxmax()]
                self.ui_components.create_metric_card(
                    "Top Scorer", f"{top_scorer['web_name']}",
                    delta=f"{top_scorer['total_points']} points", icon="🏆"
                )

        with col4:
            if 'points_per_million' in df.columns and len(df) > 0:
                best_value = df.loc[df['points_per_million'].idxmax()]
                self.ui_components.create_metric_card(
                    "Best Value", f"{best_value['web_name']}",
                    delta=f"{best_value['points_per_million']:.1f} pts/£m", icon="💎"
                )

        # Interactive visualizations
        st.markdown("### 📈 Performance Insights")

        if len(df) > 0:
            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                if 'total_points' in df.columns and 'cost_millions' in df.columns:
                    DataVisualization.create_performance_chart(
                        df, 'cost_millions', 'total_points',
                        "Price vs Performance"
                    )

            with viz_col2:
                if 'element_type' in df.columns:
                    position_counts = df['element_type'].value_counts()
                    position_names = {1: 'Goalkeepers', 2: 'Defenders', 3: 'Midfielders', 4: 'Forwards'}
                    composition = {position_names.get(k, f'Position {k}'): v for k, v in position_counts.items()}
                    DataVisualization.create_team_balance_chart(composition)

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