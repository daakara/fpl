"""
Performance Comparison Component
"""
import streamlit as st
from .base_component import BaseTeamComponent

class PerformanceComparisonComponent(BaseTeamComponent):
    def render(self, team_data):
        st.subheader("📊 Performance Comparison")
        st.info("📊 Performance comparison coming soon...")
        # TODO: Extract performance comparison logic from original file
