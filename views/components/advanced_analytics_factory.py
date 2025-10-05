"""
Advanced Analytics Components - Factory for creating advanced analysis components
"""
import streamlit as st
from utils.error_handling import logger


class AdvancedAnalyticsComponentFactory:
    """Factory for creating advanced analytics components"""
    
    @staticmethod
    def create_swot_analysis_component():
        """Create SWOT analysis component"""
        try:
            from .swot_analysis_component import SWOTAnalysisComponent
            return SWOTAnalysisComponent()
        except ImportError:
            logger.warning("SWOT Analysis component not available")
            return BasicSWOTComponent()
    
    @staticmethod
    def create_advanced_analytics_component():
        """Create advanced analytics component"""
        try:
            from .advanced_analytics_component import AdvancedAnalyticsComponent
            return AdvancedAnalyticsComponent()
        except ImportError:
            logger.warning("Advanced Analytics component not available")
            return BasicAdvancedAnalyticsComponent()
    
    @staticmethod
    def create_transfer_planning_component():
        """Create transfer planning component"""
        try:
            from .transfer_planning_component import TransferPlanningComponent
            return TransferPlanningComponent()
        except ImportError:
            logger.warning("Transfer Planning component not available")
            return BasicTransferPlanningComponent()
    
    @staticmethod
    def create_performance_comparison_component():
        """Create performance comparison component"""
        try:
            from .performance_comparison_component import PerformanceComparisonComponent
            return PerformanceComparisonComponent()
        except ImportError:
            logger.warning("Performance Comparison component not available")
            return BasicPerformanceComparisonComponent()
    
    @staticmethod
    def create_fixture_analysis_component():
        """Create fixture analysis component"""
        try:
            from .fixture_analysis_component import FixtureAnalysisComponent
            return FixtureAnalysisComponent()
        except ImportError:
            logger.warning("Fixture Analysis component not available")
            return BasicFixtureAnalysisComponent()


# Basic fallback components
class BasicSWOTComponent:
    """Basic SWOT analysis fallback"""
    
    def render_swot_analysis(self, team_data, players_df):
        st.subheader("🎯 Team SWOT Analysis")
        st.info("🚧 Advanced SWOT analysis not available. Enable advanced features to access this functionality.")
        
        # Basic analysis
        total_points = team_data.get('summary_overall_points', 0)
        overall_rank = team_data.get('summary_overall_rank', 0)
        
        st.write("**Basic Analysis:**")
        if total_points > 1500:
            st.success("✅ **Strength**: High-scoring team")
        
        if overall_rank and overall_rank > 2000000:
            st.warning("⚠️ **Weakness**: Low overall rank")
        
        st.info("💡 **Opportunity**: Analyze upcoming fixtures for transfer opportunities")
        st.warning("⛔ **Threat**: Price changes and injury risks")


class BasicAdvancedAnalyticsComponent:
    """Basic advanced analytics fallback"""
    
    def render_advanced_analytics(self, team_data, players_df):
        st.subheader("📈 Advanced Team Analytics")
        st.info("🚧 Advanced analytics not available. Enable advanced features to access this functionality.")
        
        # Show basic metrics
        total_points = team_data.get('summary_overall_points', 0)
        current_gw = team_data.get('gameweek', 1) or 1
        avg_ppg = total_points / max(current_gw, 1)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average PPG", f"{avg_ppg:.1f}")
        with col2:
            st.metric("Total Points", f"{total_points:,}")
        with col3:
            bank = team_data.get('bank', 0) / 10
            st.metric("Funds Available", f"£{bank:.1f}m")


class BasicTransferPlanningComponent:
    """Basic transfer planning fallback"""
    
    def render_transfer_planning(self, team_data, players_df):
        st.subheader("🔄 Transfer Planning Assistant")
        st.info("🚧 Advanced transfer planning not available. Enable advanced features to access this functionality.")
        
        # Basic transfer advice
        st.info("💡 **Basic Transfer Tips:**")
        st.write("• Use your free transfer each gameweek")
        st.write("• Avoid taking hits unless for urgent transfers")
        st.write("• Plan transfers around fixture swings") 
        st.write("• Monitor player price changes")
        st.write("• Consider form and injury status")


class BasicPerformanceComparisonComponent:
    """Basic performance comparison fallback"""
    
    def render_performance_comparison(self, team_data, players_df):
        st.subheader("📊 Performance Comparison")
        st.info("🚧 Advanced performance comparison not available. Enable advanced features to access this functionality.")
        
        # Basic performance insights
        total_points = team_data.get('summary_overall_points', 0)
        current_gw = team_data.get('gameweek', 1) or 1
        avg_ppg = total_points / max(current_gw, 1)
        
        st.info(f"💡 **Quick Analysis:** You're averaging {avg_ppg:.1f} points per gameweek")
        
        if avg_ppg >= 60:
            st.success("🏆 Excellent performance!")
        elif avg_ppg >= 50:
            st.info("👍 Above average performance")
        else:
            st.warning("📈 Room for improvement")


class BasicFixtureAnalysisComponent:
    """Basic fixture analysis fallback"""
    
    def render_fixture_analysis(self, team_data, players_df):
        st.subheader("⚽ Fixture Analysis")
        st.info("🚧 Advanced fixture analysis not available. Enable advanced features to access this functionality.")
        
        st.info("💡 **Basic Fixture Tips:**")
        st.write("• Check fixture difficulty ratings on the FPL website")
        st.write("• Plan transfers around fixture swings")
        st.write("• Consider double gameweeks and blank gameweeks")
        st.write("• Monitor team rotation risk during busy periods")
        st.write("• Use fixtures to inform captain choices")
