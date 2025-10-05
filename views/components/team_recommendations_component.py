"""
Basic Team Recommendations Component - Handles simple team recommendations
"""
import streamlit as st
from utils.error_handling import logger


class TeamRecommendationsComponent:
    """Handles basic team recommendations"""
    
    def render_recommendations(self, team_data):
        """Display recommendations for the team"""
        st.subheader("💡 Team Recommendations")
        
        # Basic recommendations based on available data
        recommendations = []
        
        # Bank analysis
        bank = team_data.get('bank', 0) / 10
        if bank > 2:
            recommendations.append({
                'type': 'info',
                'title': 'Unused Funds',
                'message': f"You have £{bank:.1f}m in the bank. Consider upgrading a player to improve your team."
            })
        
        # Recent performance
        gw_points = team_data.get('summary_event_points', 0)
        if gw_points < 40:
            recommendations.append({
                'type': 'warning',
                'title': 'Low Gameweek Score',
                'message': "Your recent gameweek score was below average. Consider reviewing your captain choice and active players."
            })
        
        # Overall rank
        overall_rank = team_data.get('summary_overall_rank', 0)
        if overall_rank and overall_rank > 1000000:
            recommendations.append({
                'type': 'info',
                'title': 'Rank Improvement',
                'message': "Focus on consistent captain choices and popular template players to improve your rank."
            })
        
        # Display recommendations
        if recommendations:
            for rec in recommendations:
                if rec['type'] == 'success':
                    st.success(f"✅ **{rec['title']}**: {rec['message']}")
                elif rec['type'] == 'warning':
                    st.warning(f"⚠️ **{rec['title']}**: {rec['message']}")
                else:
                    st.info(f"💡 **{rec['title']}**: {rec['message']}")
        else:
            st.success("🎉 Your team looks good! Keep monitoring form and fixtures for optimal transfers.")
        
        # General advice
        st.write("**📚 General FPL Tips:**")
        st.write("• Monitor player form and upcoming fixtures")
        st.write("• Use your free transfer each gameweek")
        st.write("• Plan your chip usage strategically")
        st.write("• Consider differential picks to climb ranks")
        st.write("• Stay active in the transfer market")
