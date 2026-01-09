"""
Global Styles Module - Manages application-wide CSS styling
"""
import streamlit as st
from dataclasses import dataclass
from typing import Optional


@dataclass
class StyleConfig:
    """Configuration for global styles"""
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    success_color: str = "#48bb78"
    warning_color: str = "#ed8936"
    error_color: str = "#f56565"
    border_radius: str = "8px"
    shadow: str = "0 2px 4px rgba(0,0,0,0.1)"
    transition: str = "all 0.3s ease"


class StyleManager:
    """Manages application-wide styling"""
    def __init__(self, config: Optional[StyleConfig] = None):
        self.config = config or StyleConfig()

    def apply_global_styles(self):
        """Apply enhanced global CSS styling"""
        st.markdown(self._get_global_styles(), unsafe_allow_html=True)

    def _get_global_styles(self) -> str:
        """Generate CSS styles based on configuration"""
        return f"""
        <style>
        /* --- CSS Variables --- */
        :root {{
            --primary-color: {self.config.primary_color};
            --secondary-color: {self.config.secondary_color};
            --success-color: {self.config.success_color};
            --warning-color: {self.config.warning_color};
            --error-color: {self.config.error_color};
            --background-color: #f8fafc;
            --text-color: #1a202c;
            --border-radius: {self.config.border_radius};
            --shadow: {self.config.shadow};
            --transition: {self.config.transition};
        }}

        /* --- Global Layout & Typography --- */
        .main {{
            padding-top: 2rem;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.02em;
        }}

        /* --- Component Styles: Buttons, Cards, Metrics --- */
        .stButton > button {{
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            letter-spacing: 0.025em;
            transition: var(--transition);
            box-shadow: var(--shadow);
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}

        .metric-container {{
            background: white;
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary-color);
            margin: 1rem 0;
            transition: var(--transition);
        }}
        .metric-container:hover {{
            transform: translateY(-2px);
        }}

        .feature-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: var(--transition);
        }}
        .feature-card:hover {{
            transform: translateY(-5px);
        }}

        /* --- Data Display: Tables & Tabs --- */
        .dataframe {{
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            font-size: 0.9rem;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
            background: #f1f5f9;
            padding: 0.25rem;
            border-radius: var(--border-radius);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            white-space: nowrap;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        /* --- State & Feedback Styles --- */
        .success-message {{
            background: linear-gradient(90deg, var(--success-color) 0%, #a8e6cf 100%);
            color: white; padding: 1rem; border-radius: var(--border-radius); margin: 1rem 0;
        }}
        .error-message {{
            background: linear-gradient(90deg, var(--error-color) 0%, #ff4b2b 100%);
            color: white; padding: 1rem; border-radius: var(--border-radius); margin: 1rem 0;
        }}
        .performance-badge {{
            display: inline-block; padding: 0.25rem 0.75rem; border-radius: 12px;
            font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
        }}
        .performance-good {{ background: var(--success-color); color: white; }}
        .performance-medium {{ background: var(--warning-color); color: white; }}
        .performance-poor {{ background: var(--error-color); color: white; }}

        /* --- Loading Spinner --- */
        .spinner {{
            border: 4px solid #f3f3f3; border-top: 4px solid var(--primary-color);
            border-radius: 50%; width: 50px; height: 50px;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        /* --- Dark Mode --- */
        @media (prefers-color-scheme: dark) {{
            .feature-card {{
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                color: white;
            }}
            .metric-container, .dataframe {{
                background: #2d3748;
                color: white;
            }}
        }}

        /* --- Mobile Responsiveness --- */
        @media (max-width: 768px) {{
            .main {{ padding: 1rem; }}
            .feature-card {{ padding: 1rem; margin: 0.5rem 0; }}
            .stButton > button {{ width: 100%; margin: 0.25rem 0; }}
            .dataframe {{ font-size: 0.8rem; overflow-x: auto; }}
            .stTabs [data-baseweb="tab-list"] {{ overflow-x: auto; }}
        }}
        </style>
        """


# Create a default style manager instance
default_style_manager = StyleManager()