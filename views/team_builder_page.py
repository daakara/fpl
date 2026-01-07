"""
Team Builder Page - Allows users to construct and optimize their FPL team.
"""
import streamlit as st
import pandas as pd
from utils.mobile_responsive import is_mobile, is_desktop, responsive_columns
from utils.best_team_generator import BestTeamGenerator
from utils.pagination import paginate_dataframe

class TeamBuilderPage:
    """Handles the rendering of the Team Builder page."""

    def __init__(self):
        self.team_generator = BestTeamGenerator()

    def render(self):
        """Render the team builder page."""
        st.markdown("## 🔧 Team Builder")

        if not st.session_state.get('data_loaded', False):
            st.warning("Please load player data to use the Team Builder.")
            return
        
        # NEW FEATURE: Copy Best Team Button
        st.markdown("### ✨ Quick Start")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            strategy = st.selectbox(
                "Strategy",
                ["balanced", "form", "value", "points"],
                help="Select team generation strategy"
            )
        
        with col2:
            if st.button("🏆 Generate Best Team", type="primary", use_container_width=True):
                with st.spinner("Building optimal squad..."):
                    df = st.session_state.get('players_df')
                    if df is not None and not df.empty:
                        result = self.team_generator.generate_best_team(df, strategy=strategy)
                        
                        if result['squad']:
                            st.session_state.generated_team = result
                            st.success(f"✅ Generated best {strategy} team!")
                            st.balloons()
                        else:
                            st.error("Could not generate team. Please check data.")
        
        # Display generated team if available
        if 'generated_team' in st.session_state and st.session_state.generated_team:
            result = st.session_state.generated_team
            
            with st.expander("🏆 Generated Squad", expanded=True):
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("Total Cost", f"£{result['total_cost']}m")
                with col_info2:
                    st.metric("Total Points", f"{result['stats']['total_points']:,}")
                with col_info3:
                    st.metric("Formation", result['formation'])
                
                # Starting XI
                st.markdown("**⚽ Starting XI:**")
                starting_df = pd.DataFrame(result['starting_xi'])
                if not starting_df.empty:
                    display_df = starting_df[['web_name', 'position', 'team', 'total_points']]
                    display_df['cost'] = starting_df['now_cost'] / 10
                    display_df = display_df.rename(columns={
                        'web_name': 'Player',
                        'position': 'Pos',
                        'team': 'Team',
                        'total_points': 'Points',
                        'cost': 'Price (£m)'
                    })
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Bench
                st.markdown("**🪑 Bench:**")
                if result['bench']:
                    bench_df = pd.DataFrame(result['bench'])
                    display_bench = bench_df[['web_name', 'position', 'total_points']]
                    display_bench['cost'] = bench_df['now_cost'] / 10
                    display_bench = display_bench.rename(columns={
                        'web_name': 'Player',
                        'position': 'Pos',
                        'total_points': 'Points',
                        'cost': 'Price (£m)'
                    })
                    st.dataframe(display_bench, use_container_width=True, hide_index=True)
        
        st.markdown("---")

        # Budget management
        st.markdown("### 💰 Budget Management")
        total_budget = 100.0
        # This would be dynamic in a real implementation
        spent = 95.5
        remaining = total_budget - spent

        # Responsive budget display
        if is_mobile():
            st.metric("Budget", f"£{remaining}M / £{total_budget}M")
        else:
            budget_col1, budget_col2 = st.columns(2)
            with budget_col1:
                st.metric("Total Budget", f"£{total_budget}M")
            with budget_col2:
                st.metric("Remaining", f"£{remaining}M")

        # Team Selection
        st.markdown("### 👥 Team Selection")
        st.markdown("""
        Build your dream team:
        - Select players by position
        - Stay within budget
        - Consider upcoming fixtures
        - Balance team structure
        """)

        # Formation selector
        st.markdown("### 📋 Formation")
        formation = st.selectbox(
            "Choose Formation",
            ["4-4-2", "4-3-3", "3-5-2", "3-4-3", "5-3-2"]
        )

        # Player search and filters - Responsive
        st.markdown("### 🔍 Player Search")
        if 'players_df' in st.session_state and not st.session_state.players_df.empty:
            # Add filters - Responsive
            if is_mobile():
                max_price = st.slider("Maximum Price", 4.0, 14.0, 10.0, 0.5)
                position = st.selectbox(
                    "Position",
                    ["All", "Goalkeeper", "Defender", "Midfielder", "Forward"],
                    key="team_builder_position_filter"
                )
            else:
                col1, col2 = st.columns(2)
                with col1:
                    max_price = st.slider("Maximum Price", 4.0, 14.0, 10.0, 0.5)
                with col2:
                    position = st.selectbox(
                        "Position",
                        ["All", "Goalkeeper", "Defender", "Midfielder", "Forward"],
                        key="team_builder_position_filter"
                    )

            # Filter players
            filtered_df = st.session_state.players_df
            if position != "All":
                # Assuming 'position' column exists from your other files
                filtered_df = filtered_df[filtered_df['position_name'] == position]
            filtered_df = filtered_df[filtered_df['now_cost'] <= max_price * 10]

            # Display available players with pagination
            st.markdown(f"**Available Players:** {len(filtered_df)} players match your criteria")
            
            paginated_df = paginate_dataframe(
                filtered_df[['web_name', 'team_name', 'now_cost', 'total_points', 'points_per_game']],
                page_size=25 if is_mobile() else 50,
                key='team_builder_players',
                position='both'
            )
            
            st.dataframe(
                paginated_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Please load player data to use the team builder.")