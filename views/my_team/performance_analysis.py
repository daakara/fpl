"""
Performance Analysis Component - Analyzes team performance metrics
"""
import streamlit as st
import pandas as pd
from .base_component import BaseTeamComponent


class PerformanceAnalysisComponent(BaseTeamComponent):
    """Component for team performance analysis"""
    
    def render(self, team_data):
        """Render performance analysis"""
        if not self.validate_team_data(team_data):
            st.error("❌ Invalid team data")
            return
        
        try:
            st.subheader("📊 Performance Analysis")
            
            # Overall performance metrics
            self._render_overall_performance(team_data)
            
            # Recent form analysis
            self._render_recent_form(team_data)
            
            # Ranking analysis
            self._render_ranking_analysis(team_data)
            
        except Exception as e:
            self.handle_error(e, "Performance Analysis")
    
    def _render_overall_performance(self, team_data):
        """Render overall performance metrics"""
        try:
            st.write("**Overall Season Performance**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                overall_points = team_data.get('summary_overall_points', 0)
                # Calculate average points per gameweek (assuming current gameweek)
                current_gw = self.get_session_data('my_team_gameweek', 8)
                if isinstance(current_gw, int) and current_gw > 0:
                    avg_points = overall_points / current_gw
                    st.metric(
                        "Points Per GW",
                        f"{avg_points:.1f}",
                        help=f"Average points per gameweek ({overall_points} total points)"
                    )
                else:
                    st.metric("Total Points", f"{overall_points:,}")
            
            with col2:
                overall_rank = team_data.get('summary_overall_rank', 0)
                if overall_rank > 0:
                    # Estimate percentile (rough calculation)
                    total_players = 10000000  # Approximate total FPL players
                    percentile = (1 - (overall_rank / total_players)) * 100
                    st.metric(
                        "Percentile",
                        f"{percentile:.1f}%",
                        help=f"You're in the top {percentile:.1f}% of managers"
                    )
            
            with col3:
                event_points = team_data.get('summary_event_points', 0)
                event_rank = team_data.get('summary_event_rank', 0)
                if event_rank > 0:
                    st.metric(
                        "Latest GW Rank",
                        f"{event_rank:,}",
                        help=f"Gameweek rank for {event_points} points"
                    )
            
        except Exception as e:
            self.logger.error(f"Error rendering overall performance: {str(e)}")
    
    def _render_recent_form(self, team_data):
        """Render recent form analysis"""
        try:
            st.write("**Recent Form Analysis**")
            
            # Get recent gameweek points if available
            event_points = team_data.get('summary_event_points', 0)
            
            if event_points > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Latest Gameweek Performance:**")
                    st.write(f"• Points Scored: {event_points}")
                    
                    # Categorize performance
                    if event_points >= 70:
                        performance = "🔥 Excellent"
                        color = "green"
                    elif event_points >= 50:
                        performance = "✅ Good"
                        color = "blue"
                    elif event_points >= 35:
                        performance = "⚠️ Average"
                        color = "orange"
                    else:
                        performance = "❌ Poor"
                        color = "red"
                    
                    st.markdown(f"• Performance: :{color}[{performance}]")
                
                with col2:
                    # Squad performance insights
                    if self.validate_player_data():
                        squad_insights = self._analyze_squad_performance(team_data)
                        st.write("**Squad Insights:**")
                        for insight in squad_insights:
                            st.write(f"• {insight}")
            else:
                st.info("Recent gameweek data not available")
                
        except Exception as e:
            self.logger.error(f"Error rendering recent form: {str(e)}")
    
    def _render_ranking_analysis(self, team_data):
        """Render ranking analysis"""
        try:
            st.write("**Ranking Analysis**")
            
            overall_rank = team_data.get('summary_overall_rank', 0)
            event_rank = team_data.get('summary_event_rank', 0)
            
            if overall_rank > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Overall Ranking:**")
                    st.write(f"• Current Rank: {overall_rank:,}")
                    
                    # Rank category
                    if overall_rank <= 10000:
                        rank_category = "🏆 Elite (Top 10K)"
                    elif overall_rank <= 100000:
                        rank_category = "⭐ Excellent (Top 100K)"
                    elif overall_rank <= 1000000:
                        rank_category = "✅ Good (Top 1M)"
                    else:
                        rank_category = "📈 Room for Improvement"
                    
                    st.write(f"• Category: {rank_category}")
                
                with col2:
                    if event_rank > 0:
                        st.write("**Latest Gameweek Ranking:**")
                        st.write(f"• GW Rank: {event_rank:,}")
                        
                        # Compare with overall rank
                        if event_rank < overall_rank:
                            trend = "📈 Improving"
                        elif event_rank > overall_rank:
                            trend = "📉 Declining"
                        else:
                            trend = "➡️ Stable"
                        
                        st.write(f"• Trend: {trend}")
                    
        except Exception as e:
            self.logger.error(f"Error rendering ranking analysis: {str(e)}")
    
    def _analyze_squad_performance(self, team_data):
        """Analyze squad performance and return insights"""
        insights = []
        
        try:
            players_df = self.get_session_data('players_df')
            picks = team_data.get('picks', [])
            
            if players_df is None or not picks:
                return ["Squad analysis not available"]
            
            # Get squad data
            squad_players = []
            for pick in picks:
                player = players_df[players_df['id'] == pick.get('element')]
                if not player.empty:
                    squad_players.append(player.iloc[0])
            
            if not squad_players:
                return ["No valid squad data found"]
            
            squad_df = pd.DataFrame(squad_players)
            
            # Analysis insights
            avg_form = squad_df['form'].astype(float).mean()
            insights.append(f"Average team form: {avg_form:.1f}")
            
            # High form players
            high_form = squad_df[squad_df['form'].astype(float) >= 6.0]
            if len(high_form) > 0:
                insights.append(f"{len(high_form)} players in excellent form (6.0+)")
            
            # Captain performance
            captain_pick = next((p for p in picks if p.get('is_captain')), None)
            if captain_pick:
                captain = squad_df[squad_df['id'] == captain_pick.get('element')]
                if not captain.empty:
                    cap_form = float(captain.iloc[0]['form'])
                    if cap_form >= 6.0:
                        insights.append(f"Captain in excellent form ({cap_form})")
                    elif cap_form < 4.0:
                        insights.append(f"Consider captain change (form: {cap_form})")
            
            return insights[:4]  # Return top 4 insights
            
        except Exception as e:
            self.logger.error(f"Error analyzing squad performance: {str(e)}")
            return ["Squad analysis unavailable"]
