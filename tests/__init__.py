"""
Tests Package
Comprehensive testing framework and example tests
"""

from .testing_framework import (
    TestContext,
    FPLTestCase,
    AsyncFPLTestCase,
    MockDataGenerator,
    mock_streamlit,
    requires_api,
    slow_test,
    PerformanceTimer,
    assert_performance,
    FPLTestUtils
)

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
