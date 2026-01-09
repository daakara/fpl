from typing import List
import flet as ft
from utils.theme import PLTheme, Spacing

def create_player_card(name: str, stats: List[tuple], icon: str = "⚽", highlight: bool = False):
    """Create a player card with stats
    stats format: [(label, value, color), ...]
    """
    stat_items = []
    for i, (label, value, color) in enumerate(stats):
        stat_items.append(ft.Text(label, size=12, color=color))
        if value: # Only add value if it's not empty
            stat_items.append(ft.Text(value, size=12, color=color))
        if i < len(stats) - 1: # Add separator between items
            stat_items.append(ft.Text("•", size=12, color=PLTheme.ON_SURFACE_VARIANT))
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(icon, size=16),
                        ft.Text(name, size=16, color=PLTheme.ON_SURFACE, expand=True, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Row(stat_items, spacing=4, wrap=True) if stat_items else ft.Container(),
            ],
            spacing=6,
        ),
        bgcolor=PLTheme.SURFACE if highlight else "transparent",
        border_radius=8 if highlight else 0,
        padding=Spacing.MD,
        border=ft.Border(
            bottom=ft.BorderSide(1, PLTheme.DIVIDER),
        ),
    )
