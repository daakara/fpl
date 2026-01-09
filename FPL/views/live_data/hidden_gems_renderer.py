"""
Hidden Gems Discovery Module - Find undervalued players and differential picks.
"""
import streamlit as st
import pandas as pd
from utils.error_handling import logger
from .helpers import LiveDataHelpers


class HiddenGemsRenderer(LiveDataHelpers):
    """Renders the Hidden Gems discovery page."""
    
    def render(self, df, teams_df):
        """Discover undervalued players and differential picks."""
        try:
            st.markdown("### 💎 **Hidden Gems Discovery**")
            st.markdown("Find undervalued players before everyone else does")
            st.markdown("---")
            
            if not df.empty:
                # Configurable filters with expander
                ownership_threshold, min_points, max_cost, positions_filter = self._render_filters()
                
                # Hidden gems algorithm
                gems = self._find_gems(df, ownership_threshold, min_points, max_cost, positions_filter)
                
                # Display summary statistics and gems
                if not gems.empty:
                    self._render_summary_stats(gems)
                    self._render_gems_sections(gems)
                else:
                    st.warning("⚠️ No gems found matching current criteria. Try relaxing the filters above.")
            else:
                st.error("❌ No player data available. Please load data first.")
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in Hidden Gems page render: {str(e)}\n{error_details}")
            st.error(f"⚠️ Error loading Hidden Gems page: {str(e)}")
            st.info("💡 Please try refreshing the page or adjusting the filters.")
    
    def _render_filters(self):
        """Render configurable filter controls."""
        with st.expander("⚙️ Customize Search Criteria", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                ownership_threshold = st.slider("Max Ownership %", 1, 20, 10, key="gems_ownership")
            with col2:
                min_points = st.slider("Min Total Points", 10, 100, 30, key="gems_points")
            with col3:
                max_cost = st.slider("Max Cost (£)", 4.0, 10.0, 8.0, 0.5, key="gems_cost")
            with col4:
                positions_filter = st.multiselect(
                    "Positions", 
                    options=['All', 'GKP', 'DEF', 'MID', 'FWD'],
                    default=['All'],
                    key="gems_positions"
                )
        return ownership_threshold, min_points, max_cost, positions_filter
    
    def _find_gems(self, df, ownership_threshold, min_points, max_cost, positions_filter):
        """Find hidden gems based on criteria."""
        df_gems = df.copy()
        
        # Calculate value score (points per million, low ownership, good form)
        df_gems['points_per_million'] = df_gems['total_points'] / (df_gems['now_cost'] / 10)
        df_gems['value_score'] = (
            df_gems['points_per_million'] * 0.4 +
            (100 - df_gems['selected_by_percent'].astype(float)) * 0.3 +
            df_gems['form'].astype(float) * 0.3
        )
        
        # Apply position filter if not 'All'
        if positions_filter and 'All' not in positions_filter:
            if 'position' in df_gems.columns:
                df_gems = df_gems[df_gems['position'].isin(positions_filter)]
        
        # Filter for potential gems (using configurable thresholds)
        gems = df_gems[
            (df_gems['selected_by_percent'].astype(float) < ownership_threshold) & 
            (df_gems['total_points'] > min_points) &
            (df_gems['now_cost'] <= max_cost * 10)
        ].nlargest(20, 'value_score')
        
        return gems
    
    def _render_summary_stats(self, gems):
        """Render summary statistics for discovered gems."""
        st.markdown("#### 📊 Discovery Summary")
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("💎 Gems Found", len(gems))
        with summary_col2:
            avg_ownership = gems['selected_by_percent'].astype(float).mean()
            st.metric("📊 Avg Ownership", f"{avg_ownership:.1f}%")
        with summary_col3:
            avg_ppm = gems['points_per_million'].mean()
            st.metric("⚡ Avg PPM", f"{avg_ppm:.2f}")
        with summary_col4:
            avg_price = gems['now_cost'].mean() / 10
            st.metric("💰 Avg Price", f"£{avg_price:.1f}m")
        
        st.markdown("---")
    
    def _render_gems_sections(self, gems):
        """Render budget and premium gems sections."""
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_budget_gems(gems)
        
        with col2:
            self._render_premium_gems(gems)
    
    def _render_budget_gems(self, gems):
        """Render budget gems section."""
        st.markdown("#### 💎 **Budget Gems** (Under £6.0m)")
        budget_gems = gems[gems['now_cost'] <= 60]
        
        if budget_gems.empty:
            st.info("💡 No budget gems found. Try adjusting the filters above.")
        else:
            for idx, player in budget_gems.head(10).iterrows():
                self._render_player_card(player, "💎", is_budget=True)
    
    def _render_premium_gems(self, gems):
        """Render premium differentials section."""
        st.markdown("#### ⚡ **Premium Differentials** (£6.0m+)")
        premium_gems = gems[gems['now_cost'] > 60]
        
        if premium_gems.empty:
            st.info("💡 No premium differentials found. Try adjusting the filters above.")
        else:
            for idx, player in premium_gems.head(10).iterrows():
                self._render_player_card(player, "⚡", is_budget=False)
    
    def _render_player_card(self, player, icon, is_budget=True):
        """Render individual player card with metrics and badges."""
        # Safe access to player data
        player_name = self.safe_get_series_value(player, 'web_name', 'Unknown')
        player_cost = self.safe_get_numeric(player, 'now_cost', 0) / 10
        
        with st.expander(f"{icon} **{player_name}** - £{player_cost:.1f}m"):
            # Add position and team info using safe access
            position = self.safe_get_series_value(player, 'position', 'N/A')
            team = self.safe_get_series_value(player, 'team', 'N/A')
            st.caption(f"📍 {position} | {team}")
            
            # Render metrics
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                points = self.safe_get_numeric(player, 'total_points', 0)
                st.metric("Points", points)
            with col_b:
                ownership_val = self.safe_get_numeric(player, 'selected_by_percent', 0.0)
                st.metric("Ownership", f"{ownership_val:.1f}%")
            with col_c:
                if is_budget:
                    ppm = self.safe_get_numeric(player, 'points_per_million', 0.0)
                    st.metric("PPM", f"{ppm:.2f}")
                else:
                    form_val = self.safe_get_numeric(player, 'form', 0.0)
                    st.metric("Form", f"{form_val:.1f}")
            
            # Add "why this player" badges
            reasons = self._get_player_badges(player, is_budget)
            if reasons:
                st.caption(" • ".join(reasons))
    
    def _get_player_badges(self, player, is_budget=True):
        """Generate badge reasons for a player."""
        reasons = []
        ppm_val = self.safe_get_numeric(player, 'points_per_million', 0)
        ownership = self.safe_get_numeric(player, 'selected_by_percent', 0.0)
        form = self.safe_get_numeric(player, 'form', 0.0)
        total_pts = self.safe_get_numeric(player, 'total_points', 0)
        
        if is_budget:
            # Budget gem badges
            if ppm_val > 15:
                reasons.append("🔥 Elite PPM")
            if ownership < 3:
                reasons.append("👻 Ultra-differential")
            if form > 7:
                reasons.append("📈 Hot form")
            if total_pts > 60:
                reasons.append("⭐ High scorer")
        else:
            # Premium gem badges
            if ppm_val > 12:
                reasons.append("💪 Strong PPM")
            if ownership < 5:
                reasons.append("👻 Low ownership")
            if form > 6:
                reasons.append("🔥 Good form")
            if total_pts > 80:
                reasons.append("⭐ Premium points")
        
        return reasons
