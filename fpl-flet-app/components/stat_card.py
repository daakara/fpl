import flet as ft
from utils.theme import PLTheme, Typography, Spacing

def create_stat_card(title: str, value: str, subtitle: str = "", icon: str = None, color: str = None):
    """Create a styled stat card with optional emoji icon"""
    if color is None:
        color = PLTheme.ACCENT
    
    # Build controls list for the column
    column_controls = []
    
    # Add title with optional icon
    if icon:
        title_row_controls = [
            ft.Text(icon, size=20),
            ft.Text(title, size=14, color=PLTheme.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
        ]
        column_controls.append(ft.Row(title_row_controls, spacing=8))
    else:
        column_controls.append(ft.Text(title, size=14, color=PLTheme.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500))
    
    # Add value
    column_controls.append(ft.Text(value, size=Typography.HEADING_1, weight=ft.FontWeight.BOLD, color=PLTheme.ON_SURFACE))
    
    # Add subtitle if provided
    if subtitle:
        column_controls.append(ft.Text(subtitle, size=Typography.CAPTION, color=PLTheme.ON_SURFACE_DIM))
    
    return ft.Container(
        content=ft.Column(
            column_controls,
            spacing=Spacing.XS,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=PLTheme.SURFACE,
        border_radius=12,
        padding=Spacing.LG,
        expand=True,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color="#00000040",
            offset=ft.Offset(0, 2),
        ),
    )
