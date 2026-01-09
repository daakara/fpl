import flet as ft
from utils.theme import PLTheme, Typography, Spacing

def create_error_view(message: str, retry_callback=None):
    """Create an error view with optional retry button"""
    controls = [
        ft.Text("❌", size=64),
        ft.Text("Oops!", size=Typography.HEADING_1, weight=ft.FontWeight.BOLD, color=PLTheme.ON_SURFACE),
        ft.Text(message, size=Typography.BODY, color=PLTheme.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER),
    ]
    
    if retry_callback:
        controls.append(
            ft.FilledButton(
                "↻ Retry",
                on_click=retry_callback,
                style=ft.ButtonStyle(
                    bgcolor=PLTheme.ACCENT,
                    color=PLTheme.PRIMARY,
                ),
            )
        )
    
    return ft.Container(
        content=ft.Column(
            controls,
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=40,
        alignment=ft.alignment.Alignment(0, 0),
    )

def create_loading_view(message: str = "Loading data..."):
    """Create a loading view"""
    return ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(color=PLTheme.ACCENT, width=48, height=48),
                ft.Container(height=Spacing.LG),
                ft.Text(message, size=Typography.BODY, color=PLTheme.ON_SURFACE_VARIANT),
            ],
            spacing=Spacing.LG,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=Spacing.XXL,
        alignment=ft.alignment.Alignment(0, 0),
        expand=True,
    )
