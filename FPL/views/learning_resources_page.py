"""
Learning Resources Page
Provides educational content, glossary, and strategy guides
"""

import streamlit as st
from components.learning_resources import render_learning_resources
from utils.error_handling import handle_errors


class LearningResourcesPage:
    """Learning resources page component"""
    
    @staticmethod
    @handle_errors("Error loading learning resources")
    def render():
        """Render the learning resources page"""
        render_learning_resources()
