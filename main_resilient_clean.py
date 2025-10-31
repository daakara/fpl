"""
FPL Analytics - Resilient Application (Refactored)
Now uses clean service-oriented architecture while maintaining backward compatibility
"""

import streamlit as st
from datetime import datetime

# Import the refactored application components
from main_refactored import RefactoredFPLApp

# For backward compatibility, inherit from refactored app
class ResilientFPLApp(RefactoredFPLApp):
    """
    Backward compatible version of the FPL Analytics application.
    Inherits from the refactored version while maintaining the same interface.
    """
    
    def __init__(self):
        """Initialize the resilient app using refactored architecture"""
        super().__init__()
        
        # Maintain compatibility properties
        self.enhanced_mode = super().enhanced_mode
        self.fallback_data = super().fallback_data
        
        # Legacy property mappings for existing code
        if hasattr(super(), 'fpl_service'):
            self.fpl_service = super().fpl_service
        if hasattr(super(), 'cache_manager'):
            self.cache_manager = super().cache_manager
    
    # Legacy method compatibility - delegate to refactored services
    def _create_fallback_data(self):
        """Legacy compatibility - delegates to refactored data service"""
        return super().fallback_data
    
    def setup_page_config(self):
        """Legacy compatibility - delegates to refactored setup"""
        return super().setup_page_config()
    
    # Legacy method wrappers for backward compatibility
    def initialize_session_state(self):
        """Legacy compatibility wrapper"""
        return super().initialize_session_state()
    
    def check_api_status(self):
        """Legacy compatibility wrapper"""
        return super().check_api_status()
    
    def get_data_safely(self):
        """Legacy compatibility wrapper"""
        return super().get_data_safely()
    
    def render_enhanced_header(self):
        """Legacy compatibility - delegates to UI service"""
        return super().ui_service.render_enhanced_header()
    
    def render_navigation(self):
        """Legacy compatibility - delegates to navigation service"""
        return super().navigation_service.render_navigation()
    
    def render_page_content(self, selected_page):
        """Legacy compatibility wrapper"""
        return super().render_page_content(selected_page)
    
    def render_sidebar(self):
        """Legacy compatibility wrapper"""
        return super().render_sidebar()
    
    def render_footer(self):
        """Legacy compatibility - delegates to UI service"""
        return super().ui_service.render_footer()
    
    def run_resilient_app(self):
        """Main entry point - delegates to refactored app"""
        return super().run_refactored_app()


# Backward compatibility: Keep the original class available
# All legacy methods delegate to the refactored service-oriented architecture

# Create and run the resilient application
resilient_app = ResilientFPLApp()

if __name__ == "__main__":
    resilient_app.run_resilient_app()