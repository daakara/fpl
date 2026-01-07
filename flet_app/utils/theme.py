"""
Theme configuration for Flet app
Matches the Streamlit app's theme system
"""

import flet as ft


def get_app_theme(dark: bool = True) -> ft.Theme:
    """Get app theme (dark or light)"""
    
    if dark:
        return ft.Theme(
            color_scheme_seed=ft.colors.GREEN_ACCENT,
            use_material3=True,
            color_scheme=ft.ColorScheme(
                primary=ft.colors.GREEN_ACCENT_400,
                on_primary=ft.colors.BLACK,
                secondary=ft.colors.BLUE_ACCENT_400,
                on_secondary=ft.colors.BLACK,
                background=ft.colors.GREY_900,
                on_background=ft.colors.WHITE,
                surface=ft.colors.GREY_850,
                on_surface=ft.colors.WHITE,
            ),
        )
    else:
        return ft.Theme(
            color_scheme_seed=ft.colors.GREEN_ACCENT,
            use_material3=True,
            color_scheme=ft.ColorScheme(
                primary=ft.colors.GREEN_700,
                on_primary=ft.colors.WHITE,
                secondary=ft.colors.BLUE_700,
                on_secondary=ft.colors.WHITE,
                background=ft.colors.GREY_50,
                on_background=ft.colors.BLACK,
                surface=ft.colors.WHITE,
                on_surface=ft.colors.BLACK,
            ),
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
