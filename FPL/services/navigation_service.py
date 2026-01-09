"""
Navigation Service
Handles page navigation and routing
"""

import streamlit as st
from streamlit_option_menu import option_menu


class NavigationService:
    """Service for handling navigation and page routing"""
    
    def __init__(self):
        """Initialize the navigation service"""
        self.pages = [
            "Dashboard",
            "Player Analysis", 
            "Team Builder",
            "My Team",
            "AI Recommendations",
            "Advanced Analytics",
            "Fixture Analysis",
            "Price Changes",
            "Live Data",
            "Market Intelligence",
            "Injury & Transfers",
            "Learning Resources"
        ]
        
        self.icons = [
            "speedometer2",
            "person-circle", 
            "tools",
            "trophy-fill",
            "robot",
            "graph-up-arrow",
            "calendar3",
            "cash-coin",
            "broadcast",
            "bar-chart-fill",
            "hospital",
            "book-fill"
        ]
    
    def render_navigation(self):
        """Render main navigation menu matching reference site structure"""
        selected_page = option_menu(
            menu_title=None,
            options=self.pages,
            icons=self.icons,
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#0e1117",
                    "border-radius": "10px",
                    "margin": "0 0 20px 0"
                },
                "icon": {"color": "#00ff87", "font-size": "18px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "center",
                    "margin": "0px",
                    "padding": "10px",
                    "--hover-color": "#60efff33",
                    "border-radius": "8px"
                },
                "nav-link-selected": {
                    "background-color": "#00ff87",
                    "color": "#000000",
                    "font-weight": "bold"
                },
            }
        )
        return selected_page
    
    def get_page_info(self, page_name):
        """Get information about a specific page"""
        page_info = {
            "Dashboard": {
                "description": "Overview of FPL performance and market intelligence",
                "features": ["Key metrics", "Market overview", "Performance analytics"]
            },
            "Player Analysis": {
                "description": "Deep dive into individual player statistics",
                "features": ["Player search", "Performance history", "Value analysis"]
            },
            "Team Builder": {
                "description": "Build and optimize your FPL team",
                "features": ["Squad builder", "Budget management", "Formation optimizer"]
            },
            "My Team": {
                "description": "Analyze your current FPL team",
                "features": ["Team overview", "Performance analysis", "Transfer suggestions"]
            },
            "AI Recommendations": {
                "description": "AI-powered player and strategy recommendations",
                "features": ["Smart picks", "Captain suggestions", "Transfer advice"]
            },
            "Advanced Analytics": {
                "description": "Advanced statistical analysis and modeling",
                "features": ["Predictive analytics", "Historical trends", "Performance modeling"]
            },
            "Fixture Analysis": {
                "description": "Comprehensive fixture difficulty analysis",
                "features": ["Overall difficulty", "Attack analysis", "Defense analysis"]
            },
            "Live Data": {
                "description": "Real-time FPL data monitoring",
                "features": ["Live updates", "API status", "Data freshness"]
            },
            "Market Intelligence": {
                "description": "Transfer market trends and price movements",
                "features": ["Transfer trends", "Price changes", "Ownership data"]
            },
            "Learning Resources": {
                "description": "FPL glossary, strategy guides, and tutorials",
                "features": ["FPL terminology glossary", "Strategy guides for all stages", "Quick start tutorial", "External resources"]
            }
        }
        
        return page_info.get(page_name, {
            "description": "Page information not available",
            "features": []
        })