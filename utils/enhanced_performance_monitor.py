"""
Enhanced Performance Monitor with Streamlit Integration
Provides comprehensive performance monitoring and optimization suggestions
"""

import time
import psutil
import streamlit as st
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import functools
import threading
from collections import defaultdict, deque

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    function_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    args_count: int = 0
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: datetime

class EnhancedPerformanceMonitor:
    """Enhanced performance monitoring for Streamlit applications"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.function_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.system_metrics: deque = deque(maxlen=max_history)
        self.active_sessions: Dict[str, datetime] = {}
        self.logger = logging.getLogger(__name__)
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
    
    def start_monitoring(self, interval: int = 5):
        """Start continuous system monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._continuous_monitoring,
            args=(interval,),
            daemon=True
        )
        self._monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1)
        self.logger.info("Performance monitoring stopped")
    
    def _continuous_monitoring(self, interval: int):
        """Continuous system monitoring loop"""
        while self._monitoring_active:
            try:
                system_metrics = self._collect_system_metrics()
                self.system_metrics.append(system_metrics)
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            return SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=memory.percent,
                memory_available=memory.available,
                disk_usage=disk.percent,
                network_io={
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available=0,
                disk_usage=0.0,
                network_io={'bytes_sent': 0, 'bytes_recv': 0},
                timestamp=datetime.now()
            )
    
    def performance_monitor(self, track_args: bool = False):
        """Decorator for monitoring function performance"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                start_cpu = psutil.cpu_percent()
                
                success = True
                error_message = None
                result = None
                
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    end_cpu = psutil.cpu_percent()
                    
                    metrics = PerformanceMetrics(
                        function_name=func.__name__,
                        execution_time=end_time - start_time,
                        memory_usage=end_memory - start_memory,
                        cpu_usage=end_cpu - start_cpu,
                        timestamp=datetime.now(),
                        args_count=len(args) + len(kwargs) if track_args else 0,
                        success=success,
                        error_message=error_message
                    )
                    
                    self.function_metrics[func.__name__].append(metrics)
                
                return result
            return wrapper
        return decorator
    
    def get_function_stats(self, function_name: str) -> Dict[str, Any]:
        """Get performance statistics for a specific function"""
        if function_name not in self.function_metrics:
            return {}
        
        metrics = list(self.function_metrics[function_name])
        if not metrics:
            return {}
        
        execution_times = [m.execution_time for m in metrics if m.success]
        memory_usage = [m.memory_usage for m in metrics if m.success]
        
        if not execution_times:
            return {'error': 'No successful executions recorded'}
        
        return {
            'total_calls': len(metrics),
            'successful_calls': len(execution_times),
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_memory_usage': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            'last_execution': metrics[-1].timestamp.isoformat(),
            'error_rate': (len(metrics) - len(execution_times)) / len(metrics) * 100
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system performance statistics"""
        if not self.system_metrics:
            current_metrics = self._collect_system_metrics()
            return {
                'current_cpu': current_metrics.cpu_percent,
                'current_memory': current_metrics.memory_percent,
                'available_memory_mb': current_metrics.memory_available / 1024 / 1024,
                'disk_usage': current_metrics.disk_usage,
                'monitoring_active': self._monitoring_active
            }
        
        recent_metrics = list(self.system_metrics)[-10:]  # Last 10 readings
        
        return {
            'current_cpu': recent_metrics[-1].cpu_percent,
            'avg_cpu_10min': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'current_memory': recent_metrics[-1].memory_percent,
            'avg_memory_10min': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'available_memory_mb': recent_metrics[-1].memory_available / 1024 / 1024,
            'disk_usage': recent_metrics[-1].disk_usage,
            'monitoring_active': self._monitoring_active,
            'readings_count': len(self.system_metrics)
        }
    
    def get_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # System-level recommendations
        system_stats = self.get_system_stats()
        
        if system_stats.get('current_cpu', 0) > 80:
            recommendations.append("⚠️ High CPU usage detected. Consider optimizing CPU-intensive operations.")
        
        if system_stats.get('current_memory', 0) > 85:
            recommendations.append("⚠️ High memory usage detected. Consider implementing data pagination or caching optimization.")
        
        if system_stats.get('available_memory_mb', float('inf')) < 500:
            recommendations.append("⚠️ Low available memory. Consider reducing data set sizes or implementing streaming.")
        
        # Function-level recommendations
        for func_name, metrics in self.function_metrics.items():
            stats = self.get_function_stats(func_name)
            
            if stats.get('avg_execution_time', 0) > 2.0:
                recommendations.append(f"🐌 Function '{func_name}' is slow (avg: {stats['avg_execution_time']:.2f}s). Consider caching or optimization.")
            
            if stats.get('error_rate', 0) > 10:
                recommendations.append(f"❌ Function '{func_name}' has high error rate ({stats['error_rate']:.1f}%). Review error handling.")
            
            if stats.get('avg_memory_usage', 0) > 100:  # MB
                recommendations.append(f"🧠 Function '{func_name}' uses significant memory ({stats['avg_memory_usage']:.1f}MB). Consider memory optimization.")
        
        if not recommendations:
            recommendations.append("✅ Performance looks good! No immediate optimizations needed.")
        
        return recommendations
    
    def render_streamlit_dashboard(self):
        """Render performance dashboard in Streamlit"""
        st.subheader("🔍 Performance Monitor")
        
        # System metrics
        col1, col2, col3, col4 = st.columns(4)
        system_stats = self.get_system_stats()
        
        with col1:
            st.metric("CPU Usage", f"{system_stats.get('current_cpu', 0):.1f}%")
        
        with col2:
            st.metric("Memory Usage", f"{system_stats.get('current_memory', 0):.1f}%")
        
        with col3:
            st.metric("Available Memory", f"{system_stats.get('available_memory_mb', 0):.0f} MB")
        
        with col4:
            st.metric("Monitoring", "Active" if system_stats.get('monitoring_active') else "Inactive")
        
        # Function performance
        if self.function_metrics:
            st.subheader("Function Performance")
            for func_name in self.function_metrics.keys():
                stats = self.get_function_stats(func_name)
                if stats and 'avg_execution_time' in stats:
                    with st.expander(f"📊 {func_name}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Avg Time", f"{stats['avg_execution_time']:.3f}s")
                            st.metric("Total Calls", stats['total_calls'])
                        
                        with col2:
                            st.metric("Min Time", f"{stats['min_execution_time']:.3f}s")
                            st.metric("Max Time", f"{stats['max_execution_time']:.3f}s")
                        
                        with col3:
                            st.metric("Memory Usage", f"{stats['avg_memory_usage']:.1f}MB")
                            st.metric("Error Rate", f"{stats['error_rate']:.1f}%")
        
        # Recommendations
        st.subheader("🚀 Performance Recommendations")
        recommendations = self.get_performance_recommendations()
        for rec in recommendations:
            st.write(rec)
    
    def export_metrics(self, format: str = 'dict') -> Any:
        """Export performance metrics in various formats"""
        data = {
            'system_stats': self.get_system_stats(),
            'function_stats': {
                name: self.get_function_stats(name) 
                for name in self.function_metrics.keys()
            },
            'recommendations': self.get_performance_recommendations(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format == 'dict':
            return data
        elif format == 'json':
            import json
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Global performance monitor instance
_performance_monitor: Optional[EnhancedPerformanceMonitor] = None

def get_performance_monitor() -> EnhancedPerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = EnhancedPerformanceMonitor()
    return _performance_monitor

def monitor_performance(track_args: bool = False):
    """Decorator shortcut for performance monitoring"""
    return get_performance_monitor().performance_monitor(track_args=track_args)
