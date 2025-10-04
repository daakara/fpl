"""
Base component class for My Team modules
"""
import streamlit as st
from abc import ABC, abstractmethod
from utils.error_handling import logger


class BaseTeamComponent(ABC):
    """Base class for all My Team components"""
    
    def __init__(self, data_service=None):
        """Initialize base component"""
        self.data_service = data_service
        self.logger = logger
    
    def get_session_data(self, key, default=None):
        """Safely get data from session state"""
        return st.session_state.get(key, default)
    
    def set_session_data(self, key, value):
        """Safely set data in session state"""
        st.session_state[key] = value
    
    def validate_team_data(self, team_data):
        """Validate team data structure"""
        if not team_data or not isinstance(team_data, dict):
            return False
        
        required_fields = ['picks', 'entry_name']
        return all(field in team_data for field in required_fields)
    
    def validate_player_data(self):
        """Check if player data is available in session state"""
        players_df = self.get_session_data('players_df')
        return players_df is not None and not players_df.empty
    
    @abstractmethod
    def render(self, *args, **kwargs):
        """Abstract method for rendering component"""
        pass
    
    def handle_error(self, error, context="Component"):
        """Standardized error handling"""
        error_msg = f"Error in {context}: {str(error)}"
        self.logger.error(error_msg)
        st.error(f"❌ {error_msg}")
        return False
