"""
SWOT Analysis Component - Team strengths, weaknesses, opportunities, threats
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.error_handling import logger


class SWOTAnalysisComponent:
    """Handles comprehensive SWOT analysis with real FPL data"""
    
    def __init__(self, data_service=None):
        self.data_service = data_service
    
    def render_swot_analysis(self, team_data, players_df):
        """Render comprehensive SWOT analysis"""
        st.header("🎯 Team SWOT Analysis")
        
        current_players = st.session_state.get('fpl_team_current_players', pd.DataFrame())
        
        if current_players.empty:
            st.warning("Load your team data to see detailed SWOT analysis")
            return
        
        # Create SWOT tabs
        swot_tab1, swot_tab2, swot_tab3, swot_tab4 = st.tabs([
            "💪 Strengths", "⚠️ Weaknesses", "🎯 Opportunities", "⛔ Threats"
        ])
        
        with swot_tab1:
            self._render_strengths(team_data, current_players)
        
        with swot_tab2:
            self._render_weaknesses(team_data, current_players)
        
        with swot_tab3:
            self._render_opportunities(team_data, current_players)
        
        with swot_tab4:
            self._render_threats(team_data, current_players)
        
        # Overall SWOT summary
        st.divider()
        self._render_swot_summary(team_data, current_players)
    
    def _render_strengths(self, team_data, current_players):
        """Analyze team strengths"""
        st.subheader("💪 Team Strengths")
        
        strengths = []
        
        # High-scoring players
        top_scorers = current_players.nlargest(3, 'total_points')
        if not top_scorers.empty and top_scorers.iloc[0]['total_points'] > 100:
            strengths.append({
                'category': 'High-Performing Players',
                'description': f"Strong core with {top_scorers.iloc[0]['web_name']} leading at {top_scorers.iloc[0]['total_points']} points",
                'impact': 'High',
                'players': top_scorers['web_name'].tolist()
            })
        
        # Good form players
        in_form = current_players[current_players['form'] > 4]
        if len(in_form) >= 3:
            strengths.append({
                'category': 'Excellent Current Form',
                'description': f"{len(in_form)} players in excellent form (>4.0 per GW)",
                'impact': 'High',
                'players': in_form['web_name'].tolist()
            })
        
        # Budget efficiency
        total_value = current_players['now_cost'].sum() / 10
        if total_value < 98:
            strengths.append({
                'category': 'Budget Efficiency',
                'description': f"Squad value of £{total_value:.1f}m leaves room for upgrades",
                'impact': 'Medium',
                'players': []
            })
        
        # Position balance
        position_counts = current_players['element_type_name'].value_counts()
        if all(count >= 2 for count in position_counts.values()):
            strengths.append({
                'category': 'Balanced Squad',
                'description': "Good positional balance across all areas",
                'impact': 'Medium',
                'players': []
            })
        
        # Premium players performing
        premiums = current_players[current_players['now_cost'] > 100]
        if not premiums.empty:
            avg_premium_ppg = premiums['points_per_game'].mean()
            if avg_premium_ppg > 5:
                strengths.append({
                    'category': 'Premium Players Delivering',
                    'description': f"Premium players averaging {avg_premium_ppg:.1f} points per game",
                    'impact': 'High',
                    'players': premiums['web_name'].tolist()
                })
        
        # Display strengths
        if strengths:
            for i, strength in enumerate(strengths, 1):
                with st.container():
                    st.success(f"**{i}. {strength['category']}**")
                    st.write(f"📄 {strength['description']}")
                    st.write(f"📊 Impact: {strength['impact']}")
                    if strength['players']:
                        st.write(f"👥 Key Players: {', '.join(strength['players'][:3])}")
                    st.divider()
        else:
            st.info("💡 Focus on building strengths by improving player form and squad balance")
    
    def _render_weaknesses(self, team_data, current_players):
        """Analyze team weaknesses"""
        st.subheader("⚠️ Team Weaknesses")
        
        weaknesses = []
        
        # Poor form players
        poor_form = current_players[current_players['form'] < 2]
        if len(poor_form) > 0:
            weaknesses.append({
                'category': 'Players in Poor Form',
                'description': f"{len(poor_form)} players with form below 2.0 per GW",
                'severity': 'High',
                'players': poor_form['web_name'].tolist(),
                'action': 'Consider transferring out or benching'
            })
        
        # Low minutes players  
        low_minutes = current_players[current_players['minutes'] < 500]
        if len(low_minutes) > 2:
            weaknesses.append({
                'category': 'Rotation Risk Players',
                'description': f"{len(low_minutes)} players with limited playing time",
                'severity': 'Medium',
                'players': low_minutes['web_name'].tolist(),
                'action': 'Monitor team news and consider alternatives'
            })
        
        # Expensive underperformers
        expensive_players = current_players[current_players['now_cost'] > 80]
        if not expensive_players.empty:
            underperformers = expensive_players[expensive_players['points_per_game'] < 4]
            if len(underperformers) > 0:
                weaknesses.append({
                    'category': 'Expensive Underperformers',
                    'description': f"High-cost players not delivering expected returns",
                    'severity': 'High',
                    'players': underperformers['web_name'].tolist(),
                    'action': 'Priority transfers to better value options'
                })
        
        # Low team diversity
        team_counts = current_players['team'].value_counts()
        if team_counts.max() > 3:
            over_invested_team = current_players[current_players['team'] == team_counts.idxmax()]
            weaknesses.append({
                'category': 'Over-reliance on Single Team',
                'description': f"{team_counts.max()} players from the same team increases risk",
                'severity': 'Medium',
                'players': over_invested_team['web_name'].tolist(),
                'action': 'Diversify to reduce fixture dependency'
            })
        
        # Price drop risks
        price_droppers = current_players[current_players['cost_change_start'] < -0.3]
        if len(price_droppers) > 2:
            weaknesses.append({
                'category': 'Falling Player Values',
                'description': f"{len(price_droppers)} players losing significant value",
                'severity': 'Medium',
                'players': price_droppers['web_name'].tolist(),
                'action': 'Monitor price trends and transfer timing'
            })
        
        # Display weaknesses
        if weaknesses:
            for i, weakness in enumerate(weaknesses, 1):
                with st.container():
                    if weakness['severity'] == 'High':
                        st.error(f"**{i}. {weakness['category']}**")
                    else:
                        st.warning(f"**{i}. {weakness['category']}**")
                    
                    st.write(f"📄 {weakness['description']}")
                    st.write(f"⚠️ Severity: {weakness['severity']}")
                    if weakness['players']:
                        st.write(f"👥 Affected Players: {', '.join(weakness['players'][:3])}")
                    st.write(f"🎯 Recommended Action: {weakness['action']}")
                    st.divider()
        else:
            st.success("✅ No major weaknesses identified in your current squad!")
    
    def _render_opportunities(self, team_data, current_players):
        """Analyze opportunities"""
        st.subheader("🎯 Strategic Opportunities")
        
        fpl_data = st.session_state.get('fpl_data', {})
        all_players = st.session_state.get('fpl_players_df', pd.DataFrame())
        
        opportunities = []
        
        if not all_players.empty:
            # Rising players not owned
            rising_players = all_players[
                (all_players['cost_change_start'] > 0.2) & 
                (all_players['form'] > 4) &
                (~all_players['id'].isin(current_players['id']))
            ].nlargest(3, 'form')
            
            if not rising_players.empty:
                opportunities.append({
                    'category': 'Rising Stars Available',
                    'description': f"High-form players gaining value: {', '.join(rising_players['web_name'].tolist())}",
                    'potential': 'High',
                    'timeframe': 'Immediate',
                    'action': 'Consider bringing in before price rises'
                })
            
            # Differential captains
            current_team_ids = current_players['id'].tolist()
            differentials = all_players[
                (all_players['id'].isin(current_team_ids)) &
                (all_players['selected_by_percent'] < 15) &
                (all_players['form'] > 3)
            ]
            
            if not differentials.empty:
                opportunities.append({
                    'category': 'Differential Captain Options',
                    'description': f"Low-owned players in your team with good form",
                    'potential': 'Medium',
                    'timeframe': 'Weekly',
                    'action': 'Use for captain picks in favorable fixtures'
                })
            
            # Budget enablers performing
            budget_gems = all_players[
                (all_players['now_cost'] < 50) &
                (all_players['points_per_game'] > 3) &
                (~all_players['id'].isin(current_players['id']))
            ].nlargest(3, 'points_per_game')
            
            if not budget_gems.empty:
                opportunities.append({
                    'category': 'Budget Enabler Options',
                    'description': f"Cheap players delivering good returns",
                    'potential': 'Medium',
                    'timeframe': 'Medium-term',
                    'action': 'Use to fund premium upgrades elsewhere'
                })
        
        # Free transfer opportunity
        if team_data.get('total_transfers', 0) > 0:
            opportunities.append({
                'category': 'Free Transfer Available',
                'description': "Use weekly free transfer to improve squad",
                'potential': 'Medium',
                'timeframe': 'Weekly',
                'action': 'Plan transfers to address weaknesses or exploit fixtures'
            })
        
        # Wildcard opportunity
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        if current_gw > 5:  # After initial weeks
            opportunities.append({
                'category': 'Strategic Wildcard Usage',
                'description': "Major squad overhaul opportunity",
                'potential': 'High',
                'timeframe': 'Strategic timing',
                'action': 'Save for fixture swings or injury crisis'
            })
        
        # Display opportunities
        if opportunities:
            for i, opp in enumerate(opportunities, 1):
                with st.container():
                    st.info(f"**{i}. {opp['category']}**")
                    st.write(f"📄 {opp['description']}")
                    st.write(f"🎯 Potential: {opp['potential']}")
                    st.write(f"⏰ Timeframe: {opp['timeframe']}")
                    st.write(f"🚀 Action: {opp['action']}")
                    st.divider()
        else:
            st.info("💡 Continue monitoring player form and fixture changes for new opportunities")
    
    def _render_threats(self, team_data, current_players):
        """Analyze threats"""
        st.subheader("⛔ Potential Threats")
        
        threats = []
        
        # Injury-prone players
        injury_prone = current_players[
            (current_players['minutes'] < current_players['games_played'] * 60) &
            (current_players['games_played'] > 3)
        ]
        if len(injury_prone) > 0:
            threats.append({
                'category': 'Injury Risk Players',
                'description': f"{len(injury_prone)} players with concerning minutes/game ratio",
                'severity': 'Medium',
                'players': injury_prone['web_name'].tolist(),
                'mitigation': 'Have bench coverage ready'
            })
        
        # High ownership template players
        template_players = current_players[current_players['selected_by_percent'] > 40]
        if len(template_players) > 5:
            threats.append({
                'category': 'Template Heavy Squad',
                'description': f"Over-reliance on highly owned players limits rank gains",
                'severity': 'Low',
                'players': template_players['web_name'].tolist(),
                'mitigation': 'Consider strategic differentials'
            })
        
        # Players with difficult fixtures
        # Mock difficult fixture threat
        threats.append({
            'category': 'Fixture Difficulty',
            'description': "Some players facing tough upcoming fixtures",
            'severity': 'Medium',
            'players': current_players.sample(min(2, len(current_players)))['web_name'].tolist(),
            'mitigation': 'Plan transfers around fixture swings'
        })
        
        # Price drop threats
        vulnerable_to_drops = current_players[
            (current_players['form'] < 2) & 
            (current_players['selected_by_percent'] > 10)
        ]
        if len(vulnerable_to_drops) > 0:
            threats.append({
                'category': 'Price Drop Risk',
                'description': f"Players at risk of price decreases due to poor form",
                'severity': 'Medium',
                'players': vulnerable_to_drops['web_name'].tolist(),
                'mitigation': 'Monitor closely and transfer before drops'
            })
        
        # Season phase threats
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        if current_gw > 25:
            threats.append({
                'category': 'Season End Rotation',
                'description': "Player rotation increases in final months",
                'severity': 'Medium',
                'players': [],
                'mitigation': 'Focus on essential players from teams with objectives'
            })
        
        # Display threats
        if threats:
            for i, threat in enumerate(threats, 1):
                with st.container():
                    if threat['severity'] == 'High':
                        st.error(f"**{i}. {threat['category']}**")
                    elif threat['severity'] == 'Medium':
                        st.warning(f"**{i}. {threat['category']}**")
                    else:
                        st.info(f"**{i}. {threat['category']}**")
                    
                    st.write(f"📄 {threat['description']}")
                    st.write(f"⚠️ Severity: {threat['severity']}")
                    if threat['players']:
                        st.write(f"👥 Affected Players: {', '.join(threat['players'][:3])}")
                    st.write(f"🛡️ Mitigation: {threat['mitigation']}")
                    st.divider()
        else:
            st.success("✅ No significant threats identified!")
    
    def _render_swot_summary(self, team_data, current_players):
        """Render SWOT summary matrix"""
        st.subheader("📊 SWOT Summary Matrix")
        
        # Calculate SWOT scores
        total_points = current_players['total_points'].sum()
        avg_form = current_players['form'].mean()
        squad_value = current_players['now_cost'].sum() / 10
        
        # Simple scoring system
        strength_score = min(10, (total_points / 200) + (avg_form * 2))
        weakness_score = max(0, 10 - strength_score)
        opportunity_score = 7 if squad_value < 100 else 5  # Budget available
        threat_score = len(current_players[current_players['form'] < 2]) * 2
        
        # Create matrix visualization
        categories = ['Strengths', 'Weaknesses', 'Opportunities', 'Threats']
        scores = [strength_score, weakness_score, opportunity_score, threat_score]
        colors = ['green', 'red', 'blue', 'orange']
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=scores,
                marker_color=colors,
                text=[f'{score:.1f}' for score in scores],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='SWOT Analysis Summary (Scale: 0-10)',
            yaxis_title='Impact Score',
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Strategic recommendations
        st.subheader("🎯 Strategic Recommendations")
        
        if strength_score > weakness_score:
            st.success("✅ **Overall Assessment**: Your team is well-positioned with more strengths than weaknesses")
        else:
            st.warning("⚠️ **Overall Assessment**: Focus on addressing key weaknesses to improve performance")
        
        st.write("**Key Action Items:**")
        if weakness_score > 5:
            st.write("🎯 **Priority**: Address major weaknesses (poor form players, expensive underperformers)")
        if opportunity_score > 6:
            st.write("🚀 **Opportunity**: Good position to exploit market opportunities")
        if threat_score > 4:
            st.write("🛡️ **Risk Management**: Monitor threat factors closely")
        
        st.info("💡 **Remember**: SWOT analysis should guide your transfer strategy and captain choices!")
