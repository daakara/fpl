"""
Enhanced Theme Manager for FPL Analytics Dashboard
Provides dark/light theme support with customizable color schemes
"""

import streamlit as st
from typing import Dict, Any

class ThemeManager:
    """Advanced theme management with dark/light mode support"""
    
    def __init__(self):
        self.themes = {
            "light": {
                "primary_color": "#1f77b4",
                "background_color": "#ffffff", 
                "secondary_background_color": "#f0f2f6",
                "text_color": "#262730",
                "font": "sans serif",
                "success_color": "#00cc44",
                "warning_color": "#ff8c00",
                "error_color": "#ff2b2b"
            },
            "dark": {
                "primary_color": "#00d4ff",
                "background_color": "#0e1117",
                "secondary_background_color": "#262730", 
                "text_color": "#fafafa",
                "font": "sans serif",
                "success_color": "#00ff88", 
                "warning_color": "#ffaa00",
                "error_color": "#ff4444"
            },
            "fpl_green": {
                "primary_color": "#00ff87",
                "background_color": "#0a0f0a",
                "secondary_background_color": "#1a2f1a",
                "text_color": "#e8ffe8",
                "font": "sans serif", 
                "success_color": "#00ff87",
                "warning_color": "#ffdd00",
                "error_color": "#ff5555"
            }
        }
    
    def apply_theme(self, theme_name: str = "light"):
        """Apply the selected theme to the Streamlit app"""
        if theme_name not in self.themes:
            theme_name = "light"
        
        theme = self.themes[theme_name]
        
        # Apply theme via CSS injection
        st.markdown(f"""
        <style>
        .stApp {{
            background-color: {theme['background_color']};
            color: {theme['text_color']};
        }}
        
        .stButton > button {{
            background-color: {theme['primary_color']};
            color: {theme['background_color']};
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: {theme['text_color']};
            color: {theme['background_color']};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .stSelectbox > div > div {{
            background-color: {theme['secondary_background_color']};
            color: {theme['text_color']};
        }}
        
        .stMetric {{
            background-color: {theme['secondary_background_color']};
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid {theme['primary_color']};
        }}
        
        .success-metric {{
            border-left-color: {theme['success_color']} !important;
        }}
        
        .warning-metric {{
            border-left-color: {theme['warning_color']} !important;
        }}
        
        .error-metric {{
            border-left-color: {theme['error_color']} !important;
        }}
        
        /* Enhanced status bar styling */
        .status-bar {{
            background: linear-gradient(90deg, {theme['primary_color']}, {theme['secondary_background_color']});
            padding: 0.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }}
        
        /* Performance metrics styling */
        .performance-widget {{
            background-color: {theme['secondary_background_color']};
            border: 1px solid {theme['primary_color']};
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Store theme preference
        st.session_state.current_theme = theme_name
    
    def render_theme_selector(self):
        """Render theme selection widget in sidebar"""
        with st.sidebar:
            st.markdown("### 🎨 Theme Settings")
            
            current_theme = st.session_state.get('current_theme', 'light')
            
            theme_choice = st.selectbox(
                "Choose Theme:",
                options=list(self.themes.keys()),
                index=list(self.themes.keys()).index(current_theme),
                format_func=lambda x: {
                    'light': '☀️ Light Mode',
                    'dark': '🌙 Dark Mode', 
                    'fpl_green': '⚽ FPL Green'
                }.get(x, x)
            )
            
            if theme_choice != current_theme:
                self.apply_theme(theme_choice)
                st.rerun()
            
            # Theme preview
            if st.checkbox("Show Theme Preview", value=False):
                theme = self.themes[theme_choice]
                st.markdown("**Theme Colors:**")
                st.color_picker("Primary", theme['primary_color'], disabled=True)
                st.color_picker("Background", theme['background_color'], disabled=True) 
                st.color_picker("Text", theme['text_color'], disabled=True)
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Get the currently active theme configuration"""
        current_theme_name = st.session_state.get('current_theme', 'light')
        return self.themes[current_theme_name]
    
    def create_themed_metric(self, label: str, value: str, delta: str = None, 
                           metric_type: str = "normal"):
        """Create a metric with theme-appropriate styling"""
        theme = self.get_current_theme()
        
        css_class = {
            "success": "success-metric",
            "warning": "warning-metric", 
            "error": "error-metric"
        }.get(metric_type, "")
        
        st.markdown(f"""
        <div class="stMetric {css_class}">
            <div style="font-size: 0.8rem; color: {theme['text_color']}; opacity: 0.7;">
                {label}
            </div>
            <div style="font-size: 1.8rem; font-weight: 600; color: {theme['text_color']};">
                {value}
            </div>
            {f'<div style="font-size: 0.9rem; color: {theme["success_color"] if "+" in str(delta) else theme["error_color"]};">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

# Global theme manager instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

def apply_current_theme():
    """Apply the current theme (convenience function)"""
    theme_manager = get_theme_manager()
    current_theme = st.session_state.get('current_theme', 'light')
    theme_manager.apply_theme(current_theme)

def render_theme_selector():
    """Render theme selector (convenience function)"""
    theme_manager = get_theme_manager()
    theme_manager.render_theme_selector()
