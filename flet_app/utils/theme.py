"""
Theme configuration for Flet app
Matches the Streamlit app's theme system
"""

import flet as ft


def get_app_theme(dark: bool = True) -> ft.Theme:
    """Get app theme (dark or light)"""
    
    if dark:
        return ft.Theme(
            color_scheme_seed="green",
            use_material3=True,
        )
    else:
        return ft.Theme(
            color_scheme_seed="green",
            use_material3=True,
        )


# Color constants (matching Streamlit theme)
COLORS = {
    "primary": "#00ff87",
    "secondary": "#60efff",
    "success": "#00ff87",
    "warning": "#feca57",
    "danger": "#ff6b6b",
    "info": "#60efff",
    "dark_bg": "#0e1117",
    "dark_surface": "#262730",
    "light_bg": "#ffffff",
    "light_surface": "#f0f2f6",
}
