"""Socratic Learning - Continuous learning system for AI agents."""

from socratic_learning.analytics import MetricsCollector, PatternDetector
from socratic_learning.core import Interaction, Metric, Pattern, Recommendation
from socratic_learning.storage import BaseLearningStore, SQLiteLearningStore
from socratic_learning.tracking import InteractionLogger, Session
from socratic_learning.integrations import LearningTool, SocraticLearningSkill

__version__ = "0.1.0"

__all__ = [
    "Interaction",
    "Pattern",
    "Metric",
    "Recommendation",
    "BaseLearningStore",
    "SQLiteLearningStore",
    "Session",
    "InteractionLogger",
    "MetricsCollector",
    "PatternDetector",
    "SocraticLearningSkill",
    "LearningTool",
]
