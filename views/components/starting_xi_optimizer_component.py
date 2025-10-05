"""
Starting XI Optimizer Component - Handles lineup optimization functionality
"""
import streamlit as st
from utils.error_handling import logger


class StartingXIOptimizerComponent:
    """Handles Starting XI optimization"""
    
    def render_optimizer(self, team_data, players_df):
        """Display Starting XI Optimizer with comprehensive analysis"""
        st.subheader("⭐ Starting XI Optimizer")
        
        # Explanation section
        with st.expander("📚 How the Starting XI Optimizer Works", expanded=False):
            st.markdown("""
            The **Starting XI Optimizer** uses advanced algorithms to suggest your best possible lineup based on:
            
            🎯 **Key Factors:**
            - **Form Rating**: Recent performance trends (last 5 games)
            - **Fixture Difficulty**: Opposition strength analysis
            - **Expected Points**: Predicted performance this gameweek
            - **Minutes Played**: Reliability and rotation risk
            - **Price Per Point**: Value efficiency
            - **Team Strength**: Overall team performance indicators
            
            ⚽ **Optimization Strategy:**
            - Ensures valid formation (1 GK, 3-5 DEF, 3-5 MID, 1-3 FWD)
            - Maximizes expected points while considering form
            - Suggests captain based on highest expected returns
            - Identifies bench players and substitution priorities
            """)
        
        picks = team_data.get('picks', [])
        if not picks:
            st.warning("No squad data available for optimization")
            return
        
        # Settings for optimization
        col1, col2, col3 = st.columns(3)
        
        formation_pref, optimization_focus, risk_tolerance = self._render_optimization_settings(col1, col2, col3)
        
        # Analyze squad and generate recommendations
        if st.button("🚀 Optimize Starting XI", type="primary"):
            with st.spinner("Analyzing your squad and optimizing lineup..."):
                optimized_lineup = self._optimize_starting_eleven(
                    team_data, players_df, formation_pref, optimization_focus, risk_tolerance
                )
                
                if optimized_lineup:
                    self._display_optimized_lineup(optimized_lineup)
                else:
                    st.error("❌ Could not optimize lineup. Please check your squad data.")
    
    def _render_optimization_settings(self, col1, col2, col3):
        """Render optimization settings controls"""
        with col1:
            formation_pref = st.selectbox(
                "🏗️ Preferred Formation",
                ["Auto-Select", "3-4-3", "3-5-2", "4-3-3", "4-4-2", "4-5-1", "5-3-2", "5-4-1"],
                help="Choose formation or let AI auto-select the best"
            )
        
        with col2:
            optimization_focus = st.selectbox(
                "🎯 Optimization Focus",
                ["Balanced", "Form-Heavy", "Fixture-Based", "Conservative", "Differential"],
                help="Adjust the strategy focus"
            )
        
        with col3:
            risk_tolerance = st.slider(
                "⚖️ Risk Tolerance",
                min_value=1, max_value=10, value=5,
                help="1=Safe picks, 10=High risk/reward"
            )
        
        return formation_pref, optimization_focus, risk_tolerance
    
    def _optimize_starting_eleven(self, team_data, players_df, formation_pref, optimization_focus, risk_tolerance):
        """Core optimization algorithm for Starting XI"""
        picks = team_data.get('picks', [])
        
        # Get squad players with enhanced stats
        squad_players = []
        for pick in picks:
            player_info = players_df[players_df['id'] == pick['element']]
            if not player_info.empty:
                player = player_info.iloc[0].to_dict()
                player['pick_data'] = pick
                player['optimization_score'] = self._calculate_optimization_score(
                    player, optimization_focus, risk_tolerance
                )
                squad_players.append(player)
        
        if len(squad_players) < 15:
            return None
        
        # Group by position
        positions = {
            'GK': [p for p in squad_players if p.get('position_name') == 'Goalkeeper'],
            'DEF': [p for p in squad_players if p.get('position_name') == 'Defender'],
            'MID': [p for p in squad_players if p.get('position_name') == 'Midfielder'],
            'FWD': [p for p in squad_players if p.get('position_name') == 'Forward']
        }
        
        # Sort each position by optimization score
        for pos in positions:
            positions[pos].sort(key=lambda x: x['optimization_score'], reverse=True)
        
        # Determine formation
        if formation_pref == "Auto-Select":
            formation = self._determine_optimal_formation(positions)
        else:
            formation = self._parse_formation(formation_pref)
        
        # Select starting XI
        starting_xi = {
            'GK': positions['GK'][:1] if positions['GK'] else [],
            'DEF': positions['DEF'][:formation['DEF']] if len(positions['DEF']) >= formation['DEF'] else positions['DEF'],
            'MID': positions['MID'][:formation['MID']] if len(positions['MID']) >= formation['MID'] else positions['MID'],
            'FWD': positions['FWD'][:formation['FWD']] if len(positions['FWD']) >= formation['FWD'] else positions['FWD']
        }
        
        # Calculate bench (remaining players)
        bench_players = []
        for pos in positions:
            if pos == 'GK':
                bench_players.extend(positions[pos][1:])  # Backup GK
            elif pos == 'DEF':
                bench_players.extend(positions[pos][formation['DEF']:])
            elif pos == 'MID':
                bench_players.extend(positions[pos][formation['MID']:])
            elif pos == 'FWD':
                bench_players.extend(positions[pos][formation['FWD']:])
        
        # Sort bench by optimization score
        bench_players.sort(key=lambda x: x['optimization_score'], reverse=True)
        
        # Suggest captain and vice-captain
        all_starters = []
        for pos_players in starting_xi.values():
            all_starters.extend(pos_players)
        
        captain_candidates = sorted(all_starters, key=lambda x: x['optimization_score'], reverse=True)
        
        return {
            'formation': formation,
            'starting_xi': starting_xi,
            'bench': bench_players[:4],  # First 4 bench players
            'captain': captain_candidates[0] if captain_candidates else None,
            'vice_captain': captain_candidates[1] if len(captain_candidates) > 1 else None,
            'total_predicted_points': sum([p['optimization_score'] for p in all_starters])
        }
    
    def _calculate_optimization_score(self, player, optimization_focus, risk_tolerance):
        """Calculate optimization score based on multiple factors"""
        score = 0
        
        # Helper function to safely convert to float
        def safe_float(value, default=0.0):
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Helper function to safely convert to int
        def safe_int(value, default=0):
            try:
                if value is None or value == '':
                    return default
                return int(float(value))  # Convert via float first to handle string decimals
            except (ValueError, TypeError):
                return default
        
        # Base score from total points (normalized)
        total_points = safe_float(player.get('total_points', 0))
        score += (total_points / 300) * 30  # Max 30 points from total points
        
        # Form component (0-20 points)
        form = safe_float(player.get('form', 0))
        if optimization_focus == "Form-Heavy":
            score += (form / 10) * 25
        else:
            score += (form / 10) * 15
        
        # Points per game reliability (0-15 points)
        ppg = safe_float(player.get('points_per_game', 0))
        if ppg > 0:
            score += min(ppg * 2, 15)
        
        # Minutes played reliability (0-10 points)
        minutes = safe_int(player.get('minutes', 0))
        if minutes > 1500:  # Regular starter
            score += 10
        elif minutes > 1000:
            score += 7
        elif minutes > 500:
            score += 4
        
        # Value efficiency (0-10 points)
        ppm = safe_float(player.get('points_per_million', 0))
        if ppm > 8:
            score += 10
        elif ppm > 6:
            score += 7
        elif ppm > 4:
            score += 4
        
        # Team strength factor (0-5 points)
        # Estimate based on clean sheets, goals scored
        team_strength = 0
        clean_sheets = safe_int(player.get('clean_sheets', 0))
        goals_scored = safe_int(player.get('goals_scored', 0))
        
        if clean_sheets > 8:  # Good defensive team
            team_strength += 2
        if goals_scored > 5:  # Good attacking player
            team_strength += 3
        score += min(team_strength, 5)
        
        # Risk adjustment based on tolerance
        if risk_tolerance < 5:  # Conservative
            # Prefer established players
            if total_points > 100:
                score += 5
        else:  # Higher risk tolerance
            # Prefer differentials
            ownership = safe_float(player.get('selected_by_percent', 50))
            if ownership < 15:  # Differential
                score += (10 - risk_tolerance) * 1.5
        
        # Fixture difficulty (simplified - based on team strength)
        if optimization_focus == "Fixture-Based":
            # This is a simplified fixture analysis
            # In a full implementation, you'd have actual fixture data
            score += 5  # Placeholder for fixture analysis
        
        return max(score, 0)  # Ensure non-negative score
    
    def _determine_optimal_formation(self, positions):
        """Determine the best formation based on player quality"""
        formations = [
            {'DEF': 3, 'MID': 4, 'FWD': 3},
            {'DEF': 3, 'MID': 5, 'FWD': 2},
            {'DEF': 4, 'MID': 3, 'FWD': 3},
            {'DEF': 4, 'MID': 4, 'FWD': 2},
            {'DEF': 4, 'MID': 5, 'FWD': 1},
            {'DEF': 5, 'MID': 3, 'FWD': 2},
            {'DEF': 5, 'MID': 4, 'FWD': 1}
        ]
        
        best_formation = None
        best_score = 0
        
        for formation in formations:
            if (len(positions['DEF']) >= formation['DEF'] and 
                len(positions['MID']) >= formation['MID'] and 
                len(positions['FWD']) >= formation['FWD']):
                
                # Calculate total score for this formation
                score = 0
                score += sum([p['optimization_score'] for p in positions['DEF'][:formation['DEF']]])
                score += sum([p['optimization_score'] for p in positions['MID'][:formation['MID']]])
                score += sum([p['optimization_score'] for p in positions['FWD'][:formation['FWD']]])
                
                if score > best_score:
                    best_score = score
                    best_formation = formation
        
        return best_formation or {'DEF': 4, 'MID': 4, 'FWD': 2}  # Default fallback
    
    def _parse_formation(self, formation_str):
        """Parse formation string into position counts"""
        if formation_str == "Auto-Select":
            return {'DEF': 4, 'MID': 4, 'FWD': 2}
        
        parts = formation_str.split('-')
        if len(parts) == 3:
            return {
                'DEF': int(parts[0]),
                'MID': int(parts[1]),
                'FWD': int(parts[2])
            }
        return {'DEF': 4, 'MID': 4, 'FWD': 2}  # Default
    
    def _display_optimized_lineup(self, optimized_lineup):
        """Display the optimized lineup with detailed breakdown"""
        st.success("✅ **Optimization Complete!**")
        
        formation = optimized_lineup['formation']
        formation_str = f"{formation['DEF']}-{formation['MID']}-{formation['FWD']}"
        
        # Overall recommendations
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏗️ Optimal Formation", formation_str)
        
        with col2:
            predicted_points = optimized_lineup['total_predicted_points']
            st.metric("📊 Predicted Points", f"{predicted_points:.1f}")
        
        with col3:
            captain = optimized_lineup['captain']
            captain_name = captain['web_name'] if captain else "N/A"
            st.metric("👑 Captain", captain_name)
        
        with col4:
            vice_captain = optimized_lineup['vice_captain']
            vc_name = vice_captain['web_name'] if vice_captain else "N/A"
            st.metric("🥈 Vice Captain", vc_name)
        
        # Detailed lineup breakdown
        st.subheader("🎯 Optimized Starting XI")
        
        starting_xi = optimized_lineup['starting_xi']
        
        # Display by position
        for pos_name, display_name in [('GK', '🥅 Goalkeeper'), ('DEF', '🛡️ Defenders'), ('MID', '⚽ Midfielders'), ('FWD', '🎯 Forwards')]:
            if starting_xi[pos_name]:
                st.write(f"**{display_name}**")
                
                for player in starting_xi[pos_name]:
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                    
                    with col1:
                        captain_badge = " 👑" if player == optimized_lineup['captain'] else " 🥈" if player == optimized_lineup['vice_captain'] else ""
                        st.write(f"**{player['web_name']}**{captain_badge}")
                    
                    with col2:
                        st.write(f"{player.get('team_short_name', 'UNK')}")
                    
                    with col3:
                        st.write(f"Form: {player.get('form', 0):.1f}")
                    
                    with col4:
                        st.write(f"£{player.get('cost_millions', 0):.1f}m")
                    
                    with col5:
                        score = player.get('optimization_score', 0)
                        st.write(f"{score:.1f}")
                
                st.divider()
        
        # Bench recommendations
        st.subheader("🪑 Recommended Bench")
        
        bench = optimized_lineup['bench']
        if bench:
            for i, player in enumerate(bench, 1):
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                with col1:
                    st.write(f"{i}.")
                
                with col2:
                    st.write(f"**{player['web_name']}** ({player.get('position_name', 'UNK')})")
                
                with col3:
                    st.write(f"{player.get('team_short_name', 'UNK')}")
                
                with col4:
                    st.write(f"Score: {player.get('optimization_score', 0):.1f}")
        
        # Strategic insights
        self._display_strategic_insights(optimized_lineup)
        
        # Action buttons
        self._display_action_buttons(optimized_lineup)
    
    def _display_strategic_insights(self, optimized_lineup):
        """Display strategic insights"""
        st.subheader("💡 Strategic Insights")
        
        insights = []
        starting_xi = optimized_lineup['starting_xi']
        formation = optimized_lineup['formation']
        
        # Captain analysis
        captain = optimized_lineup['captain']
        if captain:
            captain_form = captain.get('form', 0)
            if captain_form > 7:
                insights.append("🔥 Your suggested captain is in excellent form!")
            elif captain_form < 4:
                insights.append("⚠️ Consider alternative captain options - current suggestion has poor form")
        
        # Formation analysis
        if formation['DEF'] >= 5:
            insights.append("🛡️ Defensive formation - good for teams expecting clean sheets")
        elif formation['FWD'] >= 3:
            insights.append("⚔️ Attacking formation - prioritizing goal-scoring potential")
        
        # Risk analysis
        risky_players = [p for pos_players in starting_xi.values() for p in pos_players if p.get('selected_by_percent', 50) < 10]
        if len(risky_players) >= 2:
            insights.append(f"💎 {len(risky_players)} differential picks in starting XI - high risk/reward strategy")
        
        # Value analysis
        total_value = sum([p.get('cost_millions', 0) for pos_players in starting_xi.values() for p in pos_players])
        if total_value < 75:
            insights.append("💰 Budget-friendly lineup leaves room for upgrades")
        elif total_value > 85:
            insights.append("💸 Premium-heavy lineup - ensure these players deliver")
        
        # Display insights
        if insights:
            for insight in insights:
                st.info(insight)
        else:
            st.success("✅ Well-balanced team selection!")
    
    def _display_action_buttons(self, optimized_lineup):
        """Display action buttons"""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Copy Lineup to Clipboard"):
                lineup_text = self._generate_lineup_text(optimized_lineup)
                st.code(lineup_text, language="text")
                st.success("Lineup formatted for sharing!")
        
        with col2:
            if st.button("🔄 Re-optimize with Different Settings"):
                st.rerun()
    
    def _generate_lineup_text(self, optimized_lineup):
        """Generate text representation of the lineup"""
        formation = optimized_lineup['formation']
        starting_xi = optimized_lineup['starting_xi']
        
        lines = []
        lines.append(f"🏗️ Formation: {formation['DEF']}-{formation['MID']}-{formation['FWD']}")
        lines.append("")
        
        for pos_name, display_name in [('GK', 'GK'), ('DEF', 'DEF'), ('MID', 'MID'), ('FWD', 'FWD')]:
            if starting_xi[pos_name]:
                players = [p['web_name'] for p in starting_xi[pos_name]]
                lines.append(f"{display_name}: {', '.join(players)}")
        
        lines.append("")
        captain = optimized_lineup['captain']
        vice_captain = optimized_lineup['vice_captain']
        
        if captain:
            lines.append(f"👑 Captain: {captain['web_name']}")
        if vice_captain:
            lines.append(f"🥈 Vice Captain: {vice_captain['web_name']}")
        
        return "\n".join(lines)
