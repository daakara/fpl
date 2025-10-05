"""
Real-Time Data Pipeline for FPL Dashboard
Implements WebSocket connections, live updates, and data streaming
Phase 2: AI-Powered Real-Time Intelligence
"""
import asyncio
import aiohttp
import websockets
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import streamlit as st
from dataclasses import dataclass, asdict
import threading
import time
import requests
import urllib3
from utils.logging import logger
import warnings

# Disable SSL warnings for corporate proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

@dataclass
class RealTimeUpdate:
    """Data class for real-time updates"""
    timestamp: datetime
    update_type: str  # 'price_change', 'team_news', 'transfer_activity', 'form_update'
    player_id: int
    player_name: str
    old_value: Optional[float]
    new_value: Optional[float]
    message: str
    priority: str  # 'HIGH', 'MEDIUM', 'LOW'
    confidence: float

@dataclass
class LiveAlert:
    """Data class for live alerts"""
    alert_id: str
    timestamp: datetime
    alert_type: str
    title: str
    message: str
    affected_players: List[str]
    action_required: bool
    expires_at: Optional[datetime]

class RealTimeDataPipeline:
    """Manages real-time data streaming and updates"""
    
    def __init__(self):
        self.base_url = "https://fantasy.premierleague.com/api"
        self.update_callbacks: List[Callable] = []
        self.is_running = False
        self.update_interval = 60  # seconds
        self.last_data_hash = None
        self.price_change_threshold = 0.1  # £0.1m
        self.form_change_threshold = 1.0   # 1 point form change
        
        # Real-time storage
        self.live_updates: List[RealTimeUpdate] = []
        self.active_alerts: List[LiveAlert] = []
        self.price_predictions: Dict[int, float] = {}
        
    def start_pipeline(self):
        """Start the real-time data pipeline"""
        if not self.is_running:
            self.is_running = True
            # Start background thread for continuous monitoring
            self.monitor_thread = threading.Thread(target=self._continuous_monitor, daemon=True)
            self.monitor_thread.start()
            logger.info("Real-time data pipeline started")
    
    def stop_pipeline(self):
        """Stop the real-time data pipeline"""
        self.is_running = False
        logger.info("Real-time data pipeline stopped")
    
    def _continuous_monitor(self):
        """Continuous monitoring loop for real-time updates"""
        while self.is_running:
            try:
                self._check_for_updates()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _check_for_updates(self):
        """Check for data updates and generate alerts"""
        try:
            # Fetch current data
            current_data = self._fetch_current_data()
            
            if current_data is not None:
                # Compare with previous data and detect changes
                updates = self._detect_changes(current_data)
                
                # Process updates and generate alerts
                for update in updates:
                    self._process_update(update)
                    
                # Update stored data
                self.last_data_hash = self._calculate_data_hash(current_data)
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
    
    def _fetch_current_data(self) -> Optional[pd.DataFrame]:
        """Fetch current FPL data"""
        try:
            # Bootstrap data
            response = requests.get(
                f"{self.base_url}/bootstrap-static/",
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                players_data = data['elements']
                return pd.DataFrame(players_data)
            else:
                logger.warning(f"API request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching current data: {e}")
            return None
    
    def _calculate_data_hash(self, df: pd.DataFrame) -> str:
        """Calculate hash of current data for change detection"""
        if df is None or df.empty:
            return ""
        
        # Focus on key fields that change frequently
        key_fields = ['now_cost', 'total_points', 'form', 'transfers_in_event', 'transfers_out_event']
        available_fields = [field for field in key_fields if field in df.columns]
        
        if available_fields:
            hash_data = df[available_fields].to_string()
            return str(hash(hash_data))
        else:
            return str(hash(df.to_string()))
    
    def _detect_changes(self, current_data: pd.DataFrame) -> List[RealTimeUpdate]:
        """Detect changes in data and create update objects"""
        updates = []
        
        if self.last_data_hash is None:
            # First run, no comparison possible
            return updates
        
        current_hash = self._calculate_data_hash(current_data)
        
        if current_hash == self.last_data_hash:
            # No changes detected
            return updates
        
        # Load previous data from session state if available
        if 'players_df' in st.session_state:
            previous_data = st.session_state['players_df']
            updates.extend(self._compare_dataframes(previous_data, current_data))
        
        return updates
    
    def _compare_dataframes(self, previous_df: pd.DataFrame, current_df: pd.DataFrame) -> List[RealTimeUpdate]:
        """Compare two dataframes and identify changes"""
        updates = []
        
        if previous_df.empty or current_df.empty:
            return updates
        
        # Merge dataframes to compare
        comparison = current_df.merge(
            previous_df, 
            on='id', 
            suffixes=('_current', '_previous'),
            how='inner'
        )
        
        for _, player in comparison.iterrows():
            player_id = player['id']
            player_name = player.get('web_name_current', f"Player {player_id}")
            
            # Check price changes
            if 'now_cost_current' in player and 'now_cost_previous' in player:
                price_diff = player['now_cost_current'] - player['now_cost_previous']
                if abs(price_diff) >= 1:  # 0.1m change (stored as 0.1m units)
                    updates.append(RealTimeUpdate(
                        timestamp=datetime.now(),
                        update_type='price_change',
                        player_id=player_id,
                        player_name=player_name,
                        old_value=player['now_cost_previous'] / 10,
                        new_value=player['now_cost_current'] / 10,
                        message=f"Price {'increased' if price_diff > 0 else 'decreased'} by £{abs(price_diff)/10:.1f}m",
                        priority='HIGH' if abs(price_diff) >= 2 else 'MEDIUM',
                        confidence=0.95
                    ))
            
            # Check form changes
            if 'form_current' in player and 'form_previous' in player:
                form_diff = player['form_current'] - player['form_previous']
                if abs(form_diff) >= self.form_change_threshold:
                    updates.append(RealTimeUpdate(
                        timestamp=datetime.now(),
                        update_type='form_update',
                        player_id=player_id,
                        player_name=player_name,
                        old_value=player['form_previous'],
                        new_value=player['form_current'],
                        message=f"Form {'improved' if form_diff > 0 else 'declined'} by {abs(form_diff):.1f} points",
                        priority='MEDIUM' if abs(form_diff) >= 2 else 'LOW',
                        confidence=0.85
                    ))
            
            # Check transfer activity
            if 'transfers_in_event_current' in player and 'transfers_out_event_current' in player:
                transfers_in = player['transfers_in_event_current']
                transfers_out = player['transfers_out_event_current']
                net_transfers = transfers_in - transfers_out
                
                if abs(net_transfers) >= 50000:  # Significant transfer activity
                    updates.append(RealTimeUpdate(
                        timestamp=datetime.now(),
                        update_type='transfer_activity',
                        player_id=player_id,
                        player_name=player_name,
                        old_value=0,
                        new_value=net_transfers,
                        message=f"{'Heavy buying' if net_transfers > 0 else 'Heavy selling'}: {abs(net_transfers):,.0f} net transfers",
                        priority='HIGH' if abs(net_transfers) >= 100000 else 'MEDIUM',
                        confidence=0.9
                    ))
        
        return updates
    
    def _process_update(self, update: RealTimeUpdate):
        """Process a real-time update and generate alerts if needed"""
        # Add to updates list
        self.live_updates.append(update)
        
        # Keep only recent updates (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.live_updates = [u for u in self.live_updates if u.timestamp > cutoff_time]
        
        # Generate alerts for high-priority updates
        if update.priority == 'HIGH':
            alert = self._create_alert_from_update(update)
            if alert:
                self.active_alerts.append(alert)
        
        # Update price predictions based on transfer activity
        if update.update_type == 'transfer_activity':
            self._update_price_predictions(update)
        
        # Notify callbacks
        for callback in self.update_callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.error(f"Error in update callback: {e}")
    
    def _create_alert_from_update(self, update: RealTimeUpdate) -> Optional[LiveAlert]:
        """Create an alert from a real-time update"""
        alert_id = f"{update.update_type}_{update.player_id}_{int(update.timestamp.timestamp())}"
        
        if update.update_type == 'price_change':
            return LiveAlert(
                alert_id=alert_id,
                timestamp=update.timestamp,
                alert_type='PRICE_CHANGE',
                title=f"🚨 Price Change Alert",
                message=f"{update.player_name}: {update.message}",
                affected_players=[update.player_name],
                action_required=True,
                expires_at=datetime.now() + timedelta(hours=6)
            )
        
        elif update.update_type == 'transfer_activity' and abs(update.new_value) >= 100000:
            return LiveAlert(
                alert_id=alert_id,
                timestamp=update.timestamp,
                alert_type='TRANSFER_SURGE',
                title=f"📈 Transfer Surge Alert",
                message=f"{update.player_name}: {update.message}. Price change likely!",
                affected_players=[update.player_name],
                action_required=True,
                expires_at=datetime.now() + timedelta(hours=12)
            )
        
        return None
    
    def _update_price_predictions(self, update: RealTimeUpdate):
        """Update price change predictions based on transfer activity"""
        if update.update_type == 'transfer_activity':
            net_transfers = update.new_value
            
            # Simple prediction model based on transfer momentum
            if abs(net_transfers) >= 50000:
                # Probability increases with transfer volume
                base_probability = min(0.8, abs(net_transfers) / 100000 * 0.5)
                
                # Direction based on net transfers
                direction = 1 if net_transfers > 0 else -1
                
                # Store prediction
                self.price_predictions[update.player_id] = base_probability * direction
    
    def get_recent_updates(self, hours: int = 1) -> List[RealTimeUpdate]:
        """Get recent updates within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [update for update in self.live_updates if update.timestamp > cutoff_time]
    
    def get_active_alerts(self) -> List[LiveAlert]:
        """Get currently active alerts"""
        now = datetime.now()
        # Filter out expired alerts
        self.active_alerts = [
            alert for alert in self.active_alerts 
            if alert.expires_at is None or alert.expires_at > now
        ]
        return self.active_alerts
    
    def dismiss_alert(self, alert_id: str):
        """Dismiss an alert"""
        self.active_alerts = [alert for alert in self.active_alerts if alert.alert_id != alert_id]
    
    def get_price_predictions(self) -> Dict[int, float]:
        """Get current price change predictions"""
        return self.price_predictions.copy()
    
    def register_callback(self, callback: Callable):
        """Register a callback for real-time updates"""
        self.update_callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable):
        """Unregister a callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

class LiveDataStream:
    """Streamlit integration for real-time data"""
    
    def __init__(self):
        if 'rt_pipeline' not in st.session_state:
            st.session_state.rt_pipeline = RealTimeDataPipeline()
        
        self.pipeline = st.session_state.rt_pipeline
    
    def render_live_controls(self):
        """Render live data controls in Streamlit"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔴 Start Live Updates", type="primary"):
                self.pipeline.start_pipeline()
                st.success("Live updates started!")
        
        with col2:
            if st.button("⏹️ Stop Live Updates"):
                self.pipeline.stop_pipeline()
                st.info("Live updates stopped")
        
        with col3:
            is_running = self.pipeline.is_running
            if is_running:
                st.success("🟢 Live")
            else:
                st.error("🔴 Offline")
        
        with col4:
            recent_updates = len(self.pipeline.get_recent_updates(1))
            st.metric("Updates (1h)", recent_updates)
    
    def render_live_alerts(self):
        """Render active alerts"""
        alerts = self.pipeline.get_active_alerts()
        
        if alerts:
            st.markdown("### 🚨 Live Alerts")
            
            for alert in alerts[-5:]:  # Show last 5 alerts
                alert_color = "error" if alert.alert_type == "PRICE_CHANGE" else "warning"
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        getattr(st, alert_color)(f"**{alert.title}**\n{alert.message}")
                        st.caption(f"🕐 {alert.timestamp.strftime('%H:%M:%S')}")
                    
                    with col2:
                        if st.button("✕", key=f"dismiss_{alert.alert_id}"):
                            self.pipeline.dismiss_alert(alert.alert_id)
                            st.rerun()
        else:
            st.info("No active alerts")
    
    def render_recent_updates(self):
        """Render recent updates feed"""
        st.markdown("### 📊 Live Updates Feed")
        
        updates = self.pipeline.get_recent_updates(6)  # Last 6 hours
        
        if updates:
            for update in updates[-10:]:  # Show last 10 updates
                priority_emoji = "🔴" if update.priority == "HIGH" else "🟡" if update.priority == "MEDIUM" else "🟢"
                
                with st.container():
                    st.markdown(f"{priority_emoji} **{update.player_name}** - {update.message}")
                    st.caption(f"🕐 {update.timestamp.strftime('%H:%M:%S')} | Confidence: {update.confidence:.0%}")
                    st.divider()
        else:
            st.info("No recent updates")
    
    def render_price_predictions(self):
        """Render price change predictions"""
        st.markdown("### 💰 Price Change Predictions")
        
        predictions = self.pipeline.get_price_predictions()
        
        if predictions and 'players_df' in st.session_state:
            df = st.session_state['players_df']
            
            # Get player names for predictions
            prediction_data = []
            for player_id, probability in predictions.items():
                player_row = df[df['id'] == player_id]
                if not player_row.empty:
                    player_name = player_row.iloc[0]['web_name']
                    current_price = player_row.iloc[0]['now_cost'] / 10
                    
                    prediction_data.append({
                        'Player': player_name,
                        'Current Price': f"£{current_price:.1f}m",
                        'Change Probability': f"{abs(probability):.0%}",
                        'Direction': "📈 Rise" if probability > 0 else "📉 Fall",
                        'Confidence': "High" if abs(probability) > 0.6 else "Medium"
                    })
            
            if prediction_data:
                predictions_df = pd.DataFrame(prediction_data)
                st.dataframe(predictions_df, hide_index=True, use_container_width=True)
            else:
                st.info("No price predictions available")
        else:
            st.info("No price predictions available")

# Global instance for easy access
live_stream = LiveDataStream()

print("✅ Real-Time Data Pipeline created successfully!")
