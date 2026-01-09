"""
Enhanced Error Recovery and Circuit Breaker Pattern
Implements resilient error handling with automatic recovery strategies
"""
import time
import logging
from typing import Any, Callable, Dict, Optional, Type, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import threading
from collections import defaultdict, deque

from middleware.error_handling import FPLError, ErrorCategory, ErrorSeverity


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 2  # successes needed to close circuit
    timeout: int = 30  # request timeout


class CircuitBreaker:
    """Circuit breaker pattern implementation for API calls"""
    
    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.lock = threading.RLock()
        
        # Metrics
        self.total_requests = 0
        self.total_failures = 0
        self.total_timeouts = 0
        
        self.logger = logging.getLogger(f"circuit_breaker.{name}")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            self.total_requests += 1
            
            # Check if circuit should remain open
            if self.state == CircuitState.OPEN:
                if not self._should_attempt_reset():
                    raise FPLError(
                        f"Circuit breaker '{self.name}' is OPEN - service unavailable",
                        category=ErrorCategory.API_REQUEST,
                        severity=ErrorSeverity.HIGH,
                        user_message="Service is temporarily unavailable. Please try again later."
                    )
                else:
                    self.state = CircuitState.HALF_OPEN
                    self.logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
        
        # Attempt the call
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Success - handle state transition
            with self.lock:
                self._on_success(duration)
            
            return result
            
        except Exception as e:
            with self.lock:
                self._on_failure(e)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout
    
    def _on_success(self, duration: float) -> None:
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info(f"Circuit breaker '{self.name}' CLOSED - service recovered")
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self, exception: Exception) -> None:
        """Handle failed call"""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if isinstance(exception, (TimeoutError, ConnectionError)):
            self.total_timeouts += 1
        
        # Check if we should open the circuit
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(f"Circuit breaker '{self.name}' OPENED after {self.failure_count} failures")
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        with self.lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_requests": self.total_requests,
                "total_failures": self.total_failures,
                "total_timeouts": self.total_timeouts,
                "success_rate": 1 - (self.total_failures / max(1, self.total_requests)),
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
            }


class RetryStrategy:
    """Configurable retry strategy with exponential backoff"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:  # Don't sleep on last attempt
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
        
        # All attempts failed
        raise FPLError(
            f"All {self.max_attempts} retry attempts failed",
            category=ErrorCategory.API_REQUEST,
            severity=ErrorSeverity.HIGH,
            original_exception=last_exception,
            user_message="Service is experiencing issues. Please try again later."
        )
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt"""
        delay = self.base_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


class EnhancedErrorRecovery:
    """Enhanced error recovery with circuit breakers and retry strategies"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_strategies: Dict[str, RetryStrategy] = {}
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.recent_errors: deque = deque(maxlen=100)
        self.logger = logging.getLogger(__name__)
    
    def get_circuit_breaker(self, service_name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            config = config or CircuitBreakerConfig()
            self.circuit_breakers[service_name] = CircuitBreaker(config, service_name)
        
        return self.circuit_breakers[service_name]
    
    def get_retry_strategy(self, strategy_name: str) -> RetryStrategy:
        """Get or create retry strategy"""
        if strategy_name not in self.retry_strategies:
            if strategy_name == "api_calls":
                self.retry_strategies[strategy_name] = RetryStrategy(
                    max_attempts=3,
                    base_delay=1.0,
                    backoff_factor=2.0
                )
            elif strategy_name == "critical_operations":
                self.retry_strategies[strategy_name] = RetryStrategy(
                    max_attempts=5,
                    base_delay=0.5,
                    max_delay=10.0
                )
            else:
                self.retry_strategies[strategy_name] = RetryStrategy()
        
        return self.retry_strategies[strategy_name]
    
    def resilient_call(
        self,
        func: Callable,
        service_name: str,
        retry_strategy: str = "api_calls",
        circuit_config: Optional[CircuitBreakerConfig] = None,
        *args,
        **kwargs
    ) -> Any:
        """Make a resilient call with circuit breaker and retry"""
        circuit_breaker = self.get_circuit_breaker(service_name, circuit_config)
        retry = self.get_retry_strategy(retry_strategy)
        
        def protected_call():
            return circuit_breaker.call(func, *args, **kwargs)
        
        try:
            return retry.execute(protected_call)
        except Exception as e:
            self._record_error(service_name, e)
            raise
    
    def _record_error(self, service_name: str, error: Exception) -> None:
        """Record error for monitoring"""
        self.error_counts[service_name] += 1
        self.recent_errors.append({
            'service': service_name,
            'error': str(error),
            'type': type(error).__name__,
            'timestamp': datetime.now().isoformat()
        })
        
        self.logger.error(f"Error in {service_name}: {error}", exc_info=True)
    
    @property
    def health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        return {
            'circuit_breakers': {name: cb.metrics for name, cb in self.circuit_breakers.items()},
            'error_counts': dict(self.error_counts),
            'recent_errors': list(self.recent_errors)[-10:],  # Last 10 errors
            'timestamp': datetime.now().isoformat()
        }


# Decorator for automatic resilient calls
def resilient_api_call(service_name: str, retry_strategy: str = "api_calls"):
    """Decorator to make API calls resilient"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            recovery = EnhancedErrorRecovery()
            return recovery.resilient_call(func, service_name, retry_strategy, *args, **kwargs)
        return wrapper
    return decorator


# Global error recovery instance
error_recovery = EnhancedErrorRecovery()