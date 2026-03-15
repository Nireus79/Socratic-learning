"""Analytics and metrics for Socratic Learning."""

from socratic_learning.analytics.aggregator import DataAggregator
from socratic_learning.analytics.metrics_collector import MetricsCollector
from socratic_learning.analytics.pattern_detector import PatternDetector
from socratic_learning.analytics.reporter import ReportGenerator

__all__ = [
    "MetricsCollector",
    "PatternDetector",
    "DataAggregator",
    "ReportGenerator",
]
