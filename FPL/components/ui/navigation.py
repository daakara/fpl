"""
Unified Navigation System for FPL Analytics
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import streamlit as st


@dataclass
class NavigationItem:
    """Represents a navigation item"""
    id: str
    label: str
    icon: str
    description: str
    order: int = 0


class UnifiedNavigation:
    """Single source of truth for application navigation"""
    
    def __init__(self):
        self.nav_items: Dict[str, NavigationItem] = {
            "dashboard": NavigationItem(
                id="dashboard",
                label="Dashboard",
                icon="📊",
                description="Overview of key FPL metrics and insights",
                order=1
            ),
            "live_data": NavigationItem(
                id="live_data",
                label="Live Data",
                icon="⚡",
                description="Real-time FPL monitoring and live updates",
                order=2
            ),
            "player_analysis": NavigationItem(
                id="player_analysis",
                label="Player Analysis",
                icon="👥",
                description="Detailed player performance statistics and trends",
                order=3
            ),
            "advanced_analysis": NavigationItem(
                id="advanced_analysis",
                label="Advanced Analysis",
                icon="🔬",
                description="Advanced statistical analysis and machine learning insights",
                order=4
            ),
            "fixture_difficulty": NavigationItem(
                id="fixture_difficulty",
                label="Fixture Difficulty",
                icon="🎯",
                description="Analyze upcoming fixture difficulty ratings",
                order=5
            ),
            "my_fpl_team": NavigationItem(
                id="my_fpl_team",
                label="My FPL Team",
                icon="👤",
                description="Analyze your FPL team performance and get personalized insights",
                order=6
            ),
            "ai_recommendations": NavigationItem(
                id="ai_recommendations",
                label="AI Recommendations",
                icon="🤖",
                description="AI-powered transfer suggestions and team optimization",
                order=7
            ),
            "team_builder": NavigationItem(
                id="team_builder",
                label="Team Builder",
                icon="⚽",
                description="Build and optimize your FPL team composition",
                order=8
            )
        }
        
    def get_nav_items(self) -> Dict[str, NavigationItem]:
        """Get all navigation items"""
        return self.nav_items
    
    def get_nav_item(self, item_id: str) -> Optional[NavigationItem]:
        """Get a specific navigation item by ID"""
        return self.nav_items.get(item_id)
    
    def get_ordered_nav_items(self) -> List[NavigationItem]:
        """Get navigation items sorted by order"""
        return sorted(self.nav_items.values(), key=lambda x: x.order)
    
    def get_nav_labels(self) -> List[str]:
        """Get navigation labels for selectbox"""
        sorted_items = sorted(self.nav_items.values(), key=lambda x: x.order)
        return [f"{item.icon} {item.label}" for item in sorted_items]
    
    def get_nav_ids(self) -> List[str]:
        """Get navigation IDs in order"""
        sorted_items = sorted(self.nav_items.values(), key=lambda x: x.order)
        return [item.id for item in sorted_items]
    
    def label_to_id(self, label: str) -> Optional[str]:
        """Convert navigation label back to ID"""
        # Remove icon and space from label
        clean_label = label.split(' ', 1)[1] if ' ' in label else label
        for item in self.nav_items.values():
            if item.label == clean_label:
                return item.id
        return None
    
    def id_to_label(self, item_id: str) -> Optional[str]:
        """Convert navigation ID to full label with icon"""
        item = self.nav_items.get(item_id)
        if item:
            return f"{item.icon} {item.label}"
        return None
    
    def render_sidebar_navigation(self) -> str:
        """Render sidebar navigation and return selected page ID"""
        st.sidebar.title("⚽ FPL Analytics")
        st.sidebar.markdown("---")
        
        # Initialize current page if not exists
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        # Get navigation options
        nav_labels = self.get_nav_labels()
        nav_ids = self.get_nav_ids()
        
        # Find current selection index
        current_id = st.session_state.current_page
        try:
            current_index = nav_ids.index(current_id)
        except ValueError:
            current_index = 0
            st.session_state.current_page = nav_ids[0]
        
        # Render navigation
        selected_label = st.sidebar.selectbox(
            "Navigate to:",
            nav_labels,
            index=current_index,
            key="navigation_selectbox"
        )
        
        # Convert back to ID
        selected_id = self.label_to_id(selected_label)
        if selected_id and selected_id != st.session_state.current_page:
            st.session_state.current_page = selected_id
            st.rerun()
        
        return st.session_state.current_page
    
    def render_status_info(self):
        """Render status information in sidebar"""
        st.sidebar.markdown("---")
        
        # Current page info
        current_item = self.get_nav_item(st.session_state.get('current_page', 'dashboard'))
        if current_item:
            st.sidebar.info(f"📍 **Current:** {current_item.label}")
            st.sidebar.caption(current_item.description)
        
        # Data loading status
        data_loaded = st.session_state.get('data_loaded', False)
        team_loaded = st.session_state.get('fpl_team_loaded', False)
        
        st.sidebar.markdown("**Status:**")
        status_icon = "✅" if data_loaded else "⏳"
        st.sidebar.write(f"{status_icon} Player Data: {'Loaded' if data_loaded else 'Loading...'}")
        
        team_icon = "✅" if team_loaded else "❌"
        st.sidebar.write(f"{team_icon} My FPL Team: {'Loaded' if team_loaded else 'Not loaded'}")
        
        if team_loaded and st.session_state.get('fpl_team_id'):
            st.sidebar.write(f"🆔 Team ID: {st.session_state.fpl_team_id}")


# Create global navigation instance
navigation = UnifiedNavigation()
