"""
Transfer Planning Component - Strategic transfer analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.error_handling import logger


class TransferPlanningComponent:
    """Handles comprehensive transfer planning with real FPL data"""
    
    def __init__(self, data_service=None):
        self.data_service = data_service
    
    def render_transfer_planning(self, team_data, players_df):
        """Render comprehensive transfer planning"""
        st.header("🔄 Strategic Transfer Planning")
        
        current_players = st.session_state.get('fpl_team_current_players', pd.DataFrame())
        all_players = st.session_state.get('fpl_players_df', pd.DataFrame())
        
        if current_players.empty:
            st.warning("Load your team data to see transfer recommendations")
            return
        
        # Create transfer planning tabs
        transfer_tab1, transfer_tab2, transfer_tab3, transfer_tab4 = st.tabs([
            "🔄 Transfer Targets", "🎯 Replacement Analysis", "💰 Budget Planning", "📅 Long-term Strategy"
        ])
        
        with transfer_tab1:
            self._render_transfer_targets(team_data, current_players, all_players)
        
        with transfer_tab2:
            self._render_replacement_analysis(current_players, all_players)
        
        with transfer_tab3:
            self._render_budget_planning(team_data, current_players, all_players)
        
        with transfer_tab4:
            self._render_longterm_strategy(team_data, current_players)
    
    def _render_transfer_targets(self, team_data, current_players, all_players):
        """Render transfer target recommendations"""
        st.subheader("🎯 Priority Transfer Targets")
        
        if all_players.empty:
            st.warning("Player database not available for transfer recommendations")
            return
        
        # Get players not currently owned
        current_player_ids = current_players['id'].tolist()
        available_players = all_players[~all_players['id'].isin(current_player_ids)].copy()
        
        # Calculate transfer appeal score
        available_players['transfer_score'] = (
            available_players['form'] * 0.3 +
            available_players['points_per_game'] * 0.3 +
            (available_players['cost_change_start'] * 0.1) +  # Price rising is good
            ((50 - available_players['selected_by_percent']) * 0.01) +  # Differentials get bonus
            (available_players['total_points'] * 0.002)  # Season performance
        )
        
        # Get top targets by position
        positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        
        for position in positions:
            position_players = available_players[available_players['element_type_name'] == position]
            
            if not position_players.empty:
                top_targets = position_players.nlargest(3, 'transfer_score')
                
                st.write(f"**🎯 Top {position} Targets:**")
                
                for i, (_, player) in enumerate(top_targets.iterrows(), 1):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            if i == 1:
                                st.success(f"🥇 **{player['web_name']}** ({player['team_name']})")
                            elif i == 2:
                                st.info(f"🥈 **{player['web_name']}** ({player['team_name']})")
                            else:
                                st.write(f"🥉 **{player['web_name']}** ({player['team_name']})")
                        
                        with col2:
                            st.write(f"£{player['now_cost']/10:.1f}m")
                        
                        with col3:
                            st.write(f"Form: {player['form']}")
                        
                        with col4:
                            st.write(f"Own: {player['selected_by_percent']:.1f}%")
                        
                        # Additional details
                        st.caption(f"Points: {player['total_points']} | PPG: {player['points_per_game']:.1f} | Score: {player['transfer_score']:.1f}")
                
                st.divider()
        
        # Hot transfers (rising in price/ownership)
        st.subheader("🔥 Hot Transfer Targets")
        
        hot_players = available_players[
            (available_players['cost_change_start'] > 0.1) &
            (available_players['form'] > 3)
        ].nlargest(5, 'transfer_score')
        
        if not hot_players.empty:
            st.write("**Players gaining value and performing well:**")
            
            for _, player in hot_players.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"🔥 **{player['web_name']}** ({player['element_type_name']})")
                
                with col2:
                    price_change = player['cost_change_start']
                    st.write(f"£{player['now_cost']/10:.1f}m (+{price_change:.1f})")
                
                with col3:
                    st.write(f"Form: {player['form']}")
        else:
            st.info("No hot transfer targets identified at the moment")
        
        # Differential picks
        st.subheader("🎲 Differential Options")
        
        differentials = available_players[
            (available_players['selected_by_percent'] < 10) &
            (available_players['points_per_game'] > 3) &
            (available_players['form'] > 2)
        ].nlargest(5, 'transfer_score')
        
        if not differentials.empty:
            st.write("**Low-owned players with good potential:**")
            
            for _, player in differentials.iterrows():
                risk_level = "Low" if player['selected_by_percent'] < 5 else "Medium"
                risk_color = "🟢" if risk_level == "Low" else "🟡"
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"🎲 **{player['web_name']}** ({player['element_type_name']})")
                
                with col2:
                    st.write(f"Own: {player['selected_by_percent']:.1f}%")
                
                with col3:
                    st.write(f"{risk_color} {risk_level} Risk")
        else:
            st.info("No suitable differential options found")
    
    def _render_replacement_analysis(self, current_players, all_players):
        """Render direct replacement analysis"""
        st.subheader("🔄 Direct Replacement Analysis")
        
        if all_players.empty:
            st.warning("Player database not available for replacement analysis")
            return
        
        # Identify players who might need replacing
        problem_players = current_players[
            (current_players['form'] < 2) |
            (current_players['minutes'] < 300) |
            (current_players['cost_change_start'] < -0.3)
        ]
        
        if problem_players.empty:
            st.success("✅ No obvious replacement candidates in your current squad!")
            return
        
        st.write("**Players you might consider replacing:**")
        
        for _, player in problem_players.iterrows():
            with st.expander(f"🔄 Replace {player['web_name']} ({player['element_type_name']})"):
                # Show why they might need replacing
                issues = []
                if player['form'] < 2:
                    issues.append(f"Poor form ({player['form']} points/GW)")
                if player['minutes'] < 300:
                    issues.append(f"Limited playing time ({player['minutes']} minutes)")
                if player['cost_change_start'] < -0.3:
                    issues.append(f"Price falling ({player['cost_change_start']:.1f})")
                
                st.write(f"**Issues:** {', '.join(issues)}")
                st.write(f"**Current stats:** £{player['now_cost']/10:.1f}m | {player['total_points']} points | {player['form']} form")
                
                # Find similar price replacements
                position_players = all_players[
                    (all_players['element_type_name'] == player['element_type_name']) &
                    (~all_players['id'].isin(current_players['id'])) &
                    (all_players['now_cost'] >= player['now_cost'] - 5) &
                    (all_players['now_cost'] <= player['now_cost'] + 5)
                ]
                
                if not position_players.empty:
                    # Score replacements
                    position_players['replacement_score'] = (
                        position_players['form'] * 0.4 +
                        position_players['points_per_game'] * 0.3 +
                        (position_players['minutes'] / 100) * 0.2 +
                        (position_players['cost_change_start'] * 0.1)
                    )
                    
                    top_replacements = position_players.nlargest(3, 'replacement_score')
                    
                    st.write("**🎯 Recommended Replacements:**")
                    
                    for i, (_, replacement) in enumerate(top_replacements.iterrows(), 1):
                        price_diff = (replacement['now_cost'] - player['now_cost']) / 10
                        price_text = f"(+£{price_diff:.1f}m)" if price_diff > 0 else f"(£{price_diff:.1f}m)" if price_diff < 0 else "(same price)"
                        
                        if i == 1:
                            st.success(f"🥇 **{replacement['web_name']}** £{replacement['now_cost']/10:.1f}m {price_text}")
                        else:
                            st.info(f"🎯 **{replacement['web_name']}** £{replacement['now_cost']/10:.1f}m {price_text}")
                        
                        # Comparison stats
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.write(f"Form: {replacement['form']:.1f}")
                        with col2:
                            st.write(f"Points: {replacement['total_points']}")
                        with col3:
                            st.write(f"PPG: {replacement['points_per_game']:.1f}")
                        with col4:
                            st.write(f"Own: {replacement['selected_by_percent']:.1f}%")
                else:
                    st.warning(f"No suitable {player['element_type_name'].lower()} replacements found in similar price range")
    
    def _render_budget_planning(self, team_data, current_players, all_players):
        """Render budget planning analysis"""
        st.subheader("💰 Budget & Transfer Planning")
        
        # Current financial situation
        bank = team_data.get('bank', 0) / 10
        squad_value = current_players['now_cost'].sum() / 10
        total_budget = bank + squad_value
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Available Funds", f"£{bank:.1f}m")
        
        with col2:
            st.metric("Squad Value", f"£{squad_value:.1f}m")
        
        with col3:
            st.metric("Total Budget", f"£{total_budget:.1f}m")
        
        # Transfer scenarios
        st.subheader("🎯 Transfer Scenarios")
        
        # Free transfer scenario
        st.write("**🆓 Free Transfer Options:**")
        st.write(f"With £{bank:.1f}m available, you can upgrade any player by that amount or downgrade to free up funds.")
        
        # Most expensive upgrades possible
        if not all_players.empty:
            for position in ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']:
                pos_players = current_players[current_players['element_type_name'] == position]
                if not pos_players.empty:
                    cheapest_owned = pos_players.nsmallest(1, 'now_cost').iloc[0]
                    max_upgrade_cost = cheapest_owned['now_cost'] + (bank * 10)
                    
                    available_upgrades = all_players[
                        (all_players['element_type_name'] == position) &
                        (all_players['now_cost'] <= max_upgrade_cost) &
                        (~all_players['id'].isin(current_players['id']))
                    ]
                    
                    if not available_upgrades.empty:
                        best_upgrade = available_upgrades.nlargest(1, 'total_points').iloc[0]
                        upgrade_cost = (best_upgrade['now_cost'] - cheapest_owned['now_cost']) / 10
                        
                        if upgrade_cost <= bank:
                            st.info(f"• **{position}**: Upgrade {cheapest_owned['web_name']} → {best_upgrade['web_name']} (£{upgrade_cost:.1f}m)")
        
        # Hit scenarios
        st.write("**⚠️ Points Hit Scenarios:**")
        st.write("Taking a -4 hit is worth it if the new player scores 4+ more points than the old one.")
        
        # Calculate when hits might be worth it
        problem_players = current_players[current_players['form'] < 2]
        if not problem_players.empty:
            st.write("Players potentially worth taking a hit for:")
            for _, player in problem_players.head(3).iterrows():
                st.write(f"• {player['web_name']}: Current form {player['form']:.1f} points/GW")
        
        # Wildcard scenarios
        st.subheader("🃏 Wildcard Planning")
        st.write("**When to consider your Wildcard:**")
        
        # Calculate team issues
        issues_count = 0
        if len(current_players[current_players['form'] < 2]) > 2:
            issues_count += 1
            st.write("• Multiple players in poor form")
        
        if len(current_players[current_players['minutes'] < 400]) > 3:
            issues_count += 1
            st.write("• Several players not getting minutes")
        
        if current_players['cost_change_start'].sum() < -1.0:
            issues_count += 1
            st.write("• Significant team value lost")
        
        if bank < 0.5:
            issues_count += 1
            st.write("• Limited funds for transfers")
        
        if issues_count >= 3:
            st.error("🚨 **Wildcard Recommended**: Multiple issues suggest a major overhaul is needed")
        elif issues_count >= 2:
            st.warning("⚠️ **Consider Wildcard**: Several issues that might require multiple transfers")
        else:
            st.success("✅ **Hold Wildcard**: Team is in reasonable shape for targeted transfers")
        
        # Long-term value planning
        st.subheader("📈 Value Management Strategy")
        
        # Price change monitoring
        rising_owned = current_players[current_players['cost_change_start'] > 0.2]
        falling_owned = current_players[current_players['cost_change_start'] < -0.2]
        
        if not rising_owned.empty:
            st.success(f"✅ **Value Gains**: {len(rising_owned)} players have gained value")
            for _, player in rising_owned.iterrows():
                gain = player['cost_change_start']
                st.write(f"• {player['web_name']}: +£{gain:.1f}m")
        
        if not falling_owned.empty:
            st.error(f"📉 **Value Losses**: {len(falling_owned)} players have lost value")
            for _, player in falling_owned.iterrows():
                loss = abs(player['cost_change_start'])
                st.write(f"• {player['web_name']}: -£{loss:.1f}m")
    
    def _render_longterm_strategy(self, team_data, current_players):
        """Render long-term transfer strategy"""
        st.subheader("📅 Long-term Transfer Strategy")
        
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        
        # Season phase analysis
        if current_gw <= 10:
            phase = "Early Season"
            strategy = "Focus on form and value. Build team around consistent performers."
        elif current_gw <= 20:
            phase = "Mid Season"
            strategy = "Plan around fixture swings. Target teams with good upcoming fixtures."
        elif current_gw <= 30:
            phase = "Business End"
            strategy = "Focus on teams with strong fixtures and objectives to play for."
        else:
            phase = "Season End"
            strategy = "Avoid rotation risks. Target teams fighting for positions."
        
        st.info(f"**Current Phase**: {phase} (GW {current_gw})")
        st.write(f"**Strategy**: {strategy}")
        
        # Fixture-based planning
        st.subheader("⚽ Fixture-Based Planning")
        
        st.write("**Key Planning Periods:**")
        
        planning_periods = [
            (current_gw + 1, current_gw + 3, "Next 3 GWs", "Short-term captain and transfer decisions"),
            (current_gw + 4, current_gw + 8, "GW planning", "Medium-term fixture planning"),
            (current_gw + 9, min(current_gw + 15, 38), "Long-term", "Major squad changes and wildcards")
        ]
        
        for start_gw, end_gw, period, description in planning_periods:
            if start_gw <= 38:
                with st.expander(f"🗓️ {period} (GW {start_gw}-{min(end_gw, 38)})"):
                    st.write(f"**Focus**: {description}")
                    
                    if period == "Next 3 GWs":
                        st.write("**Actions to consider:**")
                        st.write("• Use free transfers for obvious upgrades")
                        st.write("• Captain players with favorable fixtures")
                        st.write("• Bench players facing tough opponents")
                    
                    elif period == "GW planning":
                        st.write("**Planning considerations:**")
                        st.write("• Identify fixture swings")
                        st.write("• Plan 2-3 transfer sequence")
                        st.write("• Monitor price changes")
                    
                    else:
                        st.write("**Strategic decisions:**")
                        st.write("• Wildcard timing")
                        st.write("• Chip usage strategy")
                        st.write("• End-game planning")
        
        # Transfer bank strategy
        st.subheader("💳 Transfer Management")
        
        transfers_made = team_data.get('total_transfers', 0)
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        
        # Simple calculation (would need actual data for precision)
        estimated_free_transfers = max(0, current_gw - transfers_made)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Transfers Made", transfers_made)
            st.metric("Est. Free Transfers", estimated_free_transfers)
        
        with col2:
            if estimated_free_transfers >= 2:
                st.success("✅ Banking transfers well")
            elif estimated_free_transfers >= 0:
                st.info("📊 Normal transfer usage")
            else:
                st.warning("⚠️ Heavy transfer usage")
        
        # Chip usage strategy
        st.subheader("🎯 Chip Usage Strategy")
        
        st.info("**Optimal Chip Timing:**")
        st.write("• **Wildcard**: Before major fixture swings or when 4+ players need changing")
        st.write("• **Bench Boost**: During double gameweeks with strong bench")
        st.write("• **Triple Captain**: For high-scoring players in double gameweeks")
        st.write("• **Free Hit**: For blank gameweeks or one-week punts")
        
        if current_gw < 15:
            st.write("\n**Current Recommendations:**")
            st.write("• Hold wildcard for mid-season fixture swings")
            st.write("• Plan bench boost for first double gameweek")
            st.write("• Save triple captain for premium player in double gameweek")
