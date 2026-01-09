"""
Learning Resources Component
Provides FPL glossary, strategy guides, and tutorials for users
"""

import streamlit as st
from typing import Dict, List, Tuple
from utils.error_handling import handle_errors


class FPLGlossary:
    """FPL terminology and metrics glossary"""
    
    GLOSSARY: Dict[str, Dict[str, str]] = {
        # Core Metrics
        "xG": {
            "term": "Expected Goals (xG)",
            "definition": "A statistical measure of the quality of a scoring chance",
            "explanation": "xG assigns a probability (0-1) to each shot based on factors like distance, angle, assist type, and whether it's a header. A shot with 0.5 xG has a 50% chance of being scored.",
            "usage": "Use xG to identify players who are getting good chances but may be unlucky. High xG with low goals suggests future returns.",
            "example": "If Salah has 5.2 xG but only 3 goals, he's likely to score more in upcoming games."
        },
        "xA": {
            "term": "Expected Assists (xA)",
            "definition": "The likelihood that a pass will become an assist",
            "explanation": "Similar to xG, xA measures the quality of chances created. It considers the quality of the shot the pass leads to.",
            "usage": "Identify creative players who are unlucky with teammates finishing. High xA players are valuable for assists.",
            "example": "De Bruyne with 4.8 xA but only 2 assists may see more returns soon."
        },
        "ICT Index": {
            "term": "ICT Index",
            "definition": "Influence, Creativity, Threat combined metric (0-100+)",
            "explanation": "Official FPL metric combining three elements:\n- Influence: Impact on team's result\n- Creativity: Chance creation\n- Threat: Goal threat",
            "usage": "Higher ICT (>10) indicates high involvement. Use to find undervalued differentials.",
            "example": "A midfielder with ICT of 15+ is heavily involved and likely to return points."
        },
        "BPS": {
            "term": "Bonus Points System",
            "definition": "Formula determining which players get 1-3 bonus points",
            "explanation": "Points awarded for actions: goals, assists, clean sheets, saves, key passes, etc. Top 3 players in BPS get 3, 2, 1 bonus points respectively.",
            "usage": "Defenders and midfielders often get bonus through clean sheets + attacking returns.",
            "example": "A defender with a goal and clean sheet often scores highest BPS."
        },
        "Form": {
            "term": "Form",
            "definition": "Average points per game over last 5 gameweeks",
            "explanation": "Rolling average that shows recent performance. Form > 6.0 is excellent, < 3.0 is poor.",
            "usage": "Target players in good form for captaincy and transfers. Avoid poor form.",
            "example": "Haaland with form of 9.2 is averaging 9.2 points per game recently."
        },
        "Value Score": {
            "term": "Value Score (Points Per Million)",
            "definition": "Total points divided by current price",
            "explanation": "Efficiency metric showing points returned per £1m spent. Higher is better value.",
            "usage": "Find budget players with high value scores to free up funds elsewhere.",
            "example": "A £5.0m defender with 80 points has value score of 16.0 (80/5)."
        },
        
        # Advanced Metrics
        "Selected By %": {
            "term": "Ownership Percentage",
            "definition": "Percentage of teams that own this player",
            "explanation": "Shows template popularity. High ownership (>30%) = template. Low (<5%) = differential.",
            "usage": "In mini-leagues, differentials can help you gain ground. In overall rank, template players are safer.",
            "example": "Salah at 45% ownership is a template player you likely need."
        },
        "TSB%": {
            "term": "Top 10K Selected By %",
            "definition": "Ownership among the top 10,000 managers",
            "explanation": "Shows what elite managers are doing. Often higher than overall ownership for premiums.",
            "usage": "Follow TSB% for informed decision-making. Elite managers see value early.",
            "example": "If TSB% is 65% but overall is 35%, top managers rate the player highly."
        },
        "Net Transfers": {
            "term": "Net Transfers",
            "definition": "Transfers in minus transfers out (24 hours)",
            "explanation": "Indicates price change probability. >100K net in = likely rise. <-100K = likely fall.",
            "usage": "Act early on players with high positive net transfers to avoid price rises.",
            "example": "Player with +150K net transfers will likely rise £0.1m tonight."
        },
        "Minutes": {
            "term": "Minutes Played",
            "definition": "Total minutes on the pitch this season",
            "explanation": "Shows playing time reliability. 90 mins/game = nailed. <60 = rotation risk.",
            "usage": "Prioritize players with consistent 90-minute performances.",
            "example": "A player with 1350 minutes across 15 games averages 90 mins (nailed starter)."
        },
        
        # Strategy Terms
        "Differential": {
            "term": "Differential Pick",
            "definition": "Low-owned player (<10%) with high potential",
            "explanation": "Used to gain rank in mini-leagues. Higher risk but higher reward if successful.",
            "usage": "Use differentials strategically, not randomly. Base on fixtures and form.",
            "example": "A £7.5m midfielder owned by 3% with 4 easy fixtures ahead."
        },
        "Template Team": {
            "term": "Template Team",
            "definition": "Squad structure used by majority of top managers",
            "explanation": "Usually 6-8 players owned by >40% of top 10K. Playing template is safer.",
            "usage": "Start season with template, add differentials mid-season for rank pushes.",
            "example": "Salah, Haaland, premium defenders from top teams are usually template."
        },
        "Bench Boost": {
            "term": "Bench Boost Chip",
            "definition": "One-use chip: points from all 15 players count",
            "explanation": "Best used in double gameweeks when all players have 2 games. Can yield 100+ points.",
            "usage": "Plan ahead: build full playing bench before DGW, then activate chip.",
            "example": "DGW with 15 players having 2 games = 30 potential matches for points."
        },
        "Triple Captain": {
            "term": "Triple Captain Chip",
            "definition": "One-use chip: captain points x3 instead of x2",
            "explanation": "Extra captain multiplier for one gameweek. Best in double gameweeks.",
            "usage": "Use on premium player (Salah/Haaland) in DGW with 2 favorable fixtures.",
            "example": "Haaland scores 24 points in DGW = 72 points with Triple Captain."
        },
        "Wildcard": {
            "term": "Wildcard Chip",
            "definition": "Unlimited free transfers for one gameweek",
            "explanation": "Can make 15 transfers with no point deductions. Available twice per season (before and after GW20).",
            "usage": "Use when team structure is broken or to prepare for fixture swings.",
            "example": "Use WC1 around GW8 to fix injuries and pivot to teams with good fixtures."
        },
        "Free Hit": {
            "term": "Free Hit Chip",
            "definition": "One-use chip: make unlimited transfers for one GW only",
            "explanation": "Team reverts to pre-chip squad next week. Best for blank/double gameweeks.",
            "usage": "Save for blank gameweeks when many teams don't play.",
            "example": "BGW where only 6 teams play: Free Hit to build team of those 6 teams."
        },
        
        # Fixture Analysis
        "FDR": {
            "term": "Fixture Difficulty Rating",
            "definition": "Official rating (1-5) of opponent difficulty",
            "explanation": "1 = easiest, 5 = hardest. Based on opponent's defensive/attacking strength.",
            "usage": "Target players with FDR 1-2 for next 5 fixtures. Avoid FDR 4-5.",
            "example": "Striker facing 5 teams with FDR of 2 = excellent captaincy run."
        },
        "DGW": {
            "term": "Double Gameweek",
            "definition": "Gameweek where some teams play twice",
            "explanation": "Caused by fixture congestion. Players from DGW teams can score double points.",
            "usage": "Load up on DGW players. Use Bench Boost or Triple Captain chips.",
            "example": "Liverpool plays twice in GW24 = double points potential for Salah."
        },
        "BGW": {
            "term": "Blank Gameweek",
            "definition": "Gameweek where some teams don't play",
            "explanation": "Caused by cup competitions. Fewer teams = fewer scoring opportunities.",
            "usage": "Use Free Hit to field 11 players, or plan transfers to avoid blanks.",
            "example": "Only 6 teams play in BGW31 = need players from those 6 teams."
        }
    }
    
    CATEGORIES = {
        "Core Metrics": ["xG", "xA", "ICT Index", "BPS", "Form", "Value Score"],
        "Ownership & Transfers": ["Selected By %", "TSB%", "Net Transfers", "Minutes"],
        "Strategy & Chips": ["Differential", "Template Team", "Bench Boost", "Triple Captain", "Wildcard", "Free Hit"],
        "Fixtures": ["FDR", "DGW", "BGW"]
    }
    
    @staticmethod
    @handle_errors("Error rendering glossary")
    def render_glossary():
        """Render interactive FPL glossary"""
        st.markdown("### 📖 FPL Glossary")
        st.markdown("*Understanding key terms and metrics for better FPL decisions*")
        
        # Search functionality
        search_term = st.text_input(
            "🔍 Search glossary",
            placeholder="e.g., xG, BPS, Differential...",
            key="glossary_search"
        )
        
        # Category tabs
        tab_names = list(FPLGlossary.CATEGORIES.keys()) + ["All Terms"]
        tabs = st.tabs(tab_names)
        
        for idx, (category, terms) in enumerate(FPLGlossary.CATEGORIES.items()):
            with tabs[idx]:
                FPLGlossary._render_category(category, terms, search_term)
        
        # All terms tab
        with tabs[-1]:
            all_terms = [term for terms in FPLGlossary.CATEGORIES.values() for term in terms]
            FPLGlossary._render_category("All Terms", all_terms, search_term)
    
    @staticmethod
    def _render_category(category: str, terms: List[str], search_term: str = ""):
        """Render glossary terms for a category"""
        filtered_terms = []
        
        for term_key in terms:
            term_data = FPLGlossary.GLOSSARY[term_key]
            # Filter by search term
            if search_term:
                search_lower = search_term.lower()
                if (search_lower in term_data["term"].lower() or 
                    search_lower in term_data["definition"].lower() or
                    search_lower in term_data["explanation"].lower()):
                    filtered_terms.append((term_key, term_data))
            else:
                filtered_terms.append((term_key, term_data))
        
        if not filtered_terms:
            st.info(f"No terms found matching '{search_term}'")
            return
        
        for term_key, term_data in filtered_terms:
            with st.expander(f"**{term_data['term']}**"):
                st.markdown(f"**Definition:** {term_data['definition']}")
                st.markdown(f"**Explanation:** {term_data['explanation']}")
                st.markdown(f"**How to Use:** {term_data['usage']}")
                st.markdown(f"**Example:** *{term_data['example']}*")


class StrategyGuides:
    """FPL strategy guides for different scenarios"""
    
    GUIDES = {
        "Season Start": {
            "title": "🚀 Season Start Strategy (GW1-8)",
            "overview": "Build a balanced template team and establish a strong foundation",
            "key_points": [
                "Start with premium assets (Salah, Haaland) - they consistently deliver",
                "Avoid early differentials - template is safer in opening weeks",
                "Focus on teams with good opening fixtures (check FDR 1-3)",
                "Keep 0.5-1.0m in the bank for flexibility",
                "Don't use chips early - save for DGW/BGW later"
            ],
            "team_structure": """
            **Recommended Structure:**
            - **Budget:** £100.0m
            - **Formation:** 3-4-3 or 3-5-2
            - **Premiums:** 2-3 players £10m+ (Salah, Haaland)
            - **Mid-price:** 5-6 players £6-9m (reliable returners)
            - **Enablers:** 5-7 players £4-5.5m (bench fodder or rotation)
            """,
            "example": """
            **Sample GW1 Team:**
            - GK: Raya (4.5), Turner (4.0)
            - DEF: Robertson (7.0), Gabriel (6.0), Pedro Porro (5.5), Lewis (4.5), Patterson (4.0)
            - MID: Salah (13.0), Saka (9.0), Maddison (7.5), Gordon (7.5), Rogers (5.0)
            - FWD: Haaland (14.0), Watkins (9.0), Archer (4.5)
            """,
            "tips": [
                "Monitor pre-season friendlies for form and fitness",
                "Check team news before GW1 deadline",
                "Consider players who returned from injury late last season",
                "Avoid players in Europa/Conference League (rotation risk)"
            ]
        },
        
        "Mid-Season": {
            "title": "⚡ Mid-Season Strategy (GW9-28)",
            "overview": "Navigate fixture swings, injuries, and form changes",
            "key_points": [
                "Plan transfers 3-5 weeks ahead based on fixtures",
                "Use Wildcard 1 (GW8-12) to fix structure and pivot to good fixtures",
                "Monitor form closely - move on from underperformers",
                "Build towards Double Gameweeks (usually GW24-27)",
                "Save Bench Boost for first DGW with full playing bench"
            ],
            "team_structure": """
            **Flexible Structure:**
            - Adapt formation based on fixtures (3-4-3, 4-4-2, 3-5-2)
            - 1-2 differentials if chasing rank (but keep template core)
            - Full playing bench for DGW preparation
            - Consider team stacks (3 players from same team) for good fixture runs
            """,
            "example": """
            **Fixture Swing Example:**
            - GW12-16: Liverpool (FDR 2) → Load up on Salah, TAA, Diaz
            - GW17-20: Arsenal (FDR 4-5) → Move to City assets before rise
            - GW24: DGW → Bench Boost with 15 playing DGW players
            """,
            "tips": [
                "Track price changes - sell before falls, buy before rises",
                "Don't chase last week's points - focus on upcoming fixtures",
                "Plan Wildcard exit strategy 5 GWs in advance",
                "Keep 1-2 free transfers for injury/suspension emergencies"
            ]
        },
        
        "End Game": {
            "title": "🎯 End Game Strategy (GW29-38)",
            "overview": "Final push for rank with remaining chips and differential strategy",
            "key_points": [
                "Use Wildcard 2 to set up for final run-in",
                "Free Hit for any Blank Gameweeks (BGW31 common)",
                "Plan differential captains if chasing mini-league",
                "Consider template if defending lead",
                "Monitor rotation risk as teams secure safety/titles"
            ],
            "team_structure": """
            **Risk-Adjusted Structure:**
            - **If leading:** Stick to template, minimize risk
            - **If chasing:** 3-4 differentials, aggressive captains
            - Focus on teams fighting for Europe or survival (more motivation)
            - Avoid teams with nothing to play for (rotation heavy)
            """,
            "example": """
            **Rank Chase Strategy (GW34-38):**
            - Replace template players with <5% owned alternatives
            - Captain differentials from teams with DGW
            - Bench Boost if not used (even without DGW)
            - Free Hit GW38 for perfect team selection
            """,
            "tips": [
                "Check European qualification scenarios (UCL, UEL race)",
                "Monitor relegation battles for motivated players",
                "Be bold with captains if chasing - differential (C) can swing 100K ranks",
                "Don't save chips - use them or lose them!"
            ]
        },
        
        "Chip Strategy": {
            "title": "💎 Chip Strategy Guide",
            "overview": "Maximize value from your one-time chips",
            "key_points": [
                "Plan chip usage at season start - don't waste them",
                "Wildcard 1: GW8-12 (fixture swing or team fix)",
                "Bench Boost: First DGW with 15 DGW players (GW24-27)",
                "Triple Captain: Best DGW fixture for premium (Salah/Haaland)",
                "Free Hit: BGW31 or final DGW/BGW"
            ],
            "team_structure": """
            **Chip Preparation:**
            
            **Bench Boost (2 weeks before):**
            - Build full playing bench (no 4.0 bench fodder)
            - Ensure all 15 players have DGW
            - Target 100+ points from chip
            
            **Triple Captain:**
            - Premium player in DGW with 2 favorable fixtures
            - Check opponent FDR (both games FDR ≤3)
            - Historical returns against those opponents
            
            **Free Hit:**
            - Don't prepare - that's the beauty!
            - Pick 15 players for that GW only
            - Go all-in on BGW teams or best DGW teams
            """,
            "example": """
            **Optimal Chip Timeline:**
            - GW10: Wildcard 1 (pivot to fixture swings)
            - GW19: Wildcard 2 (set up for DGW24)
            - GW24: Bench Boost (first DGW, 15 players playing)
            - GW25: Triple Captain Haaland (DGW vs easy opponents)
            - GW31: Free Hit (BGW with only 6 teams playing)
            """,
            "tips": [
                "Don't rush Wildcard 1 - only use if team is broken",
                "Bench Boost value > Triple Captain usually (15 vs 1 player)",
                "Free Hit in BGW (6-8 teams) > DGW (already have DGW players)",
                "Check FPL Twitter for DGW/BGW announcements in advance"
            ]
        }
    }
    
    @staticmethod
    @handle_errors("Error rendering strategy guides")
    def render_guides():
        """Render strategy guides"""
        st.markdown("### 📚 Strategy Guides")
        st.markdown("*Proven strategies for every stage of the FPL season*")
        
        # Guide selection
        guide_names = list(StrategyGuides.GUIDES.keys())
        selected_guide = st.selectbox(
            "Select a guide",
            guide_names,
            key="strategy_guide_select"
        )
        
        if selected_guide:
            guide = StrategyGuides.GUIDES[selected_guide]
            StrategyGuides._render_guide(guide)
    
    @staticmethod
    def _render_guide(guide: Dict):
        """Render a single strategy guide"""
        st.markdown(f"## {guide['title']}")
        st.markdown(f"**{guide['overview']}**")
        
        # Key Points
        st.markdown("### 🎯 Key Points")
        for point in guide['key_points']:
            st.markdown(f"- {point}")
        
        # Team Structure
        st.markdown("### 🏗️ Team Structure")
        st.markdown(guide['team_structure'])
        
        # Example
        st.markdown("### 💡 Example")
        st.code(guide['example'], language=None)
        
        # Tips
        st.markdown("### 💎 Pro Tips")
        for tip in guide['tips']:
            st.markdown(f"- {tip}")


class QuickStartTutorial:
    """Interactive quick start tutorial for new users"""
    
    @staticmethod
    @handle_errors("Error rendering tutorial")
    def render_tutorial():
        """Render quick start tutorial"""
        st.markdown("### 🎬 Quick Start Tutorial")
        
        # Check if user has completed tutorial
        if 'tutorial_complete' not in st.session_state:
            st.session_state.tutorial_complete = False
        
        if st.session_state.tutorial_complete:
            st.success("✅ Tutorial completed! Welcome to FPL Analytics.")
            if st.button("🔄 Restart Tutorial"):
                st.session_state.tutorial_complete = False
                st.rerun()
            return
        
        st.markdown("""
        Welcome to **FPL Analytics**! This quick guide will help you get started.
        """)
        
        # Tutorial steps
        steps = [
            {
                "title": "📊 Dashboard",
                "content": """
                The **Dashboard** is your home base. Here you'll find:
                - Top players by form, value, and points
                - Price change predictions (who's rising/falling)
                - Key statistics and trends
                
                **Pro Tip:** Check price predictions daily to avoid missing rises!
                """
            },
            {
                "title": "🔍 Player Analysis",
                "content": """
                Deep dive into any player's performance:
                - Filter by position, team, price range
                - Compare stats: xG, xA, ICT, BPS, form
                - View recent performance trends
                
                **Pro Tip:** Use the comparison tool to choose between similar players.
                """
            },
            {
                "title": "👥 Team Builder",
                "content": """
                Build and optimize your FPL team:
                - Generate best team automatically (4 strategies)
                - Respect FPL rules (budget, positions, team limits)
                - See team statistics and value
                
                **Pro Tip:** Try different strategies - "Value" finds budget gems!
                """
            },
            {
                "title": "📅 Fixture Analysis",
                "content": """
                Plan ahead with fixture difficulty:
                - See all teams' upcoming fixtures
                - Color-coded difficulty ratings (green = easy)
                - Identify fixture swings
                
                **Pro Tip:** Target players from teams with 3+ green fixtures ahead.
                """
            },
            {
                "title": "🚨 Live Data",
                "content": """
                Real-time FPL updates:
                - Live gameweek scores
                - Transfer trends
                - Price change alerts
                
                **Pro Tip:** Enable notifications for your watchlist players!
                """
            },
            {
                "title": "🎨 Customization",
                "content": """
                Make the app yours:
                - **Dark Mode:** Toggle in sidebar (easier on eyes at night)
                - **Filters:** Save your preferred player filters
                - **Pagination:** Choose how many players to view per page
                
                **Pro Tip:** Dark mode saves battery on mobile devices!
                """
            }
        ]
        
        # Step navigation
        if 'tutorial_step' not in st.session_state:
            st.session_state.tutorial_step = 0
        
        current_step = st.session_state.tutorial_step
        step_data = steps[current_step]
        
        # Progress indicator
        progress = (current_step + 1) / len(steps)
        st.progress(progress)
        st.caption(f"Step {current_step + 1} of {len(steps)}")
        
        # Step content
        st.markdown(f"## {step_data['title']}")
        st.markdown(step_data['content'])
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_step > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.tutorial_step -= 1
                    st.rerun()
        
        with col2:
            if st.button("⏭️ Skip Tutorial"):
                st.session_state.tutorial_complete = True
                st.rerun()
        
        with col3:
            if current_step < len(steps) - 1:
                if st.button("Next ➡️"):
                    st.session_state.tutorial_step += 1
                    st.rerun()
            else:
                if st.button("🎉 Complete Tutorial"):
                    st.session_state.tutorial_complete = True
                    st.balloons()
                    st.rerun()


class LearningResourcesHub:
    """Main hub for all learning resources"""
    
    @staticmethod
    @handle_errors("Error rendering learning resources hub")
    def render():
        """Render complete learning resources hub"""
        st.title("🎓 Learning Resources")
        st.markdown("*Everything you need to master FPL Analytics and improve your game*")
        
        # Main tabs
        tab1, tab2, tab3 = st.tabs([
            "📖 Glossary",
            "📚 Strategy Guides",
            "🎬 Quick Start"
        ])
        
        with tab1:
            FPLGlossary.render_glossary()
        
        with tab2:
            StrategyGuides.render_guides()
        
        with tab3:
            QuickStartTutorial.render_tutorial()
        
        # Additional resources section
        st.markdown("---")
        st.markdown("### 🔗 External Resources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Community & News:**
            - [Official FPL](https://fantasy.premierleague.com/)
            - [r/FantasyPL Reddit](https://reddit.com/r/FantasyPL)
            - [FPL Twitter Community](https://twitter.com/search?q=%23FPL)
            - [FPL Focal Podcast](https://open.spotify.com/show/fpl)
            """)
        
        with col2:
            st.markdown("""
            **Analytics & Tools:**
            - [FPL Statistics](https://www.fplstatistics.co.uk/)
            - [Fantasy Football Scout](https://www.fantasyfootballscout.co.uk/)
            - [Understat (xG data)](https://understat.com/)
            - [FBRef (Advanced Stats)](https://fbref.com/)
            """)


# Convenience function for easy import
@handle_errors("Error loading learning resources")
def render_learning_resources():
    """Render the learning resources hub"""
    LearningResourcesHub.render()
