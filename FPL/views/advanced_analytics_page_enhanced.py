"""
Advanced Analytics Page
Displays Expected Points, Differentials, and Captaincy Analysis
"""

import streamlit as st
import pandas as pd
from services.advanced_analytics_service import AdvancedAnalyticsService
from utils.performance_optimizer import LazyLoader


class AdvancedAnalyticsPage:
    """Advanced analytics features page"""
    
    def __init__(self):
        """Initialize the advanced analytics page"""
        self.analytics_service = AdvancedAnalyticsService()
    
    def render(self):
        """Render the advanced analytics page"""
        st.markdown("# 📊 Advanced Analytics")
        st.markdown("**AI-Powered insights for FPL success**")
        
        # Check if data is loaded
        if not st.session_state.get('data_loaded', False):
            st.warning("⚠️ Please load data from the Dashboard first")
            return
        
        df = st.session_state.get('players_df')
        if df is None or df.empty:
            st.error("❌ No player data available")
            return
        
        st.markdown("---")
        
        # Tab layout for different analytics
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Expected Points (xP)",
            "💎 Differential Finder",
            "👑 Captaincy Analysis",
            "📈 Combined Insights"
        ])
        
        with tab1:
            self._render_expected_points_tab(df)
        
        with tab2:
            self._render_differentials_tab(df)
        
        with tab3:
            self._render_captaincy_tab(df)
        
        with tab4:
            self._render_combined_insights(df)
    
    def _render_expected_points_tab(self, df: pd.DataFrame):
        """Render Expected Points analysis"""
        st.markdown("### 🎯 Expected Points (xP) Calculator")
        st.markdown("""
        Expected Points predicts player performance based on:
        - Recent form and points per game
        - Fixture difficulty
        - Playing time probability
        - Injury/suspension status
        - Position-specific factors
        """)
        
        st.markdown("---")
        
        # Calculate xP for all players
        with st.spinner("Calculating expected points..."):
            df_with_xp = self.analytics_service.xp_engine.calculate_xp_for_all_players(df)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            position_filter = st.selectbox(
                "Position",
                ["All", "Goalkeepers", "Defenders", "Midfielders", "Forwards"],
                key="xp_position"
            )
        
        with col2:
            min_minutes = st.slider(
                "Minimum Minutes",
                0, 2000, 500,
                step=100,
                key="xp_minutes"
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                ["Expected Points", "Form", "xP vs Form"],
                key="xp_sort"
            )
        
        # Apply filters
        filtered_df = df_with_xp[df_with_xp['minutes'] >= min_minutes].copy()
        
        if position_filter != "All":
            position_map = {
                "Goalkeepers": 1,
                "Defenders": 2,
                "Midfielders": 3,
                "Forwards": 4
            }
            filtered_df = filtered_df[filtered_df['element_type'] == position_map[position_filter]]
        
        # Sort
        sort_col_map = {
            "Expected Points": "expected_points",
            "Form": "form",
            "xP vs Form": "xp_vs_form"
        }
        filtered_df = filtered_df.sort_values(sort_col_map[sort_by], ascending=False)
        
        # Display top players
        st.markdown(f"#### Top Players by {sort_by}")
        
        # Add pagination
        from utils.performance_optimizer import PerformanceOptimizer
        
        if len(filtered_df) > 25:
            display_df = PerformanceOptimizer.paginate_dataframe(
                filtered_df,
                page_size=25,
                page_key="xp_page"
            )
        else:
            display_df = filtered_df
        
        # Prepare display columns
        if 'cost_millions' not in display_df.columns:
            display_df['cost_millions'] = display_df['now_cost'] / 10
        
        display_cols = ['web_name', 'element_type', 'cost_millions', 'form', 
                       'expected_points', 'xp_vs_form', 'minutes']
        display_cols = [col for col in display_cols if col in display_df.columns]
        
        # Display table
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "web_name": "Player",
                "element_type": "Position",
                "cost_millions": st.column_config.NumberColumn("Price", format="£%.1f"),
                "form": st.column_config.NumberColumn("Form", format="%.1f"),
                "expected_points": st.column_config.NumberColumn("xP", format="%.1f", 
                                                                 help="Expected points next GW"),
                "xp_vs_form": st.column_config.NumberColumn("xP vs Form", format="%.1f",
                                                            help="Difference between xP and form"),
                "minutes": "Minutes"
            }
        )
        
        # Visualization
        st.markdown("#### 📈 xP vs Current Form")
        
        plotly = LazyLoader.load_plotly()
        px = plotly['px']
        
        chart_df = filtered_df.head(50)  # Top 50 for clarity
        fig = px.scatter(
            chart_df,
            x='form',
            y='expected_points',
            hover_name='web_name',
            color='element_type',
            size='minutes',
            title="Expected Points vs Current Form (Size = Minutes Played)",
            labels={'form': 'Current Form', 'expected_points': 'Expected Points (xP)'}
        )
        
        # Add diagonal line (xP = form)
        import plotly.graph_objects as go
        fig.add_trace(go.Scatter(
            x=[0, 10],
            y=[0, 10],
            mode='lines',
            name='xP = Form',
            line=dict(dash='dash', color='gray')
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.markdown("#### 💡 Key Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔥 Outperforming Form (xP > Form)**")
            overperformers = filtered_df[filtered_df['xp_vs_form'] > 1.0].head(5)
            if len(overperformers) > 0:
                for _, player in overperformers.iterrows():
                    st.markdown(f"✅ **{player['web_name']}** - xP: {player['expected_points']:.1f}, Form: {player['form']:.1f}")
            else:
                st.info("No significant outperformers found")
        
        with col2:
            st.markdown("**📉 Underperforming Form (xP < Form)**")
            underperformers = filtered_df[filtered_df['xp_vs_form'] < -1.0].head(5)
            if len(underperformers) > 0:
                for _, player in underperformers.iterrows():
                    st.markdown(f"⚠️ **{player['web_name']}** - xP: {player['expected_points']:.1f}, Form: {player['form']:.1f}")
            else:
                st.info("No significant underperformers found")
    
    def _render_differentials_tab(self, df: pd.DataFrame):
        """Render Differential Finder analysis"""
        st.markdown("### 💎 Differential Finder")
        st.markdown("""
        Find low-ownership, high-potential players to gain advantage in mini-leagues.
        **Differential Score** = Form × 2 + (Max Ownership - Actual Ownership) × 0.5 + Value × 1.5
        """)
        
        st.markdown("---")
        
        # Three categories of differentials
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🌟 All Differentials")
            st.caption("Ownership < 5%, Points > 30, Form > 5")
        
        with col2:
            st.markdown("#### 💰 Premium Differentials")
            st.caption("Ownership < 20%, Points > 50, Form > 6")
        
        with col3:
            st.markdown("#### 🎯 Budget Differentials")
            st.caption("< £6.0m, Ownership < 10%, Points > 25")
        
        st.markdown("---")
        
        # Custom filters
        with st.expander("⚙️ Custom Filters", expanded=False):
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
            
            with filter_col1:
                max_ownership = st.slider("Max Ownership %", 0.0, 50.0, 5.0, 0.5)
            
            with filter_col2:
                min_points = st.number_input("Min Total Points", 0, 200, 30, 5)
            
            with filter_col3:
                min_form = st.slider("Min Form", 0.0, 10.0, 5.0, 0.5)
            
            with filter_col4:
                max_price = st.number_input("Max Price (£m)", 4.0, 15.0, 15.0, 0.5)
        
        # Calculate differentials
        with st.spinner("Finding differentials..."):
            custom_diff = self.analytics_service.differential_finder.find_differentials(
                df, max_ownership, min_points, min_form, max_price
            )
            premium_diff = self.analytics_service.differential_finder.find_premium_differentials(df)
            budget_diff = self.analytics_service.differential_finder.find_budget_differentials(df)
        
        # Display in tabs
        diff_tab1, diff_tab2, diff_tab3 = st.tabs([
            "🎯 Custom Search",
            "💰 Premium (£9m+)",
            "🏦 Budget (<£6m)"
        ])
        
        with diff_tab1:
            self._display_differential_table(custom_diff, "Custom Differential Search")
        
        with diff_tab2:
            self._display_differential_table(premium_diff, "Premium Differentials")
        
        with diff_tab3:
            self._display_differential_table(budget_diff, "Budget Differentials")
    
    def _display_differential_table(self, df: pd.DataFrame, title: str):
        """Display a differential table"""
        if df.empty:
            st.info(f"No players found matching the criteria")
            return
        
        st.markdown(f"#### {title}")
        st.caption(f"Found {len(df)} potential differentials")
        
        # Add pagination
        from utils.performance_optimizer import PerformanceOptimizer
        
        if len(df) > 20:
            display_df = PerformanceOptimizer.paginate_dataframe(
                df,
                page_size=20,
                page_key=f"diff_{title.replace(' ', '_')}"
            )
        else:
            display_df = df
        
        # Display table
        display_cols = ['web_name', 'cost_millions', 'total_points', 'form',
                       'selected_by_percent', 'differential_score', 'minutes']
        display_cols = [col for col in display_cols if col in display_df.columns]
        
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "web_name": "Player",
                "cost_millions": st.column_config.NumberColumn("Price", format="£%.1f"),
                "total_points": "Points",
                "form": st.column_config.NumberColumn("Form", format="%.1f"),
                "selected_by_percent": st.column_config.NumberColumn("Own%", format="%.1f%%"),
                "differential_score": st.column_config.NumberColumn("Diff Score", format="%.1f",
                                                                   help="Higher = Better differential"),
                "minutes": "Minutes"
            }
        )
    
    def _render_captaincy_tab(self, df: pd.DataFrame):
        """Render Captaincy Analysis"""
        st.markdown("### 👑 Captaincy Analysis")
        st.markdown("""
        **Captain Expected Value (EV)** = (Expected Points × 2 × Starting Probability) - Risk Factor
        
        Choose between **safe** options (high ownership) or **differential** captains (low ownership for mini-league gains).
        """)
        
        st.markdown("---")
        
        # Two columns for different captain types
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🛡️ Safe Captain Options")
            st.caption("High ownership, reliable options")
            
            with st.spinner("Analyzing safe captains..."):
                safe_captains = self.analytics_service.captaincy_analyzer.get_top_captain_options(
                    df, fixtures=None, top_n=10, min_ownership=15.0
                )
            
            if not safe_captains.empty:
                self._display_captain_table(safe_captains, "safe")
            else:
                st.info("No captain options found")
        
        with col2:
            st.markdown("#### ⚡ Differential Captains")
            st.caption("Lower ownership, higher risk/reward")
            
            with st.spinner("Finding differential captains..."):
                diff_captains = self.analytics_service.captaincy_analyzer.get_differential_captain_options(
                    df, fixtures=None, max_ownership=15.0
                )
            
            if not diff_captains.empty:
                self._display_captain_table(diff_captains, "diff")
            else:
                st.info("No differential captain options found")
        
        # Captain EV visualization
        st.markdown("---")
        st.markdown("#### 📊 Captain EV Comparison")
        
        # Combine both for visualization
        all_captains = pd.concat([safe_captains.head(5), diff_captains.head(5)]).reset_index(drop=True)
        
        if not all_captains.empty:
            plotly = LazyLoader.load_plotly()
            px = plotly['px']
            
            fig = px.bar(
                all_captains.head(10),
                x='web_name',
                y='captain_ev',
                color='selected_by_percent',
                title="Top 10 Captain Options by Expected Value",
                labels={'web_name': 'Player', 'captain_ev': 'Captain EV',
                       'selected_by_percent': 'Ownership %'},
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _display_captain_table(self, df: pd.DataFrame, prefix: str):
        """Display a captain options table"""
        display_cols = ['web_name', 'cost_millions', 'selected_by_percent',
                       'form', 'captain_ev', 'captain_xp', 'starting_prob', 'risk_factor']
        display_cols = [col for col in display_cols if col in df.columns]
        
        st.dataframe(
            df.head(10)[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "web_name": "Player",
                "cost_millions": st.column_config.NumberColumn("Price", format="£%.1f"),
                "selected_by_percent": st.column_config.NumberColumn("Own%", format="%.1f%%"),
                "form": st.column_config.NumberColumn("Form", format="%.1f"),
                "captain_ev": st.column_config.NumberColumn("Captain EV", format="%.2f",
                                                           help="Expected value as captain"),
                "captain_xp": st.column_config.NumberColumn("2×xP", format="%.1f"),
                "starting_prob": st.column_config.NumberColumn("Start %", format="%.0f%%"),
                "risk_factor": st.column_config.NumberColumn("Risk", format="%.2f")
            }
        )
    
    def _render_combined_insights(self, df: pd.DataFrame):
        """Render combined insights from all analytics"""
        st.markdown("### 📈 Combined Insights Dashboard")
        st.markdown("All analytics combined for comprehensive FPL strategy")
        
        st.markdown("---")
        
        with st.spinner("Generating comprehensive analytics..."):
            analytics = self.analytics_service.get_comprehensive_analytics(df)
        
        # Key insights cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            top_xp = analytics['players_with_xp'].nlargest(1, 'expected_points').iloc[0]
            st.metric(
                "🎯 Highest xP",
                top_xp['web_name'],
                f"{top_xp['expected_points']:.1f} pts"
            )
        
        with col2:
            if not analytics['all_differentials'].empty:
                top_diff = analytics['all_differentials'].iloc[0]
                st.metric(
                    "💎 Top Differential",
                    top_diff['web_name'],
                    f"{top_diff['selected_by_percent']:.1f}% owned"
                )
        
        with col3:
            if not analytics['top_captains'].empty:
                top_cap = analytics['top_captains'].iloc[0]
                st.metric(
                    "👑 Best Captain",
                    top_cap['web_name'],
                    f"EV: {top_cap['captain_ev']:.2f}"
                )
        
        with col4:
            total_differentials = len(analytics['all_differentials'])
            st.metric(
                "🔍 Differentials Found",
                total_differentials,
                "Available options"
            )
        
        st.markdown("---")
        
        # Summary tables
        summary_tab1, summary_tab2, summary_tab3 = st.tabs([
            "🌟 Best Overall Players",
            "💡 Transfer Recommendations",
            "📋 Quick Reference"
        ])
        
        with summary_tab1:
            st.markdown("#### Top Players by Combined Metrics")
            
            # Combine xP, form, value
            combined = analytics['players_with_xp'].copy()
            combined['combined_score'] = (
                combined['expected_points'] * 2 +
                combined['form'] * 1.5 +
                (combined['total_points'] / (combined.get('cost_millions', combined['now_cost'] / 10))) * 1.0
            )
            
            top_combined = combined.nlargest(20, 'combined_score')
            
            from utils.performance_optimizer import PerformanceOptimizer
            display_df = PerformanceOptimizer.paginate_dataframe(
                top_combined,
                page_size=10,
                page_key="combined_best"
            )
            
            st.dataframe(
                display_df[['web_name', 'element_type', 'expected_points', 'form',
                          'selected_by_percent', 'combined_score']],
                use_container_width=True,
                hide_index=True
            )
        
        with summary_tab2:
            st.markdown("#### 🔄 Smart Transfer Suggestions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**💚 Players to Target**")
                st.markdown("High xP + Low ownership + Good value")
                
                targets = analytics['all_differentials'].head(5)
                for _, player in targets.iterrows():
                    st.markdown(f"✅ **{player['web_name']}** - £{player['cost_millions']:.1f}m, {player['selected_by_percent']:.1f}% owned")
            
            with col2:
                st.markdown("**🔴 Players to Avoid**")
                st.markdown("Low xP despite high form")
                
                avoid = analytics['players_with_xp'][
                    analytics['players_with_xp']['xp_vs_form'] < -2.0
                ].head(5)
                
                for _, player in avoid.iterrows():
                    st.markdown(f"⚠️ **{player['web_name']}** - xP: {player['expected_points']:.1f}, Form: {player['form']:.1f}")
        
        with summary_tab3:
            st.markdown("#### 📋 Quick Reference Guide")
            
            st.markdown("""
            **Key Metrics Explained:**
            
            - **xP (Expected Points)**: Predicted points for next gameweek based on form, fixtures, and injury risk
            - **Differential Score**: Combined metric for low-owned, high-value players
            - **Captain EV**: Expected value when captaining a player (accounts for risk)
            - **xP vs Form**: Shows if a player's expected performance differs from recent form
            
            **How to Use This Data:**
            
            1. **For Transfers**: Look at differentials with high xP
            2. **For Captaincy**: Check Captain EV column, balance risk vs reward
            3. **For Long-term Planning**: Monitor xP trends vs current form
            4. **For Mini-leagues**: Target differential captains when chasing
            """)
