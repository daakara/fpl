"""
Real-time Data Synchronization Feature
Implements WebSocket connections and live data updates for FPL Analytics
"""
import asyncio
import websockets
import json
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict

from utils.error_recovery import resilient_api_call
from middleware.error_handling import FPLError, ErrorCategory, ErrorSeverity


class UpdateType(Enum):
    """Types of real-time updates"""
    PLAYER_POINTS = "player_points"
    LIVE_SCORES = "live_scores"
    TEAM_NEWS = "team_news"
    PRICE_CHANGES = "price_changes"
    INJURY_UPDATES = "injury_updates"


@dataclass
class LiveUpdate:
    """Structure for live updates"""
    update_type: UpdateType
    data: Dict[str, Any]
    timestamp: datetime
    gameweek: int
    priority: int = 1  # 1=low, 5=critical


class RealTimeDataManager:
    """Manages real-time data synchronization"""
    
    def __init__(self, update_interval: int = 30):
        self.update_interval = update_interval
        self.subscribers: Dict[UpdateType, List[Callable]] = defaultdict(list)
        self.last_updates: Dict[UpdateType, datetime] = {}
        self.running = False
        self.logger = logging.getLogger(__name__)
        self._update_thread: Optional[threading.Thread] = None
        
        # Cache for recent updates
        self.recent_updates: List[LiveUpdate] = []
        self.max_recent_updates = 100
    
    def subscribe(self, update_type: UpdateType, callback: Callable[[LiveUpdate], None]) -> None:
        """Subscribe to specific update types"""
        self.subscribers[update_type].append(callback)
        self.logger.info(f"New subscriber for {update_type.value}")
    
    def unsubscribe(self, update_type: UpdateType, callback: Callable) -> None:
        """Unsubscribe from updates"""
        if callback in self.subscribers[update_type]:
            self.subscribers[update_type].remove(callback)
    
    def start_sync(self) -> None:
        """Start real-time synchronization"""
        if self.running:
            return
        
        self.running = True
        self._update_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._update_thread.start()
        self.logger.info("Real-time sync started")
    
    def stop_sync(self) -> None:
        """Stop real-time synchronization"""
        self.running = False
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=5.0)
        self.logger.info("Real-time sync stopped")
    
    def _sync_loop(self) -> None:
        """Main synchronization loop"""
        while self.running:
            try:
                self._check_for_updates()
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}", exc_info=True)
                time.sleep(5)  # Wait before retrying
    
    @resilient_api_call("fpl_live_api")
    def _check_for_updates(self) -> None:
        """Check for updates from FPL API"""
        current_time = datetime.now()
        
        # Check different update types based on schedule
        if self._should_check_update(UpdateType.LIVE_SCORES, current_time):
            self._check_live_scores()
        
        if self._should_check_update(UpdateType.PRICE_CHANGES, current_time):
            self._check_price_changes()
        
        if self._should_check_update(UpdateType.TEAM_NEWS, current_time):
            self._check_team_news()
    
    def _should_check_update(self, update_type: UpdateType, current_time: datetime) -> bool:
        """Determine if we should check for a specific update type"""
        last_check = self.last_updates.get(update_type)
        if not last_check:
            return True
        
        # Different update frequencies for different types
        intervals = {
            UpdateType.LIVE_SCORES: 30,      # Every 30 seconds during matches
            UpdateType.PRICE_CHANGES: 300,   # Every 5 minutes
            UpdateType.TEAM_NEWS: 600,       # Every 10 minutes
            UpdateType.INJURY_UPDATES: 900   # Every 15 minutes
        }
        
        interval = intervals.get(update_type, 60)
        return (current_time - last_check).total_seconds() >= interval
    
    def _check_live_scores(self) -> None:
        """Check for live score updates"""
        try:
            # This would fetch live data from FPL API
            # Implementation depends on available endpoints
            
            # Simulate getting live data
            live_data = self._fetch_live_gameweek_data()
            
            if live_data:
                update = LiveUpdate(
                    update_type=UpdateType.LIVE_SCORES,
                    data=live_data,
                    timestamp=datetime.now(),
                    gameweek=self._get_current_gameweek(),
                    priority=3
                )
                
                self._notify_subscribers(update)
                self.last_updates[UpdateType.LIVE_SCORES] = datetime.now()
        
        except Exception as e:
            self.logger.error(f"Error checking live scores: {e}")
    
    def _check_price_changes(self) -> None:
        """Check for price changes"""
        try:
            # Fetch current prices and compare with cached values
            current_prices = self._fetch_current_prices()
            cached_prices = self._get_cached_prices()
            
            price_changes = self._detect_price_changes(current_prices, cached_prices)
            
            if price_changes:
                update = LiveUpdate(
                    update_type=UpdateType.PRICE_CHANGES,
                    data={"changes": price_changes},
                    timestamp=datetime.now(),
                    gameweek=self._get_current_gameweek(),
                    priority=4
                )
                
                self._notify_subscribers(update)
                self._cache_prices(current_prices)
                
            self.last_updates[UpdateType.PRICE_CHANGES] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error checking price changes: {e}")
    
    def _check_team_news(self) -> None:
        """Check for team news updates"""
        try:
            # This would integrate with news APIs or scrape official sources
            team_news = self._fetch_team_news()
            
            if team_news:
                update = LiveUpdate(
                    update_type=UpdateType.TEAM_NEWS,
                    data=team_news,
                    timestamp=datetime.now(),
                    gameweek=self._get_current_gameweek(),
                    priority=2
                )
                
                self._notify_subscribers(update)
            
            self.last_updates[UpdateType.TEAM_NEWS] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error checking team news: {e}")
    
    def _notify_subscribers(self, update: LiveUpdate) -> None:
        """Notify all subscribers of an update"""
        subscribers = self.subscribers.get(update.update_type, [])
        
        for callback in subscribers:
            try:
                callback(update)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
        
        # Store recent update
        self.recent_updates.append(update)
        if len(self.recent_updates) > self.max_recent_updates:
            self.recent_updates.pop(0)
    
    # Helper methods (would be implemented based on actual API)
    def _fetch_live_gameweek_data(self) -> Optional[Dict[str, Any]]:
        """Fetch live gameweek data"""
        # Implementation would depend on FPL API endpoints
        return None
    
    def _fetch_current_prices(self) -> Dict[int, float]:
        """Fetch current player prices"""
        # Implementation would fetch from bootstrap endpoint
        return {}
    
    def _get_cached_prices(self) -> Dict[int, float]:
        """Get cached prices for comparison"""
        # Implementation would use cache service
        return {}
    
    def _detect_price_changes(self, current: Dict[int, float], cached: Dict[int, float]) -> List[Dict[str, Any]]:
        """Detect price changes between current and cached"""
        changes = []
        
        for player_id, current_price in current.items():
            cached_price = cached.get(player_id)
            if cached_price and current_price != cached_price:
                changes.append({
                    "player_id": player_id,
                    "old_price": cached_price,
                    "new_price": current_price,
                    "change": current_price - cached_price
                })
        
        return changes
    
    def _cache_prices(self, prices: Dict[int, float]) -> None:
        """Cache prices for future comparison"""
        # Implementation would use cache service
        pass
    
    def _fetch_team_news(self) -> Optional[Dict[str, Any]]:
        """Fetch team news"""
        # Implementation would integrate with news sources
        return None
    
    def _get_current_gameweek(self) -> int:
        """Get current gameweek number"""
        # Implementation would determine current GW
        return 1
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get real-time sync status"""
        return {
            "running": self.running,
            "subscribers": {ut.value: len(subs) for ut, subs in self.subscribers.items()},
            "last_updates": {ut.value: lu.isoformat() for ut, lu in self.last_updates.items()},
            "recent_updates_count": len(self.recent_updates),
            "update_interval": self.update_interval
        }


class StreamlitRealTimeIntegration:
    """Integration layer for Streamlit real-time features"""
    
    def __init__(self, data_manager: RealTimeDataManager):
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
        # Streamlit session state keys for real-time data
        self.LIVE_SCORES_KEY = "live_scores"
        self.PRICE_CHANGES_KEY = "price_changes"
        self.TEAM_NEWS_KEY = "team_news"
    
    def setup_real_time_display(self) -> None:
        """Setup real-time display components in Streamlit"""
        import streamlit as st
        
        # Initialize session state
        if self.LIVE_SCORES_KEY not in st.session_state:
            st.session_state[self.LIVE_SCORES_KEY] = []
        
        if self.PRICE_CHANGES_KEY not in st.session_state:
            st.session_state[self.PRICE_CHANGES_KEY] = []
        
        if self.TEAM_NEWS_KEY not in st.session_state:
            st.session_state[self.TEAM_NEWS_KEY] = []
        
        # Subscribe to updates
        self.data_manager.subscribe(UpdateType.LIVE_SCORES, self._handle_live_scores)
        self.data_manager.subscribe(UpdateType.PRICE_CHANGES, self._handle_price_changes)
        self.data_manager.subscribe(UpdateType.TEAM_NEWS, self._handle_team_news)
        
        # Start sync if not already running
        if not self.data_manager.running:
            self.data_manager.start_sync()
    
    def _handle_live_scores(self, update: LiveUpdate) -> None:
        """Handle live score updates"""
        import streamlit as st
        
        # Update session state
        current_scores = st.session_state.get(self.LIVE_SCORES_KEY, [])
        current_scores.insert(0, update.data)
        
        # Keep only recent updates
        st.session_state[self.LIVE_SCORES_KEY] = current_scores[:10]
        
        # Trigger rerun if appropriate
        st.rerun()
    
    def _handle_price_changes(self, update: LiveUpdate) -> None:
        """Handle price change updates"""
        import streamlit as st
        
        current_changes = st.session_state.get(self.PRICE_CHANGES_KEY, [])
        current_changes.insert(0, update.data)
        
        st.session_state[self.PRICE_CHANGES_KEY] = current_changes[:20]
        st.rerun()
    
    def _handle_team_news(self, update: LiveUpdate) -> None:
        """Handle team news updates"""
        import streamlit as st
        
        current_news = st.session_state.get(self.TEAM_NEWS_KEY, [])
        current_news.insert(0, update.data)
        
        st.session_state[self.TEAM_NEWS_KEY] = current_news[:15]
        st.rerun()
    
    def display_real_time_dashboard(self) -> None:
        """Display real-time dashboard in Streamlit"""
        import streamlit as st
        
        st.subheader("🔴 Live Updates")
        
        # Live scores section
        with st.container():
            st.write("**Live Scores**")
            live_scores = st.session_state.get(self.LIVE_SCORES_KEY, [])
            
            if live_scores:
                for score in live_scores[:3]:  # Show top 3
                    st.info(f"⚽ {score.get('match', 'Match update')}")
            else:
                st.write("No live scores available")
        
        # Price changes section
        with st.container():
            st.write("**Recent Price Changes**")
            price_changes = st.session_state.get(self.PRICE_CHANGES_KEY, [])
            
            if price_changes:
                for change_data in price_changes[:5]:
                    changes = change_data.get('changes', [])
                    for change in changes[:3]:
                        direction = "📈" if change['change'] > 0 else "📉"
                        st.write(f"{direction} Player {change['player_id']}: {change['old_price']} → {change['new_price']}")
            else:
                st.write("No recent price changes")
        
        # Team news section
        with st.container():
            st.write("**Latest Team News**")
            team_news = st.session_state.get(self.TEAM_NEWS_KEY, [])
            
            if team_news:
                for news in team_news[:3]:
                    st.success(f"📰 {news.get('headline', 'Team news update')}")
            else:
                st.write("No recent team news")


# Global real-time manager instance
real_time_manager = RealTimeDataManager()