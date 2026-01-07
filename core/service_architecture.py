"""
Service Layer Architecture Enhancement
Implements clean service boundaries with dependency injection and interfaces
"""
from abc import ABC, abstractmethod
from typing import Protocol, Optional, Dict, Any, List
import pandas as pd
from datetime import datetime
import logging

# Import from our local types package (not Python's built-in types module)
try:
    from custom_types.enhanced_types import BootstrapData, PlayerData, TeamData
except ImportError:
    # Fallback type definitions if the enhanced types aren't available
    BootstrapData = Dict[str, Any]
    PlayerData = Dict[str, Any] 
    TeamData = Dict[str, Any]


class IDataRepository(Protocol):
    """Interface for data repository implementations"""
    
    async def get_bootstrap_data(self) -> BootstrapData:
        """Get bootstrap data from source"""
        ...
    
    async def get_player_data(self, player_id: int) -> Optional[PlayerData]:
        """Get specific player data"""
        ...
    
    async def get_team_data(self, team_id: int) -> Optional[TeamData]:
        """Get specific team data"""
        ...


class IDataTransformer(Protocol):
    """Interface for data transformation services"""
    
    def transform_players_data(self, raw_data: BootstrapData) -> pd.DataFrame:
        """Transform raw players data to DataFrame"""
        ...
    
    def calculate_metrics(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived metrics"""
        ...
    
    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to data"""
        ...


class IAnalyticsEngine(Protocol):
    """Interface for analytics services"""
    
    def analyze_player_performance(self, player_id: int) -> Dict[str, Any]:
        """Analyze individual player performance"""
        ...
    
    def compare_players(self, player_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple players"""
        ...
    
    def generate_recommendations(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate player recommendations"""
        ...


class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"service.{name}")
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized


class DataService(BaseService):
    """Enhanced data service with clean architecture"""
    
    def __init__(
        self,
        repository: IDataRepository,
        transformer: IDataTransformer,
        cache_service: Optional['ICacheService'] = None
    ):
        super().__init__("data_service")
        self.repository = repository
        self.transformer = transformer
        self.cache_service = cache_service
    
    async def initialize(self) -> None:
        """Initialize data service"""
        self.logger.info("Initializing data service...")
        # Perform any initialization logic
        self._initialized = True
        self.logger.info("Data service initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check data service health"""
        return {
            "service": self.name,
            "status": "healthy" if self._initialized else "not_initialized",
            "timestamp": datetime.now().isoformat(),
            "repository_available": await self._check_repository_health(),
            "cache_available": self._check_cache_health()
        }
    
    async def get_players_data(self, use_cache: bool = True) -> pd.DataFrame:
        """Get players data with caching"""
        cache_key = "players_dataframe"
        
        # Try cache first
        if use_cache and self.cache_service:
            cached_data = self.cache_service.get(cache_key)
            if cached_data is not None:
                self.logger.debug("Retrieved players data from cache")
                return cached_data
        
        # Fetch from repository
        raw_data = await self.repository.get_bootstrap_data()
        players_df = self.transformer.transform_players_data(raw_data)
        players_df = self.transformer.calculate_metrics(players_df)
        
        # Cache the result
        if use_cache and self.cache_service:
            self.cache_service.set(cache_key, players_df, ttl=3600)  # 1 hour
        
        return players_df
    
    async def get_filtered_players(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Get filtered players data"""
        players_df = await self.get_players_data()
        return self.transformer.apply_filters(players_df, filters)
    
    async def _check_repository_health(self) -> bool:
        """Check if repository is healthy"""
        try:
            # Simple health check - could be more sophisticated
            await self.repository.get_bootstrap_data()
            return True
        except Exception:
            return False
    
    def _check_cache_health(self) -> bool:
        """Check if cache is healthy"""
        if not self.cache_service:
            return True  # No cache is fine
        
        try:
            # Simple cache health check
            self.cache_service.set("health_check", "ok", ttl=1)
            return self.cache_service.get("health_check") == "ok"
        except Exception:
            return False


class AnalyticsService(BaseService):
    """Enhanced analytics service"""
    
    def __init__(
        self,
        data_service: DataService,
        analytics_engine: IAnalyticsEngine
    ):
        super().__init__("analytics_service")
        self.data_service = data_service
        self.analytics_engine = analytics_engine
    
    async def initialize(self) -> None:
        """Initialize analytics service"""
        self.logger.info("Initializing analytics service...")
        # Ensure data service is initialized
        if not self.data_service.is_initialized():
            await self.data_service.initialize()
        
        self._initialized = True
        self.logger.info("Analytics service initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check analytics service health"""
        data_health = await self.data_service.health_check()
        
        return {
            "service": self.name,
            "status": "healthy" if self._initialized else "not_initialized",
            "timestamp": datetime.now().isoformat(),
            "dependencies": {
                "data_service": data_health["status"]
            }
        }
    
    async def get_player_analysis(self, player_id: int) -> Dict[str, Any]:
        """Get comprehensive player analysis"""
        # This would use the analytics engine
        return self.analytics_engine.analyze_player_performance(player_id)
    
    async def compare_players_analysis(self, player_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple players"""
        return self.analytics_engine.compare_players(player_ids)
    
    async def get_recommendations(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get player recommendations"""
        return self.analytics_engine.generate_recommendations(criteria)


class ServiceRegistry:
    """Registry for managing application services"""
    
    def __init__(self):
        self._services: Dict[str, BaseService] = {}
        self.logger = logging.getLogger("service_registry")
    
    def register(self, service: BaseService) -> None:
        """Register a service"""
        self._services[service.name] = service
        self.logger.info(f"Registered service: {service.name}")
    
    def get(self, name: str) -> Optional[BaseService]:
        """Get a service by name"""
        return self._services.get(name)
    
    def get_required(self, name: str) -> BaseService:
        """Get a required service (raises if not found)"""
        service = self.get(name)
        if service is None:
            raise ValueError(f"Required service '{name}' not found")
        return service
    
    async def initialize_all(self) -> None:
        """Initialize all registered services"""
        self.logger.info("Initializing all services...")
        
        for service in self._services.values():
            if not service.is_initialized():
                await service.initialize()
        
        self.logger.info("All services initialized")
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Run health checks on all services"""
        results = {}
        
        for name, service in self._services.items():
            try:
                results[name] = await service.health_check()
            except Exception as e:
                results[name] = {
                    "service": name,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    @property
    def service_names(self) -> List[str]:
        """Get list of registered service names"""
        return list(self._services.keys())


# Global service registry
service_registry = ServiceRegistry()