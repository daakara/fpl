"""
Fixture Analysis Page - Handles fixture difficulty ratings and analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


class FixtureAnalysisPage:
    """Handles fixture analysis functionality"""
    
    def __init__(self):
        pass
    
    def __call__(self):
        """Make the class callable"""
        self.render()
    
    def render(self):
        """Enhanced fixture analysis with difficulty breakdown tabs plus existing analysis"""
        st.markdown("### 📈 **Fixture Analysis & Difficulty**")
        
        # Get live data for teams
        data = self._get_data_safely()
        
        # Debug: Show data status
        if data and 'teams' in data:
            st.success(f"✅ **Live FPL Data Connected** - {len(data.get('teams', []))} teams available")
        else:
            st.error("❌ **No FPL Data Available** - Please check connection")
            # Show what we do have
            st.write(f"Debug - Available session state keys: {list(st.session_state.keys())}")
        
        # Create comprehensive fixture analysis tabs - combining difficulty tabs with existing analysis
        fixture_tabs = st.tabs([
            "📊 Overall Difficulty", 
            "⚔️ Attack Difficulty", 
            "🛡️ Defense Difficulty",
            "📈 Team Strength Analysis", 
            "🏠 Home vs Away", 
            "📊 Form-Based Fixtures",
            "🎯 Transfer Recommendations"
        ])
        
        # New fixture difficulty tabs
        with fixture_tabs[0]:  # Overall Difficulty
            self._render_overall_difficulty(data)
            
        with fixture_tabs[1]:  # Attack Difficulty 
            self._render_attack_difficulty(data)
            
        with fixture_tabs[2]:  # Defense Difficulty
            self._render_defense_difficulty(data)
            
        # Existing analysis tabs
        with fixture_tabs[3]:  # Team Strength Analysis
            df = st.session_state.get('players_df', pd.DataFrame())
            if not df.empty:
                self._render_team_strength_analysis(df)
            else:
                st.warning("Player data not available for team strength analysis")
        
        with fixture_tabs[4]:  # Home vs Away
            df = st.session_state.get('players_df', pd.DataFrame())
            if not df.empty:
                self._render_home_away_analysis(df)
            else:
                st.warning("Player data not available for home vs away analysis")
        
        with fixture_tabs[5]:  # Form-Based Fixtures
            df = st.session_state.get('players_df', pd.DataFrame())
            if not df.empty:
                self._render_form_based_analysis(df)
            else:
                st.warning("Player data not available for form-based analysis")
        
        with fixture_tabs[6]:  # Transfer Recommendations
            df = st.session_state.get('players_df', pd.DataFrame())
            if not df.empty:
                self._render_fixture_transfer_recommendations(df)
            else:
                st.warning("Player data not available for transfer recommendations")
    
    def _get_data_safely(self):
        """Safely get FPL data and ensure players DataFrame is available"""
        try:
            # Try multiple ways to get the FPL data
            data = {}
            
            # Method 1: Try to import and use the enhanced FPL service directly
            try:
                from services.enhanced_fpl_data_service import EnhancedFPLDataService
                fpl_service = EnhancedFPLDataService()
                data = fpl_service.get_bootstrap_data()
                if data and 'teams' in data:
                    # Also get live fixtures data
                    fixtures = self._get_live_fixtures()
                    data['fixtures'] = fixtures
                    # Also prepare players DataFrame for existing tabs
                    self._prepare_players_dataframe(data)
                    return data
            except Exception as e:
                pass
            
            # Method 2: Try to access from session state
            if hasattr(st.session_state, 'fpl_service') and st.session_state.fpl_service:
                data = st.session_state.fpl_service.get_bootstrap_data()
                if data and 'teams' in data:
                    fixtures = self._get_live_fixtures()
                    data['fixtures'] = fixtures
                    self._prepare_players_dataframe(data)
                    return data
            
            # Method 3: Check for cached data in session state
            if 'fpl_data' in st.session_state:
                data = st.session_state.fpl_data
                if data and 'teams' in data:
                    fixtures = self._get_live_fixtures()
                    data['fixtures'] = fixtures
                    self._prepare_players_dataframe(data)
                    return data
                    
            # Method 4: Try to get from app instance if available
            if hasattr(st.session_state, 'app') and hasattr(st.session_state.app, 'fpl_service'):
                data = st.session_state.app.fpl_service.get_bootstrap_data()
                if data and 'teams' in data:
                    fixtures = self._get_live_fixtures()
                    data['fixtures'] = fixtures
                    self._prepare_players_dataframe(data)
                    return data
            
            return {}
        except Exception as e:
            st.error(f"Error accessing FPL data: {e}")
            return {}
    
    def _get_live_fixtures(self):
        """Get live fixtures data from FPL API with fallback support"""
        try:
            import requests
            response = requests.get('https://fantasy.premierleague.com/api/fixtures/', timeout=10)
            if response.status_code == 200:
                fixtures = response.json()
                if fixtures:  # Only return if we got actual data
                    return fixtures
        except Exception as e:
            pass  # Fall through to fallback
        
        # Fallback: Try to get fixtures from session state or create fallback data
        try:
            # Check if we have fallback data in session state
            if 'fpl_data' in st.session_state and 'fixtures' in st.session_state.fpl_data:
                return st.session_state.fpl_data.get('fixtures', [])
            
            # Create fallback fixtures using data utilities service
            from services.data_utilities_service import DataUtilitiesService
            data_service = DataUtilitiesService()
            fallback_data = data_service.create_fallback_data()
            return fallback_data.get('fixtures', [])
        except Exception as e:
            st.warning(f"Could not fetch fixtures (using fallback): {e}")
            return []
    
    def _get_team_fixtures_live(self, team_id, teams_dict, fixtures, max_fixtures=5):
        """Get live fixtures for a specific team with attack and defense specific difficulty"""
        upcoming_fixtures = [f for f in fixtures if not f.get('finished', True)]
        team_fixtures = []
        
        for fixture in upcoming_fixtures:
            if fixture.get('team_h') == team_id:
                # Home fixture
                opponent_id = fixture.get('team_a')
                opponent = teams_dict.get(opponent_id, {}).get('short_name', 'UNK')
                opponent_team = teams_dict.get(opponent_id, {})
                
                # Overall difficulty from FPL API
                overall_difficulty = fixture.get('team_h_difficulty', 3)
                
                # Attack difficulty: How hard to score (inverse of opponent defensive strength)
                # Use opponent team strength to estimate - stronger teams = harder to score against
                opponent_strength = opponent_team.get('strength', 3)
                attack_difficulty = min(5, max(1, opponent_strength))  # 1-5 scale
                
                # Defense difficulty: How hard to keep clean sheet (opponent attacking strength)
                # Same as overall difficulty since it represents opponent threat
                defense_difficulty = overall_difficulty
                
                team_fixtures.append({
                    'opponent': f"vs {opponent} (H)",
                    'difficulty': overall_difficulty,
                    'attack_difficulty': attack_difficulty,
                    'defense_difficulty': defense_difficulty,
                    'event': fixture.get('event', 0),
                    'home': True
                })
            elif fixture.get('team_a') == team_id:
                # Away fixture  
                opponent_id = fixture.get('team_h')
                opponent = teams_dict.get(opponent_id, {}).get('short_name', 'UNK')
                opponent_team = teams_dict.get(opponent_id, {})
                
                # Overall difficulty from FPL API
                overall_difficulty = fixture.get('team_a_difficulty', 3)
                
                # Attack difficulty: Adjust for away disadvantage
                opponent_strength = opponent_team.get('strength', 3)
                attack_difficulty = min(5, max(1, opponent_strength + 1))  # Harder away
                
                # Defense difficulty: Harder to defend away
                defense_difficulty = min(5, overall_difficulty + 1)  # +1 for away
                
                team_fixtures.append({
                    'opponent': f"@ {opponent} (A)",
                    'difficulty': overall_difficulty,
                    'attack_difficulty': attack_difficulty,
                    'defense_difficulty': defense_difficulty,
                    'event': fixture.get('event', 0),
                    'home': False
                })
        
        # Sort by event (gameweek) and take next N fixtures
        team_fixtures.sort(key=lambda x: x['event'])
        return team_fixtures[:max_fixtures]
    
    def _prepare_players_dataframe(self, data):
        """Prepare players DataFrame from FPL data for existing analysis tabs"""
        try:
            if 'elements' in data:
                import pandas as pd
                
                # Create DataFrame from players data
                players = data['elements']
                teams_dict = {team['id']: team for team in data.get('teams', [])}
                
                # Prepare players DataFrame with necessary columns
                players_data = []
                for player in players:
                    team_id = player.get('team')
                    team_info = teams_dict.get(team_id, {})
                    
                    players_data.append({
                        'web_name': player.get('web_name', ''),
                        'team_short_name': team_info.get('short_name', 'UNK'),
                        'team_name': team_info.get('name', 'Unknown'),
                        'total_points': player.get('total_points', 0),
                        'now_cost': player.get('now_cost', 0) / 10,  # Convert to millions
                        'form': float(player.get('form', 0)),
                        'points_per_game': float(player.get('points_per_game', 0)),
                        'selected_by_percent': float(player.get('selected_by_percent', 0)),
                        'element_type': player.get('element_type', 1),
                        'goals_scored': player.get('goals_scored', 0),
                        'assists': player.get('assists', 0),
                        'clean_sheets': player.get('clean_sheets', 0),
                        'minutes': player.get('minutes', 0)
                    })
                
                df = pd.DataFrame(players_data)
                st.session_state.players_df = df
                st.session_state.data_loaded = True
                
        except Exception as e:
            st.warning(f"Could not prepare players DataFrame: {e}")
            st.session_state.players_df = pd.DataFrame()
            st.session_state.data_loaded = False
    
    def _render_overall_difficulty(self, data):
        """Render overall fixture difficulty analysis using live FPL API data"""
        st.markdown("#### 📊 **Overall Fixture Difficulty**")
        st.info("💡 **Overall FDR** based on live FPL API fixture difficulty ratings")
        
        # Add CSS for better dark mode compatibility
        st.markdown("""
        <style>
        .fdr-table {
            border-collapse: collapse;
            width: 100%;
        }
        .fdr-easy {
            background-color: #22c55e !important;
            color: white !important;
            font-weight: bold !important;
        }
        .fdr-medium {
            background-color: #f59e0b !important;
            color: #1f2937 !important;
            font-weight: bold !important;
        }
        .fdr-hard {
            background-color: #ef4444 !important;
            color: white !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get teams and fixtures data
        if isinstance(data, dict) and 'teams' in data and 'fixtures' in data:
            teams = data.get('teams', [])
            fixtures = data.get('fixtures', [])
            
            if not fixtures:
                st.warning("⚠️ No live fixture data available")
                return
                
            # Create team lookup
            teams_dict = {team['id']: team for team in teams}
            
            # Get upcoming fixtures (not finished)
            upcoming_fixtures = [f for f in fixtures if not f.get('finished', True)]
            
            if not upcoming_fixtures:
                st.warning("⚠️ No upcoming fixtures found")
                return
                
            # Create fixture difficulty data for each team
            fixture_data = []
            
            for team in teams:
                team_id = team.get('id')
                team_name = team.get('name', 'Unknown')
                team_short = team.get('short_name', team_name[:3])
                
                # Get next 5 fixtures for this team
                team_fixtures = []
                for fixture in upcoming_fixtures:
                    if fixture.get('team_h') == team_id:
                        # Home fixture
                        opponent_id = fixture.get('team_a')
                        opponent = teams_dict.get(opponent_id, {}).get('short_name', 'UNK')
                        difficulty = fixture.get('team_h_difficulty', 3)
                        team_fixtures.append({
                            'opponent': f"vs {opponent} (H)",
                            'difficulty': difficulty,
                            'event': fixture.get('event', 0)
                        })
                    elif fixture.get('team_a') == team_id:
                        # Away fixture
                        opponent_id = fixture.get('team_h')
                        opponent = teams_dict.get(opponent_id, {}).get('short_name', 'UNK')
                        difficulty = fixture.get('team_a_difficulty', 3)
                        team_fixtures.append({
                            'opponent': f"@ {opponent} (A)",
                            'difficulty': difficulty,
                            'event': fixture.get('event', 0)
                        })
                
                # Sort by event (gameweek) and take next 5
                team_fixtures.sort(key=lambda x: x['event'])
                next_5 = team_fixtures[:5]
                
                if len(next_5) >= 3:  # Only show teams with at least 3 fixtures
                    avg_difficulty = sum(f['difficulty'] for f in next_5) / len(next_5)
                    
                    fixture_entry = {
                        'Team': team_name,
                        'Short': team_short,
                        'Next 5 FDR': round(avg_difficulty, 1)
                    }
                    
                    # Add individual fixtures
                    for i, fixture in enumerate(next_5):
                        gw_label = f"GW{fixture['event']}" if fixture['event'] > 0 else f"Next {i+1}"
                        fixture_entry[gw_label] = f"{fixture['opponent']} ({fixture['difficulty']})"
                    
                    fixture_data.append(fixture_entry)
            
            if not fixture_data:
                st.warning("⚠️ No fixture data available for analysis")
                return
                
            # Sort by average difficulty (best fixtures first)
            fixture_data.sort(key=lambda x: x['Next 5 FDR'])
            
            # Display fixture difficulty table
            fixture_df = pd.DataFrame(fixture_data)
            
            # Enhanced color coding for accessibility (works in light and dark mode)
            def highlight_difficulty(val):
                if isinstance(val, str) and '(' in val and ')' in val:
                    try:
                        difficulty_str = val.split('(')[1].split(')')[0]
                        # Skip if difficulty is not numeric (e.g., 'A' for Away)
                        if not difficulty_str.isdigit():
                            return ''
                        difficulty = int(difficulty_str)
                        if difficulty <= 2:
                            # Easy - Green with high contrast
                            return 'background-color: #22c55e; color: white; font-weight: bold; border: 1px solid #16a34a'
                        elif difficulty == 3:
                            # Medium - Amber/Orange with dark text for readability
                            return 'background-color: #f59e0b; color: #1f2937; font-weight: bold; border: 1px solid #d97706'
                        else:
                            # Hard - Red with white text for contrast
                            return 'background-color: #ef4444; color: white; font-weight: bold; border: 1px solid #dc2626'
                    except (ValueError, IndexError):
                        return ''
                return ''
            
            # Enhanced color coding for FDR average scores
            def highlight_fdr_average(val):
                if isinstance(val, (int, float)):
                    if val <= 2.0:
                        # Excellent - Dark Green
                        return 'background-color: #166534; color: white; font-weight: bold; border: 1px solid #15803d'
                    elif val <= 2.5:
                        # Good - Light Green
                        return 'background-color: #22c55e; color: white; font-weight: bold; border: 1px solid #16a34a'
                    elif val <= 3.0:
                        # Moderate - Yellow
                        return 'background-color: #eab308; color: #1f2937; font-weight: bold; border: 1px solid #ca8a04'
                    elif val <= 3.5:
                        # Challenging - Orange
                        return 'background-color: #f59e0b; color: #1f2937; font-weight: bold; border: 1px solid #d97706'
                    elif val <= 4.0:
                        # Difficult - Red
                        return 'background-color: #ef4444; color: white; font-weight: bold; border: 1px solid #dc2626'
                    else:
                        # Very Difficult - Dark Red
                        return 'background-color: #991b1b; color: white; font-weight: bold; border: 1px solid #b91c1c'
                return ''
            
            # Get fixture columns (exclude Team, Short, Next 5 FDR)
            fixture_cols = [col for col in fixture_df.columns if col not in ['Team', 'Short', 'Next 5 FDR']]
            
            # Apply styling to both fixture columns and FDR average
            styled_df = (fixture_df.style
                        .applymap(highlight_difficulty, subset=fixture_cols)
                        .applymap(highlight_fdr_average, subset=['Next 5 FDR']))
            
            st.dataframe(styled_df, width='stretch')
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                easy_teams = len([team for team in fixture_data if team['Next 5 FDR'] <= 2.5])
                st.metric("🟢 Easy Run", easy_teams)
            with col2:
                medium_teams = len([team for team in fixture_data if 2.5 < team['Next 5 FDR'] <= 3.5])
                st.metric("🟡 Medium Run", medium_teams)
            with col3:
                hard_teams = len([team for team in fixture_data if team['Next 5 FDR'] > 3.5])
                st.metric("🔴 Hard Run", hard_teams)
            
            # Enhanced FDR Legend with accessibility information
            st.markdown("#### 🎯 **Fixture Difficulty Legend**")
            
            # Individual Fixture Color Legend
            st.markdown("##### 🔍 **Individual Fixtures:**")
            st.markdown("""
            <div style="margin: 1rem 0;">
                <div style="display: flex; flex-wrap: wrap; gap: 0.8rem; margin: 1rem 0;">
                    <div style="background-color: #22c55e; color: white; padding: 0.4rem 0.8rem; border-radius: 0.4rem; font-weight: bold; font-size: 0.9rem;">
                        🟢 Easy (1-2): Excellent fixtures
                    </div>
                    <div style="background-color: #f59e0b; color: #1f2937; padding: 0.4rem 0.8rem; border-radius: 0.4rem; font-weight: bold; font-size: 0.9rem;">
                        � Medium (3): Average fixtures
                    </div>
                    <div style="background-color: #ef4444; color: white; padding: 0.4rem 0.8rem; border-radius: 0.4rem; font-weight: bold; font-size: 0.9rem;">
                        🔴 Hard (4-5): Difficult fixtures
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # FDR Average Color Legend
            st.markdown("##### 📊 **Next 5 FDR Average:**")
            st.markdown("""
            <div style="margin: 1rem 0;">
                <div style="display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 1rem 0;">
                    <div style="background-color: #166534; color: white; padding: 0.3rem 0.6rem; border-radius: 0.3rem; font-weight: bold; font-size: 0.85rem;">
                        ≤2.0: Excellent
                    </div>
                    <div style="background-color: #22c55e; color: white; padding: 0.3rem 0.6rem; border-radius: 0.3rem; font-weight: bold; font-size: 0.85rem;">
                        ≤2.5: Good
                    </div>
                    <div style="background-color: #eab308; color: #1f2937; padding: 0.3rem 0.6rem; border-radius: 0.3rem; font-weight: bold; font-size: 0.85rem;">
                        ≤3.0: Moderate
                    </div>
                    <div style="background-color: #f59e0b; color: #1f2937; padding: 0.3rem 0.6rem; border-radius: 0.3rem; font-weight: bold; font-size: 0.85rem;">
                        ≤3.5: Challenging
                    </div>
                    <div style="background-color: #ef4444; color: white; padding: 0.3rem 0.6rem; border-radius: 0.3rem; font-weight: bold; font-size: 0.85rem;">
                        ≤4.0: Difficult
                    </div>
                    <div style="background-color: #991b1b; color: white; padding: 0.3rem 0.6rem; border-radius: 0.3rem; font-weight: bold; font-size: 0.85rem;">
                        >4.0: Very Difficult
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Strategy tips based on color coding
            st.markdown("##### 🎯 **Strategy Tips:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("🟢 **Target for Transfers**: Teams with dark green FDR (≤2.0) are prime candidates for bringing in players")
            with col2:
                st.warning("🟡 **Rotation Candidates**: Teams with orange/yellow FDR (3.0-3.5) may need tactical rotation")
            with col3:
                st.error("🔴 **Avoid or Sell**: Teams with red FDR (>4.0) should be avoided for new transfers")
            
            # Accessibility information
            col1, col2 = st.columns(2)
            with col1:
                st.info("💡 **Dark Mode Compatible**: Colors are optimized for both light and dark themes")
            with col2:
                st.info("♿ **Accessible Design**: High contrast colors with clear text for better readability")
                
        else:
            st.warning("⚠️ Live fixture data not available - please check API connection")
            
    def _render_attack_difficulty(self, data):
        """Render attacking fixture difficulty analysis using live FPL API data"""
        st.markdown("#### ⚔️ **Attack Difficulty Analysis**")
        st.info("💡 **Attack FDR** based on live FPL API difficulty ratings - focuses on scoring potential")
        
        # Add CSS for attack difficulty styling
        st.markdown("""
        <style>
        .attack-easy {
            background-color: #06b6d4 !important;
            color: white !important;
            font-weight: bold !important;
        }
        .attack-medium {
            background-color: #f59e0b !important;
            color: #1f2937 !important;
            font-weight: bold !important;
        }
        .attack-hard {
            background-color: #ef4444 !important;
            color: white !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get teams and fixtures data
        if isinstance(data, dict) and 'teams' in data and 'fixtures' in data:
            teams = data.get('teams', [])
            fixtures = data.get('fixtures', [])
            
            if not fixtures:
                st.warning("⚠️ No live fixture data available for attack analysis")
                return
            
            # Create team lookup
            teams_dict = {team['id']: team for team in teams}
            
            # Create attack-focused difficulty data
            attack_data = []
            
            for team in teams:
                team_id = team.get('id')
                team_name = team.get('name', 'Unknown')
                team_short = team.get('short_name', team_name[:3])
                
                # Get live fixtures for this team
                team_fixtures = self._get_team_fixtures_live(team_id, teams_dict, fixtures, 5)
                
                if len(team_fixtures) >= 3:  # Only show teams with at least 3 fixtures
                    avg_attack_difficulty = sum(f['attack_difficulty'] for f in team_fixtures) / len(team_fixtures)
                    
                    attack_entry = {
                        'Team': team_name,
                        'Attack FDR': round(avg_attack_difficulty, 1)
                    }
                    
                    # Add individual fixtures with attack context
                    for i, fixture in enumerate(team_fixtures):
                        gw_label = f"GW{fixture['event']}" if fixture['event'] > 0 else f"Next {i+1}"
                        attack_entry[gw_label] = f"{fixture['opponent']} ({fixture['attack_difficulty']})"                    # Add attack recommendation
                    if avg_attack_difficulty <= 2.5:
                        recommendation = "🎯 Great attacking fixtures"
                    elif avg_attack_difficulty <= 3.5:
                        recommendation = "⚖️ Average attacking potential"
                    else:
                        recommendation = "⚠️ Difficult attacking fixtures"
                    
                    attack_entry['Recommendation'] = recommendation
                    attack_data.append(attack_entry)
            
            attack_df = pd.DataFrame(attack_data)
            
            if not attack_df.empty:
                # Enhanced color coding for attack difficulty (accessible for dark mode)
                def highlight_attack_difficulty(val):
                    if isinstance(val, str) and '(' in val and ')' in val:
                        try:
                            difficulty_str = val.split('(')[1].split(')')[0]
                            # Skip if difficulty is not numeric (e.g., 'A' for Away)
                            if not difficulty_str.isdigit():
                                return ''
                            difficulty = int(difficulty_str)
                            if difficulty <= 2:
                                # Easy attack - Blue/Cyan with white text
                                return 'background-color: #06b6d4; color: white; font-weight: bold; border: 1px solid #0891b2'
                            elif difficulty == 3:
                                # Medium attack - Orange with dark text
                                return 'background-color: #f59e0b; color: #1f2937; font-weight: bold; border: 1px solid #d97706'
                            else:
                                # Hard attack - Red with white text
                                return 'background-color: #ef4444; color: white; font-weight: bold; border: 1px solid #dc2626'
                        except (ValueError, IndexError):
                            return ''
                    return ''
                
                # Enhanced color coding for Attack FDR average scores
                def highlight_attack_fdr_average(val):
                    if isinstance(val, (int, float)):
                        if val <= 2.0:
                            # Excellent attack - Dark Cyan
                            return 'background-color: #155e75; color: white; font-weight: bold; border: 1px solid #0e7490'
                        elif val <= 2.5:
                            # Good attack - Light Cyan
                            return 'background-color: #06b6d4; color: white; font-weight: bold; border: 1px solid #0891b2'
                        elif val <= 3.0:
                            # Moderate attack - Yellow
                            return 'background-color: #eab308; color: #1f2937; font-weight: bold; border: 1px solid #ca8a04'
                        elif val <= 3.5:
                            # Challenging attack - Orange
                            return 'background-color: #f59e0b; color: #1f2937; font-weight: bold; border: 1px solid #d97706'
                        elif val <= 4.0:
                            # Difficult attack - Red
                            return 'background-color: #ef4444; color: white; font-weight: bold; border: 1px solid #dc2626'
                        else:
                            # Very Difficult attack - Dark Red
                            return 'background-color: #991b1b; color: white; font-weight: bold; border: 1px solid #b91c1c'
                    return ''
                
                # Get fixture columns dynamically (excluding Team, Attack FDR, and Recommendation)
                fixture_cols = [col for col in attack_df.columns if col not in ['Team', 'Attack FDR', 'Recommendation']]
                
                # Apply styling to both fixture columns and Attack FDR average
                styled_attack_df = (attack_df.style
                                  .applymap(highlight_attack_difficulty, subset=fixture_cols)
                                  .applymap(highlight_attack_fdr_average, subset=['Attack FDR']))
                
                st.dataframe(styled_attack_df, width='stretch')
            
            # Attack recommendations
            st.markdown("#### 🎯 **Attack Recommendations**")
            best_attack = min(attack_data, key=lambda x: x['Attack FDR'])
            worst_attack = max(attack_data, key=lambda x: x['Attack FDR'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🎯 **Best Attack Fixtures**: {best_attack['Team']} (FDR: {best_attack['Attack FDR']})")
                st.write("✅ Consider attacking players from this team")
                
            with col2:
                st.error(f"🚫 **Worst Attack Fixtures**: {worst_attack['Team']} (FDR: {worst_attack['Attack FDR']})")
                st.write("⚠️ Avoid attacking players from this team")
                
        else:
            st.warning("⚠️ Live attack difficulty data not available")
    
    def _render_defense_difficulty(self, data):
        """Render defensive fixture difficulty analysis"""
        st.markdown("#### 🛡️ **Defense Difficulty Analysis**") 
        st.info("💡 **Defense FDR** focuses on clean sheet potential and defensive returns")
        
        # Add CSS for defense difficulty styling
        st.markdown("""
        <style>
        .defense-easy {
            background-color: #10b981 !important;
            color: white !important;
            font-weight: bold !important;
        }
        .defense-medium {
            background-color: #f59e0b !important;
            color: #1f2937 !important;
            font-weight: bold !important;
        }
        .defense-hard {
            background-color: #ef4444 !important;
            color: white !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get live fixtures data
        if isinstance(data, dict) and 'teams' in data:
            teams = data.get('teams', [])
            fixtures = self._get_live_fixtures()
            
            if fixtures and len(fixtures) > 0:
                # Create teams dictionary for quick lookup - store full team objects
                teams_dict = {team.get('id'): team for team in teams}
                
                defense_data = []
                
                for team in teams:
                    team_id = team.get('id')
                    team_name = team.get('name', 'Unknown')
                    
                    # Get live team fixtures
                    team_fixtures = self._get_team_fixtures_live(team_id, teams_dict, fixtures, 5)
                    
                    if len(team_fixtures) >= 3:  # Only show teams with at least 3 fixtures
                        avg_defense_difficulty = sum(f['defense_difficulty'] for f in team_fixtures) / len(team_fixtures)
                        
                        defense_entry = {
                            'Team': team_name,
                            'Defense FDR': round(avg_defense_difficulty, 1)
                        }
                        
                        # Add individual fixtures with defense context
                        for i, fixture in enumerate(team_fixtures):
                            gw_label = f"GW{fixture['event']}" if fixture['event'] > 0 else f"Next {i+1}"
                            defense_entry[gw_label] = f"{fixture['opponent']} ({fixture['defense_difficulty']})"
                        
                        # Add clean sheet percentage and defense recommendation
                        clean_sheet_pct = max(20, 80 - (avg_defense_difficulty * 15))
                        defense_entry['Clean Sheet %'] = f"{clean_sheet_pct:.0f}%"
                        
                        if avg_defense_difficulty <= 2.5:
                            recommendation = "🛡️ Excellent clean sheet potential"
                        elif avg_defense_difficulty <= 3.5:
                            recommendation = "⚖️ Average defensive fixtures"
                        else:
                            recommendation = "⚠️ Difficult defensive fixtures"
                        
                        defense_entry['Recommendation'] = recommendation
                        defense_data.append(defense_entry)
            
                defense_df = pd.DataFrame(defense_data)
                
                if not defense_df.empty:
                    # Enhanced color coding for defense difficulty (accessible for dark mode)
                    def highlight_defense_difficulty(val):
                        if isinstance(val, str) and '(' in val and ')' in val:
                            try:
                                difficulty_str = val.split('(')[1].split(')')[0]
                                # Skip if difficulty is not numeric (e.g., 'A' for Away)
                                if not difficulty_str.isdigit():
                                    return ''
                                difficulty = int(difficulty_str)
                                if difficulty <= 2:
                                    # Easy defense - Green with white text (good clean sheet potential)
                                    return 'background-color: #10b981; color: white; font-weight: bold; border: 1px solid #059669'
                                elif difficulty == 3:
                                    # Medium defense - Orange with dark text
                                    return 'background-color: #f59e0b; color: #1f2937; font-weight: bold; border: 1px solid #d97706'
                                else:
                                    # Hard defense - Red with white text (poor clean sheet potential)
                                    return 'background-color: #ef4444; color: white; font-weight: bold; border: 1px solid #dc2626'
                            except (ValueError, IndexError):
                                return ''
                        return ''
                    
                    # Enhanced color coding for Defense FDR average scores  
                    def highlight_defense_fdr_average(val):
                        if isinstance(val, (int, float)):
                            if val <= 2.0:
                                # Excellent defense - Dark Green
                                return 'background-color: #166534; color: white; font-weight: bold; border: 1px solid #15803d'
                            elif val <= 2.5:
                                # Good defense - Light Green  
                                return 'background-color: #10b981; color: white; font-weight: bold; border: 1px solid #059669'
                            elif val <= 3.0:
                                # Moderate defense - Yellow
                                return 'background-color: #eab308; color: #1f2937; font-weight: bold; border: 1px solid #ca8a04'
                            elif val <= 3.5:
                                # Challenging defense - Orange
                                return 'background-color: #f59e0b; color: #1f2937; font-weight: bold; border: 1px solid #d97706'
                            elif val <= 4.0:
                                # Difficult defense - Red
                                return 'background-color: #ef4444; color: white; font-weight: bold; border: 1px solid #dc2626'
                            else:
                                # Very Difficult defense - Dark Red
                                return 'background-color: #991b1b; color: white; font-weight: bold; border: 1px solid #b91c1c'
                        return ''
                    
                    # Get fixture columns dynamically (excluding Team, Defense FDR, Clean Sheet %, and Recommendation)
                    fixture_cols = [col for col in defense_df.columns if col not in ['Team', 'Defense FDR', 'Clean Sheet %', 'Recommendation']]
                    
                    # Apply styling to both fixture columns and Defense FDR average
                    styled_defense_df = (defense_df.style
                                       .applymap(highlight_defense_difficulty, subset=fixture_cols)
                                       .applymap(highlight_defense_fdr_average, subset=['Defense FDR']))
                    
                    st.dataframe(styled_defense_df, width='stretch')
            
                # Defense recommendations
                st.markdown("#### 🛡️ **Defense Recommendations**")
                best_defense = min(defense_data, key=lambda x: x['Defense FDR'])
                worst_defense = max(defense_data, key=lambda x: x['Defense FDR'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"🛡️ **Best Defense Fixtures**: {best_defense['Team']} (FDR: {best_defense['Defense FDR']})")
                    st.write("✅ Strong clean sheet potential - consider defensive assets")
                    
                with col2:
                    st.error(f"🚨 **Worst Defense Fixtures**: {worst_defense['Team']} (FDR: {worst_defense['Defense FDR']})")
                    st.write("⚠️ Avoid defensive assets - clean sheets unlikely")
            else:
                st.warning("⚠️ No live defense fixture data available")
        else:
            st.warning("⚠️ Live defense difficulty data not available")
    
    def _render_simplified_fixture_analysis(self, df):
        """Render simplified fixture analysis using available data"""
        
        # Analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Team Strength Analysis", 
            "🏠 Home vs Away", 
            "📈 Form-Based Fixtures",
            "🎯 Transfer Recommendations"
        ])
        
        with tab1:
            self._render_team_strength_analysis(df)
        
        with tab2:
            self._render_home_away_analysis(df)
        
        with tab3:
            self._render_form_based_analysis(df)
        
        with tab4:
            self._render_fixture_transfer_recommendations(df)
    
    def _render_team_strength_analysis(self, df):
        """Analyze team strength for fixture difficulty estimation"""
        st.subheader("📊 Team Strength Analysis")
        st.info("💡 Stronger teams = harder fixtures when playing against them")
        
        if df.empty:
            st.warning("No data available for team strength analysis")
            return

        # Ensure required columns exist
        required_columns = {
            'team_short_name': df['team_name'].apply(lambda x: str(x)[:3].upper()) if 'team_name' in df.columns else df.index,
            'total_points': df.get('total_points', 0),
            'goals_scored': df.get('goals_scored', 0),
            'clean_sheets': df.get('clean_sheets', 0),
            'form': df.get('form', 0)
        }
        
        # Add any missing columns
        for col, default_value in required_columns.items():
            if col not in df.columns:
                df[col] = default_value
        
        # Calculate team strength metrics
        team_metrics = df.groupby('team_short_name').agg({
            'total_points': 'sum',
            'goals_scored': 'sum',
            'clean_sheets': 'sum',
            'form': 'mean'
        }).reset_index()
        
        # Calculate team strength score
        if 'total_points' in team_metrics.columns:
            team_metrics['strength_score'] = (
                team_metrics['total_points'] / team_metrics['total_points'].max() * 100
            ).round(1)
            
            team_metrics = team_metrics.sort_values('strength_score', ascending=False)
            
            # Display team strength
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔥 Strongest Teams (Hardest to face)")
                strong_teams = team_metrics.head(10)
                for _, team in strong_teams.iterrows():
                    st.write(f"🔴 **{team['team_short_name']}**: {team['strength_score']:.1f} strength")
            
            with col2:
                st.subheader("📉 Weaker Teams (Easier to face)")
                weak_teams = team_metrics.tail(10)
                for _, team in weak_teams.iterrows():
                    st.write(f"🟢 **{team['team_short_name']}**: {team['strength_score']:.1f} strength")
            
            # Team strength visualization
            fig = px.bar(
                team_metrics, 
                x='team_short_name', 
                y='strength_score',
                title="Team Strength Rankings",
                color='strength_score',
                color_continuous_scale='RdYlGn_r'
            )
            
            fig.update_layout(
                xaxis_title="Team",
                yaxis_title="Strength Score",
                height=500,
                xaxis={'categoryorder': 'total descending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("Insufficient data for team strength calculation")
    
    def _render_home_away_analysis(self, df):
        """Analyze home vs away performance"""
        st.subheader("🏠 Home vs Away Performance")
        st.info("📍 Teams typically perform better at home - use this for fixture planning")
        
        # Since we don't have fixture data, we'll use team strength as proxy
        if 'team_short_name' in df.columns and 'total_points' in df.columns:
            team_stats = df.groupby('team_short_name').agg({
                'total_points': 'sum',
                'form': 'mean' if 'form' in df.columns else 'count'
            }).reset_index()
            
            # Simulate home advantage (typically 0.3-0.5 points boost)
            team_stats['home_strength'] = team_stats['total_points'] * 1.15
            team_stats['away_strength'] = team_stats['total_points'] * 0.9
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏠 Best Home Teams")
                st.write("*Teams likely to perform well at home*")
                home_teams = team_stats.nlargest(8, 'home_strength')
                for _, team in home_teams.iterrows():
                    st.write(f"🟢 **{team['team_short_name']}**: Strong at home")
            
            with col2:
                st.subheader("✈️ Best Away Teams") 
                st.write("*Teams that travel well*")
                away_teams = team_stats.nlargest(8, 'away_strength')
                for _, team in away_teams.iterrows():
                    st.write(f"🟡 **{team['team_short_name']}**: Good away form")
            
            # Home vs Away comparison chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Home Strength',
                x=team_stats['team_short_name'],
                y=team_stats['home_strength'],
                marker_color='lightgreen'
            ))
            
            fig.add_trace(go.Bar(
                name='Away Strength',
                x=team_stats['team_short_name'], 
                y=team_stats['away_strength'],
                marker_color='lightcoral'
            ))
            
            fig.update_layout(
                title='Home vs Away Performance Comparison',
                xaxis_title='Team',
                yaxis_title='Estimated Strength',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("Home/Away analysis requires team and points data")
    
    def _render_form_based_analysis(self, df):
        """Analyze current form for fixture difficulty"""
        st.subheader("📈 Form-Based Fixture Analysis")
        st.info("🔥 Teams in good form are harder to face - adjust your transfers accordingly")
        
        if 'form' not in df.columns:
            st.warning("Form data not available - using total points as proxy")
            if 'total_points' in df.columns:
                # Use total points as form proxy
                df = df.copy()
                df['form'] = df['total_points'] / 20  # Approximate form from total points
            else:
                st.error("No suitable data for form analysis")
                return
        
        # Team form analysis
        team_form = df.groupby('team_short_name').agg({
            'form': 'mean',
            'total_points': 'sum' if 'total_points' in df.columns else 'count'
        }).reset_index()
        
        team_form = team_form.sort_values('form', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Teams in Hot Form")
            st.write("*Avoid facing these teams*")
            hot_teams = team_form.head(8)
            for _, team in hot_teams.iterrows():
                st.write(f"🔴 **{team['team_short_name']}**: {team['form']:.1f} form")
        
        with col2:
            st.subheader("❄️ Teams in Poor Form")
            st.write("*Target players facing these teams*")
            cold_teams = team_form.tail(8)
            for _, team in cold_teams.iterrows():
                st.write(f"🟢 **{team['team_short_name']}**: {team['form']:.1f} form")
        
        # Form distribution
        fig = px.histogram(
            team_form, 
            x='form',
            nbins=10,
            title="Team Form Distribution",
            labels={'form': 'Average Form', 'count': 'Number of Teams'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Form vs Points correlation
        if 'total_points' in team_form.columns:
            fig_scatter = px.scatter(
                team_form,
                x='form',
                y='total_points',
                text='team_short_name',
                title="Form vs Total Points Correlation",
                labels={'form': 'Average Form', 'total_points': 'Total Team Points'}
            )
            
            fig_scatter.update_traces(textposition="top center")
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    def _render_fixture_transfer_recommendations(self, df):
        """Provide transfer recommendations based on fixture analysis"""
        st.subheader("🎯 Fixture-Based Transfer Recommendations")
        st.info("💡 Strategic recommendations based on team strength and form analysis")
        
        if df.empty:
            st.warning("No data available for recommendations")
            return
        
        # Calculate recommendation scores
        team_analysis = df.groupby('team_short_name').agg({
            'total_points': 'sum',
            'form': 'mean' if 'form' in df.columns else 'count',
            'selected_by_percent': 'mean' if 'selected_by_percent' in df.columns else 'count'
        }).reset_index()
        
        if 'total_points' in team_analysis.columns:
            # Calculate fixture attractiveness (lower = better fixtures ahead)
            team_analysis['fixture_attractiveness'] = (
                100 - (team_analysis['total_points'] / team_analysis['total_points'].max() * 100)
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Teams to Target")
                st.write("*Players from these teams likely have easier fixtures*")
                
                # Teams with poor opponents (high fixture attractiveness)
                target_teams = team_analysis.nlargest(8, 'fixture_attractiveness')
                
                for _, team in target_teams.iterrows():
                    # Get best players from this team
                    team_players = df[df['team_short_name'] == team['team_short_name']]
                    if not team_players.empty:
                        best_player = team_players.nlargest(1, 'total_points').iloc[0]
                        st.write(f"🟢 **{team['team_short_name']}**: Consider {best_player['web_name']}")
            
            with col2:
                st.subheader("⚠️ Teams to Avoid")
                st.write("*Players from these teams likely face difficult fixtures*")
                
                # Teams with strong opponents (low fixture attractiveness) 
                avoid_teams = team_analysis.nsmallest(8, 'fixture_attractiveness')
                
                for _, team in avoid_teams.iterrows():
                    # Get popular players from this team
                    team_players = df[df['team_short_name'] == team['team_short_name']]
                    if not team_players.empty:
                        if 'selected_by_percent' in team_players.columns:
                            popular_player = team_players.nlargest(1, 'selected_by_percent').iloc[0]
                        else:
                            popular_player = team_players.nlargest(1, 'total_points').iloc[0]
                        st.write(f"🔴 **{team['team_short_name']}**: Consider selling {popular_player['web_name']}")
        
        # Transfer timing recommendations
        st.subheader("⏰ Transfer Timing Strategy")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **🚀 Immediate Targets**
            - Players from weak teams
            - Good form + easy fixtures
            - Price rises expected
            """)
        
        with col2:
            st.warning("""
            **⏳ Monitor Closely**
            - Form vs fixture conflict
            - Injury concerns
            - Rotation risks
            """)
        
        with col3:
            st.error("""
            **❌ Avoid This Week**
            - Strong opposition ahead
            - Poor recent form
            - High risk of benching
            """)
        
        # Simple fixture difficulty matrix
        st.subheader("📊 Quick Fixture Difficulty Guide")
        
        difficulty_guide = pd.DataFrame({
            'Opponent Strength': ['Very Strong', 'Strong', 'Average', 'Weak', 'Very Weak'],
            'Home Fixture': ['🔴 Very Hard', '🟠 Hard', '🟡 Average', '🟢 Easy', '🟢 Very Easy'],
            'Away Fixture': ['🔴 Extremely Hard', '🔴 Very Hard', '🟠 Hard', '🟡 Average', '🟢 Easy'],
            'Recommendation': ['Avoid', 'Consider Out', 'Monitor', 'Consider In', 'Strong Target']
        })
        
        st.dataframe(difficulty_guide, use_container_width=True, hide_index=True)

    def _generate_fixtures(self, team_short, team_strength, focus='overall'):
        """Generate realistic fixtures with difficulty ratings"""
        import random
        
        # Common Premier League team abbreviations
        all_teams = ['ARS', 'AVL', 'BOU', 'BRE', 'BHA', 'CHE', 'CRY', 'EVE', 
                    'FUL', 'IPS', 'LEI', 'LIV', 'MCI', 'MUN', 'NEW', 'NFO', 
                    'SOU', 'TOT', 'WHU', 'WOL']
        
        # Remove current team and get 5 opponents
        available_teams = [t for t in all_teams if t != team_short]
        opponents = random.sample(available_teams, 5)
        
        # Team strength ratings (simulate based on common knowledge)
        team_strength_map = {
            'MCI': 5, 'LIV': 5, 'ARS': 4, 'CHE': 4, 'TOT': 4, 'MUN': 4,
            'NEW': 3, 'AVL': 3, 'WHU': 3, 'BHA': 3, 'FUL': 3, 'CRY': 3,
            'WOL': 2, 'EVE': 2, 'BRE': 2, 'BOU': 2, 'SOU': 2, 'LEI': 2,
            'IPS': 1, 'NFO': 1
        }
        
        fixtures = []
        for opponent in opponents:
            opponent_strength = team_strength_map.get(opponent, 3)
            home_advantage = random.choice([True, False])
            
            if focus == 'attack':
                # Attack difficulty: how hard is it to score against opponent
                base_difficulty = 6 - opponent_strength  # Inverse for attack
                if home_advantage:
                    base_difficulty = max(1, base_difficulty - 1)  # Easier at home
                attack_difficulty = max(1, min(5, base_difficulty))
                
                fixtures.append({
                    'opponent': opponent,
                    'difficulty': attack_difficulty,
                    'attack_difficulty': attack_difficulty,
                    'defense_difficulty': attack_difficulty,  # Same for simplicity
                    'home': home_advantage
                })
                
            elif focus == 'defense':
                # Defense difficulty: how hard is it to keep clean sheet against opponent
                base_difficulty = opponent_strength  # Direct for defense
                if home_advantage:
                    base_difficulty = max(1, base_difficulty - 1)  # Easier at home
                defense_difficulty = max(1, min(5, base_difficulty))
                
                fixtures.append({
                    'opponent': opponent,
                    'difficulty': defense_difficulty,
                    'attack_difficulty': defense_difficulty,  # Same for simplicity
                    'defense_difficulty': defense_difficulty,
                    'home': home_advantage
                })
            else:
                # Overall difficulty: balanced approach
                base_difficulty = opponent_strength
                if home_advantage:
                    base_difficulty = max(1, base_difficulty - 1)
                overall_difficulty = max(1, min(5, base_difficulty))
                
                fixtures.append({
                    'opponent': opponent,
                    'difficulty': overall_difficulty,
                    'attack_difficulty': overall_difficulty,
                    'defense_difficulty': overall_difficulty,
                    'home': home_advantage
                })
        
        return fixtures
    
    def _get_attack_recommendation(self, avg_difficulty, team_short):
        """Get attack recommendation based on difficulty"""
        if avg_difficulty <= 2.0:
            return f"🎯 Strong BUY - {team_short} attackers"
        elif avg_difficulty <= 3.0:
            return f"👍 Consider - {team_short} assets"
        elif avg_difficulty <= 4.0:
            return f"⚠️ Monitor - {team_short} difficult fixtures"
        else:
            return f"🚫 AVOID - {team_short} very tough fixtures"
    
    def _get_defense_recommendation(self, avg_difficulty, team_short):
        """Get defense recommendation based on difficulty"""
        if avg_difficulty <= 2.0:
            return f"🛡️ Excellent - {team_short} clean sheets likely"
        elif avg_difficulty <= 3.0:
            return f"✅ Good - {team_short} solid defensive choice"
        elif avg_difficulty <= 4.0:
            return f"⚠️ Risky - {team_short} clean sheets unlikely"
        else:
            return f"🚫 Avoid - {team_short} facing strong attacks"

