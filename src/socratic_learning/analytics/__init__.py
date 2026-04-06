"""Analytics module for learning system."""

from .analytics_calculator import AnalyticsCalculator
from .cohort_analyzer import CohortAnalyzer, CohortComparison, CohortMetrics, SegmentationStrategy
from .learning_engine import LearningEngine
from .maturity_calculator import MaturityCalculator
from .pattern_detector import PatternDetector

__all__ = [
    "AnalyticsCalculator",
    "LearningEngine",
    "MaturityCalculator",
    "PatternDetector",
    # Cohort analysis
    "CohortAnalyzer",
    "CohortMetrics",
    "CohortComparison",
    "SegmentationStrategy",
]
