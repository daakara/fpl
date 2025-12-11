"""
Enhanced Type System for FPL Analytics

This module provides comprehensive type definitions, protocols, and validation
utilities for the entire FPL Analytics application.
"""

from typing import Protocol, TypedDict, Union, Optional, List, Dict, Any, Callable, TypeVar, Generic
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path

# Generic type variables
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# FPL API Response Types
class PlayerElement(TypedDict, total=False):
    """Complete type definition for FPL Player data from API.
    
    This type represents the full player object as returned by the FPL API
    bootstrap-static endpoint. All fields are optional to handle partial
    data scenarios.
    """
    # Basic Info
    id: int
    web_name: str
    first_name: str
    second_name: str
    element_type: int
    team: int
    code: int
    
    # Performance Stats
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
    
    # Advanced Stats
    influence: str
    creativity: str
    threat: str
    ict_index: str
    starts: int
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str
    
    # Status Info
    status: str
    chance_of_playing_this_round: Optional[int]
    chance_of_playing_next_round: Optional[int]
    value_form: str
    value_season: str
    cost_change_start: int
    cost_change_event: int
    cost_change_start_fall: int
    cost_change_event_fall: int
    in_dreamteam: bool
    dreamteam_count: int
    ep_this: Optional[str]
    ep_next: Optional[str]
    special: bool
    squad_number: Optional[int]
    news: str
    news_added: Optional[str]
    photo: str
    
    # Transfer Info
    transfers_in: int
    transfers_out: int
    transfers_in_event: int
    transfers_out_event: int


class TeamElement(TypedDict):
    """Type definition for FPL Team data from API."""
    id: int
    name: str
    short_name: str
    code: int
    draw: int
    form: Optional[str]
    loss: int
    played: int
    points: int
    position: int
    strength: int
    team_division: Optional[int]
    unavailable: bool
    win: int
    strength_overall_home: int
    strength_overall_away: int
    strength_attack_home: int
    strength_attack_away: int
    strength_defence_home: int
    strength_defence_away: int
    pulse_id: int


class ElementTypeElement(TypedDict):
    """Type definition for player position types."""
    id: int
    plural_name: str
    plural_name_short: str
    singular_name: str
    singular_name_short: str
    squad_select: int
    squad_min_play: int
    squad_max_play: int
    ui_shirt_specific: bool
    sub_positions_locked: List[int]
    element_count: int


class GameweekElement(TypedDict):
    """Type definition for gameweek/event data."""
    id: int
    name: str
    deadline_time: str
    average_entry_score: int
    finished: bool
    data_checked: bool
    highest_scoring_entry: Optional[int]
    deadline_time_epoch: int
    deadline_time_game_offset: int
    highest_score: Optional[int]
    is_previous: bool
    is_current: bool
    is_next: bool
    cup_leagues_created: bool
    h2h_ko_matches_created: bool
    most_selected: Optional[int]
    most_transferred_in: Optional[int]
    top_element: Optional[int]
    top_element_info: Optional[Dict[str, Any]]
    transfers_made: int
    most_captained: Optional[int]
    most_vice_captained: Optional[int]


class BootstrapStaticData(TypedDict):
    """Complete FPL bootstrap-static API response."""
    elements: List[PlayerElement]
    teams: List[TeamElement]
    element_types: List[ElementTypeElement]
    events: List[GameweekElement]
    game_settings: Dict[str, Any]
    phases: List[Dict[str, Any]]
    total_players: int


# Application State Types
class FilterState(TypedDict, total=False):
    """Type for UI filter state."""
    position: Optional[str]
    team: Optional[str]
    price_min: Optional[float]
    price_max: Optional[float]
    points_min: Optional[int]
    points_max: Optional[int]
    form_min: Optional[float]
    ownership_min: Optional[float]
    ownership_max: Optional[float]


class UserTeamData(TypedDict):
    """Type for user's FPL team data."""
    id: int
    name: str
    player_first_name: str
    player_last_name: str
    player_region_id: int
    player_region_name: str
    player_region_iso_code_short: str
    player_region_iso_code_long: str
    summary_overall_points: int
    summary_overall_rank: int
    summary_event_points: int
    summary_event_rank: int
    current_event: int
    leagues: Dict[str, Any]
    name_change_blocked: bool
    entered_events: List[int]
    kit: Optional[Dict[str, str]]
    last_deadline_bank: int
    last_deadline_value: int
    last_deadline_total_transfers: int


class AppSessionState(TypedDict, total=False):
    """Type for Streamlit session state."""
    current_page: str
    user_team_id: Optional[int]
    selected_gameweek: Optional[int]
    filters: FilterState
    theme: str
    cache_enabled: bool
    debug_mode: bool
    last_data_refresh: Optional[datetime]
    selected_players: List[int]
    comparison_players: List[int]


# Configuration Types
@dataclass(frozen=True)
class APIConfiguration:
    """Immutable API configuration with validation."""
    base_url: str = "https://fantasy.premierleague.com/api"
    timeout: int = 30
    max_retries: int = 3
    rate_limit_delay: float = 1.0
    verify_ssl: bool = False
    user_agent: str = "FPL-Analytics-Dashboard/1.0"
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        if not self.base_url.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")


@dataclass(frozen=True)
class CacheConfiguration:
    """Immutable cache configuration with validation."""
    enabled: bool = True
    ttl_seconds: int = 3600
    max_size_mb: int = 100
    cache_dir: str = "cache"
    redis_url: Optional[str] = None
    compression_enabled: bool = True
    
    def __post_init__(self):
        """Validate cache configuration."""
        if self.ttl_seconds <= 0:
            raise ValueError("TTL must be positive")
        if self.max_size_mb <= 0:
            raise ValueError("Max size must be positive")


@dataclass(frozen=True)
class MLModelConfiguration:
    """Configuration for machine learning models."""
    model_type: str = "xgboost"
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    feature_columns: List[str] = field(default_factory=list)
    target_column: str = "total_points"
    test_size: float = 0.2
    cv_folds: int = 5
    enable_feature_selection: bool = True
    random_state: int = 42
    
    def __post_init__(self):
        """Validate ML configuration."""
        if not 0 < self.test_size < 1:
            raise ValueError("Test size must be between 0 and 1")
        if self.cv_folds <= 1:
            raise ValueError("CV folds must be greater than 1")


# Error and Logging Types
class ErrorSeverity(IntEnum):
    """Error severity levels with numeric ordering."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ErrorCategory(Enum):
    """Comprehensive error categories."""
    API_ERROR = "api_error"
    DATA_ERROR = "data_error"
    UI_ERROR = "ui_error"
    CACHE_ERROR = "cache_error"
    ML_ERROR = "ml_error"
    CONFIG_ERROR = "config_error"
    AUTHENTICATION_ERROR = "auth_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"


@dataclass
class ErrorContext:
    """Context information for errors."""
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    page: Optional[str] = None
    action: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Service Interface Protocols
class DataServiceProtocol(Protocol):
    """Protocol defining the interface for data services."""
    
    def get_bootstrap_data(self) -> BootstrapStaticData:
        """Retrieve bootstrap data from FPL API."""
        ...
    
    def get_player_data(self, player_id: int) -> Optional[PlayerElement]:
        """Get specific player data by ID."""
        ...
    
    def get_team_data(self, team_id: int) -> Optional[TeamElement]:
        """Get specific team data by ID."""
        ...
    
    def test_connection(self) -> bool:
        """Test connection to the FPL API."""
        ...


class CacheServiceProtocol(Protocol):
    """Protocol for cache service implementations."""
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in cache with optional TTL."""
        ...
    
    def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        ...
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        ...
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...


class PerformanceMonitorProtocol(Protocol):
    """Protocol for performance monitoring services."""
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        ...
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        ...
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a performance metric."""
        ...
    
    def get_metrics(self, time_range: Optional[int] = None) -> Dict[str, Any]:
        """Get performance metrics for specified time range."""
        ...


class UIComponentProtocol(Protocol):
    """Protocol for UI components."""
    
    def render(self, **kwargs: Any) -> None:
        """Render the UI component."""
        ...
    
    def validate_props(self, **kwargs: Any) -> bool:
        """Validate component properties."""
        ...


# Analytics Types
@dataclass
class PlayerAnalysis:
    """Result from player performance analysis."""
    player_id: int
    player_name: str
    current_score: float
    predicted_score: float
    confidence: float
    key_metrics: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str
    analysis_date: datetime


@dataclass
class TeamOptimization:
    """Result from team optimization analysis."""
    formation: str
    selected_players: List[int]
    total_cost: float
    predicted_points: float
    optimization_score: float
    constraints_met: bool
    alternative_options: List[Dict[str, Any]]
    optimization_date: datetime


@dataclass
class ComparisonResult:
    """Result from player comparison analysis."""
    players: List[int]
    comparison_metrics: Dict[str, Dict[int, float]]
    winner: Optional[int]
    summary: str
    detailed_analysis: Dict[str, Any]
    comparison_date: datetime


# Real-time Data Types
class UpdateType(Enum):
    """Types of real-time updates."""
    PLAYER_POINTS = "player_points"
    LIVE_SCORES = "live_scores"
    TEAM_NEWS = "team_news"
    PRICE_CHANGES = "price_changes"
    INJURY_UPDATES = "injury_updates"
    LINEUP_UPDATES = "lineup_updates"


@dataclass
class LiveUpdate:
    """Structure for real-time updates."""
    update_type: UpdateType
    data: Dict[str, Any]
    timestamp: datetime
    gameweek: int
    priority: int = 1
    source: str = "fpl_api"


# Validation Types
class ValidationRule(Protocol):
    """Protocol for validation rules."""
    
    def validate(self, value: Any) -> bool:
        """Validate a value against this rule."""
        ...
    
    def get_error_message(self) -> str:
        """Get error message for validation failure."""
        ...


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# Utility Types
PathLike = Union[str, Path]
JSONSerializable = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
CacheKey = str
Timestamp = Union[datetime, str, int, float]

# Component Property Types
ComponentProps = Dict[str, Any]
RenderFunction = Callable[[], None]
EventHandler = Callable[[Any], None]

# Database Types (for future implementation)
class DatabaseProtocol(Protocol):
    """Protocol for database operations."""
    
    def connect(self) -> bool:
        """Connect to database."""
        ...
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute database query."""
        ...
    
    def close(self) -> None:
        """Close database connection."""
        ...


# Type aliases for commonly used complex types
PlayerDataFrame = pd.DataFrame  # DataFrame containing player data
TeamDataFrame = pd.DataFrame    # DataFrame containing team data  
MetricsDict = Dict[str, Union[str, int, float]]  # Dictionary of metrics
FilterDict = Dict[str, Any]     # Dictionary of filter parameters
ConfigDict = Dict[str, Any]     # Configuration dictionary


# Type guards for runtime type checking
def is_player_element(obj: Any) -> bool:
    """Type guard to check if object is a valid PlayerElement."""
    required_fields = ['id', 'web_name', 'element_type', 'team', 'total_points', 'now_cost']
    return isinstance(obj, dict) and all(field in obj for field in required_fields)


def is_bootstrap_data(obj: Any) -> bool:
    """Type guard to check if object is valid bootstrap data."""
    required_fields = ['elements', 'teams', 'element_types', 'events']
    return isinstance(obj, dict) and all(field in obj for field in required_fields)


# Generic container types
class Repository(Generic[T], Protocol):
    """Generic repository protocol."""
    
    def get(self, id: K) -> Optional[T]:
        """Get entity by ID."""
        ...
    
    def save(self, entity: T) -> bool:
        """Save entity."""
        ...
    
    def delete(self, id: K) -> bool:
        """Delete entity by ID."""
        ...
    
    def list_all(self) -> List[T]:
        """List all entities."""
        ...


class Service(Generic[T], Protocol):
    """Generic service protocol."""
    
    def initialize(self) -> None:
        """Initialize the service."""
        ...
    
    def process(self, data: T) -> T:
        """Process data."""
        ...
    
    def cleanup(self) -> None:
        """Cleanup service resources."""
        ...


# Factory type for creating services
ServiceFactory = Callable[..., Any]
ComponentFactory = Callable[[ComponentProps], UIComponentProtocol]