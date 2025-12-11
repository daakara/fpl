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
from utils.data_converters import safe_int_convert, safe_float_convert, clean_numeric_column
from components.ai.player_insights import get_insights_engine

# Disable SSL certificate verification and suppress warnings for corporate proxy environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LiveDataPageLegacy:
    """Handles the rendering of the live data dashboard with real-time updates.
    
    This is the legacy 1789-line implementation.
    New modular version is in views/live_data/
    """

    def __init__(self):
        self.ui_components = ModernUIComponents()
        self.auto_refresh_interval = 30  # seconds
        self.last_refresh = datetime.now()

    @staticmethod
    def safe_get_series_value(series, key, default=None):
        """Safely get a value from a pandas Series with fallback."""
        try:
            if key in series.index:
                return series[key]
            return default
        except (KeyError, AttributeError, TypeError):
            return default
    
    @staticmethod
    def safe_get_numeric(series, key, default=0):
        """Safely get a numeric value from a pandas Series."""
        value = LiveDataPageLegacy.safe_get_series_value(series, key, default)
        return safe_int_convert(value, default) if isinstance(default, int) else safe_float_convert(value, default)

    def render(self):
        """Render the live data dashboard with real-time FPL insights."""
        
        try:
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
            
            # Ensure position column exists (map from element_type if needed)
            if 'element_type' in df.columns and 'position' not in df.columns:
                position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                df['position'] = df['element_type'].map(position_map)
                st.session_state.players_df = df  # Update session state

            # Enhanced FPL Analysis Tabs with comprehensive live data features
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
                "🎯 Live Overview", 
                "📊 Player Analytics",
                "🏆 Squad Builder",
                "💰 Transfer Intelligence",
                "👑 Captain Selector",
                "📅 Fixture Analysis",
                "📈 Performance Tracker",
                "🚨 Live Alerts",
                "💎 Hidden Gems",
                "👤 My Team Hub"
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
                # Live Overview Dashboard - Real-time FPL status
                self._render_live_overview_dashboard(df, teams_df)
                
            with tab2:
                # Player Analytics - Deep dive into player statistics  
                self._render_player_analytics_page(df, teams_df)
                    
            with tab3:
                # Squad Builder - Interactive team building tools
                self._render_squad_builder_page(df, teams_df)
                    
            with tab4:
                # Transfer Intelligence - Market analysis and recommendations
                self._render_transfer_intelligence_page(df, teams_df)
                    
            with tab5:
                # Captain Selector - Advanced captain analysis
                self._render_captain_selector_page(df, teams_df)
                
            with tab6:
                # Fixture Analysis - Live fixture difficulty and planning
                self._render_fixture_analysis_page(df, teams_df)
                    
            with tab7:
                # Performance Tracker - Historical and trend analysis
                self._render_performance_tracker_page(df, teams_df)
                
            with tab8:
                # Live Alerts - Real-time notifications and updates
                self._render_live_alerts_page(df, teams_df)
                
            with tab9:
                # Hidden Gems - Value picks and differential players
                self._render_hidden_gems_page(df, teams_df)
                    
            with tab10:
                # My Team Hub - Personal team management
                self._render_my_team_hub_page(df, teams_df)
                
        except ValueError as e:
            if "invalid literal for int()" in str(e):
                st.error("⚠️ **Data Conversion Error**: Some player data contains invalid values. Please refresh the data.")
                logger.error(f"Integer conversion error in Live Data page: {e}")
                # Add more detailed debug info
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                if st.button("🔄 Reload Data"):
                    st.session_state.pop('players_df', None)
                    st.session_state.pop('teams_df', None)
                    st.rerun()
            else:
                st.error(f"⚠️ **Error loading Live Data page**: {str(e)}")
                logger.error(f"ValueError in Live Data page: {e}")
        except Exception as e:
            st.error(f"⚠️ **Error loading Live Data page**: {str(e)}")
            logger.error(f"Error in Live Data page render: {e}")
            # Add detailed traceback for debugging
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            if st.button("🔄 Try Again"):
                st.rerun()

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
                            # Add position column mapping from element_type
                            if 'element_type' in players_df.columns and 'position' not in players_df.columns:
                                position_map = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
                                players_df['position'] = players_df['element_type'].map(position_map)
                            
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
        # Safe conversion - handle non-numeric values (e.g., 'A' for average)
        df_history['event'] = pd.to_numeric(df_history['event'], errors='coerce')
        df_history = df_history.dropna(subset=['event'])  # Remove invalid rows
        
        if df_history.empty:
            st.info("No valid performance history data available.")
            return
        
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

    def _check_api_status(self):
        """Check API status for live overview dashboard."""
        return self._test_api_connection()

    # =================== NEW COMPREHENSIVE TAB METHODS ===================
    
    def _render_live_overview_dashboard(self, df, teams_df):
        """Enhanced live overview dashboard with real-time metrics."""
        st.markdown("### 🎯 **Live FPL Overview Dashboard**")
        st.markdown("---")
        
        # Live Status Bar
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            api_status = self._check_api_status()
            if api_status:
                st.success("🟢 **API LIVE**")
            else:
                st.error("🔴 **API DOWN**")
        
        with col2:
            # Get current gameweek from session state or FPL data
            current_gw = st.session_state.get('current_event', 1)
            if current_gw == 1 and 'fpl_data' in st.session_state:
                fpl_data = st.session_state.fpl_data
                events = fpl_data.get('events', [])
                current_event = next((e for e in events if e.get('is_current', False)), None)
                if current_event:
                    current_gw = current_event.get('id', 1)
            st.metric("Current GW", current_gw)
        
        with col3:
            total_players = len(df) if not df.empty else 0
            st.metric("Active Players", f"{total_players:,}")
        
        with col4:
            last_update = st.session_state.get('last_data_update', datetime.now())
            st.metric("Last Update", last_update.strftime("%H:%M"))
        
        st.markdown("---")
        
        # Quick Insights Cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 **Hot Right Now**")
            if not df.empty:
                # Most transferred in players
                hot_players = df.nlargest(5, 'transfers_in_event')[['web_name', 'team', 'transfers_in_event']]
                for idx, player in hot_players.iterrows():
                    st.markdown(f"**{player['web_name']}** - {player['transfers_in_event']:,} transfers")
        
        with col2:
            st.markdown("#### ❄️ **Cooling Down**")
            if not df.empty:
                # Most transferred out players
                cold_players = df.nlargest(5, 'transfers_out_event')[['web_name', 'team', 'transfers_out_event']]
                for idx, player in cold_players.iterrows():
                    st.markdown(f"**{player['web_name']}** - {player['transfers_out_event']:,} transfers out")
        
        # Live Price Changes (if available)
        st.markdown("#### 💰 **Recent Price Changes**")
        if 'cost_change_event' in df.columns:
            price_changes = df[df['cost_change_event'] != 0][['web_name', 'now_cost', 'cost_change_event']].head(10)
            if not price_changes.empty:
                for idx, player in price_changes.iterrows():
                    change = player['cost_change_event']
                    emoji = "📈" if change > 0 else "📉"
                    st.markdown(f"{emoji} **{player['web_name']}** - £{player['now_cost']/10:.1f}m ({change:+d})")
        
        # Live charts
        self._render_live_metrics(df, teams_df)

    def _render_player_analytics_page(self, df, teams_df):
        """Comprehensive player analytics with advanced filters."""
        st.markdown("### 📊 **Advanced Player Analytics**")
        st.markdown("---")
        
        # Advanced Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            positions = ['All'] + list(df['position'].unique()) if not df.empty else ['All']
            selected_position = st.selectbox("Position", positions)
        
        with col2:
            teams = ['All'] + list(df['team'].unique()) if not df.empty else ['All']
            selected_team = st.selectbox("Team", teams)
        
        with col3:
            price_range = st.select_slider(
                "Price Range (£m)",
                options=[4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
                value=(4.0, 15.0)
            )
        
        with col4:
            sort_by = st.selectbox("Sort By", [
                'Total Points', 'Form', 'Points Per Game', 'Value', 'Ownership %'
            ])
        
        # Filter data
        filtered_df = df.copy() if not df.empty else pd.DataFrame()
        
        if not filtered_df.empty:
            if selected_position != 'All':
                filtered_df = filtered_df[filtered_df['position'] == selected_position]
            if selected_team != 'All':
                filtered_df = filtered_df[filtered_df['team'] == selected_team]
            
            # Price filter
            filtered_df = filtered_df[
                (filtered_df['now_cost'] / 10 >= price_range[0]) & 
                (filtered_df['now_cost'] / 10 <= price_range[1])
            ]
        
        # Analytics Dashboard
        if not filtered_df.empty:
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Players Found", len(filtered_df))
            with col2:
                avg_price = filtered_df['now_cost'].mean() / 10
                st.metric("Avg Price", f"£{avg_price:.1f}m")
            with col3:
                avg_points = filtered_df['total_points'].mean()
                st.metric("Avg Points", f"{avg_points:.1f}")
            with col4:
                avg_ownership = filtered_df['selected_by_percent'].mean()
                st.metric("Avg Ownership", f"{avg_ownership:.1f}%")
            
            # Player Table
            st.markdown("#### 📋 **Player Comparison Table**")
            display_cols = ['web_name', 'team', 'position', 'now_cost', 'total_points', 'form', 'selected_by_percent']
            display_df = filtered_df[display_cols].copy()
            display_df['now_cost'] = display_df['now_cost'] / 10
            display_df.columns = ['Name', 'Team', 'Pos', 'Price (£m)', 'Points', 'Form', 'Ownership %']
            
            st.dataframe(display_df.head(20), use_container_width=True)
            
            # Performance Charts
            self._render_player_performance_charts(filtered_df)

    def _render_squad_builder_page(self, df, teams_df):
        """Interactive squad building tools."""
        st.markdown("### 🏆 **Smart Squad Builder**")
        st.markdown("Build your optimal FPL squad with AI assistance")
        st.markdown("---")
        
        # Budget and constraints
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget = st.slider("Budget (£m)", 80.0, 110.0, 100.0, 0.5)
        
        with col2:
            formation = st.selectbox("Formation", [
                "3-4-3", "3-5-2", "4-3-3", "4-4-2", "4-5-1", "5-3-2", "5-4-1"
            ])
        
        with col3:
            strategy = st.selectbox("Strategy", [
                "Balanced", "Premium Heavy", "Budget Focused", "Differential Heavy"
            ])
        
        # Formation breakdown
        formations = {
            "3-4-3": {"DEF": 3, "MID": 4, "FWD": 3},
            "3-5-2": {"DEF": 3, "MID": 5, "FWD": 2},
            "4-3-3": {"DEF": 4, "MID": 3, "FWD": 3},
            "4-4-2": {"DEF": 4, "MID": 4, "FWD": 2},
            "4-5-1": {"DEF": 4, "MID": 5, "FWD": 1},
            "5-3-2": {"DEF": 5, "MID": 3, "FWD": 2},
            "5-4-1": {"DEF": 5, "MID": 4, "FWD": 1}
        }
        
        if not df.empty:
            st.markdown(f"#### 🎯 **Building {formation} Squad**")
            
            form_reqs = formations[formation]
            total_budget = budget * 10  # Convert to FPL price format
            
            # Squad suggestions by position
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("##### 🛡️ **Defenders**")
                defenders = df[df['position'] == 'DEF'].nlargest(10, 'total_points')
                for idx, player in defenders.iterrows():
                    price = player['now_cost'] / 10
                    st.markdown(f"**{player['web_name']}** - £{price}m ({player['total_points']} pts)")
            
            with col2:
                st.markdown("##### ⚽ **Midfielders**")
                midfielders = df[df['position'] == 'MID'].nlargest(10, 'total_points')
                for idx, player in midfielders.iterrows():
                    price = player['now_cost'] / 10
                    st.markdown(f"**{player['web_name']}** - £{price}m ({player['total_points']} pts)")
            
            with col3:
                st.markdown("##### 🥅 **Forwards**")
                forwards = df[df['position'] == 'FWD'].nlargest(10, 'total_points')
                for idx, player in forwards.iterrows():
                    price = player['now_cost'] / 10
                    st.markdown(f"**{player['web_name']}** - £{price}m ({player['total_points']} pts)")
            
            # Auto-generate squad button
            if st.button("🤖 **Generate Optimal Squad**", type="primary", use_container_width=True):
                self._generate_optimal_squad(df, formation, budget, strategy)

    def _render_transfer_intelligence_page(self, df, teams_df):
        """Advanced transfer intelligence and market analysis."""
        st.markdown("### 💰 **Transfer Intelligence Hub**")
        st.markdown("Make informed transfer decisions with live market data")
        st.markdown("---")
        
        # Transfer tabs
        transfer_tab1, transfer_tab2, transfer_tab3, transfer_tab4 = st.tabs([
            "🔄 Transfer Targets", "📈 Price Predictions", "🌊 Market Trends", "💎 Value Picks"
        ])
        
        with transfer_tab1:
            self._render_transfer_targets(df)
        
        with transfer_tab2:
            self._render_price_predictions(df)
        
        with transfer_tab3:
            self._render_market_trends(df)
        
        with transfer_tab4:
            self._render_value_picks(df)

    def _render_captain_selector_page(self, df, teams_df):
        """Advanced captain selection analysis."""
        st.markdown("### 👑 **Captain Selector Pro**")
        st.markdown("Choose your captain with confidence using advanced analytics")
        st.markdown("---")
        
        if not df.empty:
            # Captain criteria
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 **Top Captain Options**")
                
                # Calculate captain score (combination of form, fixtures, ownership)
                df_captains = df.copy()
                df_captains['captain_score'] = (
                    df_captains['form'].astype(float) * 0.4 +
                    df_captains['total_points'].astype(float) * 0.3 +
                    (100 - df_captains['selected_by_percent'].astype(float)) * 0.2 +
                    df_captains['ict_index'].astype(float) * 0.1
                )
                
                top_captains = df_captains.nlargest(10, 'captain_score')
                
                for idx, player in top_captains.iterrows():
                    with st.expander(f"👑 **{player['web_name']}** - Captain Score: {player['captain_score']:.1f}"):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Form", player['form'])
                        with col_b:
                            st.metric("Ownership", f"{player['selected_by_percent']}%")
                        with col_c:
                            price = player['now_cost'] / 10
                            st.metric("Price", f"£{price}m")
            
            with col2:
                st.markdown("#### 📊 **Captain Analytics**")
                
                # Captain ownership vs points chart
                fig = px.scatter(
                    df.head(50), 
                    x='selected_by_percent', 
                    y='total_points',
                    hover_data=['web_name'],
                    title="Ownership vs Points (Top 50 Players)",
                    labels={'selected_by_percent': 'Ownership %', 'total_points': 'Total Points'}
                )
                st.plotly_chart(fig, use_container_width=True)

    def _render_fixture_analysis_page(self, df, teams_df):
        """Live fixture analysis and difficulty assessment."""
        st.markdown("### 📅 **Live Fixture Analysis**")
        st.markdown("Analyze upcoming fixtures for optimal transfer timing")
        st.markdown("---")
        
        # Import and use the enhanced fixture analysis
        try:
            from views.fixture_analysis_page import FixtureAnalysisPage
            fixture_page = FixtureAnalysisPage()
            
            # FixtureAnalysisPage gets data from session state internally
            fixture_page.render()
            
        except ImportError:
            st.warning("Enhanced fixture analysis not available. Using basic analysis.")
            self._render_basic_fixture_analysis(df, teams_df)

    def _render_performance_tracker_page(self, df, teams_df):
        """Performance tracking and historical analysis."""
        st.markdown("### 📈 **Performance Tracker**")
        st.markdown("Track player and team performance over time")
        st.markdown("---")
        
        # Performance tracking tabs
        perf_tab1, perf_tab2, perf_tab3 = st.tabs([
            "📊 Player Trends", "🏆 Team Performance", "📈 Form Analysis"
        ])
        
        with perf_tab1:
            self._render_player_trends(df)
        
        with perf_tab2:
            self._render_team_performance(df, teams_df)
        
        with perf_tab3:
            self._render_form_analysis(df)

    def _render_live_alerts_page(self, df, teams_df):
        """Real-time alerts and notifications."""
        st.markdown("### 🚨 **Live Alerts Center**")
        st.markdown("Stay updated with real-time FPL notifications")
        st.markdown("---")
        
        # Alert categories
        alert_tab1, alert_tab2, alert_tab3, alert_tab4 = st.tabs([
            "🔴 Price Changes", "⚡ Injury News", "🔄 Transfer Activity", "📊 Performance Alerts"
        ])
        
        with alert_tab1:
            self._render_price_change_alerts(df)
        
        with alert_tab2:
            self._render_injury_alerts(df)
        
        with alert_tab3:
            self._render_transfer_activity_alerts(df)
        
        with alert_tab4:
            self._render_performance_alerts(df)

    def _render_hidden_gems_page(self, df, teams_df):
        """Discover undervalued players and differential picks."""
        try:
            st.markdown("### 💎 **Hidden Gems Discovery**")
            st.markdown("Find undervalued players before everyone else does")
            st.markdown("---")
            
            if not df.empty:
                # Configurable filters with expander
                with st.expander("⚙️ Customize Search Criteria", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        ownership_threshold = st.slider("Max Ownership %", 1, 20, 10, key="gems_ownership")
                    with col2:
                        min_points = st.slider("Min Total Points", 10, 100, 30, key="gems_points")
                    with col3:
                        max_cost = st.slider("Max Cost (£)", 4.0, 10.0, 8.0, 0.5, key="gems_cost")
                    with col4:
                        positions_filter = st.multiselect(
                            "Positions", 
                            options=['All', 'GKP', 'DEF', 'MID', 'FWD'],
                            default=['All'],
                            key="gems_positions"
                        )
                
                # Hidden gems algorithm
                df_gems = df.copy()
                
                # Calculate value score (points per million, low ownership, good form)
                df_gems['points_per_million'] = df_gems['total_points'] / (df_gems['now_cost'] / 10)
                df_gems['value_score'] = (
                    df_gems['points_per_million'] * 0.4 +
                    (100 - df_gems['selected_by_percent'].astype(float)) * 0.3 +
                    df_gems['form'].astype(float) * 0.3
                )
                
                # Apply position filter if not 'All'
                if positions_filter and 'All' not in positions_filter:
                    # Fix: DataFrames don't have .get() method - use column access with existence check
                    if 'position' in df_gems.columns:
                        df_gems = df_gems[df_gems['position'].isin(positions_filter)]
                
                # Filter for potential gems (using configurable thresholds)
                gems = df_gems[
                    (df_gems['selected_by_percent'].astype(float) < ownership_threshold) & 
                    (df_gems['total_points'] > min_points) &
                    (df_gems['now_cost'] <= max_cost * 10)
                ].nlargest(20, 'value_score')  # Increased to 20 players
                
                # Display summary statistics
                if not gems.empty:
                    st.markdown("#### 📊 Discovery Summary")
                    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                    
                    with summary_col1:
                        st.metric("💎 Gems Found", len(gems))
                    with summary_col2:
                        avg_ownership = gems['selected_by_percent'].astype(float).mean()
                        st.metric("📊 Avg Ownership", f"{avg_ownership:.1f}%")
                    with summary_col3:
                        avg_ppm = gems['points_per_million'].mean()
                        st.metric("⚡ Avg PPM", f"{avg_ppm:.2f}")
                    with summary_col4:
                        avg_price = gems['now_cost'].mean() / 10
                        st.metric("💰 Avg Price", f"£{avg_price:.1f}m")
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💎 **Budget Gems** (Under £6.0m)")
                        budget_gems = gems[gems['now_cost'] <= 60]
                        
                        if budget_gems.empty:
                            st.info("💡 No budget gems found. Try adjusting the filters above.")
                        else:
                            for idx, player in budget_gems.head(10).iterrows():
                                # Safe access to player data
                                player_name = self.safe_get_series_value(player, 'web_name', 'Unknown')
                                player_cost = self.safe_get_numeric(player, 'now_cost', 0) / 10
                                
                                with st.expander(f"💎 **{player_name}** - £{player_cost:.1f}m"):
                                    # Add position and team info using safe access
                                    position = self.safe_get_series_value(player, 'position', 'N/A')
                                    team = self.safe_get_series_value(player, 'team', 'N/A')
                                    st.caption(f"📍 {position} | {team}")
                                    
                                    col_a, col_b, col_c = st.columns(3)
                                    with col_a:
                                        points = self.safe_get_numeric(player, 'total_points', 0)
                                        st.metric("Points", points)
                                    with col_b:
                                        ownership_val = self.safe_get_numeric(player, 'selected_by_percent', 0.0)
                                        st.metric("Ownership", f"{ownership_val:.1f}%")
                                    with col_c:
                                        ppm = self.safe_get_numeric(player, 'points_per_million', 0.0)
                                        st.metric("PPM", f"{ppm:.2f}")
                                    
                                    # Add "why this player" badges
                                    reasons = []
                                    ppm_val = self.safe_get_numeric(player, 'points_per_million', 0)
                                    ownership = self.safe_get_numeric(player, 'selected_by_percent', 0.0)
                                    form = self.safe_get_numeric(player, 'form', 0.0)
                                    total_pts = self.safe_get_numeric(player, 'total_points', 0)
                                    
                                    if ppm_val > 15:
                                        reasons.append("🔥 Elite PPM")
                                    if ownership < 3:
                                        reasons.append("👻 Ultra-differential")
                                    if form > 7:
                                        reasons.append("📈 Hot form")
                                    if total_pts > 60:
                                        reasons.append("⭐ High scorer")
                                    
                                    if reasons:
                                        st.caption(" • ".join(reasons))
                    
                    with col2:
                        st.markdown("#### ⚡ **Premium Differentials** (£6.0m+)")
                        premium_gems = gems[gems['now_cost'] > 60]
                        
                        if premium_gems.empty:
                            st.info("💡 No premium differentials found. Try adjusting the filters above.")
                        else:
                            for idx, player in premium_gems.head(10).iterrows():
                                # Safe access to player data
                                player_name = self.safe_get_series_value(player, 'web_name', 'Unknown')
                                player_cost = self.safe_get_numeric(player, 'now_cost', 0) / 10
                                
                                with st.expander(f"⚡ **{player_name}** - £{player_cost:.1f}m"):
                                    # Add position and team info using safe access
                                    position = self.safe_get_series_value(player, 'position', 'N/A')
                                    team = self.safe_get_series_value(player, 'team', 'N/A')
                                    st.caption(f"📍 {position} | {team}")
                                    
                                    col_a, col_b, col_c = st.columns(3)
                                    with col_a:
                                        points = self.safe_get_numeric(player, 'total_points', 0)
                                        st.metric("Points", points)
                                    with col_b:
                                        ownership_val = self.safe_get_numeric(player, 'selected_by_percent', 0.0)
                                        st.metric("Ownership", f"{ownership_val:.1f}%")
                                    with col_c:
                                        form_val = self.safe_get_numeric(player, 'form', 0.0)
                                        st.metric("Form", f"{form_val:.1f}")
                                    
                                    # Add "why this player" badges
                                    reasons = []
                                    ppm_val = self.safe_get_numeric(player, 'points_per_million', 0)
                                    ownership = self.safe_get_numeric(player, 'selected_by_percent', 0.0)
                                    form = self.safe_get_numeric(player, 'form', 0.0)
                                    total_pts = self.safe_get_numeric(player, 'total_points', 0)
                                    
                                    if ppm_val > 12:
                                        reasons.append("💪 Strong PPM")
                                    if ownership < 5:
                                        reasons.append("👻 Low ownership")
                                    if form > 6:
                                        reasons.append("🔥 Good form")
                                    if total_pts > 80:
                                        reasons.append("⭐ Premium points")
                                    
                                    if reasons:
                                        st.caption(" • ".join(reasons))
                else:
                    st.warning("⚠️ No gems found matching current criteria. Try relaxing the filters above.")
            else:
                st.error("❌ No player data available. Please load data first.")
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in Hidden Gems page render: {str(e)}\n{error_details}")
            st.error(f"⚠️ Error loading Hidden Gems page: {str(e)}")
            st.info("💡 Please try refreshing the page or adjusting the filters.")

    def _render_my_team_hub_page(self, df, teams_df):
        """Personal team management and analysis hub."""
        st.markdown("### 👤 **My Team Hub**")
        st.markdown("Manage and analyze your personal FPL team")
        st.markdown("---")
        
        # Team management tabs
        team_tab1, team_tab2, team_tab3, team_tab4 = st.tabs([
            "🏆 Current Squad", "🔄 Transfer Planning", "📊 Performance Review", "🎯 Gameweek Strategy"
        ])
        
        with team_tab1:
            self._render_current_squad_analysis(df)
        
        with team_tab2:
            self._render_transfer_planning_tools(df)
        
        with team_tab3:
            self._render_team_performance_review(df)
        
        with team_tab4:
            self._render_gameweek_strategy(df, teams_df)

    # =================== HELPER METHODS FOR NEW TABS ===================
    
    def _render_player_performance_charts(self, df):
        """Render performance charts for player analytics."""
        st.markdown("#### 📈 **Performance Visualizations**")
        
        # Points vs Price scatter
        fig = px.scatter(
            df.head(50), 
            x='now_cost', 
            y='total_points',
            color='position',
            hover_data=['web_name'],
            title="Points vs Price Analysis"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _generate_optimal_squad(self, df, formation, budget, strategy):
        """Generate an optimal squad based on constraints."""
        st.info("🤖 Squad generation algorithm would run here...")
        st.markdown("**Algorithm Features:**")
        st.markdown("• Position requirements optimization")
        st.markdown("• Budget constraint solving")
        st.markdown("• Team diversity rules")
        st.markdown("• Expected points maximization")
        
    def _render_transfer_targets(self, df):
        """Render transfer target recommendations."""
        st.markdown("#### 🎯 **Hot Transfer Targets**")
        if not df.empty:
            # Most transferred in players this gameweek
            hot_transfers = df.nlargest(10, 'transfers_in_event')[['web_name', 'team', 'transfers_in_event', 'form']]
            st.dataframe(hot_transfers, use_container_width=True)
    
    def _render_price_predictions(self, df):
        """Render price prediction analysis."""
        st.markdown("#### 📈 **Price Change Predictions**")
        st.info("Advanced price prediction algorithms would analyze:")
        st.markdown("• Transfer momentum patterns")
        st.markdown("• Historical price change data")
        st.markdown("• Ownership thresholds")
        st.markdown("• Market sentiment indicators")
    
    def _render_market_trends(self, df):
        """Render market trend analysis."""
        st.markdown("#### 🌊 **Market Trends**")
        if not df.empty:
            # Transfer trends by position
            position_trends = df.groupby('position').agg({
                'transfers_in_event': 'sum',
                'transfers_out_event': 'sum'
            }).round(0)
            st.dataframe(position_trends, use_container_width=True)
    
    def _render_value_picks(self, df):
        """Render value pick recommendations."""
        st.markdown("#### 💰 **Best Value Picks**")
        if not df.empty:
            df_value = df.copy()
            df_value['value'] = df_value['total_points'] / (df_value['now_cost'] / 10)
            value_picks = df_value.nlargest(15, 'value')[['web_name', 'position', 'now_cost', 'total_points', 'value']]
            value_picks['now_cost'] = value_picks['now_cost'] / 10
            st.dataframe(value_picks, use_container_width=True)
    
    def _render_basic_fixture_analysis(self, df, teams_df):
        """Basic fixture analysis fallback."""
        st.info("📅 Basic fixture analysis - showing team strengths")
        if not teams_df.empty:
            team_stats = teams_df[['name', 'strength', 'strength_overall_home', 'strength_overall_away']]
            st.dataframe(team_stats, use_container_width=True)
    
    def _render_player_trends(self, df):
        """Render player trend analysis."""
        st.markdown("#### 📊 **Player Form Trends**")
        if not df.empty:
            form_leaders = df.nlargest(10, 'form')[['web_name', 'team', 'form', 'total_points']]
            st.dataframe(form_leaders, use_container_width=True)
    
    def _render_team_performance(self, df, teams_df):
        """Render team performance analysis."""
        st.markdown("#### 🏆 **Team Performance Overview**")
        if not teams_df.empty:
            st.dataframe(teams_df[['name', 'strength', 'points', 'position']], use_container_width=True)
    
    def _render_form_analysis(self, df):
        """Render form analysis charts."""
        st.markdown("#### 📈 **Form Analysis**")
        st.info("Form trend charts and analysis would be displayed here")
    
    def _render_price_change_alerts(self, df):
        """Render price change alerts."""
        st.markdown("#### 💰 **Price Change Alerts**")
        st.info("🔔 Real-time price change notifications would appear here")
    
    def _render_injury_alerts(self, df):
        """Render injury news alerts."""
        st.markdown("#### 🏥 **Injury News**")
        st.info("⚕️ Latest injury updates and availability status")
    
    def _render_transfer_activity_alerts(self, df):
        """Render transfer activity alerts."""
        st.markdown("#### 🔄 **Transfer Activity**")
        st.info("📊 Live transfer momentum and market movements")
    
    def _render_performance_alerts(self, df):
        """Render performance-based alerts."""
        st.markdown("#### 📊 **Performance Alerts**")
        st.info("⚡ Automated alerts for performance milestones")
    
    def _render_current_squad_analysis(self, df):
        """Render current squad analysis."""
        st.markdown("#### 🏆 **Squad Overview**")
        st.info("👥 Connect your FPL team to see detailed squad analysis")
    
    def _render_transfer_planning_tools(self, df):
        """Render transfer planning tools."""
        st.markdown("#### 🔄 **Transfer Planner**")
        st.info("🎯 Interactive transfer planning with wildcard optimization")
    
    def _render_team_performance_review(self, df):
        """Render team performance review."""
        st.markdown("#### 📊 **Performance History**")
        st.info("📈 Historical performance tracking and analysis")
    
    def _render_gameweek_strategy(self, df, teams_df):
        """Render gameweek strategy planning."""
        st.markdown("#### 🎯 **Gameweek Strategy**")
        st.info("⚡ Upcoming gameweek planning and optimization tools")
