"""
Test configuration and fixtures for the entire test suite
Provides shared test utilities and configuration
"""
import pytest
import sys
import os
import asyncio
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Generator
import tempfile
import shutil

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def project_root_path():
    """Fixture to provide project root path"""
    return project_root

@pytest.fixture(scope="session")
def sample_bootstrap_data() -> Dict[str, Any]:
    """Sample FPL bootstrap data for testing"""
    return {
        "elements": [
            {
                "id": 1,
                "web_name": "Salah",
                "first_name": "Mohamed",
                "second_name": "Salah", 
                "element_type": 3,
                "team": 1,
                "total_points": 150,
                "now_cost": 130,
                "selected_by_percent": "25.5",
                "form": "4.5",
                "points_per_game": "8.2",
                "minutes": 1800,
                "goals_scored": 15,
                "assists": 8,
                "clean_sheets": 0,
                "goals_conceded": 0,
                "expected_goals": "12.5",
                "expected_assists": "6.8"
            },
            {
                "id": 2,
                "web_name": "Kane", 
                "first_name": "Harry",
                "second_name": "Kane",
                "element_type": 4,
                "team": 2,
                "total_points": 140,
                "now_cost": 125,
                "selected_by_percent": "22.1",
                "form": "4.2",
                "points_per_game": "7.8",
                "minutes": 1750,
                "goals_scored": 18,
                "assists": 5,
                "clean_sheets": 0,
                "goals_conceded": 0,
                "expected_goals": "16.2",
                "expected_assists": "4.1"
            }
        ],
        "teams": [
            {
                "id": 1,
                "name": "Liverpool",
                "short_name": "LIV",
                "strength": 5
            },
            {
                "id": 2,
                "name": "Tottenham",
                "short_name": "TOT", 
                "strength": 4
            }
        ],
        "element_types": [
            {"id": 1, "singular_name": "Goalkeeper"},
            {"id": 2, "singular_name": "Defender"},
            {"id": 3, "singular_name": "Midfielder"},
            {"id": 4, "singular_name": "Forward"}
        ]
    }

@pytest.fixture
def sample_players_dataframe(sample_bootstrap_data) -> pd.DataFrame:
    """Sample players DataFrame for testing"""
    return pd.DataFrame(sample_bootstrap_data["elements"])

@pytest.fixture
def mock_fpl_api_response(sample_bootstrap_data):
    """Mock FPL API response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_bootstrap_data
    mock_response.raise_for_status.return_value = None
    return mock_response

@pytest.fixture
def sample_config():
    """Fixture to provide sample configuration for testing"""
    return {
        'api': {
            'base_url': 'https://fantasy.premierleague.com/api',
            'timeout': 30,
            'retries': 3
        },
        'cache': {
            'enabled': True,
            'ttl': 3600,
            'max_size': 1000
        },
        'ui': {
            'theme': 'light',
            'sidebar_width': 300,
            'show_debug': False
        }
    }

@pytest.fixture
def mock_fpl_data():
    """Fixture to provide mock FPL data for testing"""
    return {
        'elements': [
            {
                'id': 1,
                'web_name': 'Test Player',
                'total_points': 100,
                'now_cost': 80,
                'selected_by_percent': 15.5
            }
        ],
        'teams': [
            {
                'id': 1,
                'name': 'Test Team',
                'short_name': 'TEST'
            }
        ],
        'events': [
            {
                'id': 1,
                'name': 'Gameweek 1',
                'is_current': True,
                'finished': False
            }
        ]
    }
