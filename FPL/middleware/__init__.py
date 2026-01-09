"""
Middleware Package
Centralized error handling, dependency injection, and logging
"""

from .error_handling import (
    ErrorHandlingMiddleware,
    FPLError,
    DataLoadingError,
    APIRequestError,
    ProcessingError,
    ExportError,
    AIProcessingError,
    ErrorSeverity,
    ErrorCategory,
    error_handler,
    get_error_middleware,
    initialize_error_handling
)

from .dependency_injection import (
    DIContainer,
    IContainer,
    ServiceLifetime,
    ScopedContainer,
    injectable,
    inject,
    get_container,
    configure_container,
    reset_container
)

from .logging_strategy import (
    LoggingStrategy,
    LogLevel,
    LogFormat,
    LogContext,
    log_performance,
    get_logging_strategy,
    initialize_logging
)

__all__ = [
    # Error Handling
    'ErrorHandlingMiddleware',
    'FPLError',
    'DataLoadingError', 
    'APIRequestError',
    'ProcessingError',
    'ExportError',
    'AIProcessingError',
    'ErrorSeverity',
    'ErrorCategory',
    'error_handler',
    'get_error_middleware',
    'initialize_error_handling',
    
    # Dependency Injection
    'DIContainer',
    'IContainer',
    'ServiceLifetime',
    'ScopedContainer',
    'injectable',
    'inject',
    'get_container',
    'configure_container',
    'reset_container',
    
    # Logging
    'LoggingStrategy',
    'LogLevel',
    'LogFormat',
    'LogContext',
    'log_performance',
    'get_logging_strategy',
    'initialize_logging'
]
