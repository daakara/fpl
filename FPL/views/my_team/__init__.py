"""
My Team Module - Core components for FPL team analysis
"""

# Team import and data loading
from .team_import import TeamImportComponent
from .team_overview import TeamOverviewComponent

# Analysis modules
from .squad_analysis import SquadAnalysisComponent
from .performance_analysis import PerformanceAnalysisComponent
from .recommendations import RecommendationsComponent

# Advanced features
from .optimizer import StartingXIOptimizerComponent
from .swot_analysis import SWOTAnalysisComponent
from .advanced_analytics import AdvancedAnalyticsComponent
from .transfer_planning import TransferPlanningComponent
from .performance_comparison import PerformanceComparisonComponent
from .fixture_analysis import FixtureAnalysisComponent

__all__ = [
    'TeamImportComponent',
    'TeamOverviewComponent',
    'SquadAnalysisComponent',
    'PerformanceAnalysisComponent',
    'RecommendationsComponent',
    'StartingXIOptimizerComponent',
    'SWOTAnalysisComponent',
    'AdvancedAnalyticsComponent',
    'TransferPlanningComponent',
    'PerformanceComparisonComponent',
    'FixtureAnalysisComponent'
]
