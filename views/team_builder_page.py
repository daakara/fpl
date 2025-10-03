"""
Team Builder Page - Allows users to construct and optimize their FPL team.
"""
import streamlit as st

class TeamBuilderPage:
    """Handles the rendering of the Team Builder page."""

    def __init__(self):
        pass

    def render(self):
        """Render the team builder page."""
        st.markdown("## 🔧 Team Builder")

        if not st.session_state.get('data_loaded', False):
            st.warning("Please load player data to use the Team Builder.")
            return

        # Budget management
        st.markdown("### 💰 Budget Management")
        total_budget = 100.0
        # This would be dynamic in a real implementation
        spent = 95.5
        remaining = total_budget - spent

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

        # Player search and filters
        st.markdown("### 🔍 Player Search")
        if 'players_df' in st.session_state and not st.session_state.players_df.empty:
            # Add filters
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

            # Display available players
            st.dataframe(
                filtered_df[['web_name', 'team_name', 'now_cost', 'total_points', 'points_per_game']],
                hide_index=True
            )
        else:
            st.warning("Please load player data to use the team builder.")