"""Socratic Learning - Continuous learning system for AI agents."""

from socratic_learning.analytics import AnalyticsCalculator, LearningEngine, MaturityCalculator, PatternDetector
from socratic_learning.async_learning import (
    AsyncBatchProcessor,
    AsyncLearningAnalyzer,
    AsyncLearningEngine,
)
from socratic_learning.core import Interaction, Metric, Pattern, Recommendation
from socratic_learning.predictions import (
    ChurnPrediction,
    ChurnPredictor,
    DifficultyPrediction,
    DifficultyPredictor,
    LearningOutcomePrediction,
    LearningOutcomePredictor,
    SkillGapAnalyzer,
    SkillGapPrediction,
)
from socratic_learning.exceptions import (  # noqa: F401
    AggregationError,
    AnalyticsException,
    DataValidationException,
    ExportError,
    InsufficientDataError,
    InteractionException,
    InteractionFeedbackError,
    InteractionNotFoundError,
    InvalidFeedbackError,
    InvalidInteractionDataError,
    InvalidMetricDataError,
    InvalidPatternDataError,
    InvalidRecommendationStateError,
    InvalidSessionStateError,
    MetricsCalculationError,
    PatternDetectionError,
    PatternException,
    RecommendationException,
    RecommendationGenerationError,
    RecommendationNotFoundError,
    ReportGenerationError,
    SessionException,
    SessionNotFoundError,
    SocraticLearningException,
    StorageBackendError,
    StorageException,
    StorageNotFoundError,
    StorageOperationError,
)
from socratic_learning.integrations import LearningTool, SocraticLearningSkill
from socratic_learning.models import (
    KnowledgeBaseDocument,
    QuestionEffectiveness,
    UserBehaviorPattern,
)
from socratic_learning.storage import BaseLearningStore, SQLiteLearningStore
from socratic_learning.tracking import InteractionLogger, Session

__version__ = "0.1.1"

__all__ = [
    "Interaction",
    "KnowledgeBaseDocument",
    "LearningEngine",
    "LearningTool",
    "Metric",
    "Pattern",
    "PatternDetector",
    "QuestionEffectiveness",
    "Recommendation",
    "SocraticLearningSkill",
    "UserBehaviorPattern",
    # Analytics
    "AnalyticsCalculator",
    "MaturityCalculator",
    # Async Learning
    "AsyncLearningEngine",
    "AsyncBatchProcessor",
    "AsyncLearningAnalyzer",
    # Predictions
    "LearningOutcomePredictor",
    "LearningOutcomePrediction",
    "ChurnPredictor",
    "ChurnPrediction",
    "DifficultyPredictor",
    "DifficultyPrediction",
    "SkillGapAnalyzer",
    "SkillGapPrediction",
    # Storage
    "BaseLearningStore",
    "SQLiteLearningStore",
    # Tracking
    "InteractionLogger",
    "Session",
    # Exceptions
    "AggregationError",
    "AnalyticsException",
    "DataValidationException",
    "ExportError",
    "InsufficientDataError",
    "InteractionException",
    "InteractionFeedbackError",
    "InteractionNotFoundError",
    "InvalidFeedbackError",
    "InvalidInteractionDataError",
    "InvalidMetricDataError",
    "InvalidPatternDataError",
    "InvalidRecommendationStateError",
    "InvalidSessionStateError",
    "MetricsCalculationError",
    "PatternDetectionError",
    "PatternException",
    "RecommendationException",
    "RecommendationGenerationError",
    "RecommendationNotFoundError",
    "ReportGenerationError",
    "SessionException",
    "SessionNotFoundError",
    "SocraticLearningException",
    "StorageBackendError",
    "StorageException",
    "StorageNotFoundError",
    "StorageOperationError",
]
