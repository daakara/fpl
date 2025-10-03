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
        /* Enhanced Global Styles */
        .main {{
            padding-top: 2rem;
        }}
        
        /* Modern Button Styles */
        .stButton > button {{
            background: linear-gradient(90deg, {self.config.primary_color} 0%, {self.config.secondary_color} 100%);
            color: white;
            border: none;
            border-radius: {self.config.border_radius};
            font-weight: 500;
            transition: {self.config.transition};
            box-shadow: {self.config.shadow};
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        /* Enhanced Metrics */
        .metric-container {{
            background: white;
            padding: 1.5rem;
            border-radius: {self.config.border_radius};
            box-shadow: {self.config.shadow};
            border-left: 4px solid {self.config.primary_color};
            margin: 1rem 0;
        }}
        
        /* Modern Cards */
        .feature-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: {self.config.transition};
        }}
        
        /* Success/Error States */
        .success-message {{
            background: linear-gradient(90deg, {self.config.success_color} 0%, #a8e6cf 100%);
            color: white;
            padding: 1rem;
            border-radius: {self.config.border_radius};
            margin: 1rem 0;
        }}
        
        .error-message {{
            background: linear-gradient(90deg, {self.config.error_color} 0%, #ff4b2b 100%);
            color: white;
            padding: 1rem;
            border-radius: {self.config.border_radius};
            margin: 1rem 0;
        }}
        
        /* Performance Indicators */
        .performance-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .performance-good {{ background: {self.config.success_color}; color: white; }}
        .performance-medium {{ background: {self.config.warning_color}; color: white; }}
        .performance-poor {{ background: {self.config.error_color}; color: white; }}
        
        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {{
            .feature-card {{
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                color: white;
            }}
            
            .metric-container {{
                background: #2d3748;
                color: white;
            }}
        }}
        
        /* Mobile Responsiveness */
        @media (max-width: 768px) {{
            .main {{ padding: 1rem; }}
            .feature-card {{ padding: 1rem; margin: 0.5rem 0; }}
            .stButton > button {{ width: 100%; margin: 0.25rem 0; }}
        }}
        </style>
        """


# Create a default style manager instance
default_style_manager = StyleManager()