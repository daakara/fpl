#!/usr/bin/env python3
"""
Launcher script for the Flet FPL Analytics app.
This script ensures the app runs correctly with relative imports.
"""

if __name__ == "__main__":
    from flet_app.main import main
    import flet as ft
    
    ft.app(main)
