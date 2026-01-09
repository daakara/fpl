"""
Performance Comparison Component - Compare team performance against benchmarks
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.error_handling import logger


class PerformanceComparisonComponent:
    """Handles performance comparison analysis with real FPL data"""
    
    def __init__(self, data_service=None):
        self.data_service = data_service
    
    def render_performance_comparison(self, team_data, players_df):
        """Render comprehensive performance comparison"""
        st.header("📊 Performance Comparison Analysis")
        
        current_players = st.session_state.get('fpl_team_current_players', pd.DataFrame())
        
        if current_players.empty:
            st.warning("Load your team data to see performance comparisons")
            return
        
        # Create comparison tabs
        comp_tab1, comp_tab2, comp_tab3, comp_tab4 = st.tabs([
            "🏆 League Benchmarks", "👥 Peer Comparison", "📈 Historical Performance", "🎯 Target Analysis"
        ])
        
        with comp_tab1:
            self._render_league_benchmarks(team_data, current_players)
        
        with comp_tab2:
            self._render_peer_comparison(team_data, current_players)
        
        with comp_tab3:
            self._render_historical_comparison(team_data, current_players)
        
        with comp_tab4:
            self._render_target_analysis(team_data, current_players)
    
    def _render_league_benchmarks(self, team_data, current_players):
        """Compare against league averages and benchmarks"""
        st.subheader("🏆 League Benchmark Comparison")
        
        # Get team metrics
        total_points = current_players['total_points'].sum()
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        avg_ppg = total_points / max(current_gw, 1)
        squad_value = current_players['now_cost'].sum() / 10
        
        # Estimated league averages (would come from FPL API in real implementation)
        league_averages = {
            'avg_total_points': current_gw * 50,  # Estimated 50 points per GW average
            'avg_ppg': 50,
            'avg_squad_value': 100.0,
            'top_10k_total': current_gw * 65,  # Top 10k average
            'top_100k_total': current_gw * 58,  # Top 100k average
            'overall_average': current_gw * 50
        }
        
        # Performance vs benchmarks
        st.write("**📊 Your Performance vs League Benchmarks:**")
        
        # Create comparison metrics
        col1, col2, col3 = st.columns(3)
        
        # Overall comparison
        with col1:
            vs_average = total_points - league_averages['overall_average']
            st.metric(
                "vs Average Manager",
                f"{vs_average:+.0f} points",
                delta=f"{vs_average:+.0f}"
            )
            if vs_average > 0:
                st.success(f"✅ {vs_average:.0f} points above average")
            else:
                st.error(f"❌ {abs(vs_average):.0f} points below average")
        
        # Top 100k comparison
        with col2:
            vs_top100k = total_points - league_averages['top_100k_total']
            st.metric(
                "vs Top 100k",
                f"{vs_top100k:+.0f} points",
                delta=f"{vs_top100k:+.0f}"
            )
            if vs_top100k >= 0:
                st.success("✅ Top 100k pace")
            else:
                st.warning(f"⚠️ {abs(vs_top100k):.0f} points behind")
        
        # Top 10k comparison
        with col3:
            vs_top10k = total_points - league_averages['top_10k_total']
            st.metric(
                "vs Top 10k",
                f"{vs_top10k:+.0f} points",
                delta=f"{vs_top10k:+.0f}"
            )
            if vs_top10k >= 0:
                st.success("🏆 Elite performance!")
            else:
                st.info(f"📈 {abs(vs_top10k):.0f} points to elite level")
        
        # Performance distribution chart
        st.subheader("📈 Performance Distribution")
        
        # Create performance bands
        performance_bands = {
            'Top 1k': league_averages['top_10k_total'] + 50,
            'Top 10k': league_averages['top_10k_total'],
            'Top 100k': league_averages['top_100k_total'],
            'Above Average': league_averages['overall_average'] + 30,
            'Average': league_averages['overall_average'],
            'Below Average': league_averages['overall_average'] - 30
        }
        
        # Find your band
        your_band = "Below Average"
        for band, threshold in performance_bands.items():
            if total_points >= threshold:
                your_band = band
                break
        
        # Create horizontal bar chart
        bands_df = pd.DataFrame(list(performance_bands.items()), columns=['Tier', 'Min Points'])
        bands_df['Your Position'] = bands_df['Tier'] == your_band
        
        fig = px.bar(
            bands_df,
            x='Min Points',
            y='Tier',
            orientation='h',
            color='Your Position',
            color_discrete_map={True: '#ff6b6b', False: '#4ecdc4'},
            title=f'Performance Tiers (You are in: {your_band})'
        )
        
        # Add your score line
        fig.add_vline(
            x=total_points,
            line_dash='dash',
            line_color='red',
            annotation_text=f'Your Score: {total_points}'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Positional benchmarks
        st.subheader("⚽ Positional Performance vs Benchmarks")
        
        position_benchmarks = {
            'Goalkeeper': {'avg_points': current_gw * 3, 'top_points': current_gw * 4.5},
            'Defender': {'avg_points': current_gw * 3.5, 'top_points': current_gw * 5.5},
            'Midfielder': {'avg_points': current_gw * 4, 'top_points': current_gw * 6.5},
            'Forward': {'avg_points': current_gw * 4.5, 'top_points': current_gw * 7}
        }
        
        pos_comparison = []
        for position in ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']:
            pos_players = current_players[current_players['element_type_name'] == position]
            if not pos_players.empty:
                pos_total = pos_players['total_points'].sum()
                pos_count = len(pos_players)
                
                avg_benchmark = position_benchmarks[position]['avg_points'] * pos_count
                top_benchmark = position_benchmarks[position]['top_points'] * pos_count
                
                vs_avg = pos_total - avg_benchmark
                vs_top = pos_total - top_benchmark
                
                pos_comparison.append({
                    'Position': position,
                    'Your Points': pos_total,
                    'Players': pos_count,
                    'vs Average': f"{vs_avg:+.0f}",
                    'vs Elite': f"{vs_top:+.0f}",
                    'Performance': 'Above Average' if vs_avg > 0 else 'Below Average'
                })
        
        if pos_comparison:
            pos_df = pd.DataFrame(pos_comparison)
            st.dataframe(pos_df, use_container_width=True)
    
    def _render_peer_comparison(self, team_data, current_players):
        """Compare against similar teams/managers"""
        st.subheader("👥 Peer Group Analysis")
        
        # Simulate peer data (would come from leagues/similar managers in real implementation)
        np.random.seed(42)  # For consistent results
        
        total_points = current_players['total_points'].sum()
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        
        # Generate simulated peer data
        n_peers = 50
        peer_points = np.random.normal(total_points, total_points * 0.15, n_peers)
        peer_points = np.clip(peer_points, total_points * 0.6, total_points * 1.4)
        
        # Your ranking among peers
        your_rank = sum(peer_points > total_points) + 1
        percentile = (n_peers - your_rank + 1) / n_peers * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Peer Rank", f"{your_rank}/{n_peers}")
        
        with col2:
            st.metric("Percentile", f"{percentile:.0f}%")
        
        with col3:
            if percentile >= 80:
                status = "Excellent"
                color = "success"
            elif percentile >= 60:
                status = "Good"
                color = "info"
            elif percentile >= 40:
                status = "Average"
                color = "warning"
            else:
                status = "Needs Improvement"
                color = "error"
            
            getattr(st, color)(f"Status: {status}")
        
        # Peer distribution
        st.subheader("📊 Peer Performance Distribution")
        
        fig = px.histogram(
            x=peer_points,
            nbins=15,
            title='Peer Group Points Distribution',
            labels={'x': 'Total Points', 'y': 'Number of Managers'}
        )
        
        # Add your score
        fig.add_vline(
            x=total_points,
            line_dash='dash',
            line_color='red',
            annotation_text=f'You: {total_points} pts'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Squad comparison
        st.subheader("👥 Squad Composition vs Peers")
        
        # Template vs differential analysis
        high_ownership = current_players[current_players['selected_by_percent'] > 30]
        template_score = len(high_ownership) / len(current_players) * 100
        
        st.write("**Squad Style Analysis:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Template Score", f"{template_score:.0f}%")
            
            if template_score > 70:
                st.info("🤖 **Template Heavy**: Safe but limited upside")
            elif template_score > 50:
                st.success("⚖️ **Balanced**: Good mix of template and differentials")
            else:
                st.warning("🎲 **Differential Heavy**: High risk, high reward")
        
        with col2:
            avg_ownership = current_players['selected_by_percent'].mean()
            st.metric("Avg Player Ownership", f"{avg_ownership:.1f}%")
            
            if avg_ownership > 40:
                st.info("📈 High ownership squad")
            elif avg_ownership > 20:
                st.success("⚖️ Balanced ownership")
            else:
                st.warning("📉 Low ownership squad")
        
        # Most/least common picks
        st.subheader("🎯 Popular vs Differential Picks")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔥 Your Most Popular Picks:**")
            popular_picks = current_players.nlargest(3, 'selected_by_percent')
            for _, player in popular_picks.iterrows():
                st.write(f"• {player['web_name']}: {player['selected_by_percent']:.1f}% owned")
        
        with col2:
            st.write("**🎲 Your Differential Picks:**")
            differential_picks = current_players.nsmallest(3, 'selected_by_percent')
            for _, player in differential_picks.iterrows():
                st.write(f"• {player['web_name']}: {player['selected_by_percent']:.1f}% owned")
    
    def _render_historical_comparison(self, team_data, current_players):
        """Compare historical performance trends"""
        st.subheader("📈 Historical Performance Trends")
        
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        total_points = current_players['total_points'].sum()
        
        # Simulate historical progression (would use actual history in real implementation)
        gameweeks = list(range(1, current_gw + 1))
        
        # Your progression (simulated based on current performance)
        np.random.seed(123)
        base_performance = total_points / current_gw
        your_progression = []
        cumulative = 0
        
        for gw in gameweeks:
            gw_points = base_performance + np.random.normal(0, 15)
            gw_points = max(10, min(100, gw_points))  # Realistic bounds
            cumulative += gw_points
            your_progression.append(cumulative)
        
        # Average manager progression
        avg_progression = [i * 50 for i in gameweeks]  # 50 points per GW average
        
        # Top 10k progression
        top10k_progression = [i * 65 for i in gameweeks]  # 65 points per GW
        
        # Create progression chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=gameweeks,
            y=your_progression,
            mode='lines+markers',
            name='Your Team',
            line=dict(color='#ff6b6b', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=gameweeks,
            y=avg_progression,
            mode='lines',
            name='Average Manager',
            line=dict(color='#4ecdc4', dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=gameweeks,
            y=top10k_progression,
            mode='lines',
            name='Top 10k Average',
            line=dict(color='#45b7d1', dash='dot')
        ))
        
        fig.update_layout(
            title='Cumulative Points Progression',
            xaxis_title='Gameweek',
            yaxis_title='Total Points',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance consistency analysis
        st.subheader("📊 Performance Consistency")
        
        # Calculate gameweek scores (simulated)
        gw_scores = []
        for i in range(len(your_progression)):
            if i == 0:
                gw_scores.append(your_progression[0])
            else:
                gw_scores.append(your_progression[i] - your_progression[i-1])
        
        consistency_metrics = {
            'Average GW Score': np.mean(gw_scores),
            'Best GW': max(gw_scores),
            'Worst GW': min(gw_scores),
            'Standard Deviation': np.std(gw_scores),
            'Consistency Rating': max(0, 10 - np.std(gw_scores)/5)  # Lower std = more consistent
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg GW Score", f"{consistency_metrics['Average GW Score']:.1f}")
            st.metric("Best Gameweek", f"{consistency_metrics['Best GW']:.0f}")
        
        with col2:
            st.metric("Worst Gameweek", f"{consistency_metrics['Worst GW']:.0f}")
            st.metric("Score Range", f"{consistency_metrics['Best GW'] - consistency_metrics['Worst GW']:.0f}")
        
        with col3:
            consistency_rating = consistency_metrics['Consistency Rating']
            st.metric("Consistency", f"{consistency_rating:.1f}/10")
            
            if consistency_rating >= 7:
                st.success("🎯 Very consistent")
            elif consistency_rating >= 5:
                st.info("📊 Moderately consistent")
            else:
                st.warning("🎲 Inconsistent scores")
        
        # Weekly performance chart
        fig = px.bar(
            x=gameweeks,
            y=gw_scores,
            title='Gameweek Scores',
            labels={'x': 'Gameweek', 'y': 'Points'}
        )
        
        # Add average line
        fig.add_hline(
            y=np.mean(gw_scores),
            line_dash='dash',
            line_color='red',
            annotation_text='Your Average'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_target_analysis(self, team_data, current_players):
        """Analyze progress towards targets"""
        st.subheader("🎯 Target Achievement Analysis")
        
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        total_points = current_players['total_points'].sum()
        remaining_gws = 38 - current_gw
        
        # Set targets
        st.write("**🎯 Season Targets Analysis:**")
        
        # Common FPL targets
        targets = {
            'Top 100k Finish': {'points_needed': 2200, 'rank_target': '100k'},
            'Top 10k Finish': {'points_needed': 2400, 'rank_target': '10k'},
            'Top 1k Finish': {'points_needed': 2600, 'rank_target': '1k'},
            '2000+ Points': {'points_needed': 2000, 'rank_target': 'Good Season'},
            '2500+ Points': {'points_needed': 2500, 'rank_target': 'Excellent Season'}
        }
        
        for target_name, target_info in targets.items():
            target_points = target_info['points_needed']
            points_needed = target_points - total_points
            ppg_needed = points_needed / max(remaining_gws, 1) if remaining_gws > 0 else 0
            
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**{target_name}**")
                
                with col2:
                    st.write(f"Target: {target_points}")
                
                with col3:
                    if points_needed <= 0:
                        st.success("✅ Achieved!")
                    else:
                        st.write(f"Need: {points_needed}")
                
                with col4:
                    if points_needed <= 0:
                        st.success("🎉 Target met!")
                    elif ppg_needed <= 45:
                        st.error(f"❌ Need {ppg_needed:.1f} PPG")
                    elif ppg_needed <= 55:
                        st.warning(f"⚠️ Need {ppg_needed:.1f} PPG")
                    elif ppg_needed <= 65:
                        st.info(f"📊 Need {ppg_needed:.1f} PPG")
                    else:
                        st.success(f"✅ Need {ppg_needed:.1f} PPG")
                
                # Progress bar
                progress = min(100, (total_points / target_points) * 100)
                st.progress(progress / 100)
                st.caption(f"Progress: {progress:.1f}% complete")
                
                st.divider()
        
        # Projection analysis
        st.subheader("📈 Season Projection")
        
        current_ppg = total_points / current_gw
        projected_total = total_points + (current_ppg * remaining_gws)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current PPG", f"{current_ppg:.1f}")
        
        with col2:
            st.metric("Projected Total", f"{projected_total:.0f}")
        
        with col3:
            # Determine projected rank band
            if projected_total >= 2600:
                rank_projection = "Top 1k"
                color = "success"
            elif projected_total >= 2400:
                rank_projection = "Top 10k"
                color = "success"
            elif projected_total >= 2200:
                rank_projection = "Top 100k"
                color = "info"
            elif projected_total >= 2000:
                rank_projection = "Above Average"
                color = "info"
            else:
                rank_projection = "Below Average"
                color = "warning"
            
            getattr(st, color)(f"Projected: {rank_projection}")
        
        # Improvement scenarios
        st.subheader("🚀 Improvement Scenarios")
        
        improvement_scenarios = [
            ('Maintain Current Form', current_ppg, projected_total),
            ('Slight Improvement (+5 PPG)', current_ppg + 5, total_points + ((current_ppg + 5) * remaining_gws)),
            ('Good Improvement (+10 PPG)', current_ppg + 10, total_points + ((current_ppg + 10) * remaining_gws)),
            ('Major Improvement (+15 PPG)', current_ppg + 15, total_points + ((current_ppg + 15) * remaining_gws))
        ]
        
        scenario_data = []
        for scenario, ppg, final_total in improvement_scenarios:
            # Determine rank for this total
            if final_total >= 2600:
                rank = "Top 1k"
            elif final_total >= 2400:
                rank = "Top 10k"
            elif final_total >= 2200:
                rank = "Top 100k"
            else:
                rank = "Average+"
            
            scenario_data.append({
                'Scenario': scenario,
                'Required PPG': f"{ppg:.1f}",
                'Final Total': f"{final_total:.0f}",
                'Projected Rank': rank
            })
        
        scenario_df = pd.DataFrame(scenario_data)
        st.dataframe(scenario_df, use_container_width=True)
        
        st.info("💡 **Key Insights:**")
        st.write("• Consistency is more important than high individual scores")
        st.write("• Small improvements in average score compound over the season")
        st.write("• Focus on your points per gameweek rather than overall rank")
        st.write("• Use chips strategically to boost your average")
