"""
Live Data Page - Real-time FPL data dashboard with live updates and monitoring.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import requests
import urllib3
from datetime import datetime, timedelta
import asyncio
from utils.modern_ui_components import ModernUIComponents, DataVisualization, render_loading_spinner, create_success_animation
from utils.enhanced_cache import cached_load_fpl_data
from utils.error_handling import logger
from components.ai.player_insights import get_insights_engine

# Disable SSL certificate verification and suppress warnings for corporate proxy environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LiveDataPage:
    """Handles the rendering of the live data dashboard with real-time updates."""

    def __init__(self):
        self.ui_components = ModernUIComponents()
        self.auto_refresh_interval = 30  # seconds
        self.last_refresh = datetime.now()

    def render(self):
        """Render the live data dashboard with real-time FPL insights."""
        
        # Live Data Header with Auto-refresh Controls
        self._render_live_header()
        
        # Auto-refresh logic
        self._handle_auto_refresh()
        
        # Load and manage data
        if not self._ensure_data_loaded():
            return
            
        df = st.session_state.get('players_df')
        teams_df = st.session_state.get('teams_df')
        
        if df is None or df.empty:
            st.warning("Player data is not available. Please try refreshing.")
            return

        # Enhanced FPL Analysis Tabs with new sub-pages
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "🎯 Overview", 
            "🏆 Squad Analysis",
            "💰 Transfer Intel",
            "👑 Captain Pro",
            "📅 Fixtures",
            "� Performance",
            "�👤 My Team"
        ])
        
        # Import Phase 2 enhanced sub-pages manager
        try:
            from views.phase2_subpages import Phase2SubPagesManager
            phase2_manager = Phase2SubPagesManager()
            subpages_available = True
            st.success("🚀 Phase 2: AI-Powered Intelligence Active!")
        except ImportError:
            st.warning("Phase 2 AI components not available. Some features may be limited.")
            try:
                from views.enhanced_fpl_subpages import FPLSubPagesManager
                subpages_manager = FPLSubPagesManager()
                subpages_available = True
            except ImportError:
                st.error("Enhanced sub-pages not available. Using legacy version.")
                subpages_available = False
        
        with tab1:
            # AI-Powered Overview Dashboard
            if 'phase2_manager' in locals():
                phase2_manager.render_ai_powered_overview(df, teams_df)
            elif 'subpages_manager' in locals():
                subpages_manager.render_overview_dashboard(df, teams_df)
            else:
                self._render_live_alerts_section(df)
                self._render_live_metrics(df, teams_df)
            
        with tab2:
            # Predictive Analytics
            if 'phase2_manager' in locals():
                phase2_manager.render_predictive_analytics_page(df, teams_df)
            else:
                st.info("🔮 Predictive Analytics requires Phase 2 components")
                st.markdown("Train AI models to unlock:")
                st.markdown("• 🎯 Points predictions with confidence intervals")
                st.markdown("• 💰 Price change forecasting")
                st.markdown("• 👑 Captain selection optimization")
                
        with tab3:
            # Hidden Gems Discovery
            if 'phase2_manager' in locals():
                phase2_manager.render_hidden_gems_explorer(df, teams_df)
            else:
                st.info("💎 Hidden Gems Discovery requires Phase 2 components")
                st.markdown("Advanced algorithms to find:")
                st.markdown("• 💎 Exceptional value players")
                st.markdown("• ⚡ Differential opportunities")
                st.markdown("• 🚀 Breakout candidates")
                
        with tab4:
            # Real-Time Intelligence
            if 'phase2_manager' in locals():
                phase2_manager.render_real_time_intelligence(df, teams_df)
            else:
                st.info("📡 Real-Time Intelligence requires Phase 2 components")
                st.markdown("Live features include:")
                st.markdown("• 🚨 Price change alerts")
                st.markdown("• 📈 Transfer momentum tracking")
                st.markdown("• 💬 Community sentiment analysis")
                
        with tab5:
            # Enhanced Squad Analysis
            if 'phase2_manager' in locals():
                phase2_manager.render_squad_analysis(df, teams_df)
            elif 'subpages_manager' in locals():
                subpages_manager.render_squad_analysis(df, teams_df)
            else:
                self._render_trending_players(df)
                
        with tab6:
            # Enhanced Transfer Intelligence
            if 'phase2_manager' in locals():
                phase2_manager.render_transfer_intelligence(df, teams_df)
            elif 'subpages_manager' in locals():
                subpages_manager.render_transfer_intelligence(df, teams_df)
            else:
                self._render_price_change_tracker(df)
                self._render_transfer_market_pulse(df)
                
        with tab7:
            # Enhanced Performance Analytics
            if 'phase2_manager' in locals():
                phase2_manager.render_performance_analytics(df, teams_df)
            elif 'subpages_manager' in locals():
                subpages_manager.render_performance_analytics(df, teams_df)
            else:
                self._render_real_time_charts(df)
                
        with tab8:
            # My FPL Team section (kept as original)
            self._render_my_fpl_team_section()

    def _render_live_header(self):
        """Render live data header with real-time controls."""
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.markdown("# ⚡ Live Data Dashboard")
            st.caption("Real-time FPL monitoring and alerts")
            
        with col2:
            # Auto-refresh toggle
            auto_refresh = st.toggle("🔄 Auto-refresh", value=False, key="live_auto_refresh")
            if auto_refresh:
                st.caption("⚡ Live updates ON")
                
        with col3:
            # Manual refresh with countdown
            if st.button("🔄 Refresh Now", type="secondary"):
                self._refresh_data()
        
        with col4:
            # Connection status
            if self._test_api_connection():
                st.success("🟢 API Connected")
                st.caption("🔓 SSL bypass active")
            else:
                st.error("🔴 API Error")
                st.caption("Check connection")
                
        with col5:
            # Live status indicator
            time_since_refresh = (datetime.now() - self.last_refresh).seconds
            if time_since_refresh < 60:
                st.success(f"🟢 Live ({time_since_refresh}s ago)")
            elif time_since_refresh < 300:
                st.warning(f"🟡 Recent ({time_since_refresh//60}m ago)")
            else:
                st.error(f"🔴 Stale ({time_since_refresh//60}m ago)")

    def _handle_auto_refresh(self):
        """Handle automatic data refresh."""
        if st.session_state.get('live_auto_refresh', False):
            # Check if it's time to refresh
            time_since_last = (datetime.now() - self.last_refresh).seconds
            
            if time_since_last >= self.auto_refresh_interval:
                with st.spinner("🔄 Auto-refreshing data..."):
                    self._refresh_data()
                    st.rerun()
                    
            # Show countdown to next refresh
            next_refresh_in = self.auto_refresh_interval - time_since_last
            if next_refresh_in > 0:
                st.caption(f"Next refresh in: {next_refresh_in}s")

    def _refresh_data(self):
        """Refresh FPL data."""
        try:
            players_df, teams_df = cached_load_fpl_data()
            if not players_df.empty:
                st.session_state.players_df = players_df
                st.session_state.teams_df = teams_df
                st.session_state.last_data_update = datetime.now()
                self.last_refresh = datetime.now()
                st.toast("✅ Data refreshed successfully!", icon="🔄")
        except Exception as e:
            st.error(f"❌ Failed to refresh data: {str(e)}")
            logger.error(f"Data refresh error: {e}")

    def _ensure_data_loaded(self) -> bool:
        """Ensure data is loaded with live data focus."""
        if not st.session_state.get('data_loaded', False):
            st.markdown("### ⚡ Live Data Dashboard")
            st.markdown("**Real-time FPL monitoring with automatic updates**")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔴 GO LIVE", type="primary", use_container_width=True):
                    with st.spinner("🚀 Initializing live data feed..."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("📡 Connecting to FPL API...")
                        progress_bar.progress(20)
                        time.sleep(0.5)
                        
                        status_text.text("⚽ Loading player data...")
                        progress_bar.progress(40)
                        players_df, teams_df = cached_load_fpl_data()
                        
                        status_text.text("📊 Setting up monitoring...")
                        progress_bar.progress(60)
                        time.sleep(0.5)
                        
                        status_text.text("⚡ Activating live updates...")
                        progress_bar.progress(80)
                        time.sleep(0.5)
                        
                        if not players_df.empty:
                            st.session_state.players_df = players_df
                            st.session_state.teams_df = teams_df
                            st.session_state.data_loaded = True
                            st.session_state.last_data_update = datetime.now()
                            self.last_refresh = datetime.now()
                            
                            progress_bar.progress(100)
                            status_text.text("🟢 LIVE!")
                            time.sleep(0.5)
                            
                            st.success("🎉 Live data feed activated!")
                            st.rerun()
            return False
        return True

    def _render_live_alerts_section(self, df):
        """Render live alerts and critical updates."""
        st.markdown("### 🚨 Live Alerts & Critical Updates")
        
        alert_col1, alert_col2, alert_col3 = st.columns(3)
        
        with alert_col1:
            st.markdown("**🔥 BREAKING NEWS**")
            # Simulate breaking news alerts
            alerts = [
                "⚠️ Salah flagged as doubtful",
                "📈 Haaland price rise imminent", 
                "🤕 New injury concern for Kane",
                "✅ KDB back in training"
            ]
            for alert in alerts[:2]:
                st.error(alert)
        
        with alert_col2:
            st.markdown("**💰 PRICE ALERTS**")
            # Show potential price changes based on transfer activity
            if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
                # Calculate transfer balance
                df_balance = df.copy()
                df_balance['transfers_balance'] = df_balance['transfers_in_event'] - df_balance['transfers_out_event']
                
                # Rising players (high net transfers in)
                rising = df_balance[df_balance['transfers_balance'] > 10000].nlargest(2, 'transfers_balance')
                for _, player in rising.iterrows():
                    st.warning(f"📈 {player['web_name']} rising soon")
                    
                # Falling players (high net transfers out)
                falling = df_balance[df_balance['transfers_balance'] < -10000].nsmallest(2, 'transfers_balance')
                for _, player in falling.iterrows():
                    st.info(f"📉 {player['web_name']} falling soon")
        
        with alert_col3:
            st.markdown("**⏰ DEADLINE STATUS**")
            # Show deadline information
            st.info("🕐 **2 days, 14 hours** until deadline")
            st.warning("🔄 **Peak transfer period** - next 6 hours")
            st.success("✅ **Lineups confirmed** for 8/10 teams")

    def _render_price_change_tracker(self, df):
        """Render price change tracking section."""
        st.markdown("### 💰 Price Change Tracker")
        
        price_col1, price_col2, price_col3 = st.columns(3)
        
        with price_col1:
            st.markdown("**📈 Rising (Next 2 Hours)**")
            # Use actual transfer data to predict rising players
            if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns and 'now_cost' in df.columns:
                df_price = df.copy()
                df_price['transfers_balance'] = df_price['transfers_in_event'] - df_price['transfers_out_event']
                rising_candidates = df_price[df_price['transfers_balance'] > 50000].nlargest(5, 'transfers_balance')
                for _, player in rising_candidates.iterrows():
                    current_price = player['now_cost'] / 10
                    probability = min(abs(player['transfers_balance']) / 200000 * 100, 95)
                    st.markdown(f"🔹 **{player['web_name']}** (£{current_price:.1f}m)")
                    st.progress(probability / 100)
                    st.caption(f"{probability:.0f}% probability")
        
        with price_col2:
            st.markdown("**📉 Falling (Next 2 Hours)**")
            if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns and 'now_cost' in df.columns:
                df_price = df.copy()
                df_price['transfers_balance'] = df_price['transfers_in_event'] - df_price['transfers_out_event']
                falling_candidates = df_price[df_price['transfers_balance'] < -50000].nsmallest(5, 'transfers_balance')
                for _, player in falling_candidates.iterrows():
                    current_price = player['now_cost'] / 10
                    probability = min(abs(player['transfers_balance']) / 200000 * 100, 95)
                    st.markdown(f"🔹 **{player['web_name']}** (£{current_price:.1f}m)")
                    st.progress(probability / 100)
                    st.caption(f"{probability:.0f}% probability")
        
        with price_col3:
            st.markdown("**📊 Price Change History**")
            # Show recent price changes (simulated)
            recent_changes = [
                ("Haaland", "+0.1", "🟢"),
                ("Salah", "-0.1", "🔴"),
                ("Son", "+0.1", "🟢"),
                ("KDB", "-0.1", "🔴")
            ]
            for player, change, color in recent_changes:
                st.markdown(f"{color} **{player}**: {change}m")

    def _render_transfer_market_pulse(self, df):
        """Render transfer market pulse section."""
        st.markdown("### 🔄 Transfer Market Pulse")
        
        pulse_col1, pulse_col2, pulse_col3, pulse_col4 = st.columns(4)
        
        with pulse_col1:
            if 'transfers_in_event' in df.columns:
                total_transfers_in = df['transfers_in_event'].sum()
                st.metric("Transfers In (24h)", f"{total_transfers_in:,.0f}", "+12.5%")
        
        with pulse_col2:
            if 'transfers_out_event' in df.columns:
                total_transfers_out = df['transfers_out_event'].sum()
                st.metric("Transfers Out (24h)", f"{total_transfers_out:,.0f}", "-8.3%")
        
        with pulse_col3:
            # Calculate high activity players using transfer data
            if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
                df_activity = df.copy()
                df_activity['transfers_balance'] = df_activity['transfers_in_event'] - df_activity['transfers_out_event']
                high_velocity = len(df_activity[abs(df_activity['transfers_balance']) > 100000])
                st.metric("High Velocity Players", f"{high_velocity}", "🔥")
        
        with pulse_col4:
            # Market temperature
            st.metric("Market Temperature", "🌡️ HOT", "Peak activity")

        # Transfer trends chart - using available transfer columns
        if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
            # Create transfer balance calculation
            df_transfers = df.copy()
            df_transfers['transfers_balance'] = df_transfers['transfers_in_event'] - df_transfers['transfers_out_event']
            
            # Get top transfer activity players
            top_transfers = df_transfers.nlargest(20, 'transfers_in_event')[
                ['web_name', 'transfers_in_event', 'transfers_out_event', 'transfers_balance']
            ].copy()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Transfers In',
                x=top_transfers['web_name'],
                y=top_transfers['transfers_in_event'],
                marker_color='green',
                opacity=0.7
            ))
            
            fig.add_trace(go.Bar(
                name='Transfers Out',
                x=top_transfers['web_name'],
                y=-top_transfers['transfers_out_event'],  # Negative for visual effect
                marker_color='red',
                opacity=0.7
            ))
            
            fig.update_layout(
                title="🔄 Top Transfer Activity (Last 24h)",
                xaxis_title="Players",
                yaxis_title="Transfer Count",
                barmode='relative',
                height=400,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def _render_gameweek_countdown(self):
        """Render gameweek countdown and deadline information."""
        st.markdown("### ⏰ Gameweek Countdown")
        
        countdown_col1, countdown_col2, countdown_col3, countdown_col4 = st.columns(4)
        
        # Simulate countdown (in real app, calculate from actual deadline)
        days = 2
        hours = 14
        minutes = 32
        seconds = 45
        
        with countdown_col1:
            st.metric("Days", f"{days:02d}", "⏰")
        
        with countdown_col2:
            st.metric("Hours", f"{hours:02d}", "🕐")
        
        with countdown_col3:
            st.metric("Minutes", f"{minutes:02d}", "⏱️")
        
        with countdown_col4:
            st.metric("Seconds", f"{seconds:02d}", "⚡")
        
        # Deadline urgency indicator
        total_hours_left = days * 24 + hours
        if total_hours_left < 6:
            st.error("🚨 **URGENT**: Deadline approaching! Make your transfers now!")
        elif total_hours_left < 24:
            st.warning("⚠️ **ATTENTION**: Less than 24 hours to deadline")
        else:
            st.info("✅ **PLANNING**: Plenty of time for transfers")

    def _render_live_metrics(self, df, teams_df):
        """Render live metrics with real-time updates."""
        st.markdown("### 📊 Live Performance Metrics")
        
        # Real-time filters
        metric_col1, metric_col2 = st.columns([1, 3])
        
        with metric_col1:
            time_filter = st.selectbox(
                "Time Window:",
                options=["Last Hour", "Last 6 Hours", "Last 24 Hours", "Live Session"],
                key="live_time_filter"
            )
        
        # Live metrics display
        live_col1, live_col2, live_col3, live_col4, live_col5 = st.columns(5)
        
        with live_col1:
            # Most active player (transfers)
            if 'transfers_in_event' in df.columns:
                most_active = df.loc[df['transfers_in_event'].idxmax()]
                transfers = most_active['transfers_in_event']
                self.ui_components.create_metric_card(
                    "Most Active", f"{most_active['web_name'][:10]}",
                    delta=f"+{transfers:,.0f} transfers", icon="🔥"
                )
        
        with live_col2:
            # Highest price change probability
            if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
                df_balance = df.copy()
                df_balance['transfers_balance'] = df_balance['transfers_in_event'] - df_balance['transfers_out_event']
                price_candidate = df_balance.loc[df_balance['transfers_balance'].abs().idxmax()]
                balance = price_candidate['transfers_balance']
                direction = "📈" if balance > 0 else "📉"
                self.ui_components.create_metric_card(
                    "Price Alert", f"{price_candidate['web_name'][:10]}",
                    delta=f"{direction} {abs(balance):,.0f} net", icon="💰"
                )
        
        with live_col3:
            # Live form leader
            if 'form' in df.columns:
                form_leader = df.loc[df['form'].idxmax()]
                form_value = form_leader['form']
                self.ui_components.create_metric_card(
                    "Form King", f"{form_leader['web_name'][:10]}",
                    delta=f"{form_value:.1f} form rating", icon="👑"
                )
        
        with live_col4:
            # Ownership leader
            if 'selected_by_percent' in df.columns:
                ownership_leader = df.loc[df['selected_by_percent'].idxmax()]
                ownership = ownership_leader['selected_by_percent']
                self.ui_components.create_metric_card(
                    "Most Owned", f"{ownership_leader['web_name'][:10]}",
                    delta=f"{ownership:.1f}% owned", icon="📊"
                )
        
        with live_col5:
            # Live value king
            if 'total_points' in df.columns and 'now_cost' in df.columns:
                df_temp = df.copy()
                df_temp['live_value'] = df_temp['total_points'] / (df_temp['now_cost'] / 10)
                value_king = df_temp.loc[df_temp['live_value'].idxmax()]
                value_score = value_king['live_value']
                self.ui_components.create_metric_card(
                    "Value King", f"{value_king['web_name'][:10]}",
                    delta=f"{value_score:.1f} pts/£m", icon="💎"
                )

    def _render_trending_players(self, df):
        """Render trending players section."""
        st.markdown("### 📈 Trending Players")
        
        trend_tab1, trend_tab2, trend_tab3 = st.tabs(["🔥 Hot", "❄️ Cold", "💎 Value"])
        
        with trend_tab1:
            # Hot trending players (based on form)
            if 'form' in df.columns and 'now_cost' in df.columns:
                hot_players = df.nlargest(10, 'form')[
                    ['web_name', 'form', 'total_points', 'now_cost', 'selected_by_percent']
                ].copy()
                hot_players['now_cost'] = hot_players['now_cost'] / 10
                hot_players.columns = ['Player', 'Form', 'Total Points', 'Price (£m)', 'Ownership %']
                
                st.dataframe(
                    hot_players,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Form": st.column_config.NumberColumn(
                            "Form",
                            help="Recent form rating",
                            format="%.1f"
                        )
                    }
                )
        
        with trend_tab2:
            # Cold trending players (based on poor form)
            if 'form' in df.columns and 'now_cost' in df.columns:
                cold_players = df.nsmallest(10, 'form')[
                    ['web_name', 'form', 'total_points', 'now_cost', 'selected_by_percent']
                ].copy()
                cold_players['now_cost'] = cold_players['now_cost'] / 10
                cold_players.columns = ['Player', 'Form', 'Total Points', 'Price (£m)', 'Ownership %']
                
                st.dataframe(
                    cold_players,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Form": st.column_config.NumberColumn(
                            "Form",
                            help="Recent form rating (lower is worse)",
                            format="%.1f"
                        )
                    }
                )
        
        with trend_tab3:
            # Best value players
            if 'total_points' in df.columns and 'now_cost' in df.columns:
                df_value = df.copy()
                df_value['value_score'] = df_value['total_points'] / (df_value['now_cost'] / 10)
                value_players = df_value.nlargest(10, 'value_score')[
                    ['web_name', 'value_score', 'total_points', 'now_cost', 'selected_by_percent']
                ].copy()
                value_players['now_cost'] = value_players['now_cost'] / 10
                value_players.columns = ['Player', 'Value Score', 'Total Points', 'Price (£m)', 'Ownership %']
                
                st.dataframe(
                    value_players,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Value Score": st.column_config.NumberColumn(
                            "Value Score",
                            help="Points per million spent",
                            format="%.1f"
                        )
                    }
                )

    def _render_real_time_charts(self, df):
        """Render real-time interactive charts."""
        st.markdown("### 📊 Live Analytics Charts")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Live transfer momentum chart
            if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns and 'form' in df.columns:
                df_momentum = df.copy()
                df_momentum['transfers_balance'] = df_momentum['transfers_in_event'] - df_momentum['transfers_out_event']
                fig = px.scatter(
                    df_momentum.head(100),
                    x='form',
                    y='transfers_balance',
                    size='selected_by_percent' if 'selected_by_percent' in df.columns else None,
                    color='element_type',
                    hover_name='web_name',
                    title="⚡ Live Transfer Momentum vs Form",
                    labels={
                        'form': 'Current Form',
                        'transfers_balance': 'Transfer Balance (24h)'
                    }
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Price change probability heatmap
            if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns and 'now_cost' in df.columns:
                # Create price change probability
                df_price = df.copy()
                df_price['transfers_balance'] = df_price['transfers_in_event'] - df_price['transfers_out_event']
                df_price['price_change_prob'] = df_price['transfers_balance'].apply(
                    lambda x: min(abs(x) / 200000 * 100, 95) if pd.notna(x) else 0
                )
                df_price['price_millions'] = df_price['now_cost'] / 10
                
                fig = px.scatter(
                    df_price.head(100),
                    x='price_millions',
                    y='price_change_prob',
                    color='transfers_balance',
                    size='selected_by_percent' if 'selected_by_percent' in df_price.columns else None,
                    hover_name='web_name',
                    title="💰 Price Change Probability Matrix",
                    labels={
                        'price_millions': 'Current Price (£m)',
                        'price_change_prob': 'Price Change Probability (%)'
                    },
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

    def _render_live_insights(self, df):
        """Render live AI insights and recommendations."""
        st.markdown("### 🤖 Live AI Insights")
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown("**🎯 Real-Time Recommendations**")
            
            # Generate live recommendations based on current data
            recommendations = [
                "🔥 Consider transferring in players with high transfer momentum",
                "⚠️ Monitor price change alerts for your current players",
                "💎 Look for value players with low ownership but good form",
                "📈 Captain players with favorable upcoming fixtures"
            ]
            
            for rec in recommendations:
                st.info(rec)
        
        with insight_col2:
            st.markdown("**📊 Market Intelligence**")
            
            # Market insights
            insights = [
                f"🔄 **{len(df)}** players tracked in real-time",
                "📈 **High transfer activity** detected in midfield",
                "💰 **3 price changes** expected in next 2 hours",
                "🎯 **Premium forwards** showing strong momentum"
            ]
            
            for insight in insights:
                st.success(insight)
        
        # Live AI predictions
        if st.session_state.get('feature_flags', {}).get('ai_recommendations', True):
            st.markdown("---")
            st.markdown("**🔮 Live AI Predictions**")
            try:
                insights_engine = get_insights_engine()
                insights_engine.render_insights_dashboard(df)
            except Exception as e:
                st.warning("AI insights temporarily unavailable in live mode")
                logger.error(f"Live AI insights error: {e}")

    def _render_my_fpl_team_section(self):
        """Render My FPL Team section with team ID input and official API data."""
        st.markdown("### 👤 My FPL Team Dashboard")
        st.markdown("Connect your official FPL team to get live updates and personalized insights.")
        
        # Team ID Input Section
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            team_id = st.text_input(
                "🔢 Enter your FPL Team ID",
                placeholder="e.g., 123456",
                help="Find your Team ID in the FPL website URL: https://fantasy.premierleague.com/entry/YOUR_TEAM_ID/",
                key="fpl_team_id_input",
                value=st.session_state.get('saved_team_id', '')
            )
        
        with col2:
            load_team = st.button("🔍 Load Team", type="primary", disabled=not team_id)
        
        with col3:
            if st.session_state.get('saved_team_id'):
                if st.button("🗑️ Clear", type="secondary"):
                    st.session_state.pop('saved_team_id', None)
                    st.session_state.pop('fpl_team_data', None)
                    st.session_state.pop('fpl_team_history', None)
                    st.rerun()
        
        # Validate Team ID
        if team_id and not team_id.isdigit():
            st.error("❌ Team ID must be a number (e.g., 123456)")
            return
        
        # Load team data when button is clicked
        if load_team and team_id and team_id.isdigit():
            with st.spinner("🔄 Loading your FPL team data..."):
                team_data = self._fetch_fpl_team_data(team_id)
                if team_data:
                    st.session_state.saved_team_id = team_id
                    st.session_state.fpl_team_data = team_data
                    st.success(f"✅ Successfully loaded team: {team_data.get('name', 'Unknown')}")
                    st.rerun()
        
        # Display team data if available
        if st.session_state.get('fpl_team_data'):
            self._display_fpl_team_dashboard(st.session_state.fpl_team_data)
        else:
            # Show instructions if no team loaded
            self._show_team_id_instructions()
    
    def _fetch_fpl_team_data(self, team_id: str) -> dict:
        """Fetch team data from the official FPL API."""
        import json
        
        try:
            base_url = "https://fantasy.premierleague.com/api"
            
            # Fetch team general info
            team_url = f"{base_url}/entry/{team_id}/"
            response = requests.get(team_url, timeout=10, verify=False)
            
            if response.status_code == 404:
                st.error("❌ Team ID not found. Please check your Team ID and try again.")
                return None
            elif response.status_code != 200:
                st.error(f"❌ Error fetching team data: HTTP {response.status_code}")
                return None
            
            team_info = response.json()
            
            # Fetch current gameweek info
            bootstrap_url = f"{base_url}/bootstrap-static/"
            bootstrap_response = requests.get(bootstrap_url, timeout=10, verify=False)
            bootstrap_data = bootstrap_response.json()
            
            # Get current gameweek
            current_gw = None
            for event in bootstrap_data['events']:
                if event['is_current']:
                    current_gw = event['id']
                    break
            
            if not current_gw:
                # Get next gameweek if no current
                for event in bootstrap_data['events']:
                    if event['is_next']:
                        current_gw = event['id']
                        break
            
            # Fetch team picks for current gameweek
            picks_data = None
            if current_gw:
                picks_url = f"{base_url}/entry/{team_id}/event/{current_gw}/picks/"
                picks_response = requests.get(picks_url, timeout=10, verify=False)
                if picks_response.status_code == 200:
                    picks_data = picks_response.json()
            
            # Fetch team history
            history_url = f"{base_url}/entry/{team_id}/history/"
            history_response = requests.get(history_url, timeout=10, verify=False)
            history_data = None
            if history_response.status_code == 200:
                history_data = history_response.json()
            
            # Combine all data
            team_data = {
                'team_info': team_info,
                'picks': picks_data,
                'history': history_data,
                'bootstrap': bootstrap_data,
                'current_gw': current_gw,
                'name': f"{team_info.get('player_first_name', '')} {team_info.get('player_last_name', '')}".strip(),
                'team_name': team_info.get('name', 'Unknown Team')
            }
            
            return team_data
            
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Please try again.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error. Please check your internet connection.")
            return None
        except Exception as e:
            st.error(f"❌ Error fetching team data: {str(e)}")
            logger.error(f"FPL API error: {e}")
            return None
    
    def _display_fpl_team_dashboard(self, team_data: dict):
        """Display the FPL team dashboard with all the fetched data."""
        team_info = team_data['team_info']
        picks = team_data.get('picks')
        history = team_data.get('history')
        bootstrap = team_data['bootstrap']
        
        # Team Header
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### 🏆 {team_data['team_name']}")
            st.markdown(f"**Manager:** {team_data['name']}")
        
        with col2:
            st.metric("🏅 Overall Rank", f"{team_info.get('summary_overall_rank', 'N/A'):,}")
        
        with col3:
            st.metric("💰 Team Value", f"£{team_info.get('last_deadline_value', 0)/10:.1f}m")
        
        # Key Statistics
        st.markdown("#### 📊 Season Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Total Points", team_info.get('summary_overall_points', 0))
        
        with col2:
            st.metric("🔄 Transfers Made", team_info.get('summary_total_transfers', 0))
        
        with col3:
            st.metric("💸 Transfer Cost", f"-{team_info.get('summary_transfer_cost', 0)}")
        
        with col4:
            st.metric("💎 Free Transfers", team_info.get('last_deadline_total_transfers', 0))
        
        # Current Squad
        if picks and picks.get('picks'):
            st.markdown("#### ⚽ Current Squad")
            self._display_current_squad(picks, bootstrap)
        
        # Performance History
        if history and history.get('current'):
            st.markdown("#### 📈 Performance History")
            self._display_performance_history(history)
        
        # Team Analysis
        st.markdown("#### 🔍 Team Analysis")
        self._display_team_analysis(team_data)
    
    def _display_current_squad(self, picks, bootstrap):
        """Display the current squad with player details."""
        players_data = {p['id']: p for p in bootstrap['elements']}
        teams_data = {t['id']: t for t in bootstrap['teams']}
        positions_data = {p['id']: p for p in bootstrap['element_types']}
        
        # Create squad dataframe
        squad_data = []
        for pick in picks['picks']:
            player = players_data.get(pick['element'])
            if player:
                team = teams_data.get(player['team'])
                position = positions_data.get(player['element_type'])
                
                squad_data.append({
                    'Name': f"{player['first_name']} {player['second_name']}",
                    'Position': position['singular_name_short'] if position else 'N/A',
                    'Team': team['short_name'] if team else 'N/A',
                    'Price': f"£{player['now_cost']/10:.1f}m",
                    'Points': player['total_points'],
                    'Form': player['form'],
                    'Captain': '(C)' if pick['is_captain'] else '(VC)' if pick['is_vice_captain'] else '',
                    'Playing': '✅' if pick['multiplier'] > 0 else '❌'
                })
        
        if squad_data:
            df = pd.DataFrame(squad_data)
            
            # Separate starting XI and bench
            starting_xi = df.head(11)
            bench = df.tail(4)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("##### 🥇 Starting XI")
                st.dataframe(starting_xi, hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("##### 🪑 Bench")
                st.dataframe(bench[['Name', 'Position', 'Points']], hide_index=True, use_container_width=True)
    
    def _display_performance_history(self, history):
        """Display performance history charts."""
        current_season = history['current']
        if not current_season:
            st.info("No performance history available.")
            return
        
        # Create performance dataframe
        df_history = pd.DataFrame(current_season)
        df_history['event'] = df_history['event'].astype(int)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Points per gameweek
            fig = px.line(df_history, x='event', y='points', 
                         title='Points per Gameweek',
                         labels={'event': 'Gameweek', 'points': 'Points'})
            fig.update_traces(line=dict(color='#00ff88', width=3))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Overall rank progression
            fig = px.line(df_history, x='event', y='overall_rank',
                         title='Overall Rank Progression',
                         labels={'event': 'Gameweek', 'overall_rank': 'Rank'})
            fig.update_traces(line=dict(color='#ff6b6b', width=3))
            fig.update_yaxes(autorange='reversed')  # Lower rank is better
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Season summary
        if df_history is not None and len(df_history) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_points = df_history['points'].mean()
                st.metric("📊 Avg Points/GW", f"{avg_points:.1f}")
            
            with col2:
                best_gw = df_history['points'].max()
                st.metric("🏆 Best Gameweek", f"{best_gw}")
            
            with col3:
                worst_gw = df_history['points'].min()
                st.metric("😰 Worst Gameweek", f"{worst_gw}")
            
            with col4:
                total_transfers = df_history['event_transfers'].sum()
                st.metric("🔄 Total Transfers", f"{total_transfers}")
    
    def _display_team_analysis(self, team_data):
        """Display team analysis insights."""
        team_info = team_data['team_info']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 💡 Team Insights")
            
            # Generate insights based on team data
            insights = []
            
            rank = team_info.get('summary_overall_rank', 0)
            if rank:
                if rank <= 100000:
                    insights.append("🏆 You're in the top 100k! Excellent performance!")
                elif rank <= 500000:
                    insights.append("📈 Solid performance, keep pushing for top 100k!")
                else:
                    insights.append("💪 Room for improvement - analyze top teams for inspiration!")
            
            transfers = team_info.get('summary_total_transfers', 0)
            if transfers < 10:
                insights.append("🧘 Conservative transfer strategy - great for long-term stability!")
            elif transfers > 30:
                insights.append("🔄 Active transfer strategy - watch out for point deductions!")
            
            value = team_info.get('last_deadline_value', 0) / 10
            if value > 103:
                insights.append(f"💎 High team value (£{value:.1f}m) - excellent price rise timing!")
            
            for insight in insights:
                st.success(insight)
        
        with col2:
            st.markdown("##### 🎯 Quick Actions")
            
            if st.button("📊 Detailed Analysis", key="detailed_analysis"):
                st.info("🚧 Detailed analysis feature coming soon!")
            
            if st.button("🔄 Refresh Team Data", key="refresh_team"):
                team_id = st.session_state.get('saved_team_id')
                if team_id:
                    with st.spinner("🔄 Refreshing team data..."):
                        team_data = self._fetch_fpl_team_data(team_id)
                        if team_data:
                            st.session_state.fpl_team_data = team_data
                            st.success("✅ Team data refreshed!")
                            st.rerun()
            
            if st.button("📱 Share Team Stats", key="share_stats"):
                st.info("🚧 Sharing feature coming soon!")
    
    def _show_team_id_instructions(self):
        """Show instructions on how to find FPL Team ID."""
        st.markdown("#### 🔍 How to find your FPL Team ID")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            **Step-by-step guide:**
            
            1. 🌐 Go to [fantasy.premierleague.com](https://fantasy.premierleague.com)
            2. 🔐 Log in to your account
            3. 📊 Go to "Points" or "Transfers" page
            4. 👀 Look at the URL in your browser
            5. 🔢 Your Team ID is the number after `/entry/`
            
            **Example URL:**
            `https://fantasy.premierleague.com/entry/123456/event/10`
            
            Your Team ID would be: **123456**
            """)
        
        with col2:
            st.info("""
            **What you'll get:**
            
            ✅ Live team performance stats
            ✅ Current squad with prices
            ✅ Gameweek history charts  
            ✅ Overall rank tracking
            ✅ Transfer history analysis
            ✅ Personalized insights
            ✅ Team value progression
            ✅ Captain choice analysis
            """)
        
        # Demo section
        st.markdown("---")
        st.markdown("#### 🎮 Try the Demo")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("🎯 Load Demo Team", type="secondary", use_container_width=True):
                # Use a demo team ID (this should be a valid public team)
                demo_team_id = "1437667"  # Popular FPL content creator or public team
                with st.spinner("🔄 Loading demo team..."):
                    team_data = self._fetch_fpl_team_data(demo_team_id)
                    if team_data:
                        st.session_state.fpl_team_data = team_data
                        st.session_state.saved_team_id = demo_team_id
                        st.success("✅ Demo team loaded!")
                        st.rerun()

    def _test_api_connection(self):
        """Test FPL API connection with SSL verification disabled."""
        try:
            response = requests.get(
                "https://fantasy.premierleague.com/api/bootstrap-static/",
                timeout=5,
                verify=False
            )
            return response.status_code == 200
        except:
            return False
