# Service Migration Guide

## Migration to Core Modules

This guide documents the migration from old data services to the new unified `core/data` and `core/cache` modules.

### New Import Pattern

**OLD (deprecated):**
```python
from services.fpl_data_service import get_fpl_service
from services.enhanced_fpl_data_service import EnhancedFPLDataService
from services.data_services import DataService
```

**NEW (standardized):**
```python
from core.data import get_fpl_data_fetcher, get_data_validator, get_data_transformer
from core.cache import cache_5min, cache_15min, cache_1hour, CacheTTL
```

### Usage Examples

#### 1. Fetching Data

**OLD:**
```python
service = get_fpl_service()
data = service.get_bootstrap_static()
players_df = pd.DataFrame(data['elements'])
```

**NEW:**
```python
fetcher = get_fpl_data_fetcher()
players_df = fetcher.get_players_dataframe()  # Already a DataFrame!
teams_df = fetcher.get_teams_dataframe()
```

#### 2. Data Validation

**NEW (added functionality):**
```python
validator = get_data_validator()
clean_df = validator.validate_and_clean(players_df, 'players')
```

#### 3. Data Transformation

**OLD:**
```python
# Manual type conversion
df['now_cost'] = pd.to_numeric(df['now_cost'], errors='coerce')
df['price_millions'] = df['now_cost'] / 10
```

**NEW:**
```python
transformer = get_data_transformer()
enriched_df = transformer.transform_players(players_df, teams_df)
# Now has: price_millions, points_per_million, position, team_name, per_90 stats, etc.
```

#### 4. Caching

**OLD:**
```python
@st.cache_data(ttl=300)
def some_function():
    pass
```

**NEW:**
```python
@cache_5min  # Semantic naming!
def some_function():
    pass

# Or with custom TTL:
from core.cache import cache_with_ttl, CacheTTL
@cache_with_ttl(CacheTTL.SHORT)  # 5 minutes
def another_function():
    pass
```

### Migration Checklist

- [ ] Replace old data service imports
- [ ] Use `get_fpl_data_fetcher()` instead of multiple services
- [ ] Add data validation where appropriate
- [ ] Use transformer for enriched data
- [ ] Replace TTL values with semantic cache decorators
- [ ] Test each migrated service

### Services to Migrate

Priority order:
1. ✅ Test core modules (DONE)
2. [ ] services/advanced_ai_engine.py
3. [ ] services/hidden_gems_discovery.py  
4. [ ] services/player_recommendation_service.py
5. [ ] services/transfer_planning_service.py
6. [ ] services/fixture_service.py
7. [ ] views/dashboard_page.py
8. [ ] views/player_analysis_page.py
9. [ ] views/team_builder_page.py

### Services to DEPRECATE/DELETE

After migration complete:
- services/fpl_data_service.py → Use core/data/fetcher.py
- services/enhanced_fpl_data_service.py → Use core/data/fetcher.py
- services/data_services.py → Use core/data/fetcher.py
- services/realtime_pipeline.py → Use core/data/fetcher.py
- services/enhanced_data_manager.py → Use core/data/fetcher.py
