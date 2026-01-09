"""
Comprehensive Logging Strategy
Provides structured logging with different outputs and formats
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pathlib import Path
from enum import Enum
import traceback
import os
from dataclasses import dataclass, asdict

class LogLevel(Enum):
    """Enhanced log levels"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class LogFormat(Enum):
    """Log output formats"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"

@dataclass
class LogContext:
    """Structured log context information"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None

class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add custom fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data, default=str, indent=None)

class StructuredFormatter(logging.Formatter):
    """Structured log formatter with key-value pairs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured key-value pairs"""
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        base_info = [
            f"timestamp={timestamp}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"module={record.module}",
            f"function={record.funcName}",
            f"line={record.lineno}",
            f"message=\"{record.getMessage()}\""
        ]
        
        # Add custom fields
        custom_fields = []
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                if isinstance(value, str):
                    custom_fields.append(f'{key}="{value}"')
                else:
                    custom_fields.append(f'{key}={value}')
        
        all_fields = base_info + custom_fields
        return " ".join(all_fields)

class LoggingStrategy:
    """Comprehensive logging strategy implementation"""
    
    def __init__(self, 
                 app_name: str = "fpl_analytics",
                 log_level: LogLevel = LogLevel.INFO,
                 log_format: LogFormat = LogFormat.DETAILED,
                 log_directory: Optional[Path] = None):
        
        self.app_name = app_name
        self.log_level = log_level
        self.log_format = log_format
        self.log_directory = log_directory or Path("logs")
        self.log_directory.mkdir(exist_ok=True)
        
        # Create loggers for different purposes
        self.loggers = {
            'main': self._create_logger('main'),
            'error': self._create_logger('error'),
            'performance': self._create_logger('performance'),
            'audit': self._create_logger('audit'),
            'debug': self._create_logger('debug')
        }
        
        # Context storage
        self._context = LogContext()
    
    def _create_logger(self, logger_type: str) -> logging.Logger:
        """Create a configured logger for specific type"""
        logger_name = f"{self.app_name}.{logger_type}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level.value)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Add handlers based on logger type
        if logger_type == 'main':
            self._add_console_handler(logger)
            self._add_file_handler(logger, "application.log")
            
        elif logger_type == 'error':
            self._add_file_handler(logger, "errors.log", logging.ERROR)
            self._add_email_handler(logger)  # For critical errors
            
        elif logger_type == 'performance':
            self._add_file_handler(logger, "performance.log")
            
        elif logger_type == 'audit':
            self._add_file_handler(logger, "audit.log")
            self._add_rotating_handler(logger, "audit_archive.log")
            
        elif logger_type == 'debug':
            self._add_file_handler(logger, "debug.log", logging.DEBUG)
        
        return logger
    
    def _add_console_handler(self, logger: logging.Logger) -> None:
        """Add console handler with appropriate formatting"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        if self.log_format == LogFormat.JSON:
            formatter = JsonFormatter()
        elif self.log_format == LogFormat.STRUCTURED:
            formatter = StructuredFormatter()
        elif self.log_format == LogFormat.DETAILED:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
            )
        else:  # SIMPLE
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def _add_file_handler(self, logger: logging.Logger, filename: str, 
                         min_level: int = logging.DEBUG) -> None:
        """Add file handler"""
        file_path = self.log_directory / filename
        handler = logging.FileHandler(file_path)
        handler.setLevel(min_level)
        
        if self.log_format == LogFormat.JSON:
            formatter = JsonFormatter()
        elif self.log_format == LogFormat.STRUCTURED:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def _add_rotating_handler(self, logger: logging.Logger, filename: str) -> None:
        """Add rotating file handler for large log files"""
        file_path = self.log_directory / filename
        handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=10*1024*1024, backupCount=5  # 10MB files, keep 5
        )
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def _add_email_handler(self, logger: logging.Logger) -> None:
        """Add email handler for critical errors (if configured)"""
        # This would be configured with actual SMTP settings in production
        # For now, we'll skip this to avoid configuration dependencies
        pass
    
    def set_context(self, context: LogContext) -> None:
        """Set logging context information"""
        self._context = context
    
    def update_context(self, **kwargs) -> None:
        """Update specific context fields"""
        for key, value in kwargs.items():
            if hasattr(self._context, key):
                setattr(self._context, key, value)
    
    def _add_context_to_record(self, record: logging.LogRecord) -> None:
        """Add context information to log record"""
        context_dict = asdict(self._context)
        for key, value in context_dict.items():
            if value is not None:
                setattr(record, key, value)
    
    def log(self, level: LogLevel, message: str, logger_type: str = 'main', 
            extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log a message with specified level and type"""
        logger = self.loggers.get(logger_type, self.loggers['main'])
        
        # Create log record
        exc_info_data = None
        if exc_info:
            import sys
            exc_info_data = sys.exc_info()
        
        record = logger.makeRecord(
            logger.name, level.value, "", 0, message, (), exc_info_data
        )
        
        # Add context
        self._add_context_to_record(record)
        
        # Add extra fields
        if extra:
            for key, value in extra.items():
                setattr(record, key, value)
        
        logger.handle(record)
    
    def trace(self, message: str, **kwargs) -> None:
        """Log trace message"""
        self.log(LogLevel.TRACE, message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        # Remove exc_info from kwargs to avoid conflict
        kwargs.pop('exc_info', None)
        self.log(LogLevel.ERROR, message, logger_type='error', exc_info=True, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        # Remove exc_info from kwargs to avoid conflict
        kwargs.pop('exc_info', None)
        self.log(LogLevel.CRITICAL, message, logger_type='error', exc_info=True, **kwargs)
    
    def performance(self, message: str, execution_time: float, **kwargs) -> None:
        """Log performance metrics"""
        extra = {"execution_time": execution_time, **kwargs}
        self.log(LogLevel.INFO, message, logger_type='performance', extra=extra)
    
    def audit(self, action: str, user_id: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log audit information"""
        extra = {
            "action": action,
            "user_id": user_id,
            "details": details or {}
        }
        self.log(LogLevel.INFO, f"Audit: {action}", logger_type='audit', extra=extra)
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            "log_directory": str(self.log_directory),
            "log_files": [],
            "total_size": 0
        }
        
        for log_file in self.log_directory.glob("*.log"):
            file_stats = log_file.stat()
            stats["log_files"].append({
                "name": log_file.name,
                "size": file_stats.st_size,
                "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            })
            stats["total_size"] += file_stats.st_size
        
        return stats

# Performance logging decorator
def log_performance(logger_strategy: LoggingStrategy, 
                   threshold_ms: float = 1000.0,
                   log_args: bool = False):
    """Decorator to log function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                if execution_time > threshold_ms:
                    extra = {"function": func.__name__}
                    if log_args:
                        extra["args"] = str(args)[:200]  # Limit arg logging
                        extra["kwargs"] = str(kwargs)[:200]
                    
                    logger_strategy.performance(
                        f"Function {func.__name__} executed in {execution_time:.2f}ms",
                        execution_time,
                        **extra
                    )
                
                return result
            
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger_strategy.error(
                    f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}"
                )
                raise
        
        return wrapper
    return decorator

# Global logging strategy instance
_global_logging_strategy: Optional[LoggingStrategy] = None

def get_logging_strategy() -> LoggingStrategy:
    """Get the global logging strategy instance"""
    global _global_logging_strategy
    if _global_logging_strategy is None:
        _global_logging_strategy = LoggingStrategy()
    return _global_logging_strategy

def initialize_logging(app_name: str = "fpl_analytics",
                      log_level: LogLevel = LogLevel.INFO,
                      log_format: LogFormat = LogFormat.DETAILED) -> LoggingStrategy:
    """Initialize the logging strategy"""
    global _global_logging_strategy
    _global_logging_strategy = LoggingStrategy(app_name, log_level, log_format)
    return _global_logging_strategy
