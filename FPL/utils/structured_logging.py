"""
Enhanced Structured Logging System

Provides comprehensive logging with structured data, correlation IDs, and 
performance metrics integration for the FPL Analytics application.
"""

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
import traceback
from contextlib import contextmanager

# Import from our local types package
try:
    from custom_types.enhanced_types import LogLevel, ErrorSeverity, ErrorCategory
except ImportError:
    # Fallback definitions
    from enum import Enum
    class LogLevel(Enum):
        DEBUG = "debug"
        INFO = "info"
        WARNING = "warning" 
        ERROR = "error"
        CRITICAL = "critical"
    
    class ErrorSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    class ErrorCategory(Enum):
        API_ERROR = "api_error"
        DATA_ERROR = "data_error"
        SYSTEM_ERROR = "system_error"


@dataclass
class LogEntry:
    """Structured log entry with comprehensive metadata."""
    timestamp: datetime
    level: str
    message: str
    logger_name: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    duration_ms: Optional[float] = None
    error_category: Optional[str] = None
    error_severity: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for JSON serialization."""
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class StructuredLogFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Get correlation ID from thread-local storage
        correlation_id = getattr(LoggingContext._local, 'correlation_id', None)
        user_id = getattr(LoggingContext._local, 'user_id', None)
        session_id = getattr(LoggingContext._local, 'session_id', None)
        
        # Create structured log entry
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,
            message=record.getMessage(),
            logger_name=record.name,
            correlation_id=correlation_id,
            user_id=user_id,
            session_id=session_id,
            component=getattr(record, 'component', None),
            operation=getattr(record, 'operation', None),
            duration_ms=getattr(record, 'duration_ms', None),
            error_category=getattr(record, 'error_category', None),
            error_severity=getattr(record, 'error_severity', None)
        )
        
        # Add exception info if present
        if record.exc_info:
            log_entry.stack_trace = self.formatException(record.exc_info)
        
        # Add any additional data
        if self.include_extra:
            extra_data = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'lineno', 'funcName', 'created',
                              'msecs', 'relativeCreated', 'thread', 'threadName',
                              'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                    extra_data[key] = value
            
            if extra_data:
                log_entry.additional_data = extra_data
        
        return log_entry.to_json()


class LoggingContext:
    """Thread-local context for logging correlation IDs and user data."""
    
    _local = threading.local()
    
    @classmethod
    def set_correlation_id(cls, correlation_id: str) -> None:
        """Set correlation ID for current thread."""
        cls._local.correlation_id = correlation_id
    
    @classmethod
    def get_correlation_id(cls) -> Optional[str]:
        """Get correlation ID for current thread."""
        return getattr(cls._local, 'correlation_id', None)
    
    @classmethod
    def set_user_context(cls, user_id: str, session_id: Optional[str] = None) -> None:
        """Set user context for current thread."""
        cls._local.user_id = user_id
        if session_id:
            cls._local.session_id = session_id
    
    @classmethod
    def clear_context(cls) -> None:
        """Clear all context for current thread."""
        for attr in ['correlation_id', 'user_id', 'session_id', 'request_id']:
            if hasattr(cls._local, attr):
                delattr(cls._local, attr)
    
    @classmethod
    @contextmanager
    def correlation_context(cls, correlation_id: Optional[str] = None):
        """Context manager for correlation ID."""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        old_id = cls.get_correlation_id()
        cls.set_correlation_id(correlation_id)
        try:
            yield correlation_id
        finally:
            if old_id:
                cls.set_correlation_id(old_id)
            else:
                cls.clear_context()


class PerformanceLogger:
    """Logger specifically for performance metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_operation_time(
        self, 
        operation: str, 
        duration_ms: float, 
        component: str,
        success: bool = True,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log operation timing information."""
        level = logging.INFO if success else logging.WARNING
        
        self.logger.log(
            level,
            f"Operation '{operation}' completed in {duration_ms:.2f}ms",
            extra={
                'component': component,
                'operation': operation,
                'duration_ms': duration_ms,
                'success': success,
                'performance_metric': True,
                **(additional_data or {})
            }
        )
    
    def log_resource_usage(
        self,
        component: str,
        memory_mb: float,
        cpu_percent: float,
        additional_metrics: Optional[Dict[str, float]] = None
    ) -> None:
        """Log resource usage metrics."""
        metrics = {
            'memory_mb': memory_mb,
            'cpu_percent': cpu_percent,
            **(additional_metrics or {})
        }
        
        self.logger.info(
            f"Resource usage for {component}",
            extra={
                'component': component,
                'resource_metrics': metrics,
                'performance_metric': True
            }
        )


class ErrorLogger:
    """Logger specifically for error tracking and analysis."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_error(
        self,
        error: Exception,
        component: str,
        operation: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        user_message: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log comprehensive error information."""
        self.logger.error(
            f"Error in {component}.{operation}: {str(error)}",
            exc_info=True,
            extra={
                'component': component,
                'operation': operation,
                'error_category': category.value,
                'error_severity': severity.name,
                'error_type': type(error).__name__,
                'user_message': user_message,
                'error_context': additional_context or {}
            }
        )
    
    def log_validation_error(
        self,
        field: str,
        value: Any,
        expected: str,
        component: str
    ) -> None:
        """Log validation errors."""
        self.logger.warning(
            f"Validation failed for field '{field}' in {component}",
            extra={
                'component': component,
                'validation_error': True,
                'field': field,
                'invalid_value': str(value),
                'expected_format': expected,
                'error_category': ErrorCategory.VALIDATION_ERROR.value
            }
        )


class SecurityLogger:
    """Logger for security-related events."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_authentication_attempt(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Log authentication attempts."""
        level = logging.INFO if success else logging.WARNING
        status = "successful" if success else "failed"
        
        self.logger.log(
            level,
            f"Authentication attempt {status} for user {user_id}",
            extra={
                'security_event': True,
                'event_type': 'authentication',
                'user_id': user_id,
                'success': success,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
        )
    
    def log_suspicious_activity(
        self,
        activity_type: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """Log suspicious activities."""
        self.logger.warning(
            f"Suspicious activity detected: {activity_type}",
            extra={
                'security_event': True,
                'event_type': 'suspicious_activity',
                'activity_type': activity_type,
                'description': description,
                'user_id': user_id,
                'ip_address': ip_address,
                'severity': 'high'
            }
        )


class EnhancedLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create specialized loggers
        self.performance = PerformanceLogger(self.logger)
        self.error = ErrorLogger(self.logger)
        self.security = SecurityLogger(self.logger)
        
        # Add structured formatter if not already configured
        if not self.logger.handlers:
            self._setup_default_handler()
    
    def _setup_default_handler(self) -> None:
        """Setup default console handler with structured formatting."""
        handler = logging.StreamHandler()
        formatter = StructuredLogFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def add_file_handler(self, log_file: Path, level: str = "INFO") -> None:
        """Add file handler with structured logging."""
        handler = logging.FileHandler(log_file)
        handler.setLevel(getattr(logging, level.upper()))
        formatter = StructuredLogFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with additional context."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with additional context."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with additional context."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with additional context."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with additional context."""
        self.logger.critical(message, extra=kwargs)
    
    @contextmanager
    def operation_context(self, operation: str, component: Optional[str] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        correlation_id = str(uuid.uuid4())
        
        with LoggingContext.correlation_context(correlation_id):
            self.info(
                f"Starting operation: {operation}",
                operation=operation,
                component=component,
                phase="start"
            )
            
            try:
                yield correlation_id
                
                duration_ms = (time.time() - start_time) * 1000
                self.performance.log_operation_time(
                    operation, duration_ms, component or "unknown", success=True
                )
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.performance.log_operation_time(
                    operation, duration_ms, component or "unknown", success=False
                )
                
                self.error.log_error(
                    e, 
                    component or "unknown", 
                    operation,
                    ErrorCategory.SYSTEM_ERROR,
                    ErrorSeverity.HIGH
                )
                raise


def get_enhanced_logger(name: str, level: str = "INFO") -> EnhancedLogger:
    """Get or create an enhanced logger instance."""
    return EnhancedLogger(name, level)


def setup_application_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_structured_logging: bool = True
) -> None:
    """Setup application-wide logging configuration."""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    if enable_structured_logging:
        # Add structured console handler
        console_handler = logging.StreamHandler()
        console_formatter = StructuredLogFormatter()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = StructuredLogFormatter()
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
    else:
        # Use standard formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)


# Performance timing decorator
def log_performance(operation: str, component: Optional[str] = None):
    """Decorator to automatically log operation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_enhanced_logger(func.__module__)
            
            with logger.operation_context(operation, component):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global application logger
app_logger = get_enhanced_logger("fpl_analytics")