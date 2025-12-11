"""
Type definitions and interfaces for the FPL Analytics application
Provides comprehensive type safety across the application
"""
from typing import Protocol, TypedDict, Union, Optional, List, Dict, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


# API Response Types
class PlayerData(TypedDict):
    """Type definition for FPL Player data from API"""
    id: int
    web_name: str
    element_type: int
    team: int
    total_points: int
    now_cost: int
    selected_by_percent: str
    form: str
    points_per_game: str
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: str
    creativity: str
    threat: str
    ict_index: str
    starts: int
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str


class TeamData(TypedDict):
    """Type definition for FPL Team data from API"""
    id: int
    name: str
    short_name: str
    strength: int
    strength_overall_home: int
    strength_overall_away: int
    strength_attack_home: int
    strength_attack_away: int
    strength_defence_home: int
    strength_defence_away: int


class BootstrapData(TypedDict):
    """Type definition for FPL Bootstrap data from API"""
    elements: List[PlayerData]
    teams: List[TeamData]
    element_types: List[Dict[str, Any]]
    events: List[Dict[str, Any]]


# Service Interface Protocols
class DataServiceProtocol(Protocol):
    """Protocol for data service implementations"""
    
    def get_bootstrap_data(self) -> BootstrapData:
        """Get bootstrap data from FPL API"""
        ...
    
    def get_player_data(self, player_id: int) -> Optional[PlayerData]:
        """Get specific player data"""
        ...
    
    def test_connection(self) -> bool:
        """Test API connection"""
        ...


class CacheServiceProtocol(Protocol):
    """Protocol for cache service implementations"""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ...
    
    def invalidate(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        ...


class PerformanceMonitorProtocol(Protocol):
    """Protocol for performance monitoring"""
    
    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        ...
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a performance metric"""
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        ...


# Application State Types
class FilterState(TypedDict, total=False):
    """Type for filter state"""
    position: Optional[str]
    team: Optional[str]
    price_min: Optional[float]
    price_max: Optional[float]
    points_min: Optional[int]


class AppState(TypedDict, total=False):
    """Type for application state"""
    current_page: str
    user_team_id: Optional[int]
    selected_gameweek: Optional[int]
    filters: FilterState
    theme: str


# Configuration Types
@dataclass(frozen=True)
class APIConfiguration:
    """Immutable API configuration"""
    base_url: str
    timeout: int
    max_retries: int
    rate_limit_delay: float
    verify_ssl: bool


@dataclass(frozen=True) 
class CacheConfiguration:
    """Immutable cache configuration"""
    enabled: bool
    ttl_seconds: int
    max_size_mb: int
    cache_dir: str


# Error Types
class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"  
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    API_ERROR = "api_error"
    DATA_ERROR = "data_error"
    UI_ERROR = "ui_error" 
    CACHE_ERROR = "cache_error"
    SYSTEM_ERROR = "system_error"


# Component Types
ComponentProps = Dict[str, Any]
RenderFunction = Callable[[], None]


# Utility Types  
JSONSerializable = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
CacheKey = str
Timestamp = datetime


# Analysis Types
class AnalysisResult(TypedDict):
    """Result from player analysis"""
    player_id: int
    player_name: str
    recommendation: str
    confidence_score: float
    reasons: List[str]
    metrics: Dict[str, float]


class ComparisonResult(TypedDict):
    """Result from player comparison"""
    players: List[int]
    winner: int
    comparison_metrics: Dict[str, Dict[int, float]]
    summary: str