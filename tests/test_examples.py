"""
Example Tests - Demonstrating the enhanced testing framework
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
import pytest

from tests.testing_framework import (
    FPLTestCase, 
    AsyncFPLTestCase,
    TestContext,
    MockDataGenerator,
    mock_streamlit,
    requires_api,
    slow_test,
    PerformanceTimer,
    assert_performance,
    FPLTestUtils
)

from middleware import (
    FPLError,
    DataLoadingError,
    APIRequestError,
    ErrorCategory,
    ErrorSeverity,
    DIContainer
)

class TestErrorHandling(FPLTestCase):
    """Test error handling middleware"""
    
    def test_fpl_error_creation(self):
        """Test FPL error creation with proper categorization"""
        error = DataLoadingError(
            "Failed to load player data",
            severity=ErrorSeverity.HIGH,
            context={"url": "https://fantasy.premierleague.com/api/bootstrap-static/"}
        )
        
        self.assertEqual(error.category, ErrorCategory.DATA_LOADING)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
        self.assertIn("Unable to load FPL data", error.user_message)
        self.assertIsNotNone(error.timestamp)
    
    def test_error_middleware_handling(self):
        """Test error middleware handles errors properly"""
        from middleware.error_handling import get_error_middleware
        
        middleware = get_error_middleware()
        
        with patch('streamlit.error') as mock_st_error:
            error = APIRequestError("Connection timeout")
            middleware.handle_error(error)
            
            # Verify user message was displayed
            mock_st_error.assert_called_once()
            call_args = mock_st_error.call_args[0][0]
            self.assertIn("Error connecting to FPL servers", call_args)
    
    def test_error_statistics(self):
        """Test error statistics collection"""
        from middleware.error_handling import get_error_middleware
        
        middleware = get_error_middleware()
        
        # Generate some test errors
        middleware.handle_error(DataLoadingError("Test error 1"), show_user_message=False)
        middleware.handle_error(APIRequestError("Test error 2"), show_user_message=False)
        
        stats = middleware.get_error_statistics()
        self.assertGreater(stats["total_errors"], 0)
        self.assertIn("data_loading", stats["error_counts"])
        self.assertIn("api_request", stats["error_counts"])

class TestDependencyInjection(FPLTestCase):
    """Test dependency injection container"""
    
    def test_container_registration(self):
        """Test service registration in container"""
        container = DIContainer()
        
        # Test interface for demonstration
        class ITestService:
            def get_data(self):
                pass
        
        class TestService(ITestService):
            def get_data(self):
                return "test data"
        
        # Register and resolve service
        container.register(ITestService, TestService)
        service = container.resolve(ITestService)
        
        self.assertIsInstance(service, TestService)
        self.assertEqual(service.get_data(), "test data")
    
    def test_singleton_lifetime(self):
        """Test singleton service lifetime"""
        container = DIContainer()
        
        class SingletonService:
            def __init__(self):
                self.id = id(self)
        
        container.register_singleton(SingletonService, SingletonService)
        
        service1 = container.resolve(SingletonService)
        service2 = container.resolve(SingletonService)
        
        # Should be the same instance
        self.assertEqual(service1.id, service2.id)
    
    def test_mock_registration(self):
        """Test registering mocks in test context"""
        mock_service = Mock()
        mock_service.get_players.return_value = self.create_mock_players_df(50)
        
        self.test_context.register_mock(type(mock_service), mock_service)
        
        resolved_service = self.test_context.container.resolve(type(mock_service))
        players_df = resolved_service.get_players()
        
        self.assertIsInstance(players_df, pd.DataFrame)
        self.assertEqual(len(players_df), 50)

class TestFPLDataProcessing(FPLTestCase):
    """Test FPL data processing functionality"""
    
    def test_mock_players_df_structure(self):
        """Test mock players DataFrame has correct structure"""
        players_df = self.create_mock_players_df(100)
        
        expected_columns = [
            'id', 'web_name', 'element_type', 'total_points', 
            'now_cost', 'form', 'selected_by_percent'
        ]
        
        self.assert_dataframe_structure(players_df, expected_columns)
        self.assertEqual(len(players_df), 100)
    
    def test_team_composition_validation(self):
        """Test team composition validation"""
        # Create a valid team composition
        players_df = pd.DataFrame({
            'element_type': [1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4],  # Valid formation
            'web_name': [f'Player_{i}' for i in range(14)]
        })
        
        # Should not raise an exception
        FPLTestUtils.assert_valid_team_composition(players_df)
        
        # Test invalid composition (too many forwards)
        invalid_df = pd.DataFrame({
            'element_type': [4, 4, 4, 4],  # 4 forwards (max is 3)
            'web_name': ['F1', 'F2', 'F3', 'F4']
        })
        
        with self.assertRaises(AssertionError):
            FPLTestUtils.assert_valid_team_composition(invalid_df)
    
    @mock_streamlit()
    def test_streamlit_component_integration(self):
        """Test integration with mocked Streamlit components"""
        # This test would run without actual Streamlit UI
        from components.ai.player_insights import SmartPlayerInsights
        
        insights_engine = SmartPlayerInsights()
        players_df = self.create_mock_players_df(50)
        
        # This should not raise errors even though Streamlit is mocked
        insights_engine.render_insights_dashboard(players_df)

class TestPerformance(FPLTestCase):
    """Test performance requirements"""
    
    @assert_performance(max_duration_ms=100)
    def test_player_score_calculation_performance(self):
        """Test that player score calculation is fast enough"""
        from components.ai.player_insights import SmartPlayerInsights
        
        insights_engine = SmartPlayerInsights()
        players_df = self.create_mock_players_df(1000)  # Large dataset
        
        # Calculate scores for all players
        scores = []
        for _, player in players_df.iterrows():
            score = insights_engine.calculate_player_score(player)
            scores.append(score)
        
        # Verify all scores are valid
        for score in scores:
            FPLTestUtils.assert_valid_player_score(score)
    
    def test_performance_timer(self):
        """Test performance timer utility"""
        import time
        
        with PerformanceTimer(max_duration_ms=50) as timer:
            time.sleep(0.01)  # Sleep for 10ms
        
        self.assertLess(timer.duration_ms, 50)
        self.assertGreater(timer.duration_ms, 5)  # Should be at least 10ms

@pytest.mark.unit
class TestPytestIntegration:
    """Demonstrate pytest integration"""
    
    def test_with_test_context(self, test_context):
        """Test using pytest fixture"""
        mock_service = Mock()
        mock_service.get_data.return_value = "pytest test data"
        
        test_context.register_mock(type(mock_service), mock_service)
        service = test_context.container.resolve(type(mock_service))
        
        assert service.get_data() == "pytest test data"
    
    def test_with_mock_data(self, mock_players_df):
        """Test using mock data fixture"""
        assert isinstance(mock_players_df, pd.DataFrame)
        assert len(mock_players_df) > 0
        assert 'web_name' in mock_players_df.columns

@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests (would require actual API access)"""
    
    @requires_api()
    def test_fpl_api_connection(self):
        """Test connection to actual FPL API"""
        # This test would only run when API access is available
        # and would be marked with @requires_api() decorator
        pytest.skip("Skipping API test in example")

@pytest.mark.slow
class TestSlowOperations:
    """Tests that are known to be slow"""
    
    @slow_test()
    def test_large_dataset_processing(self):
        """Test processing of large datasets"""
        # This test would only run when slow tests are enabled
        pytest.skip("Skipping slow test in example")

class TestAsyncOperations(AsyncFPLTestCase):
    """Test async operations"""
    
    def test_async_operation(self):
        """Test async functionality"""
        async def async_function():
            return "async result"
        
        result = self.run_async(async_function())
        self.assertEqual(result, "async result")

if __name__ == '__main__':
    # Run unittest tests
    unittest.main(verbosity=2)
