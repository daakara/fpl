"""
Enhanced Testing Framework
Integrates with dependency injection container for better testability
"""

import pytest
import unittest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Any, Dict, Type, TypeVar, Optional, Callable, List
import inspect
from functools import wraps
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from middleware.dependency_injection import DIContainer, get_container, reset_container
from middleware.error_handling import FPLError, ErrorCategory, ErrorSeverity
from middleware.logging_strategy import LoggingStrategy, LogLevel

T = TypeVar('T')

class TestContext:
    """Test context manager for dependency injection"""
    
    def __init__(self):
        self.container = DIContainer()
        self.mocks: Dict[Type, Mock] = {}
        self.original_container = None
    
    def __enter__(self) -> 'TestContext':
        # Store original container
        import middleware.dependency_injection as di_module
        self.original_container = di_module._global_container
        di_module._global_container = self.container
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original container
        import middleware.dependency_injection as di_module
        di_module._global_container = self.original_container
        
        # Clean up mocks
        for mock in self.mocks.values():
            if hasattr(mock, 'reset_mock'):
                mock.reset_mock()
    
    def register_mock(self, interface: Type[T], mock_instance: Optional[Mock] = None) -> Mock:
        """Register a mock for a service interface"""
        if mock_instance is None:
            mock_instance = MagicMock(spec=interface)
        
        self.container.register_instance(interface, mock_instance)
        self.mocks[interface] = mock_instance
        return mock_instance
    
    def get_mock(self, interface: Type[T]) -> Mock:
        """Get the mock for a service interface"""
        return self.mocks.get(interface)

class FPLTestCase(unittest.TestCase):
    """Base test case with FPL-specific testing utilities"""
    
    def setUp(self):
        """Set up test case with clean container"""
        self.test_context = TestContext()
        self.test_context.__enter__()
        
        # Set up test logging
        self.test_logger = LoggingStrategy("test", LogLevel.DEBUG)
    
    def tearDown(self):
        """Clean up test case"""
        self.test_context.__exit__(None, None, None)
    
    def create_mock_players_df(self, num_players: int = 100) -> pd.DataFrame:
        """Create mock players DataFrame for testing"""
        np.random.seed(42)  # For reproducible tests
        
        positions = [1, 2, 3, 4]  # GK, DEF, MID, FWD
        position_weights = [0.1, 0.3, 0.4, 0.2]
        
        data = {
            'id': range(1, num_players + 1),
            'web_name': [f'Player_{i}' for i in range(1, num_players + 1)],
            'element_type': np.random.choice(positions, num_players, p=position_weights),
            'total_points': np.random.randint(0, 250, num_players),
            'now_cost': np.random.randint(40, 130, num_players),  # £4.0m to £13.0m
            'form': np.random.uniform(0, 10, num_players).round(1),
            'selected_by_percent': np.random.uniform(0.1, 50, num_players).round(1),
            'minutes': np.random.randint(0, 3000, num_players),
            'goals_scored': np.random.randint(0, 25, num_players),
            'assists': np.random.randint(0, 20, num_players),
            'clean_sheets': np.random.randint(0, 20, num_players),
            'bonus': np.random.randint(0, 30, num_players),
            'bps': np.random.randint(0, 800, num_players),
            'influence': np.random.uniform(0, 2000, num_players).round(1),
            'creativity': np.random.uniform(0, 1500, num_players).round(1),
            'threat': np.random.uniform(0, 1200, num_players).round(1),
            'ict_index': np.random.uniform(0, 20, num_players).round(1)
        }
        
        df = pd.DataFrame(data)
        
        # Add calculated columns
        df['cost_millions'] = df['now_cost'] / 10
        df['points_per_million'] = df['total_points'] / df['cost_millions']
        df['value_form'] = df['form'] * df['points_per_million']
        df['value_season'] = df['total_points'] / df['cost_millions']
        
        return df
    
    def create_mock_teams_df(self, num_teams: int = 20) -> pd.DataFrame:
        """Create mock teams DataFrame for testing"""
        data = {
            'id': range(1, num_teams + 1),
            'name': [f'Team {i}' for i in range(1, num_teams + 1)],
            'short_name': [f'T{i:02d}' for i in range(1, num_teams + 1)],
            'strength': np.random.randint(2, 6, num_teams),
            'strength_overall_home': np.random.randint(1000, 1400, num_teams),
            'strength_overall_away': np.random.randint(900, 1300, num_teams),
            'strength_attack_home': np.random.randint(1000, 1400, num_teams),
            'strength_attack_away': np.random.randint(900, 1300, num_teams),
            'strength_defence_home': np.random.randint(1000, 1400, num_teams),
            'strength_defence_away': np.random.randint(900, 1300, num_teams)
        }
        
        return pd.DataFrame(data)
    
    def assert_dataframe_structure(self, df: pd.DataFrame, expected_columns: List[str]):
        """Assert that DataFrame has expected structure"""
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty, "DataFrame should not be empty")
        
        for column in expected_columns:
            self.assertIn(column, df.columns, f"Column '{column}' should be present")
    
    def assert_error_handling(self, func: Callable, expected_error_type: Type[Exception] = None):
        """Assert that function handles errors properly"""
        if expected_error_type:
            with self.assertRaises(expected_error_type):
                func()
        else:
            try:
                func()
            except Exception as e:
                self.assertIsInstance(e, FPLError, "Should raise FPLError or subclass")

class AsyncFPLTestCase(FPLTestCase):
    """Base test case for async testing"""
    
    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
        super().tearDown()
    
    def run_async(self, coro):
        """Run async coroutine in test"""
        return self.loop.run_until_complete(coro)

class MockDataGenerator:
    """Utility class for generating mock data"""
    
    @staticmethod
    def mock_fpl_api_response() -> Dict[str, Any]:
        """Generate mock FPL API response"""
        return {
            'events': [
                {
                    'id': 1,
                    'name': 'Gameweek 1',
                    'deadline_time': datetime.now().isoformat(),
                    'finished': True,
                    'is_current': False,
                    'is_next': False
                }
            ],
            'teams': [
                {
                    'id': 1,
                    'name': 'Arsenal',
                    'short_name': 'ARS',
                    'strength': 4
                }
            ],
            'elements': [
                {
                    'id': 1,
                    'web_name': 'Salah',
                    'element_type': 3,
                    'team': 1,
                    'total_points': 200,
                    'now_cost': 130,
                    'form': '8.5',
                    'selected_by_percent': '25.5'
                }
            ]
        }
    
    @staticmethod
    def mock_player_data(player_id: int = 1) -> Dict[str, Any]:
        """Generate mock individual player data"""
        return {
            'id': player_id,
            'web_name': f'Player_{player_id}',
            'element_type': 3,
            'team': 1,
            'total_points': 150 + player_id,
            'now_cost': 80 + player_id,
            'form': '7.5',
            'selected_by_percent': '15.5',
            'minutes': 2500,
            'goals_scored': 10,
            'assists': 8,
            'clean_sheets': 5
        }

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as requiring API access"
    )

@pytest.fixture
def test_context():
    """Pytest fixture for test context"""
    with TestContext() as context:
        yield context

@pytest.fixture
def mock_players_df():
    """Pytest fixture for mock players DataFrame"""
    test_case = FPLTestCase()
    test_case.setUp()
    try:
        yield test_case.create_mock_players_df()
    finally:
        test_case.tearDown()

@pytest.fixture
def mock_teams_df():
    """Pytest fixture for mock teams DataFrame"""
    test_case = FPLTestCase()
    test_case.setUp()
    try:
        yield test_case.create_mock_teams_df()
    finally:
        test_case.tearDown()

@pytest.fixture
def mock_fpl_api_response():
    """Pytest fixture for mock FPL API response"""
    return MockDataGenerator.mock_fpl_api_response()

def mock_streamlit():
    """Decorator to mock Streamlit components for testing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with patch('streamlit.markdown'), \
                 patch('streamlit.columns'), \
                 patch('streamlit.metric'), \
                 patch('streamlit.button'), \
                 patch('streamlit.selectbox'), \
                 patch('streamlit.slider'), \
                 patch('streamlit.dataframe'), \
                 patch('streamlit.plotly_chart'), \
                 patch('streamlit.error'), \
                 patch('streamlit.warning'), \
                 patch('streamlit.info'), \
                 patch('streamlit.success'), \
                 patch('streamlit.spinner'):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def requires_api():
    """Decorator to mark tests that require API access"""
    return pytest.mark.api

def slow_test():
    """Decorator to mark slow tests"""
    return pytest.mark.slow

class PerformanceTimer:
    """Context manager for timing test operations"""
    
    def __init__(self, max_duration_ms: float = 1000):
        self.max_duration_ms = max_duration_ms
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000
        
        if duration_ms > self.max_duration_ms:
            raise AssertionError(
                f"Operation took {duration_ms:.2f}ms, "
                f"which exceeds the maximum allowed {self.max_duration_ms}ms"
            )
    
    @property
    def duration_ms(self) -> float:
        """Get the duration in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

def assert_performance(max_duration_ms: float = 1000):
    """Decorator to assert function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceTimer(max_duration_ms):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Test utilities for specific FPL components
class FPLTestUtils:
    """Utility methods for FPL-specific testing"""
    
    @staticmethod
    def assert_valid_player_score(score: float):
        """Assert that a player score is valid"""
        assert isinstance(score, (int, float)), "Score should be numeric"
        assert 0 <= score <= 100, "Score should be between 0 and 100"
    
    @staticmethod
    def assert_valid_team_composition(players_df: pd.DataFrame):
        """Assert that team composition is valid"""
        assert len(players_df) <= 15, "Team should have maximum 15 players"
        
        if 'element_type' in players_df.columns:
            position_counts = players_df['element_type'].value_counts()
            assert position_counts.get(1, 0) <= 2, "Maximum 2 goalkeepers"
            assert position_counts.get(2, 0) <= 5, "Maximum 5 defenders"
            assert position_counts.get(3, 0) <= 5, "Maximum 5 midfielders"
            assert position_counts.get(4, 0) <= 3, "Maximum 3 forwards"
    
    @staticmethod
    def assert_valid_fpl_data_structure(data: Dict[str, Any]):
        """Assert that FPL API data has valid structure"""
        required_keys = ['events', 'teams', 'elements']
        for key in required_keys:
            assert key in data, f"FPL data should contain '{key}'"
            assert isinstance(data[key], list), f"'{key}' should be a list"

# Export commonly used testing components
__all__ = [
    'TestContext',
    'FPLTestCase', 
    'AsyncFPLTestCase',
    'MockDataGenerator',
    'mock_streamlit',
    'requires_api',
    'slow_test',
    'PerformanceTimer',
    'assert_performance',
    'FPLTestUtils'
]
