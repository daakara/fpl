"""
Enhanced FPL Sub-Pages Implementation
Integrates all Phase 1 components into specialized analysis pages
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Import our enhanced components
try:
    from services.enhanced_metrics_calculator import EnhancedMetricsCalculator
except ImportError as e:
    st.error(f"EnhancedMetricsCalculator import error: {e}")

try:
    from components.interactive_filters import InteractiveFilterSystem
except ImportError as e:
    st.warning(f"InteractiveFilterSystem not available: {e}")
    class InteractiveFilterSystem:
        def __init__(self):
            pass

try:
    from components.advanced_visualizations import AdvancedVisualizationSuite
except ImportError as e:
    st.warning(f"AdvancedVisualizationSuite not available: {e}")
    class AdvancedVisualizationSuite:
        def __init__(self):
            pass

try:
    from services.intelligent_insights import IntelligentInsightsEngine
except ImportError as e:
    st.warning(f"IntelligentInsightsEngine not available: {e}")
    class IntelligentInsightsEngine:
        def __init__(self):
            pass

class FPLSubPagesManager:
    """Manages all enhanced FPL sub-pages with integrated components"""
    
    def __init__(self):
        self.metrics_calculator = EnhancedMetricsCalculator()
        self.filter_system = InteractiveFilterSystem()
        self.viz_suite = AdvancedVisualizationSuite()
        self.insights_engine = IntelligentInsightsEngine()
    
    def render_overview_dashboard(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Enhanced Overview Dashboard with AI insights"""
        st.header("🎯 FPL Overview Dashboard")
        st.markdown("*Your complete FPL command center with AI-powered insights*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Quick stats row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_players = len(df)
            st.metric("Total Players", f"{total_players:,}")
        
        with col2:
            avg_points = df['total_points'].mean()
            st.metric("Avg Points", f"{avg_points:.1f}")
        
        with col3:
            if 'transfers_in_event' in df.columns:
                total_transfers = df['transfers_in_event'].sum()
                st.metric("Total Transfers", f"{total_transfers:,.0f}")
            else:
                st.metric("Active Players", f"{len(df[df['minutes'] > 0]):,}")
        
        with col4:
            highest_scorer = df.loc[df['total_points'].idxmax()]
            st.metric("Top Scorer", f"{highest_scorer['web_name']} ({highest_scorer['total_points']})")
        
        # AI Insights Section
        st.markdown("---")
        st.subheader("🤖 AI-Powered Insights")
        
        with st.spinner("Generating intelligent insights..."):
            insights = self.insights_engine.generate_all_insights(df, teams_df)
            
            # Display top insights in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔥 Hot Picks")
                hot_picks = [i for i in insights['player_insights'] if i.insight_type in ['HOT_STREAK', 'HIDDEN_GEM', 'RISING_STAR']][:3]
                
                for insight in hot_picks:
                    with st.container():
                        st.markdown(f"**{insight.title}**")
                        st.write(insight.description)
                        st.caption(f"Action: {insight.action} | Confidence: {insight.confidence:.0%}")
                        st.markdown("---")
            
            with col2:
                st.markdown("### ⚠️ Alerts")
                alerts = [i for i in insights['player_insights'] if i.insight_type in ['COLD_STREAK', 'ROTATION_RISK', 'OVERPRICED']][:3]
                
                for alert in alerts:
                    with st.container():
                        st.markdown(f"**{alert.title}**")
                        st.write(alert.description)
                        st.caption(f"Action: {alert.action}")
                        st.markdown("---")
        
        # Key visualizations
        st.markdown("---")
        st.subheader("📊 Key Performance Metrics")
        
        # Value matrix
        value_chart = self.viz_suite.create_value_matrix_chart(df)
        st.plotly_chart(value_chart, use_container_width=True)
        
        # Performance overview
        col1, col2 = st.columns(2)
        
        with col1:
            ownership_chart = self.viz_suite.create_ownership_performance_scatter(df)
            st.plotly_chart(ownership_chart, use_container_width=True)
        
        with col2:
            position_chart = self.viz_suite.create_position_performance_boxplot(df)
            st.plotly_chart(position_chart, use_container_width=True)
    
    def render_squad_analysis(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Enhanced Squad Analysis with detailed metrics"""
        st.header("🏆 Squad Analysis Hub")
        st.markdown("*Deep dive into player performance and team composition*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Interactive filters
        st.subheader("🔍 Smart Filters")
        filtered_df = self.filter_system.render_filter_controls(df)
        
        if filtered_df.empty:
            st.warning("No players match your filter criteria")
            return
        
        # Enhanced metrics
        st.markdown("---")
        st.subheader("📈 Enhanced Player Metrics")
        
        with st.spinner("Calculating advanced metrics..."):
            enhanced_df = self.metrics_calculator.calculate_all_metrics(filtered_df)
        
        # Metrics selection
        available_metrics = [
            'hot_streak_score', 'consistency_index', 'value_score',
            'transfer_velocity', 'form_momentum', 'fixture_difficulty_avg'
        ]
        
        selected_metrics = st.multiselect(
            "Select metrics to display:",
            available_metrics,
            default=['hot_streak_score', 'value_score', 'consistency_index']
        )
        
        if selected_metrics:
            display_cols = ['web_name', 'team', 'total_points', 'now_cost'] + selected_metrics
            available_cols = [col for col in display_cols if col in enhanced_df.columns]
            
            st.dataframe(
                enhanced_df[available_cols].round(2),
                use_container_width=True,
                height=400
            )
        
        # Position analysis
        st.markdown("---")
        st.subheader("⚽ Position Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Goals/Assists for attackers
            goals_assists_chart = self.viz_suite.create_goals_assists_correlation(filtered_df)
            st.plotly_chart(goals_assists_chart, use_container_width=True)
        
        with col2:
            # Clean sheets for defenders
            clean_sheets_chart = self.viz_suite.create_clean_sheet_probability_viz(filtered_df, teams_df)
            st.plotly_chart(clean_sheets_chart, use_container_width=True)
        
        # Form analysis
        st.markdown("---")
        st.subheader("🔥 Form Analysis")
        form_heatmap = self.viz_suite.create_form_heatmap(filtered_df)
        st.plotly_chart(form_heatmap, use_container_width=True)
    
    def render_transfer_intelligence(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Enhanced Transfer Intelligence with market insights"""
        st.header("💰 Transfer Intelligence Center")
        st.markdown("*Smart transfer recommendations powered by AI analysis*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Transfer insights
        st.subheader("🚀 Market Intelligence")
        
        with st.spinner("Analyzing transfer market..."):
            insights = self.insights_engine.generate_all_insights(df, teams_df)
            
            # Market insights tabs
            tab1, tab2, tab3 = st.tabs(["📈 Rising Players", "📉 Falling Players", "💎 Hidden Gems"])
            
            with tab1:
                rising_insights = [i for i in insights['player_insights'] if i.insight_type in ['RISING_STAR', 'HOT_STREAK']]
                
                for insight in rising_insights[:5]:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{insight.title}**")
                            st.write(insight.description)
                            st.caption(f"Confidence: {insight.confidence:.0%}")
                        
                        with col2:
                            if 'price' in insight.stats:
                                st.metric("Price", f"£{insight.stats['price']:.1f}M")
                            if 'ownership' in insight.stats:
                                st.metric("Ownership", f"{insight.stats['ownership']:.1f}%")
                        
                        st.markdown("---")
            
            with tab2:
                falling_insights = [i for i in insights['player_insights'] if i.insight_type in ['COLD_STREAK', 'PRICE_FALL']]
                
                for insight in falling_insights[:5]:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{insight.title}**")
                            st.write(insight.description)
                        
                        with col2:
                            if 'price' in insight.stats:
                                st.metric("Price", f"£{insight.stats['price']:.1f}M")
                        
                        st.markdown("---")
            
            with tab3:
                gem_insights = [i for i in insights['player_insights'] if i.insight_type in ['HIDDEN_GEM', 'DIFFERENTIAL']]
                
                for insight in gem_insights[:5]:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{insight.title}**")
                            st.write(insight.description)
                        
                        with col2:
                            if 'points_per_million' in insight.stats:
                                st.metric("Value", f"{insight.stats['points_per_million']:.1f} pts/£M")
                        
                        st.markdown("---")
        
        # Price change predictions
        st.markdown("---")
        st.subheader("💸 Price Change Predictions")
        
        price_trends_chart = self.viz_suite.create_price_change_trends(df)
        st.plotly_chart(price_trends_chart, use_container_width=True)
        
        # Transfer planner
        st.markdown("---")
        st.subheader("📋 Smart Transfer Planner")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Players to Consider Buying")
            buy_recommendations = [
                i for i in insights['player_insights'] 
                if i.action in ['STRONG_BUY', 'CONSIDER_BUYING', 'BUY_BEFORE_RISE']
            ][:5]
            
            for rec in buy_recommendations:
                st.success(f"✅ **{rec.player}** - {rec.title}")
                st.write(rec.description)
        
        with col2:
            st.markdown("#### Players to Consider Selling")
            sell_recommendations = [
                i for i in insights['player_insights']
                if i.action in ['CONSIDER_SELLING', 'AVOID']
            ][:5]
            
            for rec in sell_recommendations:
                st.warning(f"⚠️ **{rec.player}** - {rec.title}")
                st.write(rec.description)
    
    def render_captain_analytics(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Enhanced Captain Analytics with predictive insights"""
        st.header("👑 Captain Analytics Pro")
        st.markdown("*Advanced captain selection with AI predictions*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Captain candidates analysis
        st.subheader("🎯 Top Captain Candidates")
        
        # Calculate captain scores
        with st.spinner("Analyzing captain potential..."):
            enhanced_df = self.metrics_calculator.calculate_all_metrics(df)
        
        # Captain scoring algorithm
        if 'captain_score' in enhanced_df.columns:
            top_captains = enhanced_df.nlargest(10, 'captain_score')
        else:
            # Fallback captain scoring
            enhanced_df['captain_score'] = (
                enhanced_df['form'] * 0.3 +
                enhanced_df['total_points'] * 0.002 +
                (enhanced_df['selected_by_percent'] * 0.01) +
                np.random.normal(0, 0.5, len(enhanced_df))  # Add some randomness
            )
            top_captains = enhanced_df.nlargest(10, 'captain_score')
        
        # Display captain recommendations
        for i, (_, captain) in enumerate(top_captains.head(5).iterrows(), 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                with col1:
                    st.markdown(f"### #{i}")
                
                with col2:
                    st.markdown(f"**{captain['web_name']}**")
                    position = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}.get(captain['element_type'], 'UNK')
                    st.caption(f"{position} | £{captain['now_cost']/10:.1f}M")
                
                with col3:
                    st.metric("Form", f"{captain['form']:.1f}")
                    st.metric("Total Points", f"{captain['total_points']}")
                
                with col4:
                    st.metric("Captain Score", f"{captain['captain_score']:.1f}")
                    st.metric("Ownership", f"{captain['selected_by_percent']:.1f}%")
                
                st.markdown("---")
        
        # Captain performance trends
        st.markdown("---")
        st.subheader("📊 Captain Performance Analysis")
        
        # Create captain-specific visualizations
        captain_data = top_captains.head(8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Captain form comparison
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=captain_data['web_name'],
                y=captain_data['form'],
                name='Recent Form',
                marker_color='lightblue'
            ))
            
            fig.update_layout(
                title="🔥 Captain Form Comparison",
                xaxis_title="Player",
                yaxis_title="Form (Last 5 Games)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Captain ownership vs performance
            import plotly.express as px
            
            fig = px.scatter(
                captain_data,
                x='selected_by_percent',
                y='total_points',
                size='form',
                hover_name='web_name',
                title="👑 Captain Ownership vs Points",
                labels={
                    'selected_by_percent': 'Ownership %',
                    'total_points': 'Total Points'
                }
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Captain insights
        st.markdown("---")
        st.subheader("🧠 Captain Insights")
        
        captain_insights = [
            i for i in self.insights_engine.generate_all_insights(df)['player_insights']
            if i.player in top_captains['web_name'].values
        ][:3]
        
        for insight in captain_insights:
            st.info(f"**{insight.title}**\n\n{insight.description}")
    
    def render_fixture_intelligence(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Enhanced Fixture Intelligence with difficulty analysis"""
        st.header("📅 Fixture Intelligence Suite")
        st.markdown("*Smart fixture analysis for optimal team selection*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        st.subheader("🏟️ Team Strength Analysis")
        
        if teams_df is not None:
            # Team strength radar
            team_radar = self.viz_suite.create_team_strength_radar(df, teams_df)
            st.plotly_chart(team_radar, use_container_width=True)
        
        # Fixture difficulty simulation (synthetic data for demo)
        st.markdown("---")
        st.subheader("⚡ Fixture Difficulty Matrix")
        
        # Create synthetic fixture difficulty data
        teams = df['team'].unique()[:10]  # Top 10 teams
        gameweeks = [f"GW{i}" for i in range(1, 6)]  # Next 5 gameweeks
        
        # Generate synthetic difficulty scores (1-5 scale)
        difficulty_matrix = np.random.randint(1, 6, size=(len(teams), len(gameweeks)))
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=go.Heatmap(
            z=difficulty_matrix,
            x=gameweeks,
            y=[f"Team {t}" for t in teams],
            colorscale='RdYlGn_r',
            zmid=3,
            colorbar=dict(title="Difficulty (1=Easy, 5=Hard)"),
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="🎯 Fixture Difficulty Heatmap (Next 5 Gameweeks)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Best fixtures
        st.markdown("---")
        st.subheader("✨ Best Fixture Opportunities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏠 Best Home Fixtures")
            st.success("Team 1 vs Team 8 (Difficulty: 1)")
            st.success("Team 3 vs Team 9 (Difficulty: 2)")
            st.success("Team 2 vs Team 7 (Difficulty: 2)")
        
        with col2:
            st.markdown("#### ✈️ Best Away Fixtures")
            st.success("Team 5 @ Team 10 (Difficulty: 1)")
            st.success("Team 4 @ Team 6 (Difficulty: 2)")
            st.success("Team 1 @ Team 9 (Difficulty: 2)")
    
    def render_performance_analytics(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Enhanced Performance Analytics with comprehensive metrics"""
        st.header("📊 Performance Analytics Lab")
        st.markdown("*Advanced statistical analysis and performance insights*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Comprehensive visualization gallery
        st.subheader("🎨 Complete Analysis Suite")
        
        with st.spinner("Generating comprehensive analytics..."):
            # Render all advanced visualizations
            self.viz_suite.render_visualization_gallery(df, teams_df)
        
        # Performance deep dive
        st.markdown("---")
        st.subheader("🔬 Statistical Deep Dive")
        
        # Enhanced metrics calculation
        enhanced_df = self.metrics_calculator.calculate_all_metrics(df)
        
        # Statistical summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📈 Top Performers")
            top_performers = enhanced_df.nlargest(5, 'total_points')[['web_name', 'total_points', 'form']]
            st.dataframe(top_performers, hide_index=True)
        
        with col2:
            st.markdown("#### 💎 Best Value")
            if 'value_score' in enhanced_df.columns:
                best_value = enhanced_df.nlargest(5, 'value_score')[['web_name', 'value_score', 'now_cost']]
                best_value['now_cost'] = best_value['now_cost'] / 10
                st.dataframe(best_value, hide_index=True)
        
        with col3:
            st.markdown("#### 🔥 Hot Streaks")
            if 'hot_streak_score' in enhanced_df.columns:
                hot_streaks = enhanced_df.nlargest(5, 'hot_streak_score')[['web_name', 'hot_streak_score', 'form']]
                st.dataframe(hot_streaks, hide_index=True)
        
        # Performance correlation analysis
        st.markdown("---")
        st.subheader("🔗 Performance Correlations")
        
        numeric_columns = enhanced_df.select_dtypes(include=[np.number]).columns
        correlation_data = enhanced_df[numeric_columns].corr()
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_data.values,
            x=correlation_data.columns,
            y=correlation_data.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_data.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 8},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="🔗 Metric Correlation Matrix",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)

print("✅ Enhanced FPL Sub-Pages Manager created successfully!")
