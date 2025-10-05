"""
Performance Analysis Component - Handles team performance metrics and insights
"""
import streamlit as st
from utils.error_handling import logger


class PerformanceAnalysisComponent:
    """Handles performance analysis display"""
    
    def render_performance_analysis(self, team_data):
        """Display performance analysis"""
        st.subheader("📊 Performance Analysis")
        
        # Basic performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self._render_season_performance(team_data)
        
        with col2:
            self._render_recent_performance(team_data)
        
        with col3:
            self._render_team_value_metrics(team_data)
        
        # Performance insights
        self._render_performance_insights(team_data)
    
    def _render_season_performance(self, team_data):
        """Render season performance metrics"""
        st.write("**📈 Season Performance**")
        total_points = team_data.get('summary_overall_points', 0)
        overall_rank = team_data.get('summary_overall_rank', 0)
        
        current_gw = team_data.get('gameweek', 1)
        avg_points_per_gw = total_points / max(current_gw, 1)
        
        st.metric("Total Points", f"{total_points:,}")
        st.metric("Points/GW", f"{avg_points_per_gw:.1f}")
        st.metric("Overall Rank", f"{overall_rank:,}" if overall_rank else "N/A")
    
    def _render_recent_performance(self, team_data):
        """Render recent performance metrics"""
        st.write("**🎯 Recent Performance**")
        gw_points = team_data.get('summary_event_points', 0)
        gw_rank = team_data.get('summary_event_rank', 0)
        
        # Performance indicators
        avg_gw_points = 50  # League average
        performance = "🔥 Excellent" if gw_points >= 70 else "👍 Good" if gw_points >= avg_gw_points else "📈 Below Average"
        
        st.metric("GW Points", f"{gw_points}")
        st.metric("GW Rank", f"{gw_rank:,}" if gw_rank else "N/A")
        st.metric("Performance", performance)
    
    def _render_team_value_metrics(self, team_data):
        """Render team value metrics"""
        st.write("**💰 Team Value**")
        team_value = team_data.get('value', 1000) / 10
        bank = team_data.get('bank', 0) / 10
        total_budget = team_value + bank
        
        st.metric("Team Value", f"£{team_value:.1f}m")
        st.metric("In Bank", f"£{bank:.1f}m")
        st.metric("Total Budget", f"£{total_budget:.1f}m")
    
    def _render_performance_insights(self, team_data):
        """Render performance insights"""
        st.write("**💡 Performance Insights**")
        
        overall_rank = team_data.get('summary_overall_rank', 0)
        if overall_rank:
            total_players = 8000000  # Approximate
            percentile = (1 - (overall_rank / total_players)) * 100
            
            if percentile >= 90:
                st.success("🏆 Elite performance - Top 10% of all managers!")
            elif percentile >= 75:
                st.info("🥇 Excellent performance - Top 25% of all managers!")
            elif percentile >= 50:
                st.info("👍 Above average performance - Top 50% of all managers")
            else:
                st.warning("📈 Room for improvement - Focus on consistency and transfers")
