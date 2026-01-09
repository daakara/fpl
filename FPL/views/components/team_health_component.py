"""
Team Health & Insights Component - Advanced team analysis and insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.error_handling import logger


class TeamHealthComponent:
    """Provides advanced team health analysis and insights"""
    
    def __init__(self, data_service=None):
        self.data_service = data_service
    
    def render_team_health(self, team_data, players_df=None):
        """Render comprehensive team health analysis"""
        st.header("🏥 Team Health & Insights")
        
        team_name = team_data.get('entry_name', 'Unknown Team')
        st.info(f"🔍 Deep analysis of {team_name}'s team composition and health")
        
        # Create tabs for different health metrics
        health_tab1, health_tab2, health_tab3, health_tab4 = st.tabs([
            "🏥 Player Fitness", "💰 Financial Health", "🎯 Strategy Analysis", "⚠️ Risk Assessment"
        ])
        
        with health_tab1:
            self._render_fitness_analysis(team_data, players_df)
        
        with health_tab2:
            self._render_financial_health(team_data, players_df)
        
        with health_tab3:
            self._render_strategy_analysis(team_data, players_df)
        
        with health_tab4:
            self._render_risk_assessment(team_data, players_df)
    
    def _render_fitness_analysis(self, team_data, players_df):
        """Analyze player fitness and availability"""
        st.subheader("🏥 Player Fitness Status")
        
        picks = team_data.get('picks', [])
        if not picks:
            st.warning("No team data available for fitness analysis")
            return
        
        # Sample fitness data (in real implementation, get from FPL API)
        fitness_data = []
        statuses = ['Fit', 'Fit', 'Fit', 'Minor Doubt', 'Fit', 'Injured', 'Fit', 'Fit', 'Suspended', 'Fit', 'Fit', 'Fit', 'Fit', 'Fit', 'Fit']
        
        for i, pick in enumerate(picks):
            player_id = pick.get('element', 0)
            status = statuses[i % len(statuses)]
            
            # Determine risk level
            if status == 'Fit':
                risk = 'Low'
                risk_color = 'green'
            elif status in ['Minor Doubt', 'Suspended']:
                risk = 'Medium'
                risk_color = 'orange'
            else:
                risk = 'High'
                risk_color = 'red'
            
            fitness_data.append({
                'Player_ID': player_id,
                'Position': i + 1,
                'Status': status,
                'Risk': risk,
                'Risk_Color': risk_color,
                'Expected_Minutes': 90 if status == 'Fit' else 45 if status == 'Minor Doubt' else 0
            })
        
        df_fitness = pd.DataFrame(fitness_data)
        
        # Fitness overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fit_players = len(df_fitness[df_fitness['Status'] == 'Fit'])
            st.metric("Fit Players", f"{fit_players}/15", delta=f"{fit_players-13}")
        
        with col2:
            doubtful_players = len(df_fitness[df_fitness['Status'] == 'Minor Doubt'])
            st.metric("Doubtful", doubtful_players)
        
        with col3:
            injured_players = len(df_fitness[df_fitness['Status'] == 'Injured'])
            st.metric("Injured", injured_players)
        
        with col4:
            suspended_players = len(df_fitness[df_fitness['Status'] == 'Suspended'])
            st.metric("Suspended", suspended_players)
        
        # Fitness status pie chart
        status_counts = df_fitness['Status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Team Fitness Overview",
            color_discrete_map={
                'Fit': '#28a745',
                'Minor Doubt': '#ffc107',
                'Injured': '#dc3545',
                'Suspended': '#6c757d'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed fitness table
        st.subheader("Detailed Fitness Report")
        
        # Display fitness data (simplified for demo)
        for i, row in df_fitness.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**Player {row['Player_ID']}** (Pos {row['Position']})")
                
                with col2:
                    status_color = {
                        'Fit': '🟢',
                        'Minor Doubt': '🟡',
                        'Injured': '🔴',
                        'Suspended': '⚫'
                    }
                    st.write(f"{status_color.get(row['Status'], '⚪')} {row['Status']}")
                
                with col3:
                    st.write(f"Risk: {row['Risk']}")
                
                with col4:
                    st.write(f"Expected: {row['Expected_Minutes']}min")
                
                if i < len(df_fitness) - 1:
                    st.divider()
    
    def _render_financial_health(self, team_data, players_df):
        """Analyze team's financial health"""
        st.subheader("💰 Financial Health Analysis")
        
        # Sample financial data
        team_value = 101.2
        bank = 0.8
        total_budget = team_value + bank
        
        # Financial metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Team Value", f"£{team_value}m")
        
        with col2:
            st.metric("Bank", f"£{bank}m")
        
        with col3:
            st.metric("Total Budget", f"£{total_budget}m")
        
        with col4:
            budget_efficiency = (team_value / total_budget) * 100
            st.metric("Budget Efficiency", f"{budget_efficiency:.1f}%")
        
        # Value distribution by position
        position_values = {
            'Goalkeepers': 9.5,
            'Defenders': 28.3,
            'Midfielders': 35.8,
            'Forwards': 27.6
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(position_values.keys()),
                y=list(position_values.values()),
                marker_color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            )
        ])
        
        fig.update_layout(
            title="Team Value Distribution by Position",
            xaxis_title="Position",
            yaxis_title="Value (£m)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Value efficiency analysis
        st.subheader("Value Efficiency")
        
        efficiency_data = [
            {'Position': 'Goalkeepers', 'Avg_Cost': 4.75, 'Avg_Points': 2.8, 'Points_per_£m': 0.59},
            {'Position': 'Defenders', 'Avg_Cost': 5.66, 'Avg_Points': 3.2, 'Points_per_£m': 0.57},
            {'Position': 'Midfielders', 'Avg_Cost': 7.16, 'Avg_Points': 4.1, 'Points_per_£m': 0.57},
            {'Position': 'Forwards', 'Avg_Cost': 9.2, 'Avg_Points': 4.8, 'Points_per_£m': 0.52},
        ]
        
        df_efficiency = pd.DataFrame(efficiency_data)
        st.dataframe(df_efficiency, use_container_width=True, hide_index=True)
        
        # Financial recommendations
        st.subheader("💡 Financial Recommendations")
        
        recommendations = [
            "🔄 Consider upgrading your £4.0m defender to a £5.0m option for better returns",
            "💰 Your £0.8m bank could be invested in player upgrades",
            "⚖️ Forward line is well-balanced for price range",
            "📈 Midfield showing good value for money spent"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")
    
    def _render_strategy_analysis(self, team_data, players_df):
        """Analyze team strategy and composition"""
        st.subheader("🎯 Strategy Analysis")
        
        # Formation analysis
        formation = "3-5-2"  # Sample formation
        st.write(f"**Current Formation:** {formation}")
        
        # Strategy metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Attacking Focus", "65%", delta="5%")
            st.caption("Balance between attacking and defensive players")
        
        with col2:
            st.metric("Premium Players", "3/15", delta="0")
            st.caption("Players costing £9m or more")
        
        with col3:
            st.metric("Differential Count", "4/15", delta="1")
            st.caption("Players owned by <10% of managers")
        
        # Team composition analysis
        st.subheader("Team Composition")
        
        composition_data = {
            'Category': ['Premium (£9m+)', 'Mid-range (£6-9m)', 'Budget (£4-6m)', 'Bench fodder (<£4.5m)'],
            'Count': [3, 7, 4, 1],
            'Total_Value': [31.5, 49.8, 16.2, 3.7]
        }
        
        df_comp = pd.DataFrame(composition_data)
        
        # Composition charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.pie(df_comp, values='Count', names='Category', title='Player Count by Price Category')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.pie(df_comp, values='Total_Value', names='Category', title='Value Distribution by Category')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Strategy recommendations
        st.subheader("🎯 Strategic Insights")
        
        insights = [
            {"Type": "Formation", "Insight": "3-5-2 formation maximizes midfield points potential", "Impact": "Positive"},
            {"Type": "Balance", "Insight": "Good mix of premium and budget players", "Impact": "Positive"},
            {"Type": "Differentials", "Insight": "4 differential picks could provide rank boost if successful", "Impact": "High Risk/Reward"},
            {"Type": "Bench", "Insight": "Weak bench limits rotation options", "Impact": "Negative"},
        ]
        
        for insight in insights:
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    st.write(f"**{insight['Type']}**")
                
                with col2:
                    st.write(insight['Insight'])
                
                with col3:
                    impact_color = {
                        'Positive': '🟢',
                        'Negative': '🔴',
                        'High Risk/Reward': '🟡'
                    }
                    st.write(impact_color.get(insight['Impact'], '⚪'))
                
                st.divider()
    
    def _render_risk_assessment(self, team_data, players_df):
        """Assess various risks in the team"""
        st.subheader("⚠️ Risk Assessment")
        
        # Overall risk score
        risk_score = 6.5  # Out of 10
        risk_color = "🟡" if 4 <= risk_score <= 7 else "🔴" if risk_score > 7 else "🟢"
        
        st.metric("Overall Risk Score", f"{risk_color} {risk_score}/10")
        
        # Risk categories
        risk_categories = [
            {'Category': 'Injury Risk', 'Score': 7, 'Description': 'High due to 2 injury-prone players'},
            {'Category': 'Price Fall Risk', 'Score': 5, 'Description': 'Moderate risk from 3 underperforming assets'},
            {'Category': 'Rotation Risk', 'Score': 8, 'Description': 'High due to insufficient bench depth'},
            {'Category': 'Fixture Risk', 'Score': 4, 'Description': 'Low - good fixture spread across team'},
            {'Category': 'Differential Risk', 'Score': 7, 'Description': 'High due to 4 differential picks'},
        ]
        
        # Risk breakdown
        for risk in risk_categories:
            col1, col2, col3 = st.columns([2, 1, 4])
            
            with col1:
                st.write(f"**{risk['Category']}**")
            
            with col2:
                risk_color = "🟢" if risk['Score'] <= 3 else "🟡" if risk['Score'] <= 6 else "🔴"
                st.write(f"{risk_color} {risk['Score']}/10")
            
            with col3:
                st.write(risk['Description'])
        
        # Risk visualization
        fig = go.Figure(go.Bar(
            x=[r['Score'] for r in risk_categories],
            y=[r['Category'] for r in risk_categories],
            orientation='h',
            marker_color=['#28a745' if score <= 3 else '#ffc107' if score <= 6 else '#dc3545' 
                         for score in [r['Score'] for r in risk_categories]]
        ))
        
        fig.update_layout(
            title="Risk Assessment Breakdown",
            xaxis_title="Risk Score (1-10)",
            yaxis_title="Risk Category",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk mitigation suggestions
        st.subheader("🛡️ Risk Mitigation Suggestions")
        
        mitigations = [
            "🏥 Consider transferring out injury-prone players before their next difficult fixture",
            "💰 Monitor price changes daily and act quickly on falling assets",
            "🔄 Strengthen bench with playing substitutes (£4.5m+ range)",
            "📊 Balance differential picks with safer, template players",
            "⏰ Plan transfers 2-3 gameweeks ahead to avoid panic moves"
        ]
        
        for mitigation in mitigations:
            st.write(f"• {mitigation}")
        
        # Emergency action plan
        with st.expander("🚨 Emergency Action Plan"):
            st.write("**If multiple players get injured/suspended:**")
            st.write("1. Use free transfer on highest priority position")
            st.write("2. Consider taking -4 point hit if 2+ players affected")
            st.write("3. Activate bench players with good fixtures")
            st.write("4. Monitor press conferences for late team news")
            
            st.write("**If team value drops significantly:**")
            st.write("1. Identify which players are causing the drop")
            st.write("2. Transfer out before further price falls")
            st.write("3. Reinvest in rising assets or secure picks")
