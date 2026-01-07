# FPL Analytics - Architecture Documentation

**Version:** 2.0 (Refactored Architecture)  
**Date:** January 7, 2026  
**Status:** In Progress - Architecture Improvements Phase

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Directory Structure](#directory-structure)
4. [Core Modules](#core-modules)
5. [Service Layer](#service-layer)
6. [View Layer](#view-layer)
7. [Data Flow](#data-flow)
8. [Caching Strategy](#caching-strategy)
9. [Error Handling](#error-handling)
10. [Migration Guide](#migration-guide)

---

## Overview

The FPL Analytics application follows a **clean, layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│          Views (Streamlit UI)           │
│  ┌─────────────────────────────────┐   │
│  │   dashboard, player_analysis,    │   │
│  │   team_builder, live_alerts      │   │
│  └─────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Services (Business Logic)       │
│  ┌─────────────────────────────────┐   │
│  │  analytics, recommendations,     │   │
│  │  predictions, export/import      │   │
│  └─────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Core (Data & Infrastructure)    │
│  ┌──────────────┬──────────────────┐   │
│  │    Data      │      Cache       │   │
│  │  ┌────────┐  │   ┌──────────┐  │   │
│  │  │Fetcher │  │   │ Manager  │  │   │
│  │  │Validator│ │   │ TTL      │  │   │
│  │  │Transform│ │   │ Strategy │  │   │
│  │  └────────┘  │   └──────────┘  │   │
│  └──────────────┴──────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Middleware (Cross-cutting Concerns)  │
│  Error Handling │ Logging │ DI          │
└──────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          FPL API / External Data         │
└──────────────────────────────────────────┘
```

---

## Architecture Principles

### 1. **Single Responsibility**
- Each module has one clear purpose
- No mixing of data fetching, transformation, and presentation

### 2. **Dependency Injection**
- Services receive dependencies through constructors
- Easy testing and mocking

### 3. **Interface Segregation**
- Clear, minimal interfaces for each service
- Clients don't depend on methods they don't use

### 4. **DRY (Don't Repeat Yourself)**
- Single source of truth for each concern
- Shared utilities in centralized modules

### 5. **Fail-Safe Defaults**
- Graceful degradation when APIs fail
- Fallback data for offline operation

---

## Directory Structure

### New Unified Structure

```
fpl/
├── main_modular.py              # 📍 Production entry point
├── 
├── core/                        # ⚙️ Core infrastructure
│   ├── data/                    # 🔄 Data management
│   │   ├── __init__.py
│   │   ├── fetcher.py           # API data fetching (SINGLE SOURCE)
│   │   ├── validator.py         # Data quality validation
│   │   └── transformer.py       # Type conversion & enrichment
│   │
│   ├── cache/                   # 💾 Caching strategy
│   │   ├── __init__.py
│   │   └── manager.py           # Unified cache management
│   │
│   ├── analytics/               # 📊 Analytics engines (TODO)
│   │   ├── calculator.py        # Core calculations
│   │   ├── predictor.py         # ML predictions
│   │   └── optimizer.py         # Team optimization
│   │
│   ├── app_controller.py        # Main app orchestration
│   ├── page_router.py           # Page routing
│   ├── header_component.py      # Header UI
│   └── sidebar_component.py     # Sidebar UI
│
├── services/                    # 🔧 Business services
│   ├── __init__.py
│   ├── advanced_analytics_engine.py      # Expected points, differentials
│   ├── player_recommendation_service.py  # Player suggestions
│   ├── hidden_gems_discovery.py          # Low-ownership finds
│   ├── price_change_predictor_service.py # Price predictions
│   ├── transfer_planning_service.py      # Transfer optimization
│   ├── fixture_service.py                # Fixture analysis
│   ├── data_export_import.py             # Import/export
│   └── ...
│
├── views/                       # 🎨 UI pages
│   ├── __init__.py
│   ├── dashboard_page.py        # Main dashboard
│   ├── player_analysis_page.py  # Player deep-dive
│   ├── team_builder_page.py     # Team construction
│   ├── fixture_analysis_page.py # Fixture difficulty
│   ├── ai_recommendations_page.py # AI insights
│   ├── live_data_page.py        # Live gameweek data
│   ├── my_team_page.py          # User team analysis
│   └── price_changes_page.py    # Price change tracking
│
├── middleware/                  # 🛡️ Cross-cutting concerns
│   ├── error_handling.py        # Centralized error handling
│   ├── logging_strategy.py      # Structured logging
│   └── dependency_injection.py  # DI container
│
├── utils/                       # 🔨 Utilities
│   ├── error_handling.py        # Logger setup
│   ├── error_recovery.py        # Circuit breaker
│   ├── modern_ui_components.py  # UI helpers
│   ├── enhanced_visualizations.py # Chart utilities
│   └── ...
│
├── config/                      # ⚙️ Configuration
│   ├── secure_config.py         # Secure config management
│   └── app_config.py            # App settings
│
└── tests/                       # 🧪 Test suite
    ├── test_integration.py
    └── ...
```

### Deprecated/Legacy Files (To Be Removed)

```
❌ views/my_team_page_backup.py
❌ views/my_team_page_new.py
❌ views/live_data_page_legacy.py
❌ main_resilient_backup.py
❌ main_resilient_clean.py
❌ main_resilient_compatibility.py
❌ main_complete.py
❌ main_comprehensive.py
❌ main_enhanced.py
❌ main_integrated.py
❌ services/fpl_data_service.py (replaced by core/data/fetcher.py)
❌ services/enhanced_fpl_data_service.py (replaced by core/data/fetcher.py)
```

---

## Core Modules

### core/data/

**Purpose:** Single source of truth for all FPL data operations

#### fetcher.py - FPLDataFetcher
**Responsibility:** Fetch data from FPL API

```python
from core.data import get_fpl_data_fetcher

fetcher = get_fpl_data_fetcher()
players_df, teams_df = fetcher.load_fpl_data()
```

**Features:**
- ✅ Streamlit-integrated caching (@st.cache_data)
- ✅ Circuit breaker pattern
- ✅ Automatic retry with exponential backoff
- ✅ SSL handling for corporate environments
- ✅ Type-safe data validation

**Key Methods:**
- `get_bootstrap_data()` - Main data endpoint (cached 1hr)
- `get_fixtures(event)` - Fixture data (cached 30min)
- `get_player_history(player_id)` - Player history (cached 30min)
- `get_live_gameweek_data(event)` - Live GW data (cached 30min)
- `get_players_dataframe()` - Processed players DataFrame
- `get_teams_dataframe()` - Processed teams DataFrame

#### validator.py - DataValidator
**Responsibility:** Ensure data quality and integrity

```python
from core.data import get_data_validator

validator = get_data_validator()
clean_df = validator.validate_and_clean(raw_df, 'players')
```

**Features:**
- ✅ Schema validation
- ✅ Type checking and enforcement
- ✅ Missing value detection
- ✅ Outlier detection
- ✅ Range validation

#### transformer.py - DataTransformer
**Responsibility:** Convert and enrich data

```python
from core.data import get_data_transformer

transformer = get_data_transformer()
enriched_df = transformer.transform_players(raw_df, teams_df)
```

**Features:**
- ✅ Type conversion (strings → numbers)
- ✅ Derived columns (price_millions, value_score)
- ✅ Data enrichment (team names, positions)
- ✅ Per-90 statistics
- ✅ Form indicators

### core/cache/

**Purpose:** Unified caching strategy across the application

#### manager.py - CacheManager

```python
from core.cache import get_cache_manager, CacheTTL, cache_5min

# Using decorators
@cache_5min
def expensive_operation():
    return fetch_from_api()

# Using cache manager
cache = get_cache_manager()
cache.clear_all_caches()
```

**TTL Standards:**
- `VERY_SHORT` = 60s (live scores, price changes)
- `SHORT` = 300s (player form, ownership)
- `MEDIUM` = 900s (player stats, team data)
- `LONG` = 3600s (bootstrap data, fixtures)
- `VERY_LONG` = 7200s (historical data)
- `PERMANENT` = 86400s (static data)

---

## Service Layer

Services contain business logic and orchestrate core modules.

### Key Services:

1. **advanced_analytics_engine.py**
   - Expected points calculation
   - Differential finder
   - Captaincy EV analysis
   - Team synergy scoring

2. **player_recommendation_service.py**
   - AI-powered player suggestions
   - Position-specific recommendations
   - Budget-aware suggestions

3. **hidden_gems_discovery.py**
   - Low-ownership, high-potential players
   - Multi-tier discovery (Budget/Mid/Premium)
   - Form-based filtering

4. **fixture_service.py**
   - Fixture difficulty analysis
   - Team form vs fixtures
   - Swing gameweek detection

5. **price_change_predictor_service.py**
   - Net transfer tracking
   - Price rise/fall predictions
   - Alert generation

---

## View Layer

Views are pure UI - no business logic or data fetching.

### Responsibilities:
- ✅ Render Streamlit components
- ✅ Handle user input
- ✅ Call services for data
- ✅ Display results

### Anti-patterns to Avoid:
- ❌ Direct API calls from views
- ❌ Business logic in views
- ❌ Data transformation in views

### Example Pattern:

```python
# views/player_analysis_page.py

from core.data import get_fpl_data_fetcher
from services.player_recommendation_service import PlayerRecommendationService

def render():
    # 1. Get data from core
    fetcher = get_fpl_data_fetcher()
    players_df = fetcher.get_players_dataframe()
    
    # 2. Use services for business logic
    rec_service = PlayerRecommendationService()
    recommendations = rec_service.get_recommendations(players_df)
    
    # 3. Render UI
    st.title("Player Analysis")
    st.dataframe(recommendations)
```

---

## Data Flow

### Standard Data Flow Pattern:

```
1. User Action (View)
       ↓
2. Service Call (Business Logic)
       ↓
3. Core Data Fetch (if needed)
       ├─→ Check Cache (CacheManager)
       │   ├─→ Hit: Return cached data
       │   └─→ Miss: Proceed to API
       ├─→ API Call (FPLDataFetcher)
       ├─→ Validate (DataValidator)
       └─→ Transform (DataTransformer)
       ↓
4. Service Processing
       ↓
5. Return to View
       ↓
6. Render UI
```

### Example Flow: Getting Top Players

```python
# View layer
def render_dashboard():
    service = get_dashboard_service()
    top_players = service.get_top_players()
    st.dataframe(top_players)

# Service layer
class DashboardService:
    def get_top_players(self):
        fetcher = get_fpl_data_fetcher()
        players_df = fetcher.get_players_dataframe()  # Cached
        return players_df.nlargest(10, 'total_points')
```

---

## Caching Strategy

### Caching Layers:

1. **Streamlit Cache** (`@st.cache_data`)
   - Automatic cache key generation
   - TTL-based invalidation
   - Shared across sessions

2. **Service-Level Cache**
   - Expensive calculations
   - ML model predictions
   - Aggregated statistics

3. **Resource Cache** (`@st.cache_resource`)
   - Service instances
   - Database connections
   - ML models

### Best Practices:

```python
# ✅ DO: Use appropriate TTL
@cache_with_ttl(CacheTTL.MEDIUM)
def get_player_stats(player_id):
    return fetch_stats(player_id)

# ✅ DO: Exclude instance from cache key
@st.cache_data(ttl=300)
def get_data(_self, player_id):  # Note: _self
    return _self.fetch(player_id)

# ❌ DON'T: Cache user-specific data globally
@st.cache_data  # Bad - will cache for all users
def get_my_team(team_id):
    return fetch_team(team_id)
```

---

## Error Handling

### Three-Layer Error Handling:

1. **Middleware Layer** (`middleware/error_handling.py`)
   - FPLError exception classes
   - Error categorization
   - Severity levels

2. **Recovery Layer** (`utils/error_recovery.py`)
   - Circuit breaker pattern
   - Exponential backoff
   - Fallback data

3. **View Layer**
   - User-friendly error messages
   - Graceful degradation
   - Retry mechanisms

### Example:

```python
from middleware.error_handling import FPLError, ErrorCategory, ErrorSeverity

try:
    data = fetch_from_api()
except requests.RequestException as e:
    raise FPLError(
        "Failed to fetch FPL data",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        original_error=e
    )
```

---

## Migration Guide

### For Developers: Updating Code to New Architecture

#### Step 1: Update Data Fetching

**Before:**
```python
from services.fpl_data_service import get_fpl_service
service = get_fpl_service()
players_df, teams_df = service.load_fpl_data()
```

**After:**
```python
from core.data import get_fpl_data_fetcher
fetcher = get_fpl_data_fetcher()
players_df, teams_df = fetcher.load_fpl_data()
```

#### Step 2: Update Caching

**Before:**
```python
@st.cache_data(ttl=300)
def get_data(self):
    return self.fetch()
```

**After:**
```python
from core.cache import cache_5min

@cache_5min
def get_data(_self):  # Note: _self to exclude from cache key
    return _self.fetch()
```

#### Step 3: Update Validation

**Before:**
```python
# Manual type conversion
players_df['total_points'] = pd.to_numeric(players_df['total_points'], errors='coerce')
players_df = players_df.fillna(0)
```

**After:**
```python
from core.data import get_data_validator

validator = get_data_validator()
players_df = validator.validate_and_clean(players_df, 'players')
```

### Import Map:

| Old Import | New Import |
|------------|------------|
| `services.fpl_data_service` | `core.data.fetcher` |
| `services.enhanced_fpl_data_service` | `core.data.fetcher` |
| Manual caching decorators | `core.cache.manager` |
| Manual validation | `core.data.validator` |

---

## Future Enhancements

### Planned Additions:

1. **core/analytics/** (Section 4 from recommendations)
   - `calculator.py` - Core FPL calculations
   - `predictor.py` - ML-based predictions
   - `optimizer.py` - Team optimization engine

2. **services/fpl_api.py** (Consolidation)
   - Merge all API-related services
   - Single interface for all endpoints

3. **services/external_data.py**
   - Injury news integration
   - Press conference updates
   - Bookmaker odds

4. **services/notifications.py**
   - Price change alerts
   - Form change notifications
   - Gameweek reminders

---

## Key Decisions & Rationale

### 1. Why Separate core/data from services/?

**Reason:** Separation of concerns
- `core/data` = Infrastructure (how we get data)
- `services` = Business logic (what we do with data)

### 2. Why Three Data Modules (fetcher, validator, transformer)?

**Reason:** Single Responsibility Principle
- Easier to test each independently
- Can be used in isolation
- Clear boundaries

### 3. Why Unified Cache Manager?

**Reason:** Consistency
- Standard TTL values across app
- Central cache invalidation
- Performance monitoring

### 4. Why Keep Multiple main_*.py Files Initially?

**Reason:** Safety
- Gradual migration
- Rollback capability
- A/B testing

---

## Testing Strategy

### Unit Tests:
- Test each core module independently
- Mock external dependencies
- Validate data transformations

### Integration Tests:
- Test service orchestration
- Verify cache behavior
- End-to-end data flow

### UI Tests:
- Page rendering
- User interactions
- Error state handling

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Page load time | < 2s | ~3s |
| API response time | < 500ms | ~300ms |
| Cache hit rate | > 80% | TBD |
| Memory usage | < 500MB | TBD |

---

## Contributing

When adding new features:

1. **Data fetching?** → Add to `core/data/fetcher.py`
2. **Data validation?** → Add to `core/data/validator.py`
3. **Business logic?** → Create/update service in `services/`
4. **UI component?** → Add to appropriate view in `views/`
5. **Caching needed?** → Use `core/cache` decorators

---

## Changelog

### Version 2.0 (January 7, 2026)
- ✅ Created `core/data/` module with unified fetcher
- ✅ Created `core/data/validator.py` for data quality
- ✅ Created `core/data/transformer.py` for enrichment
- ✅ Created `core/cache/manager.py` for unified caching
- ✅ Documented architecture patterns
- 🔄 In Progress: Migrate services to use new core modules
- 📋 Pending: Remove duplicate/legacy files

### Previous Versions
- v1.x: Multiple data services, inconsistent caching
- v0.x: Initial implementation

---

## Questions & Contact

For architecture questions:
- Review this document
- Check code comments in core modules
- Reference APP_IMPROVEMENT_RECOMMENDATIONS.md Section 9

---

**Last Updated:** January 7, 2026  
**Next Review:** After completing migration and duplicate removal
