"""Exception hierarchy for Socratic Learning.

Provides domain-specific exceptions for learning system operations,
organized by functional area for better error handling and debugging.
"""


class SocraticLearningException(Exception):
    """Base exception for all Socratic Learning errors."""

    pass


# Storage exceptions


class StorageException(SocraticLearningException):
    """Base exception for storage operation failures."""

    pass


class StorageBackendError(StorageException):
    """Raised when storage backend initialization fails."""

    pass


class StorageOperationError(StorageException):
    """Raised when a storage operation (read/write/delete) fails."""

    pass


class StorageNotFoundError(StorageException):
    """Raised when a requested item is not found in storage."""

    pass


# Data validation exceptions


class DataValidationException(SocraticLearningException):
    """Base exception for data validation failures."""

    pass


class InvalidInteractionDataError(DataValidationException):
    """Raised when interaction data fails validation."""

    pass


class InvalidFeedbackError(DataValidationException):
    """Raised when feedback data is invalid.

    Common causes:
    - Rating outside 1-5 range
    - Feedback string is empty when required
    - Invalid feedback timestamp
    """

    pass


class InvalidMetricDataError(DataValidationException):
    """Raised when metric data fails validation."""

    pass


class InvalidPatternDataError(DataValidationException):
    """Raised when pattern data fails validation."""

    pass


# Interaction exceptions


class InteractionException(SocraticLearningException):
    """Base exception for interaction-related errors."""

    pass


class InteractionNotFoundError(InteractionException):
    """Raised when an interaction cannot be found."""

    pass


class InteractionFeedbackError(InteractionException):
    """Raised when feedback addition/update fails."""

    pass


# Session exceptions


class SessionException(SocraticLearningException):
    """Base exception for session-related errors."""

    pass


class SessionNotFoundError(SessionException):
    """Raised when a session cannot be found."""

    pass


class InvalidSessionStateError(SessionException):
    """Raised when a session operation violates session state."""

    pass


# Pattern detection exceptions


class PatternException(SocraticLearningException):
    """Base exception for pattern detection failures."""

    pass


class PatternDetectionError(PatternException):
    """Raised when pattern detection fails."""

    pass


class InsufficientDataError(PatternException):
    """Raised when there is insufficient data for pattern detection."""

    pass


# Recommendation exceptions


class RecommendationException(SocraticLearningException):
    """Base exception for recommendation generation failures."""

    pass


class RecommendationGenerationError(RecommendationException):
    """Raised when recommendation generation fails."""

    pass


class RecommendationNotFoundError(RecommendationException):
    """Raised when a recommendation cannot be found."""

    pass


class InvalidRecommendationStateError(RecommendationException):
    """Raised when a recommendation operation violates its state."""

    pass


# Analytics exceptions


class AnalyticsException(SocraticLearningException):
    """Base exception for analytics operation failures."""

    pass


class MetricsCalculationError(AnalyticsException):
    """Raised when metrics calculation fails."""

    pass


class ReportGenerationError(AnalyticsException):
    """Raised when report generation fails."""

    pass


class AggregationError(AnalyticsException):
    """Raised when data aggregation fails."""

    pass


class ExportError(AnalyticsException):
    """Raised when data export fails.

    Common causes:
    - File write permission denied
    - Invalid export format
    - Export destination unavailable
    """

    pass
