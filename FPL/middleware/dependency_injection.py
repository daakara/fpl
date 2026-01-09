"""
Dependency Injection Container
Implements container pattern for better testability and easier mocking
"""

from typing import Any, Dict, Type, TypeVar, Callable, Optional, Union
from abc import ABC, abstractmethod
import inspect
from functools import wraps
import threading

T = TypeVar('T')

class ContainerError(Exception):
    """Exception raised by the DI container"""
    pass

class Singleton:
    """Marker class to indicate singleton lifetime"""
    pass

class Transient:
    """Marker class to indicate transient lifetime"""
    pass

class Scoped:
    """Marker class to indicate scoped lifetime"""
    pass

class ServiceLifetime:
    """Service lifetime management"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class IContainer(ABC):
    """Abstract interface for dependency injection container"""
    
    @abstractmethod
    def register(self, interface: Type[T], implementation: Union[Type[T], Callable[[], T]], 
                lifetime: str = ServiceLifetime.TRANSIENT) -> None:
        """Register a service with the container"""
        pass
    
    @abstractmethod
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service from the container"""
        pass
    
    @abstractmethod
    def is_registered(self, interface: Type[T]) -> bool:
        """Check if a service is registered"""
        pass

class DIContainer(IContainer):
    """Dependency Injection Container implementation"""
    
    def __init__(self):
        self._services: Dict[Type, Dict[str, Any]] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()
        self._scope_active = False
    
    def register(self, interface: Type[T], implementation: Union[Type[T], Callable[[], T]], 
                lifetime: str = ServiceLifetime.TRANSIENT) -> 'DIContainer':
        """Register a service with the container"""
        with self._lock:
            if interface in self._services:
                raise ContainerError(f"Service {interface.__name__} is already registered")
            
            self._services[interface] = {
                'implementation': implementation,
                'lifetime': lifetime,
                'dependencies': self._get_dependencies(implementation) if inspect.isclass(implementation) else []
            }
        
        return self
    
    def register_singleton(self, interface: Type[T], implementation: Union[Type[T], Callable[[], T]]) -> 'DIContainer':
        """Register a singleton service"""
        return self.register(interface, implementation, ServiceLifetime.SINGLETON)
    
    def register_transient(self, interface: Type[T], implementation: Union[Type[T], Callable[[], T]]) -> 'DIContainer':
        """Register a transient service"""
        return self.register(interface, implementation, ServiceLifetime.TRANSIENT)
    
    def register_scoped(self, interface: Type[T], implementation: Union[Type[T], Callable[[], T]]) -> 'DIContainer':
        """Register a scoped service"""
        return self.register(interface, implementation, ServiceLifetime.SCOPED)
    
    def register_instance(self, interface: Type[T], instance: T) -> 'DIContainer':
        """Register a specific instance as singleton"""
        with self._lock:
            self._services[interface] = {
                'implementation': lambda: instance,
                'lifetime': ServiceLifetime.SINGLETON,
                'dependencies': []
            }
            self._singletons[interface] = instance
        return self
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service from the container"""
        with self._lock:
            if interface not in self._services:
                raise ContainerError(f"Service {interface.__name__} is not registered")
            
            service_info = self._services[interface]
            lifetime = service_info['lifetime']
            
            # Handle singleton lifetime
            if lifetime == ServiceLifetime.SINGLETON:
                if interface not in self._singletons:
                    self._singletons[interface] = self._create_instance(interface, service_info)
                return self._singletons[interface]
            
            # Handle scoped lifetime
            elif lifetime == ServiceLifetime.SCOPED:
                if not self._scope_active:
                    raise ContainerError("Cannot resolve scoped service outside of scope")
                
                if interface not in self._scoped_instances:
                    self._scoped_instances[interface] = self._create_instance(interface, service_info)
                return self._scoped_instances[interface]
            
            # Handle transient lifetime
            else:
                return self._create_instance(interface, service_info)
    
    def _create_instance(self, interface: Type[T], service_info: Dict[str, Any]) -> T:
        """Create an instance of the service"""
        implementation = service_info['implementation']
        dependencies = service_info['dependencies']
        
        # If it's a factory function
        if callable(implementation) and not inspect.isclass(implementation):
            return implementation()
        
        # If it's a class with dependencies
        if dependencies:
            resolved_deps = {}
            for dep_name, dep_type in dependencies.items():
                resolved_deps[dep_name] = self.resolve(dep_type)
            return implementation(**resolved_deps)
        
        # If it's a simple class
        return implementation()
    
    def _get_dependencies(self, implementation: Type) -> Dict[str, Type]:
        """Extract dependencies from constructor signature"""
        if not inspect.isclass(implementation):
            return {}
        
        try:
            signature = inspect.signature(implementation.__init__)
            dependencies = {}
            
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    dependencies[param_name] = param.annotation
            
            return dependencies
        except Exception:
            return {}
    
    def is_registered(self, interface: Type[T]) -> bool:
        """Check if a service is registered"""
        return interface in self._services
    
    def start_scope(self) -> 'DIContainer':
        """Start a new scope for scoped services"""
        self._scope_active = True
        self._scoped_instances.clear()
        return self
    
    def end_scope(self) -> 'DIContainer':
        """End the current scope"""
        self._scope_active = False
        self._scoped_instances.clear()
        return self
    
    def clear(self) -> None:
        """Clear all registrations"""
        with self._lock:
            self._services.clear()
            self._singletons.clear()
            self._scoped_instances.clear()
            self._scope_active = False
    
    def get_registration_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered services"""
        info = {}
        for interface, service_info in self._services.items():
            info[interface.__name__] = {
                'implementation': service_info['implementation'].__name__ if hasattr(service_info['implementation'], '__name__') else str(service_info['implementation']),
                'lifetime': service_info['lifetime'],
                'dependencies': list(service_info['dependencies'].keys()) if service_info['dependencies'] else [],
                'is_singleton_created': interface in self._singletons
            }
        return info

class ScopedContainer:
    """Context manager for scoped services"""
    
    def __init__(self, container: DIContainer):
        self.container = container
    
    def __enter__(self) -> DIContainer:
        self.container.start_scope()
        return self.container
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.end_scope()

def injectable(*dependencies: Type):
    """Decorator to mark a class as injectable and specify its dependencies"""
    def decorator(cls):
        # Store dependency information
        cls._injectable_dependencies = dependencies
        
        # Modify the __init__ method to accept container
        original_init = cls.__init__
        
        @wraps(original_init)
        def new_init(self, container: Optional[DIContainer] = None, **kwargs):
            if container:
                # Resolve dependencies from container
                resolved_deps = {}
                for dep in dependencies:
                    if dep not in kwargs:  # Don't override explicitly provided dependencies
                        resolved_deps[dep.__name__.lower()] = container.resolve(dep)
                kwargs.update(resolved_deps)
            
            original_init(self, **kwargs)
        
        cls.__init__ = new_init
        return cls
    
    return decorator

def inject(dependency_type: Type[T]) -> Callable[[DIContainer], T]:
    """Function to inject a dependency"""
    def injector(container: DIContainer) -> T:
        return container.resolve(dependency_type)
    return injector

# Global container instance
_global_container: Optional[DIContainer] = None

def get_container() -> DIContainer:
    """Get the global container instance"""
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container

def configure_container() -> DIContainer:
    """Configure the global container with default services"""
    container = get_container()
    
    # Import and register core services (only if not already registered)
    try:
        from middleware.error_handling import ErrorHandlingMiddleware
        if not container.is_registered(ErrorHandlingMiddleware):
            container.register_singleton(ErrorHandlingMiddleware, ErrorHandlingMiddleware)
    except ImportError:
        pass
    
    try:
        from services.enhanced_fpl_data_service import EnhancedFPLDataService
        if not container.is_registered(EnhancedFPLDataService):
            container.register_singleton(EnhancedFPLDataService, EnhancedFPLDataService)
    except ImportError:
        pass
    
    try:
        from utils.advanced_cache_manager import AdvancedCacheManager
        if not container.is_registered(AdvancedCacheManager):
            container.register_singleton(AdvancedCacheManager, AdvancedCacheManager)
    except ImportError:
        pass
    
    try:
        from components.ai.player_insights import SmartPlayerInsights
        if not container.is_registered(SmartPlayerInsights):
            container.register_singleton(SmartPlayerInsights, SmartPlayerInsights)
    except ImportError:
        pass
    
    try:
        from components.ui.theme_manager import ThemeManager
        if not container.is_registered(ThemeManager):
            container.register_singleton(ThemeManager, ThemeManager)
    except ImportError:
        pass
    
    try:
        from components.ui.dashboard_exporter import DashboardExporter
        if not container.is_registered(DashboardExporter):
            container.register_singleton(DashboardExporter, DashboardExporter)
    except ImportError:
        pass
    
    return container

def reset_container() -> None:
    """Reset the global container (useful for testing)"""
    global _global_container
    if _global_container:
        _global_container.clear()
    _global_container = None
