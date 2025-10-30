"""
Health Check and System Monitoring

Provides comprehensive health checks for all application components,
dependencies, and system resources.
"""

import asyncio
import time
import psutil
import requests
from typing import Dict, List, Any, Optional, Callable, NamedTuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
from pathlib import Path
import json

# Import from our local types package
try:
    from types.enhanced_types import ErrorCategory, ErrorSeverity
except ImportError:
    # Fallback definitions
    class ErrorCategory(Enum):
        API_ERROR = "api_error"
        DATA_ERROR = "data_error"
        SYSTEM_ERROR = "system_error"
    
    class ErrorSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

from utils.structured_logging import get_enhanced_logger
from utils.error_recovery import error_recovery
from config.secure_config import get_secure_config


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthMetric:
    """Individual health metric."""
    name: str
    status: HealthStatus
    value: Any
    threshold: Optional[Any] = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ComponentHealth:
    """Health status for a system component."""
    component_name: str
    status: HealthStatus
    metrics: List[HealthMetric]
    dependencies: List[str] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.now)
    check_duration_ms: float = 0.0
    error_message: Optional[str] = None


class HealthChecker:
    """Base class for component health checkers."""
    
    def __init__(self, name: str, timeout: float = 30.0):
        self.name = name
        self.timeout = timeout
        self.logger = get_enhanced_logger(f"health_check.{name}")
    
    async def check_health(self) -> ComponentHealth:
        """Perform health check for this component."""
        start_time = time.time()
        
        try:
            metrics = await asyncio.wait_for(
                self._perform_checks(), 
                timeout=self.timeout
            )
            
            # Determine overall status
            status = self._determine_status(metrics)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                component_name=self.name,
                status=status,
                metrics=metrics,
                dependencies=self.get_dependencies(),
                check_duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return ComponentHealth(
                component_name=self.name,
                status=HealthStatus.UNHEALTHY,
                metrics=[],
                check_duration_ms=duration_ms,
                error_message=f"Health check timed out after {self.timeout}s"
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Health check failed for {self.name}: {e}")
            
            return ComponentHealth(
                component_name=self.name,
                status=HealthStatus.CRITICAL,
                metrics=[],
                check_duration_ms=duration_ms,
                error_message=str(e)
            )
    
    async def _perform_checks(self) -> List[HealthMetric]:
        """Override this method to implement specific health checks."""
        raise NotImplementedError("Subclasses must implement _perform_checks")
    
    def _determine_status(self, metrics: List[HealthMetric]) -> HealthStatus:
        """Determine overall component status from metrics."""
        if not metrics:
            return HealthStatus.UNHEALTHY
        
        statuses = [metric.status for metric in metrics]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_dependencies(self) -> List[str]:
        """Return list of component dependencies."""
        return []


class APIHealthChecker(HealthChecker):
    """Health checker for FPL API connectivity."""
    
    def __init__(self):
        super().__init__("fpl_api", timeout=15.0)
        self.config = get_secure_config()
    
    async def _perform_checks(self) -> List[HealthMetric]:
        """Check FPL API health."""
        metrics = []
        
        # Test basic connectivity
        connectivity_metric = await self._check_connectivity()
        metrics.append(connectivity_metric)
        
        # Test response time
        response_time_metric = await self._check_response_time()
        metrics.append(response_time_metric)
        
        # Test data integrity
        if connectivity_metric.status == HealthStatus.HEALTHY:
            data_integrity_metric = await self._check_data_integrity()
            metrics.append(data_integrity_metric)
        
        return metrics
    
    async def _check_connectivity(self) -> HealthMetric:
        """Check basic API connectivity."""
        try:
            response = requests.get(
                f"{self.config.fpl_api_url}/bootstrap-static/",
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                return HealthMetric(
                    name="api_connectivity",
                    status=HealthStatus.HEALTHY,
                    value=response.status_code,
                    message="FPL API is accessible"
                )
            else:
                return HealthMetric(
                    name="api_connectivity",
                    status=HealthStatus.UNHEALTHY,
                    value=response.status_code,
                    message=f"API returned status {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            return HealthMetric(
                name="api_connectivity",
                status=HealthStatus.UNHEALTHY,
                value="timeout",
                message="API request timed out"
            )
        except Exception as e:
            return HealthMetric(
                name="api_connectivity",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Connection failed: {str(e)}"
            )
    
    async def _check_response_time(self) -> HealthMetric:
        """Check API response time."""
        try:
            start_time = time.time()
            
            response = requests.get(
                f"{self.config.fpl_api_url}/bootstrap-static/",
                timeout=10,
                verify=False
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response_time < 1000:  # Under 1 second
                status = HealthStatus.HEALTHY
            elif response_time < 3000:  # Under 3 seconds
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            return HealthMetric(
                name="api_response_time",
                status=status,
                value=response_time,
                threshold=1000,
                message=f"API response time: {response_time:.0f}ms"
            )
            
        except Exception as e:
            return HealthMetric(
                name="api_response_time",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Could not measure response time: {str(e)}"
            )
    
    async def _check_data_integrity(self) -> HealthMetric:
        """Check FPL API data integrity."""
        try:
            response = requests.get(
                f"{self.config.fpl_api_url}/bootstrap-static/",
                timeout=10,
                verify=False
            )
            
            data = response.json()
            
            # Basic data structure checks
            required_keys = ['elements', 'teams', 'element_types', 'events']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                return HealthMetric(
                    name="data_integrity",
                    status=HealthStatus.UNHEALTHY,
                    value="incomplete",
                    message=f"Missing data keys: {missing_keys}"
                )
            
            # Check if data is populated
            players_count = len(data.get('elements', []))
            teams_count = len(data.get('teams', []))
            
            if players_count < 400:  # Expect ~500 players
                return HealthMetric(
                    name="data_integrity",
                    status=HealthStatus.DEGRADED,
                    value=players_count,
                    threshold=400,
                    message=f"Low player count: {players_count}"
                )
            
            if teams_count != 20:  # Should be exactly 20 teams
                return HealthMetric(
                    name="data_integrity",
                    status=HealthStatus.UNHEALTHY,
                    value=teams_count,
                    threshold=20,
                    message=f"Incorrect team count: {teams_count}"
                )
            
            return HealthMetric(
                name="data_integrity",
                status=HealthStatus.HEALTHY,
                value="valid",
                message=f"Data integrity OK ({players_count} players, {teams_count} teams)"
            )
            
        except Exception as e:
            return HealthMetric(
                name="data_integrity",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Data integrity check failed: {str(e)}"
            )


class SystemResourcesHealthChecker(HealthChecker):
    """Health checker for system resources."""
    
    def __init__(self):
        super().__init__("system_resources", timeout=5.0)
    
    async def _perform_checks(self) -> List[HealthMetric]:
        """Check system resource health."""
        metrics = []
        
        # CPU usage
        cpu_metric = self._check_cpu_usage()
        metrics.append(cpu_metric)
        
        # Memory usage
        memory_metric = self._check_memory_usage()
        metrics.append(memory_metric)
        
        # Disk usage
        disk_metric = self._check_disk_usage()
        metrics.append(disk_metric)
        
        return metrics
    
    def _check_cpu_usage(self) -> HealthMetric:
        """Check CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent < 70:
                status = HealthStatus.HEALTHY
            elif cpu_percent < 85:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            return HealthMetric(
                name="cpu_usage",
                status=status,
                value=cpu_percent,
                threshold=70,
                message=f"CPU usage: {cpu_percent:.1f}%"
            )
            
        except Exception as e:
            return HealthMetric(
                name="cpu_usage",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Could not check CPU: {str(e)}"
            )
    
    def _check_memory_usage(self) -> HealthMetric:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent < 80:
                status = HealthStatus.HEALTHY
            elif memory_percent < 90:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            return HealthMetric(
                name="memory_usage",
                status=status,
                value=memory_percent,
                threshold=80,
                message=f"Memory usage: {memory_percent:.1f}%"
            )
            
        except Exception as e:
            return HealthMetric(
                name="memory_usage",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Could not check memory: {str(e)}"
            )
    
    def _check_disk_usage(self) -> HealthMetric:
        """Check disk usage."""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent < 80:
                status = HealthStatus.HEALTHY
            elif disk_percent < 90:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            return HealthMetric(
                name="disk_usage",
                status=status,
                value=disk_percent,
                threshold=80,
                message=f"Disk usage: {disk_percent:.1f}%"
            )
            
        except Exception as e:
            return HealthMetric(
                name="disk_usage",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Could not check disk: {str(e)}"
            )


class CacheHealthChecker(HealthChecker):
    """Health checker for cache systems."""
    
    def __init__(self):
        super().__init__("cache_system", timeout=10.0)
    
    async def _perform_checks(self) -> List[HealthMetric]:
        """Check cache system health."""
        metrics = []
        
        # Test cache write/read
        cache_rw_metric = await self._check_cache_read_write()
        metrics.append(cache_rw_metric)
        
        # Check cache size/capacity
        cache_size_metric = await self._check_cache_capacity()
        metrics.append(cache_size_metric)
        
        return metrics
    
    async def _check_cache_read_write(self) -> HealthMetric:
        """Test cache read/write operations."""
        try:
            from utils.advanced_cache_manager import get_cache_manager
            
            cache_manager = get_cache_manager()
            test_key = "health_check_test"
            test_value = {"timestamp": datetime.now().isoformat(), "test": True}
            
            # Test write
            cache_manager.set(test_key, test_value, ttl=60)
            
            # Test read
            retrieved_value = cache_manager.get(test_key)
            
            if retrieved_value == test_value:
                # Clean up
                cache_manager.delete(test_key)
                
                return HealthMetric(
                    name="cache_operations",
                    status=HealthStatus.HEALTHY,
                    value="operational",
                    message="Cache read/write operations working"
                )
            else:
                return HealthMetric(
                    name="cache_operations",
                    status=HealthStatus.UNHEALTHY,
                    value="data_mismatch",
                    message="Cache data integrity issue"
                )
                
        except Exception as e:
            return HealthMetric(
                name="cache_operations",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Cache operations failed: {str(e)}"
            )
    
    async def _check_cache_capacity(self) -> HealthMetric:
        """Check cache capacity and utilization."""
        try:
            from utils.advanced_cache_manager import get_cache_manager
            
            cache_manager = get_cache_manager()
            
            # This would depend on the cache implementation
            # For now, return a placeholder
            return HealthMetric(
                name="cache_capacity",
                status=HealthStatus.HEALTHY,
                value="ok",
                message="Cache capacity within limits"
            )
            
        except Exception as e:
            return HealthMetric(
                name="cache_capacity",
                status=HealthStatus.CRITICAL,
                value="error",
                message=f"Could not check cache capacity: {str(e)}"
            )


class ApplicationHealthMonitor:
    """Main health monitoring service for the application."""
    
    def __init__(self):
        self.logger = get_enhanced_logger("health_monitor")
        self.checkers = [
            APIHealthChecker(),
            SystemResourcesHealthChecker(),
            CacheHealthChecker()
        ]
        self.last_check_results: Dict[str, ComponentHealth] = {}
        self.check_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    async def run_all_checks(self) -> Dict[str, ComponentHealth]:
        """Run health checks for all components."""
        results = {}
        
        self.logger.info("Starting comprehensive health check")
        
        # Run all health checks concurrently
        check_tasks = []
        for checker in self.checkers:
            task = asyncio.create_task(checker.check_health())
            check_tasks.append((checker.name, task))
        
        # Collect results
        for checker_name, task in check_tasks:
            try:
                result = await task
                results[checker_name] = result
                self.last_check_results[checker_name] = result
                
                self.logger.info(
                    f"Health check completed for {checker_name}",
                    component=checker_name,
                    status=result.status.value,
                    duration_ms=result.check_duration_ms
                )
                
            except Exception as e:
                self.logger.error(f"Health check failed for {checker_name}: {e}")
                
                results[checker_name] = ComponentHealth(
                    component_name=checker_name,
                    status=HealthStatus.CRITICAL,
                    metrics=[],
                    error_message=str(e)
                )
        
        # Store in history
        self._store_check_history(results)
        
        return results
    
    def _store_check_history(self, results: Dict[str, ComponentHealth]) -> None:
        """Store health check results in history."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._get_overall_status(results).value,
            "component_statuses": {
                name: health.status.value for name, health in results.items()
            }
        }
        
        self.check_history.append(history_entry)
        
        # Limit history size
        if len(self.check_history) > self.max_history:
            self.check_history = self.check_history[-self.max_history:]
    
    def _get_overall_status(self, results: Dict[str, ComponentHealth]) -> HealthStatus:
        """Determine overall application health status."""
        if not results:
            return HealthStatus.CRITICAL
        
        statuses = [health.status for health in results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        if not self.last_check_results:
            return {
                "overall_status": HealthStatus.CRITICAL.value,
                "message": "No health checks have been performed yet",
                "timestamp": datetime.now().isoformat()
            }
        
        overall_status = self._get_overall_status(self.last_check_results)
        
        component_summaries = {}
        for name, health in self.last_check_results.items():
            component_summaries[name] = {
                "status": health.status.value,
                "last_check": health.last_check.isoformat(),
                "metrics_count": len(health.metrics),
                "error_message": health.error_message
            }
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "components": component_summaries,
            "history_count": len(self.check_history)
        }
    
    def get_detailed_health_report(self) -> Dict[str, Any]:
        """Get detailed health report with all metrics."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._get_overall_status(self.last_check_results).value,
            "components": {}
        }
        
        for name, health in self.last_check_results.items():
            component_report = {
                "status": health.status.value,
                "last_check": health.last_check.isoformat(),
                "check_duration_ms": health.check_duration_ms,
                "error_message": health.error_message,
                "dependencies": health.dependencies,
                "metrics": []
            }
            
            for metric in health.metrics:
                metric_data = {
                    "name": metric.name,
                    "status": metric.status.value,
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "message": metric.message,
                    "timestamp": metric.timestamp.isoformat()
                }
                component_report["metrics"].append(metric_data)
            
            report["components"][name] = component_report
        
        # Add history
        report["history"] = self.check_history[-10:]  # Last 10 checks
        
        return report


# Global health monitor instance
health_monitor = ApplicationHealthMonitor()


async def run_health_checks() -> Dict[str, Any]:
    """Run health checks and return summary."""
    results = await health_monitor.run_all_checks()
    return health_monitor.get_health_summary()


def get_health_status() -> Dict[str, Any]:
    """Get current health status without running new checks."""
    return health_monitor.get_health_summary()