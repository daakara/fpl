"""
Advanced Analytics Component - Deep statistical analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.error_handling import logger


class AdvancedAnalyticsComponent:
    """Handles advanced statistical analysis with real FPL data"""
    
    def __init__(self, data_service=None):
        self.data_service = data_service
    
    def render_advanced_analytics(self, team_data, players_df):
        """Render comprehensive advanced analytics"""
        st.header("📈 Advanced Team Analytics")
        
        current_players = st.session_state.get('fpl_team_current_players', pd.DataFrame())
        
        if current_players.empty:
            st.warning("Load your team data to see advanced analytics")
            return
        
        # Create analytics tabs
        analytics_tab1, analytics_tab2, analytics_tab3, analytics_tab4 = st.tabs([
            "📊 Performance Metrics", "🎯 Efficiency Analysis", "📈 Trend Analysis", "🔮 Predictive Models"
        ])
        
        with analytics_tab1:
            self._render_performance_metrics(team_data, current_players)
        
        with analytics_tab2:
            self._render_efficiency_analysis(team_data, current_players)
        
        with analytics_tab3:
            self._render_trend_analysis(team_data, current_players)
        
        with analytics_tab4:
            self._render_predictive_models(team_data, current_players)
    
    def _render_performance_metrics(self, team_data, current_players):
        """Render detailed performance metrics"""
        st.subheader("📊 Comprehensive Performance Metrics")
        
        # Key metrics calculation
        total_points = current_players['total_points'].sum()
        current_gw = st.session_state.get('fpl_team_gameweek', 8)
        avg_ppg = total_points / max(current_gw, 1)
        squad_value = current_players['now_cost'].sum() / 10
        
        # Advanced metrics
        points_per_million = total_points / squad_value if squad_value > 0 else 0
        form_score = current_players['form'].mean()
        consistency_score = 10 - current_players['form'].std()  # Lower std = more consistent
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Points", f"{total_points:,}")
            st.metric("Points/GW", f"{avg_ppg:.1f}")
        
        with col2:
            st.metric("Squad Value", f"£{squad_value:.1f}m")
            st.metric("Points/£m", f"{points_per_million:.1f}")
        
        with col3:
            st.metric("Team Form", f"{form_score:.1f}")
            st.metric("Consistency", f"{consistency_score:.1f}/10")
        
        with col4:
            bank = team_data.get('bank', 0) / 10
            st.metric("Available Funds", f"£{bank:.1f}m")
            total_value = squad_value + bank
            st.metric("Total Budget", f"£{total_value:.1f}m")
        
        # Performance distribution
        st.subheader("🎯 Player Performance Distribution")
        
        # Create performance categories
        current_players['performance_category'] = pd.cut(
            current_players['points_per_game'],
            bins=[0, 3, 5, 7, float('inf')],
            labels=['Below Average', 'Average', 'Good', 'Excellent']
        )
        
        perf_dist = current_players['performance_category'].value_counts()
        
        fig = px.pie(
            values=perf_dist.values,
            names=perf_dist.index,
            title="Player Performance Distribution (Points per Game)",
            color_discrete_map={
                'Below Average': '#ff7f7f',
                'Average': '#ffbf7f',
                'Good': '#7fbfff',
                'Excellent': '#7fff7f'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Position analysis
        st.subheader("⚽ Positional Analysis")
        
        pos_analysis = current_players.groupby('element_type_name').agg({
            'total_points': ['sum', 'mean'],
            'now_cost': 'sum',
            'form': 'mean'
        }).round(1)
        
        pos_analysis.columns = ['Total Points', 'Avg Points', 'Total Cost (0.1m)', 'Avg Form']
        pos_analysis['Total Cost (£m)'] = pos_analysis['Total Cost (0.1m)'] / 10
        pos_analysis = pos_analysis.drop('Total Cost (0.1m)', axis=1)
        
        st.dataframe(pos_analysis, use_container_width=True)
        
        # Performance vs Cost scatter
        st.subheader("💰 Value for Money Analysis")
        
        fig = px.scatter(
            current_players,
            x='now_cost',
            y='total_points',
            color='element_type_name',
            size='form',
            hover_data=['web_name', 'points_per_game'],
            title='Player Value vs Performance',
            labels={
                'now_cost': 'Cost (0.1m)',
                'total_points': 'Total Points'
            }
        )
        
        # Add trend line
        z = np.polyfit(current_players['now_cost'], current_players['total_points'], 1)
        p = np.poly1d(z)
        fig.add_traces(go.Scatter(
            x=current_players['now_cost'],
            y=p(current_players['now_cost']),
            mode='lines',
            name='Trend Line',
            line=dict(dash='dash', color='red')
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_efficiency_analysis(self, team_data, current_players):
        """Render efficiency analysis"""
        st.subheader("🎯 Team Efficiency Analysis")
        
        # Calculate efficiency metrics
        current_players['efficiency'] = current_players['total_points'] / (current_players['now_cost'] / 10)
        current_players['form_efficiency'] = current_players['form'] / (current_players['now_cost'] / 10)
        
        # Top efficient players
        st.write("**Most Efficient Players (Points per £m):**")
        top_efficient = current_players.nlargest(5, 'efficiency')[['web_name', 'efficiency', 'total_points', 'now_cost']]
        top_efficient['now_cost'] = top_efficient['now_cost'] / 10
        top_efficient.columns = ['Player', 'Points per £m', 'Total Points', 'Cost (£m)']
        
        st.dataframe(top_efficient, use_container_width=True)
        
        # Efficiency distribution
        fig = px.histogram(
            current_players,
            x='efficiency',
            nbins=10,
            title='Team Efficiency Distribution (Points per £m)',
            color_discrete_sequence=['skyblue']
        )
        
        fig.add_vline(
            x=current_players['efficiency'].mean(),
            line_dash='dash',
            line_color='red',
            annotation_text='Team Average'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Positional efficiency comparison
        st.subheader("⚽ Positional Efficiency Comparison")
        
        pos_efficiency = current_players.groupby('element_type_name').agg({
            'efficiency': 'mean',
            'form_efficiency': 'mean',
            'total_points': 'sum',
            'now_cost': 'sum'
        }).round(2)
        
        pos_efficiency['total_cost_m'] = pos_efficiency['now_cost'] / 10
        pos_efficiency = pos_efficiency.drop('now_cost', axis=1)
        pos_efficiency.columns = ['Avg Efficiency', 'Form Efficiency', 'Total Points', 'Total Cost (£m)']
        
        # Create efficiency comparison chart
        fig = px.bar(
            x=pos_efficiency.index,
            y=pos_efficiency['Avg Efficiency'],
            title='Average Efficiency by Position (Points per £m)',
            color=pos_efficiency['Avg Efficiency'],
            color_continuous_scale='Viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Budget allocation analysis
        st.subheader("💰 Budget Allocation Analysis")
        
        budget_analysis = current_players.groupby('element_type_name')['now_cost'].sum() / 10
        total_budget = budget_analysis.sum()
        budget_pct = (budget_analysis / total_budget * 100).round(1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=budget_analysis.values,
                names=budget_analysis.index,
                title='Budget Allocation by Position (£m)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Budget Breakdown:**")
            for pos, amount in budget_analysis.items():
                pct = budget_pct[pos]
                st.write(f"• {pos}: £{amount:.1f}m ({pct:.1f}%)")
            
            st.write(f"\n**Total Spent:** £{total_budget:.1f}m")
            bank = team_data.get('bank', 0) / 10
            st.write(f"**Available:** £{bank:.1f}m")
            
            # Efficiency recommendations
            st.info("💡 **Efficiency Tips:**")
            if budget_pct.get('Forward', 0) > 35:
                st.write("• Consider cheaper forwards to fund midfield")
            if budget_pct.get('Defender', 0) < 20:
                st.write("• Invest more in attacking defenders")
    
    def _render_trend_analysis(self, team_data, current_players):
        """Render trend analysis"""
        st.subheader("📈 Performance Trend Analysis")
        
        # Form trend analysis
        st.write("**Current Form Trends:**")
        
        # Categorize players by form trend
        current_players['form_category'] = pd.cut(
            current_players['form'],
            bins=[0, 2, 4, 6, float('inf')],
            labels=['Poor Form', 'Average Form', 'Good Form', 'Excellent Form']
        )
        
        form_dist = current_players['form_category'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                x=form_dist.index,
                y=form_dist.values,
                title='Form Distribution',
                color=form_dist.values,
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Form vs Season average
            current_players['season_avg'] = current_players['total_points'] / max(st.session_state.get('fpl_team_gameweek', 8), 1)
            current_players['form_vs_avg'] = current_players['form'] - current_players['season_avg']
            
            improving_players = current_players[current_players['form_vs_avg'] > 1]
            declining_players = current_players[current_players['form_vs_avg'] < -1]
            
            st.success(f"📈 **Improving Form**: {len(improving_players)} players")
            if not improving_players.empty:
                for _, player in improving_players.head(3).iterrows():
                    st.write(f"• {player['web_name']}: +{player['form_vs_avg']:.1f}")
            
            st.error(f"📉 **Declining Form**: {len(declining_players)} players")
            if not declining_players.empty:
                for _, player in declining_players.head(3).iterrows():
                    st.write(f"• {player['web_name']}: {player['form_vs_avg']:.1f}")
        
        # Price trend analysis
        st.subheader("💰 Price Movement Analysis")
        
        current_players['price_change_category'] = pd.cut(
            current_players['cost_change_start'],
            bins=[-float('inf'), -0.2, 0, 0.2, float('inf')],
            labels=['Falling', 'Slight Drop', 'Stable/Rising', 'Rising Well']
        )
        
        price_dist = current_players['price_change_category'].value_counts()
        
        fig = px.pie(
            values=price_dist.values,
            names=price_dist.index,
            title='Price Movement Distribution',
            color_discrete_map={
                'Falling': '#ff4444',
                'Slight Drop': '#ffaa44',
                'Stable/Rising': '#44aa44',
                'Rising Well': '#44ff44'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create combined trend matrix
        st.subheader("🎯 Form vs Price Trend Matrix")
        
        # Create scatter plot showing form vs price change
        fig = px.scatter(
            current_players,
            x='cost_change_start',
            y='form',
            color='element_type_name',
            size='total_points',
            hover_data=['web_name'],
            title='Player Form vs Price Change',
            labels={
                'cost_change_start': 'Price Change (£0.1m)',
                'form': 'Current Form'
            }
        )
        
        # Add quadrant lines
        fig.add_hline(y=current_players['form'].mean(), line_dash='dash', line_color='gray')
        fig.add_vline(x=0, line_dash='dash', line_color='gray')
        
        # Add quadrant annotations
        fig.add_annotation(x=0.3, y=6, text="Rising Stars", showarrow=False, bgcolor="lightgreen")
        fig.add_annotation(x=-0.3, y=6, text="Hidden Gems", showarrow=False, bgcolor="lightblue")
        fig.add_annotation(x=0.3, y=2, text="Avoid", showarrow=False, bgcolor="lightcoral")
        fig.add_annotation(x=-0.3, y=2, text="Falling Knives", showarrow=False, bgcolor="lightcoral")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_predictive_models(self, team_data, current_players):
        """Render predictive analysis"""
        st.subheader("🔮 Predictive Performance Models")
        
        # Simple predictive models based on current data
        st.info("💡 These predictions are based on current form, historical performance, and statistical trends")
        
        # Next gameweek predictions
        st.write("**Next Gameweek Predictions:**")
        
        predictions = []
        for _, player in current_players.iterrows():
            # Simple prediction model
            form_weight = 0.4
            season_avg_weight = 0.3
            price_momentum_weight = 0.2
            random_factor_weight = 0.1
            
            season_avg = player['total_points'] / max(st.session_state.get('fpl_team_gameweek', 8), 1)
            price_momentum = max(0, player['cost_change_start'] * 2)  # Price rising = positive momentum
            random_factor = np.random.normal(0, 1)  # Add some variance
            
            predicted_points = (
                player['form'] * form_weight +
                season_avg * season_avg_weight +
                price_momentum * price_momentum_weight +
                random_factor * random_factor_weight
            )
            
            predicted_points = max(0, predicted_points)  # Can't be negative
            
            # Confidence based on consistency
            games_played = player.get('games_played', 1)
            confidence = min(95, 60 + (games_played * 2))  # More games = higher confidence
            
            predictions.append({
                'Player': player['web_name'],
                'Position': player['element_type_name'],
                'Current Form': player['form'],
                'Predicted Points': round(predicted_points, 1),
                'Confidence': f"{confidence}%",
                'Recommendation': self._get_prediction_recommendation(predicted_points, player['form'])
            })
        
        pred_df = pd.DataFrame(predictions).sort_values('Predicted Points', ascending=False)
        st.dataframe(pred_df, use_container_width=True)
        
        # Captain prediction model
        st.subheader("👑 Captain Choice Predictor")
        
        captain_candidates = pred_df.head(5)
        
        st.write("**Top Captain Predictions for Next GW:**")
        for i, (_, candidate) in enumerate(captain_candidates.iterrows(), 1):
            if i == 1:
                st.success(f"🥇 **Top Choice**: {candidate['Player']} - {candidate['Predicted Points']} points ({candidate['Confidence']} confidence)")
            elif i == 2:
                st.info(f"🥈 **Alternative**: {candidate['Player']} - {candidate['Predicted Points']} points ({candidate['Confidence']} confidence)")
            else:
                st.write(f"🥉 **Option {i}**: {candidate['Player']} - {candidate['Predicted Points']} points")
        
        # Team total prediction
        st.subheader("📊 Team Score Prediction")
        
        total_predicted = pred_df['Predicted Points'].sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Predicted Team Score", f"{total_predicted:.0f} points")
        
        with col2:
            current_avg = current_players['form'].sum()
            difference = total_predicted - current_avg
            st.metric("vs Current Form", f"{difference:+.0f} points")
        
        with col3:
            season_avg = current_players['total_points'].sum() / max(st.session_state.get('fpl_team_gameweek', 8), 1)
            vs_season = total_predicted - season_avg
            st.metric("vs Season Avg", f"{vs_season:+.0f} points")
        
        # Model accuracy disclaimer
        st.warning("⚠️ **Disclaimer**: These predictions are for guidance only. Actual FPL performance depends on many unpredictable factors including injuries, rotation, opponent strength, and match events.")
    
    def _get_prediction_recommendation(self, predicted_points, current_form):
        """Get recommendation based on prediction"""
        if predicted_points > current_form + 1:
            return "Strong Captain Option"
        elif predicted_points > current_form:
            return "Good Pick"
        elif predicted_points > current_form - 1:
            return "Hold"
        else:
            return "Consider Transfer"
