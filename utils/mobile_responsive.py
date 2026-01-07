"""
Mobile Responsiveness Utility
Provides viewport detection and responsive layout helpers
"""

import streamlit as st
from typing import Literal, Tuple


class MobileResponsive:
    """Handles mobile responsiveness detection and layout optimization"""
    
    # Breakpoints
    MOBILE_BREAKPOINT = 768
    TABLET_BREAKPOINT = 1024
    
    @staticmethod
    def detect_viewport() -> dict:
        """
        Detect viewport size using Streamlit's browser info
        Returns dict with viewport info
        """
        # Use JavaScript to get actual viewport width
        viewport_script = """
        <script>
        const width = window.innerWidth;
        const height = window.innerHeight;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            viewport: {width: width, height: height}
        }, '*');
        </script>
        """
        
        # Initialize in session state
        if 'viewport_width' not in st.session_state:
            st.session_state.viewport_width = 1920  # Default desktop
        if 'viewport_height' not in st.session_state:
            st.session_state.viewport_height = 1080
            
        return {
            'width': st.session_state.viewport_width,
            'height': st.session_state.viewport_height
        }
    
    @staticmethod
    def is_mobile() -> bool:
        """Check if viewport is mobile size"""
        viewport = MobileResponsive.detect_viewport()
        return viewport['width'] < MobileResponsive.MOBILE_BREAKPOINT
    
    @staticmethod
    def is_tablet() -> bool:
        """Check if viewport is tablet size"""
        viewport = MobileResponsive.detect_viewport()
        width = viewport['width']
        return MobileResponsive.MOBILE_BREAKPOINT <= width < MobileResponsive.TABLET_BREAKPOINT
    
    @staticmethod
    def is_desktop() -> bool:
        """Check if viewport is desktop size"""
        viewport = MobileResponsive.detect_viewport()
        return viewport['width'] >= MobileResponsive.TABLET_BREAKPOINT
    
    @staticmethod
    def get_device_type() -> Literal['mobile', 'tablet', 'desktop']:
        """Get current device type"""
        if MobileResponsive.is_mobile():
            return 'mobile'
        elif MobileResponsive.is_tablet():
            return 'tablet'
        else:
            return 'desktop'
    
    @staticmethod
    def get_column_config() -> Tuple[int, ...]:
        """
        Get optimal column configuration based on device
        Returns tuple of column counts
        """
        device = MobileResponsive.get_device_type()
        
        if device == 'mobile':
            return (1,)  # Single column
        elif device == 'tablet':
            return (1, 1)  # Two columns
        else:
            return (1, 1, 1)  # Three columns
    
    @staticmethod
    def responsive_columns(*args, **kwargs):
        """
        Create responsive columns that adapt to viewport
        
        Usage:
            cols = responsive_columns()  # Auto-detects device
            # or
            cols = responsive_columns(mobile=1, tablet=2, desktop=3)
        """
        if args:
            # Standard streamlit columns call
            return st.columns(*args, **kwargs)
        
        # Responsive mode
        device = MobileResponsive.get_device_type()
        mobile_cols = kwargs.get('mobile', 1)
        tablet_cols = kwargs.get('tablet', 2)
        desktop_cols = kwargs.get('desktop', 3)
        
        if device == 'mobile':
            return st.columns(mobile_cols)
        elif device == 'tablet':
            return st.columns(tablet_cols)
        else:
            return st.columns(desktop_cols)
    
    @staticmethod
    def responsive_metric(label: str, value, delta=None, **kwargs):
        """
        Display metric with responsive sizing
        """
        device = MobileResponsive.get_device_type()
        
        if device == 'mobile':
            # Smaller font on mobile
            st.markdown(f"**{label}**")
            st.markdown(f"# {value}")
            if delta:
                st.markdown(f"_{delta}_")
        else:
            # Standard metric on larger screens
            st.metric(label=label, value=value, delta=delta, **kwargs)
    
    @staticmethod
    def responsive_dataframe(df, **kwargs):
        """
        Display dataframe with responsive configuration
        """
        device = MobileResponsive.get_device_type()
        
        if device == 'mobile':
            # Fewer columns on mobile, scrollable
            height = kwargs.get('height', 300)
            st.dataframe(df, height=height, width='stretch')
        elif device == 'tablet':
            # Medium height on tablet
            height = kwargs.get('height', 400)
            st.dataframe(df, height=height, width='stretch')
        else:
            # Full view on desktop
            st.dataframe(df, width='stretch', **kwargs)
    
    @staticmethod
    def add_responsive_css():
        """
        Add custom CSS for mobile optimization
        """
        css = """
        <style>
        /* Mobile optimizations */
        @media (max-width: 768px) {
            /* Increase touch target size */
            .stButton > button {
                min-height: 44px;
                font-size: 16px;
                padding: 12px 24px;
            }
            
            /* Make inputs larger */
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stSelectbox > div > div > select {
                font-size: 16px;
                min-height: 44px;
            }
            
            /* Reduce padding on mobile */
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }
            
            /* Make tables scrollable */
            .dataframe-container {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            
            /* Stack metrics vertically */
            [data-testid="stMetricValue"] {
                font-size: 1.5rem;
            }
            
            /* Larger expander headers */
            .streamlit-expanderHeader {
                font-size: 1.1rem;
                padding: 0.75rem;
            }
        }
        
        /* Tablet optimizations */
        @media (min-width: 769px) and (max-width: 1024px) {
            .block-container {
                padding-left: 2rem;
                padding-right: 2rem;
            }
        }
        
        /* Desktop optimizations */
        @media (min-width: 1025px) {
            .block-container {
                max-width: 1200px;
                padding-left: 3rem;
                padding-right: 3rem;
            }
        }
        
        /* Universal touch improvements */
        * {
            -webkit-tap-highlight-color: rgba(0, 0, 0, 0.1);
        }
        
        /* Improve scrolling on all devices */
        .main {
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    @staticmethod
    def show_device_info(debug=False):
        """
        Show device info for debugging (optional)
        """
        if debug:
            viewport = MobileResponsive.detect_viewport()
            device = MobileResponsive.get_device_type()
            
            with st.expander("🔍 Device Info (Debug)", expanded=False):
                st.write(f"**Device Type:** {device}")
                st.write(f"**Viewport:** {viewport['width']}x{viewport['height']}")
                st.write(f"**Breakpoints:** Mobile < {MobileResponsive.MOBILE_BREAKPOINT}px, Tablet < {MobileResponsive.TABLET_BREAKPOINT}px")


# Convenience functions
def is_mobile() -> bool:
    """Quick check if on mobile device"""
    return MobileResponsive.is_mobile()


def is_tablet() -> bool:
    """Quick check if on tablet device"""
    return MobileResponsive.is_tablet()


def is_desktop() -> bool:
    """Quick check if on desktop device"""
    return MobileResponsive.is_desktop()


def get_device_type() -> Literal['mobile', 'tablet', 'desktop']:
    """Get current device type"""
    return MobileResponsive.get_device_type()


def responsive_columns(*args, **kwargs):
    """Create responsive columns"""
    return MobileResponsive.responsive_columns(*args, **kwargs)


def responsive_metric(label: str, value, delta=None, **kwargs):
    """Display responsive metric"""
    return MobileResponsive.responsive_metric(label, value, delta, **kwargs)


def responsive_dataframe(df, **kwargs):
    """Display responsive dataframe"""
    return MobileResponsive.responsive_dataframe(df, **kwargs)


def add_responsive_css():
    """Add responsive CSS"""
    return MobileResponsive.add_responsive_css()
