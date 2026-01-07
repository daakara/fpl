"""
Learning Resources page for Flet app
FPL glossary and strategy guides
"""

import flet as ft


class LearningResourcesPage:
    """Learning resources page component"""
    
    def __init__(self):
        self.current_tab = 0
    
    def build(self) -> ft.Control:
        """Build learning resources UI"""
        
        # Glossary terms (sample - full list in components/learning_resources.py)
        glossary_terms = {
            "xG": {
                "term": "Expected Goals (xG)",
                "definition": "Statistical measure of scoring chance quality",
                "usage": "High xG with low goals suggests future returns"
            },
            "ICT Index": {
                "term": "ICT Index",
                "definition": "Influence, Creativity, Threat combined metric",
                "usage": "Higher ICT (>10) indicates high involvement"
            },
            "FDR": {
                "term": "Fixture Difficulty Rating",
                "definition": "Official rating (1-5) of opponent difficulty",
                "usage": "Target players with FDR 1-2 for next 5 fixtures"
            },
        }
        
        # Strategy guides (sample)
        strategy_guides = {
            "Season Start": {
                "title": "Season Start Strategy (GW1-8)",
                "tips": [
                    "Start with premium assets (Salah, Haaland)",
                    "Focus on teams with good opening fixtures",
                    "Keep 0.5-1.0m in the bank for flexibility",
                    "Don't use chips early - save for DGW/BGW"
                ]
            },
            "Chip Strategy": {
                "title": "Chip Strategy Guide",
                "tips": [
                    "Wildcard 1: GW8-12 (fixture swing)",
                    "Bench Boost: First DGW with 15 DGW players",
                    "Triple Captain: Best DGW for premium",
                    "Free Hit: BGW31 or final DGW/BGW"
                ]
            },
        }
        
        # Build tabs
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Glossary",
                    icon=ft.icons.BOOK,
                    content=self._build_glossary_tab(glossary_terms)
                ),
                ft.Tab(
                    text="Strategies",
                    icon=ft.icons.LIGHTBULB,
                    content=self._build_strategies_tab(strategy_guides)
                ),
            ],
            expand=True,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Learning Resources",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                        padding=ft.padding.only(left=16, right=16, top=16, bottom=8)
                    ),
                    tabs,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _build_glossary_tab(self, terms: dict) -> ft.Control:
        """Build glossary tab content"""
        
        term_cards = []
        for key, data in terms.items():
            term_cards.append(
                ft.ExpansionTile(
                    title=ft.Text(data['term'], weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(data['definition']),
                    controls=[
                        ft.ListTile(
                            title=ft.Text("How to Use", size=12, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(data['usage']),
                        ),
                    ],
                )
            )
        
        return ft.ListView(
            controls=term_cards,
            padding=16,
        )
    
    def _build_strategies_tab(self, guides: dict) -> ft.Control:
        """Build strategies tab content"""
        
        guide_cards = []
        for key, data in guides.items():
            tips_list = [
                ft.Text(f"• {tip}", size=14)
                for tip in data['tips']
            ]
            
            guide_cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    data['title'],
                                    size=18,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Divider(height=1),
                                *tips_list,
                            ],
                            spacing=8,
                        ),
                        padding=16,
                    ),
                )
            )
        
        return ft.ListView(
            controls=guide_cards,
            padding=16,
            spacing=16,
        )
