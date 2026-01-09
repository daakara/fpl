"""
Theme Manager - Dark/Light mode toggle for FPL app

Provides dark and light theme switching with:
- CSS-based theme implementation
- Session state persistence
- Smooth transitions
- Responsive design

Example:
    >>> theme = ThemeManager()
    >>> theme.inject_theme_css()
    >>> theme.render_theme_toggle()
"""
import streamlit as st
from typing import Literal
from utils.error_handling import logger


ThemeType = Literal['light', 'dark']


class ThemeManager:
    """
    Manage app theme (dark/light mode).
    
    Features:
    - Dark and light color schemes
    - Smooth theme transitions
    - Persistent theme selection
    - Mobile responsive
    """
    
    # Color schemes
    THEMES = {
        'light': {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'background': '#ffffff',
            'secondary_bg': '#f8f9fa',
            'text': '#1a1a1a',
            'text_secondary': '#6c757d',
            'border': '#dee2e6',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
            'card_bg': '#ffffff',
            'card_shadow': 'rgba(0, 0, 0, 0.1)',
            'hover': '#f8f9fa',
            'link': '#667eea'
        },
        'dark': {
            'primary': '#7c3aed',
            'secondary': '#8b5cf6',
            'background': '#0e1117',
            'secondary_bg': '#1a1d24',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0',
            'border': '#2d3139',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'card_bg': '#1a1d24',
            'card_shadow': 'rgba(0, 0, 0, 0.3)',
            'hover': '#262933',
            'link': '#8b5cf6'
        }
    }
    
    def __init__(self):
        """Initialize theme manager."""
        self.logger = logger
        
        # Initialize theme in session state
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
    
    def get_current_theme(self) -> ThemeType:
        """
        Get current theme setting.
        
        Returns:
            Current theme ('light' or 'dark')
        """
        return st.session_state.get('theme', 'light')
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        current = self.get_current_theme()
        st.session_state.theme = 'dark' if current == 'light' else 'light'
    
    def set_theme(self, theme: ThemeType) -> None:
        """
        Set specific theme.
        
        Args:
            theme: 'light' or 'dark'
        """
        if theme in ['light', 'dark']:
            st.session_state.theme = theme
        else:
            self.logger.warning(f"Invalid theme: {theme}, using 'light'")
            st.session_state.theme = 'light'
    
    def inject_theme_css(self) -> None:
        """Inject theme CSS into the app."""
        theme = self.get_current_theme()
        colors = self.THEMES[theme]
        
        css = f"""
        <style>
        /* Theme CSS Variables */
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --background-color: {colors['background']};
            --secondary-bg: {colors['secondary_bg']};
            --text-color: {colors['text']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border']};
            --success-color: {colors['success']};
            --warning-color: {colors['warning']};
            --danger-color: {colors['danger']};
            --info-color: {colors['info']};
            --card-bg: {colors['card_bg']};
            --card-shadow: {colors['card_shadow']};
            --hover-color: {colors['hover']};
            --link-color: {colors['link']};
        }}
        
        /* Global Styles */
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
            transition: all 0.3s ease;
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: var(--secondary-bg);
            border-right: 1px solid var(--border-color);
        }}
        
        section[data-testid="stSidebar"] .css-1d391kg {{
            background-color: var(--secondary-bg);
        }}
        
        /* Cards and Containers */
        .element-container {{
            background-color: var(--card-bg);
        }}
        
        .stMetric {{
            background-color: var(--card-bg);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 4px var(--card-shadow);
        }}
        
        .stMetric:hover {{
            background-color: var(--hover-color);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }}
        
        /* Dataframes */
        .dataframe {{
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
        }}
        
        .dataframe thead tr th {{
            background-color: var(--secondary-bg) !important;
            color: var(--text-color) !important;
            border-bottom: 2px solid var(--primary-color) !important;
        }}
        
        .dataframe tbody tr:hover {{
            background-color: var(--hover-color) !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px var(--card-shadow);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px var(--card-shadow);
        }}
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {{
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }}
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--secondary-bg);
            border-bottom: 2px solid var(--border-color);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: var(--text-secondary);
            background-color: transparent;
        }}
        
        .stTabs [aria-selected="true"] {{
            color: var(--primary-color);
            border-bottom: 2px solid var(--primary-color);
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: var(--secondary-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }}
        
        .streamlit-expanderHeader:hover {{
            background-color: var(--hover-color);
        }}
        
        /* Links */
        a {{
            color: var(--link-color);
        }}
        
        a:hover {{
            color: var(--primary-color);
            text-decoration: underline;
        }}
        
        /* Success/Warning/Error Messages */
        .stSuccess {{
            background-color: var(--success-color);
            color: white;
            border-radius: 6px;
        }}
        
        .stWarning {{
            background-color: var(--warning-color);
            color: white;
            border-radius: 6px;
        }}
        
        .stError {{
            background-color: var(--danger-color);
            color: white;
            border-radius: 6px;
        }}
        
        .stInfo {{
            background-color: var(--info-color);
            color: white;
            border-radius: 6px;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color);
        }}
        
        /* Plotly Charts */
        .js-plotly-plot {{
            background-color: var(--card-bg) !important;
        }}
        
        .js-plotly-plot .plotly .bg {{
            fill: var(--card-bg) !important;
        }}
        
        /* Theme Toggle Button Styling */
        .theme-toggle {{
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 999;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 8px var(--card-shadow);
            transition: all 0.3s ease;
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 12px var(--card-shadow);
        }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def render_theme_toggle(self, position: str = 'sidebar') -> None:
        """
        Render theme toggle button.
        
        Args:
            position: 'sidebar' or 'main'
        """
        current_theme = self.get_current_theme()
        
        # Icon based on current theme
        icon = '🌙' if current_theme == 'light' else '☀️'
        label = 'Dark Mode' if current_theme == 'light' else 'Light Mode'
        
        if position == 'sidebar':
            # Render in sidebar
            if st.button(f"{icon} {label}", key='theme_toggle_sidebar', use_container_width=True):
                self.toggle_theme()
                st.rerun()
        else:
            # Render in main area
            col1, col2, col3 = st.columns([6, 1, 1])
            with col2:
                if st.button(icon, key='theme_toggle_main', help=label):
                    self.toggle_theme()
                    st.rerun()
    
    def get_theme_colors(self) -> dict:
        """
        Get current theme color scheme.
        
        Returns:
            Dict with theme colors
        """
        theme = self.get_current_theme()
        return self.THEMES[theme].copy()
    
    def get_plotly_template(self) -> str:
        """
        Get Plotly template name for current theme.
        
        Returns:
            Plotly template name
        """
        theme = self.get_current_theme()
        return 'plotly_dark' if theme == 'dark' else 'plotly_white'
    
    def apply_plotly_theme(self, fig):
        """
        Apply theme to Plotly figure.
        
        Args:
            fig: Plotly figure object
            
        Returns:
            Updated figure
        """
        colors = self.get_theme_colors()
        template = self.get_plotly_template()
        
        fig.update_layout(
            template=template,
            paper_bgcolor=colors['card_bg'],
            plot_bgcolor=colors['background'],
            font=dict(color=colors['text']),
            title_font=dict(color=colors['text']),
            legend=dict(
                bgcolor=colors['secondary_bg'],
                bordercolor=colors['border']
            )
        )
        
        return fig


# Global instance for convenience
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """
    Get global theme manager instance.
    
    Returns:
        ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def inject_theme() -> None:
    """Inject theme CSS (convenience function)."""
    manager = get_theme_manager()
    manager.inject_theme_css()


def render_theme_toggle(position: str = 'sidebar') -> None:
    """Render theme toggle (convenience function)."""
    manager = get_theme_manager()
    manager.render_theme_toggle(position)


def get_current_theme() -> ThemeType:
    """Get current theme (convenience function)."""
    manager = get_theme_manager()
    return manager.get_current_theme()
