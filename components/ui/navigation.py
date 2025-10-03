"""
Unified Navigation System for FPL Analytics
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import streamlit as st


@dataclass
class NavigationItem:
    """Represents a navigation item"""
    id: str
    label: str
    icon: str
    description: str
    order: int = 0


class UnifiedNavigation:
    """Single source of truth for application navigation"""
    
    def __init__(self):
        self.nav_items: Dict[str, NavigationItem] = {
            "dashboard": NavigationItem(
                id="dashboard",
                label="Dashboard",
                icon="📊",
                description="Overview of key FPL metrics and insights",
                order=1
            ),
            "player_analysis": NavigationItem(
                id="player_analysis",
                label="Player Analysis",
                icon="👥",
                description="Detailed player performance statistics and trends",
                order=2
            ),
            "fixture_difficulty": NavigationItem(
                id="fixture_difficulty",
                label="Fixture Difficulty",
                icon="🎯",
                description="Analyze upcoming fixture difficulty ratings",
                order=3
            ),
            "my_fpl_team": NavigationItem(
                id="my_fpl_team",
                label="My FPL Team",
                icon="⚽",
                description="Manage and optimize your FPL team",
                order=4
            ),
            "ai_recommendations": NavigationItem(
                id="ai_recommendations",
                label="AI Recommendations",
                icon="🤖",
                description="Get AI-powered transfer and team suggestions",
                order=5
            ),
            "team_builder": NavigationItem(
                id="team_builder",
                label="Team Builder",
                icon="🔧",
                description="Build and plan your optimal FPL team",
                order=6
            )
        }
        
        # Ensure navigation state exists
        if "nav_selection" not in st.session_state:
            st.session_state.nav_selection = "player_analysis"

    def render(self) -> str:
        """Render the mobile-optimized navigation component"""
        st.markdown("""
            <style>
                /* Enhanced navigation styles for web */
                .nav-container {
                    background: white;
                    border-radius: var(--border-radius);
                    padding: 0.75rem;
                    margin: 0 0 2rem 0;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }
                
                .nav-pills {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.75rem;
                    padding: 0.5rem;
                    justify-content: center;
                }
                
                /* Hide scrollbar for better aesthetics */
                .nav-pills::-webkit-scrollbar {
                    display: none;
                }
                
                /* Enhanced navigation pills */
                .nav-pill {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.75rem 1.25rem;
                    border-radius: var(--border-radius);
                    background: var(--background-color);
                    color: var(--text-color);
                    font-weight: 500;
                    transition: all 0.2s ease;
                    cursor: pointer;
                    border: 1px solid #e2e8f0;
                    min-width: 120px;
                    justify-content: center;
                }
                
                .nav-pill:hover {
                    background: #f8fafc;
                    transform: translateY(-1px);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                
                .nav-pill.active {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    border: none;
                    box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.2);
                }
                
                .nav-pill.active:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 8px -2px rgba(102, 126, 234, 0.25);
                }
                
                /* Navigation icons */
                .nav-icon {
                    font-size: 1.25rem;
                    display: inline-block;
                    vertical-align: middle;
                }
                
                /* Responsive adjustments */
                @media (min-width: 1024px) {
                    .nav-container {
                        padding: 1rem;
                    }
                    
                    .nav-pills {
                        gap: 1rem;
                    }
                    
                    .nav-pill {
                        padding: 1rem 1.5rem;
                    }
                }
                
                /* Mobile optimizations */
                @media (max-width: 768px) {
                    .nav-pills {
                        flex-wrap: nowrap;
                        overflow-x: auto;
                        justify-content: flex-start;
                        -webkit-overflow-scrolling: touch;
                        padding: 0.25rem;
                    }
                    
                    .nav-pill {
                        min-width: auto;
                        padding: 0.5rem 1rem;
                    }
                }
                
                .nav-pill {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 0.5rem 1rem;
                    white-space: nowrap;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-size: 0.875rem;
                }
                
                .nav-pill.active {
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                }
                
                @media (min-width: 768px) {
                    .nav-pills {
                        flex-wrap: wrap;
                        justify-content: center;
                    }
                    
                    .nav-pill {
                        font-size: 1rem;
                    }
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Create navigation pills
        sorted_items = sorted(self.nav_items.values(), key=lambda x: x.order)
        
        st.markdown('<div class="nav-container"><div class="nav-pills">', unsafe_allow_html=True)
        
        for item in sorted_items:
            active_class = "active" if st.session_state.nav_selection == item.id else ""
            if st.markdown(f"""
                <div class="nav-pill {active_class}" onclick="handle_{item.id}_click()">
                    {item.icon} {item.label}
                </div>
                <script>
                    function handle_{item.id}_click() {{
                        window.streamlitPythonData = "{item.id}";
                    }}
                </script>
                """, unsafe_allow_html=True):
                st.session_state.nav_selection = item.id
                st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Add a subtle separator
        st.markdown('<hr style="margin: 1rem 0; opacity: 0.1;">', unsafe_allow_html=True)
        
        return st.session_state.nav_selection
        
        return selected

    def render_sidebar_nav(self) -> None:
        """Legacy sidebar navigation - can be used for additional navigation options"""
        pass

    def get_current_page(self) -> str:
        """Get the current page ID"""
        return st.session_state.nav_selection


# Create a singleton instance for use throughout the application
navigation = UnifiedNavigation()