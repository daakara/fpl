"""
Phase 2 Enhanced Sub-Pages: AI-Powered Real-Time Intelligence
Integrates predictive analytics, real-time data, and hidden gems discovery
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# Import Phase 2 AI Services with fallbacks
LiveDataStream = None
try:
    from services.realtime_pipeline import LiveDataStream
except ImportError as e:
    print(f"LiveDataStream not available: {e}")
    
    class LiveDataStreamFallback:
        def __init__(self):
            pass
        def render_live_controls(self):
            try:
                st.info("🔧 Live controls in fallback mode - Real-time features not available")
            except:
                print("Live controls in fallback mode")
        def render_live_alerts(self):
            try:
                st.info("📢 No live alerts - Real-time pipeline not available")
            except:
                print("No live alerts available")
        def render_price_predictions(self):
            try:
                st.info("💰 Price predictions in fallback mode")
            except:
                print("Price predictions in fallback mode")
        def render_recent_updates(self):
            try:
                st.info("📡 Recent updates feed not available - Real-time pipeline offline")
            except:
                print("Recent updates not available")
    
    LiveDataStream = LiveDataStreamFallback

PredictiveAnalyticsEngine = None
try:
    from services.predictive_analytics import PredictiveAnalyticsEngine
except ImportError as e:
    print(f"PredictiveAnalyticsEngine not available: {e}")
    
    class PredictiveAnalyticsEngineFallback:
        def __init__(self):
            self.models_trained = False
        def train_models(self, features, targets):
            pass
        def predict_next_gameweek_points(self, features):
            return [5.0] * len(features)
        def get_captain_recommendations(self, features, targets):
            return []
    
    PredictiveAnalyticsEngine = PredictiveAnalyticsEngineFallback

HiddenGemsDiscovery = None
try:
    from services.hidden_gems_discovery import HiddenGemsDiscovery
except ImportError as e:
    print(f"HiddenGemsDiscovery not available: {e}")
    
    class HiddenGemsDiscoveryFallback:
        def __init__(self):
            pass
        def discover_all_gems(self, df):
            return []
        def find_value_gems(self, df):
            return []
        def find_form_gems(self, df):
            return []
    
    HiddenGemsDiscovery = HiddenGemsDiscoveryFallback

# Import base class with fallback
FPLSubPagesManager = None
try:
    from views.enhanced_fpl_subpages import FPLSubPagesManager
except ImportError as e:
    print(f"FPLSubPagesManager not available: {e}")
    
    class FPLSubPagesManagerFallback:
        def __init__(self):
            pass
    
    FPLSubPagesManager = FPLSubPagesManagerFallback

class Phase2SubPagesManager(FPLSubPagesManager):
    """Enhanced sub-pages manager with Phase 2 AI features"""
    
    def __init__(self):
        super().__init__()
        self.predictive_engine = PredictiveAnalyticsEngine()
        self.gems_discovery = HiddenGemsDiscovery()
        self.live_stream = LiveDataStream()
        
        # Initialize models if not already done (safe streamlit access)
        try:
            if 'models_trained' not in st.session_state:
                st.session_state.models_trained = False
        except:
            # Running outside of streamlit context
            pass
    
    def render_ai_powered_overview(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """AI-Powered Overview Dashboard with predictive insights"""
        st.header("🤖 AI-Powered FPL Command Center")
        st.markdown("*Real-time intelligence with machine learning predictions*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Real-time controls and status
        st.markdown("### ⚡ Live Data Control Center")
        self.live_stream.render_live_controls()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Live alerts
            self.live_stream.render_live_alerts()
        
        with col2:
            # Price predictions
            self.live_stream.render_price_predictions()
        
        # AI Model Training Section
        st.markdown("---")
        st.subheader("🧠 AI Model Performance Center")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Train AI Models", type="primary"):
                with st.spinner("Training machine learning models..."):
                    try:
                        performance = self.predictive_engine.train_models(df)
                        st.session_state.models_trained = True
                        st.session_state.model_performance = performance
                        st.success("✅ AI models trained successfully!")
                        
                        # Display performance metrics
                        for model_name, perf in performance.items():
                            st.metric(
                                f"{model_name.replace('_', ' ').title()}",
                                f"MAE: {perf.mae:.2f}",
                                f"R²: {perf.r2:.3f}"
                            )
                    except Exception as e:
                        st.error(f"Model training failed: {e}")
        
        with col2:
            if st.session_state.get('models_trained', False):
                st.success("🟢 AI Models Ready")
                st.caption("Predictive analytics active")
            else:
                st.warning("🟡 Models Not Trained")
                st.caption("Train models for predictions")
        
        with col3:
            if st.session_state.get('model_performance'):
                avg_performance = np.mean([p.r2 for p in st.session_state.model_performance.values()])
                st.metric("Model Accuracy", f"{avg_performance:.1%}")
        
        # Hidden Gems Discovery
        st.markdown("---")
        st.subheader("💎 AI Hidden Gems Discovery")
        
        if st.button("🔍 Discover Hidden Gems"):
            with st.spinner("Running advanced gem discovery algorithms..."):
                try:
                    all_gems = self.gems_discovery.discover_all_gems(df, teams_df)
                    st.session_state.discovered_gems = all_gems
                    
                    if all_gems:
                        # Summary stats
                        gem_stats = self.gems_discovery.get_gem_summary_stats(all_gems)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Gems", gem_stats['total_gems'])
                        with col2:
                            st.metric("High Confidence", gem_stats['high_confidence_gems'])
                        with col3:
                            st.metric("Avg Ownership", f"{gem_stats['avg_ownership']:.1f}%")
                        with col4:
                            st.metric("Avg Confidence", f"{gem_stats['avg_confidence']:.0%}")
                        
                        # Opportunity alerts
                        alerts = self.gems_discovery.generate_opportunity_alerts(all_gems)
                        if alerts:
                            st.markdown("#### 🚨 Opportunity Alerts")
                            for alert in alerts:
                                alert_color = "error" if alert.priority == "HIGH" else "warning"
                                getattr(st, alert_color)(f"**{alert.title}**\n{alert.description}")
                        
                    else:
                        st.info("No hidden gems discovered with current criteria")
                        
                except Exception as e:
                    st.error(f"Gem discovery failed: {e}")
        
        # Display discovered gems
        if st.session_state.get('discovered_gems'):
            self._display_gems_summary(st.session_state.discovered_gems)
        
        # Live updates feed
        st.markdown("---")
        st.subheader("📡 Live Intelligence Feed")
        self.live_stream.render_recent_updates()
    
    def render_predictive_analytics_page(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Predictive Analytics with ML models"""
        st.header("🔮 Predictive Analytics Lab")
        st.markdown("*Machine learning powered performance predictions*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Check if models are trained
        if not st.session_state.get('models_trained', False):
            st.warning("⚠️ AI models need to be trained first. Go to the Overview page to train models.")
            
            if st.button("🚀 Quick Train Models"):
                with st.spinner("Training models..."):
                    try:
                        performance = self.predictive_engine.train_models(df)
                        st.session_state.models_trained = True
                        st.session_state.model_performance = performance
                        st.success("Models trained!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Training failed: {e}")
            return
        
        # Prediction options
        st.subheader("🎯 Prediction Center")
        
        prediction_type = st.radio(
            "Select Prediction Type:",
            ["Points Prediction", "Price Change Prediction", "Captain Selection"],
            horizontal=True
        )
        
        if prediction_type == "Points Prediction":
            self._render_points_predictions(df)
        elif prediction_type == "Price Change Prediction":
            self._render_price_predictions(df)
        else:
            self._render_captain_predictions(df)
        
        # Model performance dashboard
        st.markdown("---")
        st.subheader("📊 Model Performance Dashboard")
        
        if st.session_state.get('model_performance'):
            performance_data = []
            for model_name, perf in st.session_state.model_performance.items():
                performance_data.append({
                    'Model': model_name.replace('_', ' ').title(),
                    'MAE': perf.mae,
                    'RMSE': perf.rmse,
                    'R² Score': perf.r2,
                    'CV Score': perf.cv_score
                })
            
            perf_df = pd.DataFrame(performance_data)
            st.dataframe(perf_df, hide_index=True, use_container_width=True)
            
            # Feature importance visualization
            st.markdown("#### 🔍 Feature Importance Analysis")
            
            model_to_analyze = st.selectbox(
                "Select model for feature analysis:",
                list(st.session_state.model_performance.keys())
            )
            
            if model_to_analyze:
                importance = st.session_state.model_performance[model_to_analyze].feature_importance
                if importance:
                    # Create feature importance chart
                    top_features = dict(list(importance.items())[:10])  # Top 10 features
                    
                    fig = px.bar(
                        x=list(top_features.values()),
                        y=list(top_features.keys()),
                        orientation='h',
                        title=f"Top Features for {model_to_analyze.replace('_', ' ').title()}",
                        labels={'x': 'Importance', 'y': 'Features'}
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
    
    def render_hidden_gems_explorer(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Hidden Gems Explorer with advanced discovery"""
        st.header("💎 Hidden Gems Explorer")
        st.markdown("*AI-powered discovery of undervalued FPL assets*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Discovery controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            gem_types = st.multiselect(
                "Select Gem Types:",
                ["Value", "Form", "Fixture", "Differential", "Breakout", "Rotation Proof"],
                default=["Value", "Differential", "Form"]
            )
        
        with col2:
            max_ownership = st.slider("Max Ownership %", 1.0, 20.0, 10.0, 0.5)
        
        with col3:
            min_confidence = st.slider("Min Confidence", 0.3, 0.9, 0.6, 0.05)
        
        if st.button("🔍 Run Gem Discovery", type="primary"):
            with st.spinner("Discovering hidden gems..."):
                try:
                    all_gems = self.gems_discovery.discover_all_gems(df, teams_df)
                    
                    # Filter by user preferences
                    filtered_gems = {}
                    type_mapping = {
                        'Value': 'value_gems',
                        'Form': 'form_gems', 
                        'Fixture': 'fixture_gems',
                        'Differential': 'differential_gems',
                        'Breakout': 'breakout_gems',
                        'Rotation Proof': 'rotation_proof'
                    }
                    
                    for gem_type in gem_types:
                        mapped_type = type_mapping.get(gem_type)
                        if mapped_type in all_gems:
                            filtered_gems[mapped_type] = [
                                gem for gem in all_gems[mapped_type]
                                if gem.ownership <= max_ownership and gem.confidence >= min_confidence
                            ]
                    
                    st.session_state.filtered_gems = filtered_gems
                    
                    if filtered_gems:
                        st.success(f"✅ Found {sum(len(gems) for gems in filtered_gems.values())} hidden gems!")
                    else:
                        st.warning("No gems found matching your criteria. Try adjusting filters.")
                        
                except Exception as e:
                    st.error(f"Discovery failed: {e}")
        
        # Display filtered gems
        if st.session_state.get('filtered_gems'):
            self._display_detailed_gems(st.session_state.filtered_gems)
        
        # Gem comparison tool
        st.markdown("---")
        st.subheader("⚔️ Gem Comparison Tool")
        
        if st.session_state.get('filtered_gems'):
            all_gems = []
            for gem_list in st.session_state.filtered_gems.values():
                all_gems.extend(gem_list)
            
            if len(all_gems) >= 2:
                gem_names = [f"{gem.player_name} ({gem.gem_type})" for gem in all_gems]
                
                selected_gems = st.multiselect(
                    "Select gems to compare:",
                    gem_names,
                    max_selections=4
                )
                
                if selected_gems:
                    self._render_gem_comparison(all_gems, selected_gems)
    
    def render_real_time_intelligence(self, df: pd.DataFrame, teams_df: pd.DataFrame = None):
        """Real-time intelligence dashboard"""
        st.header("📡 Real-Time Intelligence Center")
        st.markdown("*Live monitoring and instant insights*")
        
        if df.empty:
            st.warning("No player data available")
            return
        
        # Real-time status and controls
        st.subheader("🔴 Live Data Pipeline")
        self.live_stream.render_live_controls()
        
        # Live monitoring dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚨 Active Alerts")
            self.live_stream.render_live_alerts()
        
        with col2:
            st.markdown("#### 💰 Price Change Intel")
            self.live_stream.render_price_predictions()
        
        # Real-time updates feed
        st.markdown("---")
        st.subheader("📊 Live Updates Stream")
        self.live_stream.render_recent_updates()
        
        # Market pulse indicators
        st.markdown("---")
        st.subheader("📈 Market Pulse Indicators")
        
        # Calculate market metrics
        if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
            total_transfers_in = df['transfers_in_event'].sum()
            total_transfers_out = df['transfers_out_event'].sum()
            net_transfers = total_transfers_in - total_transfers_out
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transfers In", f"{total_transfers_in:,.0f}")
            with col2:
                st.metric("Total Transfers Out", f"{total_transfers_out:,.0f}")
            with col3:
                st.metric("Net Transfer Activity", f"{net_transfers:,.0f}")
            with col4:
                market_activity = "High" if abs(net_transfers) > 1000000 else "Moderate" if abs(net_transfers) > 500000 else "Low"
                st.metric("Market Activity", market_activity)
            
            # Transfer activity heatmap
            top_transfers_in = df.nlargest(10, 'transfers_in_event')[['web_name', 'transfers_in_event']]
            top_transfers_out = df.nlargest(10, 'transfers_out_event')[['web_name', 'transfers_out_event']]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 📈 Most Transferred In")
                fig = px.bar(
                    top_transfers_in,
                    x='transfers_in_event',
                    y='web_name',
                    orientation='h',
                    title="Top Transfers In",
                    color='transfers_in_event',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("##### 📉 Most Transferred Out")
                fig = px.bar(
                    top_transfers_out,
                    x='transfers_out_event',
                    y='web_name',
                    orientation='h',
                    title="Top Transfers Out",
                    color='transfers_out_event',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Live sentiment analysis (simulated)
        st.markdown("---")
        st.subheader("📊 Community Sentiment Analysis")
        
        sentiment_data = self._generate_sentiment_analysis(df)
        if sentiment_data:
            sentiment_df = pd.DataFrame(sentiment_data)
            
            fig = px.scatter(
                sentiment_df,
                x='ownership',
                y='sentiment_score',
                size='mentions',
                color='sentiment_category',
                hover_name='player_name',
                title="Community Sentiment vs Ownership",
                labels={
                    'ownership': 'Ownership %',
                    'sentiment_score': 'Sentiment Score',
                    'sentiment_category': 'Sentiment'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _display_gems_summary(self, all_gems: Dict):
        """Display summary of discovered gems"""
        st.markdown("#### 💎 Discovered Gems Summary")
        
        # Create tabs for different gem types
        gem_tabs = st.tabs([
            "💰 Value", "🔥 Form", "⚡ Differential", 
            "🚀 Breakout", "📅 Fixture", "🔒 Rotation Proof"
        ])
        
        gem_type_mapping = {
            0: 'value_gems',
            1: 'form_gems', 
            2: 'differential_gems',
            3: 'breakout_gems',
            4: 'fixture_gems',
            5: 'rotation_proof'
        }
        
        for idx, tab in enumerate(gem_tabs):
            with tab:
                gem_type = gem_type_mapping.get(idx)
                if gem_type in all_gems and all_gems[gem_type]:
                    for gem in all_gems[gem_type][:3]:  # Top 3 per category
                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{gem.player_name}** ({gem.position})")
                                st.caption(f"💡 {gem.reasons[0]}")
                            
                            with col2:
                                st.metric("Price", f"£{gem.current_price:.1f}m")
                                st.metric("Ownership", f"{gem.ownership:.1f}%")
                            
                            with col3:
                                st.metric("Gem Score", f"{gem.gem_score:.1f}")
                                confidence_color = "🟢" if gem.confidence >= 0.8 else "🟡" if gem.confidence >= 0.6 else "🔴"
                                st.metric("Confidence", f"{confidence_color} {gem.confidence:.0%}")
                            
                            st.markdown("---")
                else:
                    st.info(f"No {gem_type.replace('_', ' ').title()} gems found")
    
    def _display_detailed_gems(self, filtered_gems: Dict):
        """Display detailed view of filtered gems"""
        st.markdown("#### 💎 Detailed Gem Analysis")
        
        for gem_type, gems in filtered_gems.items():
            if gems:
                st.markdown(f"##### {gem_type.replace('_', ' ').title()}")
                
                for gem in gems:
                    with st.expander(f"💎 {gem.player_name} - £{gem.current_price:.1f}m ({gem.ownership:.1f}% owned)"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Why it's a gem:**")
                            for reason in gem.reasons:
                                st.write(f"• {reason}")
                            
                            st.markdown("**Key Stats:**")
                            for stat, value in gem.stats.items():
                                st.write(f"• {stat.replace('_', ' ').title()}: {value}")
                        
                        with col2:
                            st.markdown("**Projections:**")
                            for proj, value in gem.projection.items():
                                st.write(f"• {proj.replace('_', ' ').title()}: {value}")
                            
                            st.markdown(f"**Confidence Score:** {gem.confidence:.0%}")
                            st.markdown(f"**Discovery Date:** {gem.discovery_date.strftime('%Y-%m-%d %H:%M')}")
    
    def _render_points_predictions(self, df: pd.DataFrame):
        """Render points prediction interface"""
        st.markdown("#### 🎯 Next Gameweek Points Predictions")
        
        # Player selection
        position_filter = st.selectbox(
            "Filter by position:",
            ["All", "GKP", "DEF", "MID", "FWD"]
        )
        
        if position_filter != "All":
            position_map = {"GKP": 1, "DEF": 2, "MID": 3, "FWD": 4}
            filtered_df = df[df['element_type'] == position_map[position_filter]]
        else:
            filtered_df = df
        
        # Get predictions
        if st.button("🔮 Generate Points Predictions"):
            with st.spinner("Running ML predictions..."):
                try:
                    predictions = self.predictive_engine.predict_player_points(filtered_df)
                    
                    if predictions:
                        # Display predictions table
                        pred_data = []
                        for pred in predictions[:20]:  # Top 20
                            pred_data.append({
                                'Player': pred.player_name,
                                'Predicted Points': f"{pred.predicted_value:.1f}",
                                'Confidence': f"{pred.confidence_score:.0%}",
                                'Range': f"{pred.confidence_interval[0]:.1f} - {pred.confidence_interval[1]:.1f}",
                                'Model': pred.model_used
                            })
                        
                        pred_df = pd.DataFrame(pred_data)
                        st.dataframe(pred_df, hide_index=True, use_container_width=True)
                        
                        # Visualization
                        fig = px.bar(
                            pred_df.head(10),
                            x='Predicted Points',
                            y='Player',
                            orientation='h',
                            title="Top 10 Predicted Point Scorers",
                            color='Predicted Points',
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No predictions generated. Check model training.")
                        
                except Exception as e:
                    st.error(f"Prediction failed: {e}")
    
    def _render_price_predictions(self, df: pd.DataFrame):
        """Render price change prediction interface"""
        st.markdown("#### 💰 Price Change Predictions")
        
        if st.button("📈 Predict Price Changes"):
            with st.spinner("Analyzing transfer trends..."):
                try:
                    predictions = self.predictive_engine.predict_price_changes(df)
                    
                    if predictions:
                        # Separate rises and falls
                        rises = [p for p in predictions if p.predicted_value > 0]
                        falls = [p for p in predictions if p.predicted_value < 0]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("##### 📈 Predicted Price Rises")
                            if rises:
                                rise_data = []
                                for pred in rises:
                                    rise_data.append({
                                        'Player': pred.player_name,
                                        'Predicted Rise': f"£{pred.predicted_value:.1f}m",
                                        'Confidence': f"{pred.confidence_score:.0%}"
                                    })
                                
                                st.dataframe(pd.DataFrame(rise_data), hide_index=True)
                            else:
                                st.info("No price rises predicted")
                        
                        with col2:
                            st.markdown("##### 📉 Predicted Price Falls")
                            if falls:
                                fall_data = []
                                for pred in falls:
                                    fall_data.append({
                                        'Player': pred.player_name,
                                        'Predicted Fall': f"£{abs(pred.predicted_value):.1f}m",
                                        'Confidence': f"{pred.confidence_score:.0%}"
                                    })
                                
                                st.dataframe(pd.DataFrame(fall_data), hide_index=True)
                            else:
                                st.info("No price falls predicted")
                    else:
                        st.info("No significant price changes predicted")
                        
                except Exception as e:
                    st.error(f"Price prediction failed: {e}")
    
    def _render_captain_predictions(self, df: pd.DataFrame):
        """Render captain selection predictions"""
        st.markdown("#### 👑 AI Captain Recommendations")
        
        if st.button("🎯 Get Captain Predictions"):
            with st.spinner("Analyzing captain potential..."):
                try:
                    predictions = self.predictive_engine.predict_captain_scores(df)
                    
                    if predictions:
                        st.markdown("##### 🏆 Top Captain Recommendations")
                        
                        for i, pred in enumerate(predictions[:5], 1):
                            with st.container():
                                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                                
                                with col1:
                                    st.markdown(f"### #{i}")
                                
                                with col2:
                                    st.markdown(f"**{pred.player_name}**")
                                    st.caption(f"Captain Score: {pred.predicted_value:.1f}")
                                
                                with col3:
                                    st.metric("Confidence", f"{pred.confidence_score:.0%}")
                                
                                with col4:
                                    range_text = f"{pred.confidence_interval[0]:.1f} - {pred.confidence_interval[1]:.1f}"
                                    st.metric("Score Range", range_text)
                                
                                st.markdown("---")
                        
                        # Captain score visualization
                        captain_data = []
                        for pred in predictions[:8]:
                            captain_data.append({
                                'Player': pred.player_name,
                                'Captain Score': pred.predicted_value,
                                'Confidence': pred.confidence_score
                            })
                        
                        fig = px.bar(
                            pd.DataFrame(captain_data),
                            x='Captain Score',
                            y='Player',
                            orientation='h',
                            title="Captain Score Comparison",
                            color='Confidence',
                            color_continuous_scale='RdYlGn'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No captain predictions generated")
                        
                except Exception as e:
                    st.error(f"Captain prediction failed: {e}")
    
    def _render_gem_comparison(self, all_gems: List, selected_gems: List[str]):
        """Render gem comparison visualization"""
        # Find selected gem objects
        selected_gem_objects = []
        for gem_name in selected_gems:
            player_name = gem_name.split(' (')[0]  # Extract player name
            for gem in all_gems:
                if gem.player_name == player_name:
                    selected_gem_objects.append(gem)
                    break
        
        if len(selected_gem_objects) >= 2:
            # Create comparison table
            comparison_data = []
            for gem in selected_gem_objects:
                comparison_data.append({
                    'Player': gem.player_name,
                    'Position': gem.position,
                    'Price': f"£{gem.current_price:.1f}m",
                    'Ownership': f"{gem.ownership:.1f}%",
                    'Gem Score': f"{gem.gem_score:.1f}",
                    'Confidence': f"{gem.confidence:.0%}",
                    'Gem Type': gem.gem_type
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, hide_index=True, use_container_width=True)
            
            # Radar chart comparison
            fig = go.Figure()
            
            for gem in selected_gem_objects:
                # Normalize metrics for radar chart
                metrics = [
                    gem.gem_score / 20 * 100,  # Gem score
                    gem.confidence * 100,      # Confidence
                    (10 - gem.ownership) * 10, # Ownership (inverted)
                    min(100, gem.current_price * 10)  # Price
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=metrics,
                    theta=['Gem Score', 'Confidence', 'Low Ownership', 'Value'],
                    fill='toself',
                    name=gem.player_name
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="Gem Comparison Radar Chart",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _generate_sentiment_analysis(self, df: pd.DataFrame) -> List[Dict]:
        """Generate simulated sentiment analysis data"""
        # This would connect to Twitter API, Reddit, etc. in production
        sentiment_data = []
        
        # Select popular players for sentiment analysis
        popular_players = df[df['selected_by_percent'] >= 5.0].sample(min(20, len(df)))
        
        for _, player in popular_players.iterrows():
            # Simulate sentiment based on form and ownership
            base_sentiment = (player['form'] - 5) * 20  # -100 to +100 scale
            
            # Add some randomness
            sentiment_score = base_sentiment + np.random.normal(0, 15)
            sentiment_score = np.clip(sentiment_score, -100, 100)
            
            # Categorize sentiment
            if sentiment_score >= 30:
                category = "Positive"
            elif sentiment_score <= -30:
                category = "Negative"
            else:
                category = "Neutral"
            
            # Simulate mention volume based on ownership
            mentions = int(player['selected_by_percent'] * np.random.uniform(10, 50))
            
            sentiment_data.append({
                'player_name': player['web_name'],
                'sentiment_score': sentiment_score,
                'sentiment_category': category,
                'mentions': mentions,
                'ownership': player['selected_by_percent']
            })
        
        return sentiment_data

print("✅ Phase 2 Enhanced Sub-Pages created successfully!")
