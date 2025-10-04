"""
Transfer Planning Component
"""
import streamlit as st
from .base_component import BaseTeamComponent

class TransferPlanningComponent(BaseTeamComponent):
    def render(self, team_data):
        st.subheader("🔄 Transfer Planning")
        st.info("🔄 Transfer planning coming soon...")
        # TODO: Extract transfer planning logic from original file
