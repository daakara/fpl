import flet as ft
from utils.theme import PLTheme, Typography, Spacing

def create_section_header(text: str, icon: str = None):
    """Create a section header with optional emoji icon"""
    controls = []
    if icon:
        controls.append(ft.Text(icon, size=Typography.HEADING_3))
    controls.append(ft.Text(text, size=Typography.HEADING_2, weight=ft.FontWeight.BOLD, color=PLTheme.ON_SURFACE))
    
    return ft.Container(
        content=ft.Row(
            controls,
            spacing=Spacing.SM,
        ),
        padding=ft.Padding(top=Spacing.MD, bottom=Spacing.SM, left=0, right=0),
    )
