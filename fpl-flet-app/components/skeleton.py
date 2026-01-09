import flet as ft
from utils.theme import PLTheme, Spacing

def create_skeleton_card(height: int = 80):
    """Create a loading skeleton card with shimmer effect"""
    return ft.Container(
        height=height,
        bgcolor=PLTheme.SURFACE_VARIANT,
        border_radius=12,
        animate_opacity=300,
        opacity=0.6,
    )

def create_skeleton_list(count: int = 5):
    """Create multiple skeleton cards for list loading"""
    return ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    [
                        create_skeleton_card(60),
                        ft.Container(height=Spacing.SM),
                    ],
                ),
            )
            for _ in range(count)
        ],
        spacing=Spacing.SM,
    )
