"""
AI Recommendations Page - Displays AI-powered suggestions.
"""
import streamlit as st
from services.ai_recommendation_engine import get_player_recommendations

class AIRecommendationsPage:
    """Handles the rendering of the AI Recommendations page."""

    def __init__(self):
        pass

    def render(self):
        """Render AI-powered recommendations page with enhanced UI."""
        st.markdown("## 🤖 AI Recommendations")

        if not st.session_state.get('data_loaded', False) or st.session_state.get('players_df') is None:
            st.warning("Please load player data from the Dashboard to get recommendations.")
            return

        players_df = st.session_state.players_df
        if players_df.empty:
            st.warning("Player data is empty.")
            return

        with st.spinner("🧠 Generating AI recommendations..."):
            # Add filters for recommendations
            st.markdown("#### Filter Recommendations")
            col1, col2 = st.columns(2)
            with col1:
                pos_filter = st.selectbox(
                    "Filter by Position",
                    ["All", "Goalkeeper", "Defender", "Midfielder", "Forward"],
                    key="ai_rec_pos_filter"
                )
            with col2:
                budget_filter = st.slider(
                    "Max Budget (£m)", 4.0, 14.0, 14.0, 0.5,
                    key="ai_rec_budget_filter"
                )

            # Get recommendations from the engine
            suggestions = get_player_recommendations(
                players_df,
                position=pos_filter if pos_filter != "All" else None,
                budget=budget_filter,
                top_n=15
            )

        if suggestions:
            st.markdown("### 🎯 Top AI Transfer Targets")
            # Display top 3 in columns, then the rest
            top_3_cols = st.columns(3)
            for i, suggestion in enumerate(suggestions[:3]):
                with top_3_cols[i]:
                    self._render_player_recommendation_card(suggestion)

            if len(suggestions) > 3:
                with st.expander("Show More Recommendations"):
                    for suggestion in suggestions[3:]:
                        self._render_player_recommendation_card(suggestion)
        else:
            st.info("No specific recommendations match your criteria. Try adjusting the filters.")

    def _render_player_recommendation_card(self, rec):
        """Render a single player recommendation card."""
        with st.container(border=True):
            st.markdown(f"##### {rec.web_name} ({rec.team_name})")
            st.markdown(f"**{rec.position} | £{rec.current_price:.1f}m**")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Predicted Points", f"{rec.predicted_points:.1f}", help="Predicted points for the next gameweek.")
            with col2:
                st.metric("Value Score", f"{rec.value_score:.1f}", help="Points per million, adjusted for form.")

            st.progress(rec.confidence_score, text=f"Confidence: {rec.confidence_score:.0%}")

            with st.expander("🤖 AI Reasoning"):
                if rec.reasoning:
                    for reason in rec.reasoning:
                        st.markdown(f"- {reason}")
                else:
                    st.markdown("- A solid pick based on a combination of form, value, and fixture difficulty.")