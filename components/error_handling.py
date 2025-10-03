"""
Error Handler Module - Manages application-wide error handling and recovery
"""
import streamlit as st
import traceback
from dataclasses import dataclass
from typing import Optional, Callable, Dict
from abc import ABC, abstractmethod


class ErrorHandler(ABC):
    """Abstract base class for error handlers"""
    @abstractmethod
    def handle(self, error: Exception) -> None:
        """Handle an error"""
        pass


@dataclass
class ErrorInfo:
    """Container for error information"""
    type_name: str
    message: str
    recovery_steps: list[str]
    possible_solutions: list[str]


class ErrorRecoveryAction:
    """Represents a recovery action that can be taken"""
    def __init__(self, label: str, action: Callable, button_type: str = "primary"):
        self.label = label
        self.action = action
        self.button_type = button_type


class StreamlitErrorHandler(ErrorHandler):
    """Error handler for Streamlit applications"""
    def __init__(self):
        self.error_types: Dict[str, ErrorInfo] = {
            "DataTypeError": ErrorInfo(
                type_name="Data Type Error",
                message="Error in data type conversion",
                recovery_steps=[
                    "Click '🔄 Refresh Data' in the sidebar",
                    "Try your action again",
                    "Refresh the browser page"
                ],
                possible_solutions=[
                    "Data cleaning has been automatically applied",
                    "Check input data formats",
                    "Verify numeric columns are properly formatted"
                ]
            ),
            "ConnectionError": ErrorInfo(
                type_name="Connection Error",
                message="Failed to connect to the FPL API",
                recovery_steps=[
                    "Check your internet connection",
                    "Wait 30 seconds and try again",
                    "The FPL API might be temporarily unavailable"
                ],
                possible_solutions=[
                    "Verify your network connection",
                    "Check if the FPL API is down",
                    "Try using a cached version of the data"
                ]
            ),
            "CacheError": ErrorInfo(
                type_name="Cache Error",
                message="Error accessing or writing to cache",
                recovery_steps=[
                    "Clear cache using the sidebar button",
                    "Refresh the page",
                    "Reload your data"
                ],
                possible_solutions=[
                    "Clear browser cache",
                    "Check disk space",
                    "Verify cache directory permissions"
                ]
            )
        }

    def _get_error_info(self, error: Exception) -> ErrorInfo:
        """Get error info based on error type"""
        error_type = type(error).__name__
        error_str = str(error).lower()
        
        if "multiply sequence" in error_str:
            return self.error_types["DataTypeError"]
        elif "connection" in error_str:
            return self.error_types["ConnectionError"]
        elif "cache" in error_str:
            return self.error_types["CacheError"]
        
        # Default error info
        return ErrorInfo(
            type_name=error_type,
            message=str(error),
            recovery_steps=["Refresh the page", "Try again", "Contact support if the issue persists"],
            possible_solutions=["Check the error details", "Review recent changes", "Clear cache and try again"]
        )

    def handle(self, error: Exception) -> None:
        """Handle an error with comprehensive UI feedback"""
        error_info = self._get_error_info(error)
        
        st.error("❌ Application encountered an unexpected error")
        
        with st.expander("🔍 Error Details & Recovery"):
            st.write("**Error Type:**", error_info.type_name)
            st.write("**Error Message:**", error_info.message)
            
            st.markdown("### 🚨 Recovery Steps")
            for step in error_info.recovery_steps:
                st.markdown(f"- {step}")
            
            st.markdown("### 💡 Possible Solutions")
            for solution in error_info.possible_solutions:
                st.markdown(f"- {solution}")
            
            # Recovery actions
            st.markdown("### 🛠️ Quick Recovery Actions")
            
            recovery_col1, recovery_col2, recovery_col3 = st.columns(3)
            
            with recovery_col1:
                if st.button("🔄 Refresh Page", type="primary"):
                    st.rerun()
            
            with recovery_col2:
                if st.button("🗑️ Clear Cache"):
                    try:
                        from utils.enhanced_cache import cache_manager
                        cache_manager.clear_cache()
                        st.success("Cache cleared!")
                    except Exception as e:
                        st.error(f"Could not clear cache: {str(e)}")
            
            with recovery_col3:
                if st.button("🏠 Go to Dashboard"):
                    st.session_state.current_page = "dashboard"
                    st.rerun()
            
            # Debug information for developers
            if st.checkbox("🔬 Show Technical Details"):
                st.code(str(error))
                st.text("Stack Trace:")
                st.code(traceback.format_exc())


# Create a default error handler instance
default_error_handler = StreamlitErrorHandler()