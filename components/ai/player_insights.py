"""
Smart Player Insights Engine
AI-powered analysis and recommendations for FPL players
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class SmartPlayerInsights:
    """AI-powered player analysis and recommendation engine"""
    
    def __init__(self):
        self.position_weights = {
            1: {'points': 0.4, 'saves': 0.3, 'clean_sheets': 0.3},  # Goalkeeper
            2: {'points': 0.3, 'clean_sheets': 0.4, 'assists': 0.3},  # Defender  
            3: {'points': 0.4, 'assists': 0.3, 'goals': 0.3},  # Midfielder
            4: {'points': 0.3, 'goals': 0.5, 'assists': 0.2}   # Forward
        }
        
        self.form_thresholds = {
            'excellent': 8.0,
            'good': 6.0, 
            'average': 4.0,
            'poor': 2.0
        }
    
    def calculate_player_score(self, player_data: pd.Series) -> float:
        """Calculate comprehensive player performance score"""
        
        position = int(player_data.get('element_type', 3))
        weights = self.position_weights.get(position, self.position_weights[3])
        
        # Base score from total points (normalized)
        points_score = min(player_data.get('total_points', 0) / 200, 1.0)
        
        # Form factor (recent performance)
        form_score = min(float(player_data.get('form', 0)) / 10, 1.0)
        
        # Value factor (points per million)
        cost = player_data.get('now_cost', 50) / 10
        if cost > 0:
            value_score = min((player_data.get('total_points', 0) / cost) / 20, 1.0)
        else:
            value_score = 0
        
        # Ownership factor (differential potential)
        ownership = float(player_data.get('selected_by_percent', 50))
        differential_score = 1.0 - (ownership / 100)  # Lower ownership = higher differential
        
        # Playing time factor
        minutes = player_data.get('minutes', 0)
        playing_time_score = min(minutes / 2500, 1.0)  # ~27 games * 90 minutes
        
        # Combine scores with intelligent weighting
        final_score = (
            points_score * 0.3 +
            form_score * 0.25 +
            value_score * 0.2 +
            playing_time_score * 0.15 +
            differential_score * 0.1
        )
        
        return round(final_score * 100, 1)  # Convert to 0-100 scale
    
    def get_player_insights(self, player_data: pd.Series) -> Dict:
        """Generate detailed insights for a specific player"""
        
        insights = {
            'overall_score': self.calculate_player_score(player_data),
            'strengths': [],
            'concerns': [],
            'recommendation': '',
            'form_status': '',
            'value_rating': '',
            'differential_potential': ''
        }
        
        # Analyze form
        form = float(player_data.get('form', 0))
        if form >= self.form_thresholds['excellent']:
            insights['form_status'] = '🔥 Excellent Form'
            insights['strengths'].append('Outstanding recent performances')
        elif form >= self.form_thresholds['good']:
            insights['form_status'] = '✅ Good Form'
            insights['strengths'].append('Consistent recent performances')
        elif form >= self.form_thresholds['average']:
            insights['form_status'] = '⚠️ Average Form'
        else:
            insights['form_status'] = '❌ Poor Form'
            insights['concerns'].append('Struggling for form recently')
        
        # Analyze value
        cost = player_data.get('now_cost', 50) / 10
        points = player_data.get('total_points', 0)
        if cost > 0:
            points_per_million = points / cost
            if points_per_million > 15:
                insights['value_rating'] = '💎 Excellent Value'
                insights['strengths'].append('Outstanding points per million')
            elif points_per_million > 10:
                insights['value_rating'] = '✅ Good Value'
                insights['strengths'].append('Good points per million ratio')
            elif points_per_million > 6:
                insights['value_rating'] = '⚠️ Fair Value'
            else:
                insights['value_rating'] = '❌ Poor Value'
                insights['concerns'].append('Expensive for points returned')
        
        # Analyze ownership/differential potential
        ownership = float(player_data.get('selected_by_percent', 50))
        if ownership < 5:
            insights['differential_potential'] = '🚀 High Differential'
            insights['strengths'].append('Low ownership - high differential potential')
        elif ownership < 15:
            insights['differential_potential'] = '📈 Good Differential'
            insights['strengths'].append('Moderate ownership - good differential')
        elif ownership > 50:
            insights['differential_potential'] = '📊 Template Player'
        else:
            insights['differential_potential'] = '⚖️ Balanced Ownership'
        
        # Generate recommendation
        if insights['overall_score'] >= 80:
            insights['recommendation'] = '🌟 STRONG BUY - Excellent all-around option'
        elif insights['overall_score'] >= 65:
            insights['recommendation'] = '✅ BUY - Good option to consider'
        elif insights['overall_score'] >= 50:
            insights['recommendation'] = '🤔 CONSIDER - Has potential but monitor closely'
        elif insights['overall_score'] >= 35:
            insights['recommendation'] = '⚠️ CAUTION - Several concerns identified'
        else:
            insights['recommendation'] = '❌ AVOID - Too many red flags'
        
        return insights
    
    def get_team_recommendations(self, players_df: pd.DataFrame) -> Dict:
        """Generate team-wide recommendations and insights"""
        
        if players_df.empty:
            return {'recommendations': [], 'team_score': 0, 'balance_analysis': {}}
        
        recommendations = []
        
        # Calculate team score
        player_scores = [self.calculate_player_score(row) for _, row in players_df.iterrows()]
        team_score = round(np.mean(player_scores), 1)
        
        # Position balance analysis
        if 'element_type' in players_df.columns:
            position_counts = players_df['element_type'].value_counts()
            balance_analysis = {
                'goalkeepers': position_counts.get(1, 0),
                'defenders': position_counts.get(2, 0),
                'midfielders': position_counts.get(3, 0),
                'forwards': position_counts.get(4, 0)
            }
            
            # Check for imbalances
            if balance_analysis['defenders'] < 3:
                recommendations.append("⚠️ Consider adding more defensive coverage")
            if balance_analysis['midfielders'] < 3:
                recommendations.append("⚠️ Midfield lacks depth - consider reinforcement")
            if balance_analysis['forwards'] < 1:
                recommendations.append("❌ Need at least one premium forward")
        else:
            balance_analysis = {}
        
        # Form analysis
        if 'form' in players_df.columns:
            poor_form_players = len(players_df[players_df['form'].astype(float) < 4.0])
            if poor_form_players > 2:
                recommendations.append(f"📉 {poor_form_players} players in poor form - consider transfers")
        
        # Value analysis
        if 'now_cost' in players_df.columns and 'total_points' in players_df.columns:
            total_value = players_df['now_cost'].sum() / 10
            total_points = players_df['total_points'].sum()
            
            if total_value > 95:
                recommendations.append("💰 Team value is high - consider budget options")
            
            if total_points / len(players_df) < 80:
                recommendations.append("📊 Average player points below 80 - look for upgrades")
        
        # General recommendations
        if team_score >= 75:
            recommendations.append("🌟 Excellent team composition - minor tweaks only")
        elif team_score >= 60:
            recommendations.append("✅ Solid team foundation - few areas for improvement") 
        elif team_score >= 45:
            recommendations.append("🔧 Team needs significant improvements")
        else:
            recommendations.append("🚨 Major overhaul recommended")
        
        return {
            'recommendations': recommendations,
            'team_score': team_score,
            'balance_analysis': balance_analysis
        }
    
    def find_transfer_targets(self, players_df: pd.DataFrame, budget: float = 15.0, 
                            position: Optional[int] = None) -> List[Dict]:
        """Find optimal transfer targets within budget"""
        
        if players_df.empty:
            return []
        
        # Filter by position if specified
        candidates = players_df.copy()
        if position:
            candidates = candidates[candidates['element_type'] == position]
        
        # Filter by budget
        candidates = candidates[candidates['now_cost'] <= budget * 10]  # Convert to API format
        
        # Calculate scores and sort
        candidates['ai_score'] = candidates.apply(self.calculate_player_score, axis=1)
        top_targets = candidates.nlargest(10, 'ai_score')
        
        transfer_targets = []
        for _, player in top_targets.iterrows():
            insights = self.get_player_insights(player)
            
            transfer_targets.append({
                'name': player.get('web_name', 'Unknown'),
                'cost': player.get('now_cost', 0) / 10,
                'points': player.get('total_points', 0),
                'form': player.get('form', 0),
                'ai_score': insights['overall_score'],
                'recommendation': insights['recommendation'],
                'key_strength': insights['strengths'][0] if insights['strengths'] else 'No specific strengths identified'
            })
        
        return transfer_targets
    
    def render_insights_dashboard(self, players_df: pd.DataFrame):
        """Render AI insights dashboard in Streamlit"""
        
        st.markdown("### 🤖 AI-Powered Player Insights")
        
        if players_df.empty:
            st.warning("Load FPL data to see AI-powered insights!")
            return
        
        # Team overview
        team_insights = self.get_team_recommendations(players_df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Team AI Score", f"{team_insights['team_score']}/100")
        with col2:
            st.metric("Players Analyzed", len(players_df))
        with col3:
            avg_form = players_df['form'].astype(float).mean() if 'form' in players_df.columns else 0
            st.metric("Average Form", f"{avg_form:.1f}/10")
        
        # Recommendations
        if team_insights['recommendations']:
            st.markdown("#### 🎯 AI Recommendations:")
            for rec in team_insights['recommendations'][:5]:
                st.markdown(f"• {rec}")
        
        # Top performers
        if len(players_df) > 0:
            st.markdown("#### ⭐ Top 3 AI-Rated Players:")
            
            players_with_scores = players_df.copy()
            players_with_scores['ai_score'] = players_with_scores.apply(self.calculate_player_score, axis=1)
            top_3 = players_with_scores.nlargest(3, 'ai_score')
            
            for i, (_, player) in enumerate(top_3.iterrows(), 1):
                with st.expander(f"{i}. {player.get('web_name', 'Unknown')} (Score: {player['ai_score']}/100)"):
                    insights = self.get_player_insights(player)
                    
                    st.write(f"**{insights['recommendation']}**")
                    st.write(f"Form: {insights['form_status']}")
                    st.write(f"Value: {insights['value_rating']}")
                    
                    if insights['strengths']:
                        st.write("**Strengths:**")
                        for strength in insights['strengths']:
                            st.write(f"• {strength}")
                    
                    if insights['concerns']:
                        st.write("**Concerns:**")
                        for concern in insights['concerns']:
                            st.write(f"• {concern}")

# Global insights engine
_insights_engine = None

def get_insights_engine():
    """Get the global insights engine instance"""
    global _insights_engine
    if _insights_engine is None:
        _insights_engine = SmartPlayerInsights()
    return _insights_engine
