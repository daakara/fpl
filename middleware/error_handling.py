"""
Centralized Error Handling Middleware
Provides comprehensive error handling, user-friendly messages, and logging strategy
"""

import streamlit as st
import traceback
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Type, Union
from functools import wraps
from enum import Enum
import sys
from pathlib import Path

class ErrorSeverity(Enum):
    """Error severity levels for better categorization"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better organization"""
    DATA_LOADING = "data_loading"
    API_REQUEST = "api_request"
    PROCESSING = "processing"
    UI_RENDERING = "ui_rendering"
    CACHE_OPERATION = "cache_operation"
    EXPORT_OPERATION = "export_operation"
    AI_PROCESSING = "ai_processing"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    SYSTEM = "system"

class FPLError(Exception):
    """Base exception class for FPL Analytics application"""
    
    def __init__(
        self, 
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.user_message = user_message or self._generate_user_friendly_message()
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        super().__init__(self.message)
    
    def _generate_user_friendly_message(self) -> str:
        """Generate user-friendly error messages based on category"""
        friendly_messages = {
            ErrorCategory.DATA_LOADING: "Unable to load FPL data. Please check your internet connection and try again.",
            ErrorCategory.API_REQUEST: "Error connecting to FPL servers. Please try again in a few moments.",
            ErrorCategory.PROCESSING: "Error processing your request. Please try again or contact support.",
            ErrorCategory.UI_RENDERING: "Display error occurred. Please refresh the page.",
            ErrorCategory.CACHE_OPERATION: "Cache error - data may load slower than usual.",
            ErrorCategory.EXPORT_OPERATION: "Unable to export data. Please try a different format or try again.",
            ErrorCategory.AI_PROCESSING: "AI analysis temporarily unavailable. Basic features still work.",
            ErrorCategory.AUTHENTICATION: "Authentication required. Please log in to continue.",
            ErrorCategory.CONFIGURATION: "Configuration error. Please contact your administrator.",
            ErrorCategory.SYSTEM: "System error occurred. Our team has been notified."
        }
        return friendly_messages.get(self.category, "An unexpected error occurred. Please try again.")

class DataLoadingError(FPLError):
    """Specific error for data loading operations"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.DATA_LOADING, **kwargs)

class APIRequestError(FPLError):
    """Specific error for API request operations"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.API_REQUEST, **kwargs)

class ProcessingError(FPLError):
    """Specific error for data processing operations"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.PROCESSING, **kwargs)

class ExportError(FPLError):
    """Specific error for export operations"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.EXPORT_OPERATION, **kwargs)

class AIProcessingError(FPLError):
    """Specific error for AI processing operations"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.AI_PROCESSING, **kwargs)

class ErrorHandlingMiddleware:
    """Centralized error handling middleware"""
    
    def __init__(self, logger_name: str = "fpl_analytics"):
        self.logger = self._setup_logger(logger_name)
        self._error_counts = {}
        self._user_notifications = []
    
    def _setup_logger(self, logger_name: str) -> logging.Logger:
        """Setup comprehensive logging configuration"""
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        # File handler for detailed logging
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "fpl_analytics.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Error-specific file handler
        error_handler = logging.FileHandler(log_dir / "fpl_errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def handle_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None,
        show_user_message: bool = True
    ) -> None:
        """Central error handling method"""
        
        # Convert to FPLError if not already
        if not isinstance(error, FPLError):
            fpl_error = FPLError(
                message=str(error),
                category=self._categorize_error(error),
                severity=self._assess_severity(error),
                context=context,
                original_exception=error
            )
        else:
            fpl_error = error
            if context:
                fpl_error.context.update(context)
        
        # Log the error
        self._log_error(fpl_error)
        
        # Update error statistics
        self._update_error_stats(fpl_error)
        
        # Show user-friendly message
        if show_user_message:
            self._show_user_message(fpl_error)
        
        # Handle critical errors
        if fpl_error.severity == ErrorSeverity.CRITICAL:
            self._handle_critical_error(fpl_error)
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Automatically categorize errors based on type and context"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        if "connection" in error_str or "network" in error_str or "request" in error_str:
            return ErrorCategory.API_REQUEST
        elif "data" in error_str or "dataframe" in error_str or "csv" in error_str:
            return ErrorCategory.DATA_LOADING
        elif "streamlit" in error_str or "widget" in error_str:
            return ErrorCategory.UI_RENDERING
        elif "cache" in error_str or "redis" in error_str:
            return ErrorCategory.CACHE_OPERATION
        elif "export" in error_str or "pdf" in error_str or "excel" in error_str:
            return ErrorCategory.EXPORT_OPERATION
        elif "ai" in error_str or "model" in error_str or "prediction" in error_str:
            return ErrorCategory.AI_PROCESSING
        elif "auth" in error_str or "permission" in error_str:
            return ErrorCategory.AUTHENTICATION
        elif "config" in error_str or "setting" in error_str:
            return ErrorCategory.CONFIGURATION
        else:
            return ErrorCategory.PROCESSING
    
    def _assess_severity(self, error: Exception) -> ErrorSeverity:
        """Assess error severity based on type and impact"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        critical_indicators = ["memory", "disk", "database", "critical", "fatal"]
        high_indicators = ["connection", "authentication", "authorization", "security"]
        medium_indicators = ["processing", "calculation", "rendering"]
        
        if any(indicator in error_str for indicator in critical_indicators):
            return ErrorSeverity.CRITICAL
        elif any(indicator in error_str for indicator in high_indicators):
            return ErrorSeverity.HIGH
        elif any(indicator in error_str for indicator in medium_indicators):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _log_error(self, error: FPLError) -> None:
        """Log error with comprehensive details"""
        log_data = {
            "timestamp": error.timestamp.isoformat(),
            "category": error.category.value,
            "severity": error.severity.value,
            "error_message": error.message,  # Changed from 'message' to 'error_message'
            "user_message": error.user_message,
            "context": error.context,
            "traceback": traceback.format_exc() if error.original_exception else None
        }
        
        log_message = f"[{error.category.value.upper()}][{error.severity.value.upper()}] {error.message}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message, extra=log_data)
        else:
            self.logger.info(log_message, extra=log_data)
    
    def _update_error_stats(self, error: FPLError) -> None:
        """Update error statistics for monitoring"""
        category_key = error.category.value
        severity_key = error.severity.value
        
        if category_key not in self._error_counts:
            self._error_counts[category_key] = {}
        
        if severity_key not in self._error_counts[category_key]:
            self._error_counts[category_key][severity_key] = 0
        
        self._error_counts[category_key][severity_key] += 1
    
    def _show_user_message(self, error: FPLError) -> None:
        """Display user-friendly error messages in Streamlit"""
        icon_map = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️", 
            ErrorSeverity.HIGH: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }
        
        icon = icon_map.get(error.severity, "⚠️")
        
        if error.severity == ErrorSeverity.CRITICAL:
            st.error(f"{icon} **Critical Error**: {error.user_message}")
        elif error.severity == ErrorSeverity.HIGH:
            st.error(f"{icon} **Error**: {error.user_message}")
        elif error.severity == ErrorSeverity.MEDIUM:
            st.warning(f"{icon} **Warning**: {error.user_message}")
        else:
            st.info(f"{icon} **Notice**: {error.user_message}")
        
        # Add to notification history
        self._user_notifications.append({
            "timestamp": error.timestamp,
            "severity": error.severity,
            "message": error.user_message,
            "category": error.category
        })
    
    def _handle_critical_error(self, error: FPLError) -> None:
        """Handle critical errors with special procedures"""
        self.logger.critical(f"CRITICAL ERROR DETECTED: {error.message}")
        
        # Could implement additional critical error handling:
        # - Send alerts to administrators
        # - Create incident tickets
        # - Trigger failover procedures
        # - Store error details for post-mortem analysis
        
        # For now, show prominent user message
        st.error("🚨 **CRITICAL SYSTEM ERROR** 🚨")
        st.error("The application has encountered a critical error. Please contact support immediately.")
        st.error("Error ID: " + str(hash(error.message))[:8])
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring dashboard"""
        return {
            "error_counts": self._error_counts,
            "total_errors": sum(
                sum(severities.values()) 
                for severities in self._error_counts.values()
            ),
            "recent_notifications": self._user_notifications[-10:],  # Last 10
            "categories": list(ErrorCategory),
            "severities": list(ErrorSeverity)
        }
    
    def render_error_dashboard(self) -> None:
        """Render error monitoring dashboard in Streamlit"""
        stats = self.get_error_statistics()
        
        st.markdown("### 🛡️ Error Monitoring Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Errors", stats["total_errors"])
        
        with col2:
            critical_count = sum(
                cats.get("critical", 0) 
                for cats in stats["error_counts"].values()
            )
            st.metric("Critical Errors", critical_count)
        
        with col3:
            categories_with_errors = len(stats["error_counts"])
            st.metric("Affected Categories", categories_with_errors)
        
        if stats["recent_notifications"]:
            st.markdown("#### Recent Error Notifications")
            for notification in reversed(stats["recent_notifications"]):
                severity_color = {
                    ErrorSeverity.LOW: "blue",
                    ErrorSeverity.MEDIUM: "orange", 
                    ErrorSeverity.HIGH: "red",
                    ErrorSeverity.CRITICAL: "red"
                }
                
                st.markdown(
                    f"**{notification['timestamp'].strftime('%H:%M:%S')}** - "
                    f":{severity_color.get(notification['severity'], 'gray')}[{notification['severity'].value.upper()}] "
                    f"{notification['message']}"
                )

def error_handler(
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    user_message: Optional[str] = None,
    show_message: bool = True
):
    """Decorator for automatic error handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_middleware = get_error_middleware()
                
                if isinstance(e, FPLError):
                    error_middleware.handle_error(e, show_user_message=show_message)
                else:
                    fpl_error = FPLError(
                        message=str(e),
                        category=category,
                        severity=severity,
                        user_message=user_message,
                        context={"function": func.__name__, "args": str(args)[:200]},
                        original_exception=e
                    )
                    error_middleware.handle_error(fpl_error, show_user_message=show_message)
                
                # Re-raise for critical errors
                if severity == ErrorSeverity.CRITICAL:
                    raise
                
                return None
        return wrapper
    return decorator

# Global error middleware instance
_error_middleware = None

def get_error_middleware() -> ErrorHandlingMiddleware:
    """Get the global error middleware instance"""
    global _error_middleware
    if _error_middleware is None:
        _error_middleware = ErrorHandlingMiddleware()
    return _error_middleware

def initialize_error_handling() -> ErrorHandlingMiddleware:
    """Initialize the error handling system"""
    global _error_middleware
    _error_middleware = ErrorHandlingMiddleware()
    
    # Setup global exception handler for unhandled exceptions
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if exc_type != KeyboardInterrupt:
            _error_middleware.handle_error(
                FPLError(
                    message=f"Unhandled {exc_type.__name__}: {exc_value}",
                    category=ErrorCategory.SYSTEM,
                    severity=ErrorSeverity.CRITICAL,
                    original_exception=exc_value
                )
            )
        
        # Call the original handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = global_exception_handler
    
    return _error_middleware
