"""
Fixture Ticker - Scrolling banner of upcoming FPL fixtures

Displays a scrolling banner showing:
- Next 5 gameweeks of fixtures
- Team names and kickoff times
- Fixture difficulty ratings
- Auto-scrolling CSS animation

Example:
    >>> ticker = FixtureTicker()
    >>> ticker.render(fixtures_data)
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from utils.error_handling import logger


class FixtureTicker:
    """
    Scrolling fixture ticker component for FPL.
    
    Features:
    - Auto-scrolling animation
    - Difficulty color coding
    - Responsive design
    - Click to pause
    """
    
    # Difficulty colors
    DIFFICULTY_COLORS = {
        1: '#00FF00',  # Very Easy (Green)
        2: '#90EE90',  # Easy (Light Green)
        3: '#FFD700',  # Medium (Gold)
        4: '#FF8C00',  # Hard (Dark Orange)
        5: '#FF0000'   # Very Hard (Red)
    }
    
    def __init__(self):
        """Initialize the fixture ticker."""
        self.logger = logger
    
    def render(
        self,
        fixtures: pd.DataFrame,
        teams: pd.DataFrame,
        num_gameweeks: int = 5,
        speed: str = 'medium'
    ) -> None:
        """
        Render the scrolling fixture ticker.
        
        Args:
            fixtures: DataFrame with fixture data
            teams: DataFrame with team data
            num_gameweeks: Number of gameweeks to show
            speed: 'slow', 'medium', or 'fast'
        """
        try:
            # Get upcoming fixtures
            upcoming = self._get_upcoming_fixtures(fixtures, teams, num_gameweeks)
            
            if not upcoming:
                st.info("🗓️ No upcoming fixtures available")
                return
            
            # Get animation speed
            duration = self._get_animation_duration(speed)
            
            # Inject CSS
            self._inject_ticker_css(duration)
            
            # Render ticker HTML
            ticker_html = self._build_ticker_html(upcoming)
            st.markdown(ticker_html, unsafe_allow_html=True)
            
        except Exception as e:
            self.logger.error(f"Error rendering fixture ticker: {e}")
            st.error("Could not load fixture ticker")
    
    def _get_upcoming_fixtures(
        self,
        fixtures: pd.DataFrame,
        teams: pd.DataFrame,
        num_gameweeks: int
    ) -> List[Dict]:
        """
        Get upcoming fixtures for next N gameweeks.
        
        Args:
            fixtures: Fixture DataFrame
            teams: Teams DataFrame
            num_gameweeks: Number of gameweeks to fetch
            
        Returns:
            List of fixture dicts
        """
        if fixtures.empty:
            return []
        
        # Get current gameweek
        current_gw = self._get_current_gameweek(fixtures)
        
        # Filter for upcoming gameweeks
        upcoming_gws = range(current_gw, min(current_gw + num_gameweeks, 39))
        upcoming_fixtures = fixtures[
            fixtures['event'].isin(upcoming_gws)
        ].copy()
        
        # Sort by gameweek and kickoff time
        upcoming_fixtures = upcoming_fixtures.sort_values(['event', 'kickoff_time'])
        
        # Build fixture list with team names
        fixture_list = []
        team_map = self._build_team_map(teams)
        
        for _, fixture in upcoming_fixtures.head(30).iterrows():  # Limit to 30 fixtures
            home_team = team_map.get(fixture['team_h'], 'Unknown')
            away_team = team_map.get(fixture['team_a'], 'Unknown')
            
            fixture_list.append({
                'gameweek': int(fixture['event']),
                'home_team': home_team,
                'away_team': away_team,
                'home_difficulty': int(fixture.get('team_h_difficulty', 3)),
                'away_difficulty': int(fixture.get('team_a_difficulty', 3)),
                'kickoff_time': self._format_kickoff_time(fixture.get('kickoff_time')),
                'display': f"GW{int(fixture['event'])}: {home_team} vs {away_team}"
            })
        
        return fixture_list
    
    def _get_current_gameweek(self, fixtures: pd.DataFrame) -> int:
        """
        Determine current gameweek.
        
        Args:
            fixtures: Fixture DataFrame
            
        Returns:
            Current gameweek number
        """
        # Check for finished fixtures
        if 'finished' in fixtures.columns:
            finished_fixtures = fixtures[fixtures['finished'] == True]
            if not finished_fixtures.empty:
                return int(finished_fixtures['event'].max()) + 1
        
        # Default to first gameweek
        return int(fixtures['event'].min()) if not fixtures.empty else 1
    
    def _build_team_map(self, teams: pd.DataFrame) -> Dict[int, str]:
        """
        Build mapping of team ID to short name.
        
        Args:
            teams: Teams DataFrame
            
        Returns:
            Dict mapping team_id -> short_name
        """
        if teams.empty:
            return {}
        
        team_map = {}
        for _, team in teams.iterrows():
            team_id = int(team.get('id', team.get('code', 0)))
            short_name = team.get('short_name', team.get('name', f'Team {team_id}'))
            team_map[team_id] = short_name
        
        return team_map
    
    def _format_kickoff_time(self, kickoff: str) -> str:
        """
        Format kickoff time to readable format.
        
        Args:
            kickoff: ISO format kickoff time
            
        Returns:
            Formatted time string
        """
        if pd.isna(kickoff) or not kickoff:
            return "TBD"
        
        try:
            dt = datetime.fromisoformat(kickoff.replace('Z', '+00:00'))
            return dt.strftime('%a %H:%M')
        except:
            return "TBD"
    
    def _get_animation_duration(self, speed: str) -> int:
        """
        Get animation duration based on speed setting.
        
        Args:
            speed: 'slow', 'medium', or 'fast'
            
        Returns:
            Duration in seconds
        """
        speeds = {
            'slow': 60,
            'medium': 40,
            'fast': 20
        }
        return speeds.get(speed, 40)
    
    def _inject_ticker_css(self, duration: int) -> None:
        """
        Inject CSS for scrolling ticker animation.
        
        Args:
            duration: Animation duration in seconds
        """
        css = f"""
        <style>
        .fixture-ticker {{
            width: 100%;
            overflow: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 12px 0;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .ticker-wrap {{
            width: 100%;
            overflow: hidden;
        }}
        
        .ticker-content {{
            display: flex;
            animation: scroll-left {duration}s linear infinite;
            white-space: nowrap;
        }}
        
        .ticker-content:hover {{
            animation-play-state: paused;
        }}
        
        .ticker-item {{
            display: inline-block;
            padding: 0 30px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }}
        
        .ticker-item .gameweek {{
            background: rgba(255, 255, 255, 0.2);
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 8px;
        }}
        
        .ticker-item .teams {{
            margin: 0 8px;
        }}
        
        .ticker-item .time {{
            opacity: 0.8;
            font-size: 14px;
            margin-left: 8px;
        }}
        
        @keyframes scroll-left {{
            0% {{
                transform: translateX(0);
            }}
            100% {{
                transform: translateX(-50%);
            }}
        }}
        
        /* Difficulty indicators */
        .difficulty {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin: 0 3px;
        }}
        
        .diff-1 {{ background-color: #00FF00; }}
        .diff-2 {{ background-color: #90EE90; }}
        .diff-3 {{ background-color: #FFD700; }}
        .diff-4 {{ background-color: #FF8C00; }}
        .diff-5 {{ background-color: #FF0000; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def _build_ticker_html(self, fixtures: List[Dict]) -> str:
        """
        Build HTML for ticker content.
        
        Args:
            fixtures: List of fixture dicts
            
        Returns:
            HTML string for ticker
        """
        # Duplicate content for seamless loop
        items_html = []
        
        for fixture in fixtures:
            home_diff_class = f"diff-{fixture['home_difficulty']}"
            away_diff_class = f"diff-{fixture['away_difficulty']}"
            
            item = f"""
            <div class="ticker-item">
                <span class="gameweek">GW{fixture['gameweek']}</span>
                <span class="teams">
                    <span class="difficulty {home_diff_class}"></span>
                    {fixture['home_team']} vs {fixture['away_team']}
                    <span class="difficulty {away_diff_class}"></span>
                </span>
                <span class="time">{fixture['kickoff_time']}</span>
            </div>
            """
            items_html.append(item)
        
        # Duplicate for seamless scrolling
        all_items = ''.join(items_html) * 2
        
        html = f"""
        <div class="fixture-ticker">
            <div class="ticker-wrap">
                <div class="ticker-content">
                    {all_items}
                </div>
            </div>
        </div>
        """
        
        return html
    
    def render_simple(
        self,
        fixtures: pd.DataFrame,
        teams: pd.DataFrame,
        num_fixtures: int = 10
    ) -> None:
        """
        Render simple non-scrolling fixture list (fallback).
        
        Args:
            fixtures: DataFrame with fixture data
            teams: DataFrame with team data
            num_fixtures: Number of fixtures to show
        """
        upcoming = self._get_upcoming_fixtures(fixtures, teams, 2)
        
        if not upcoming:
            st.info("No upcoming fixtures")
            return
        
        st.markdown("### 📅 Upcoming Fixtures")
        
        for fixture in upcoming[:num_fixtures]:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.caption(f"GW{fixture['gameweek']}")
            
            with col2:
                st.write(f"**{fixture['home_team']}** vs **{fixture['away_team']}**")
            
            with col3:
                st.caption(fixture['kickoff_time'])


# Convenience function
def render_fixture_ticker(
    fixtures: pd.DataFrame,
    teams: pd.DataFrame,
    num_gameweeks: int = 5,
    speed: str = 'medium'
) -> None:
    """
    Render fixture ticker (convenience function).
    
    Args:
        fixtures: Fixture DataFrame
        teams: Teams DataFrame
        num_gameweeks: Number of gameweeks to show
        speed: Animation speed
    """
    ticker = FixtureTicker()
    ticker.render(fixtures, teams, num_gameweeks, speed)
