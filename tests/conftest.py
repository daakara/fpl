import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def project_root_path():
    """Fixture to provide project root path"""
    return project_root

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
