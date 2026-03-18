"""Abstract storage interface for learning data."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from socratic_learning.core import Interaction, Metric, Pattern, Recommendation


class BaseLearningStore(ABC):
    """Abstract interface for learning data storage."""

    # Interaction operations
    @abstractmethod
    def create_interaction(self, interaction: Interaction) -> Interaction:
        """Create and store an interaction."""
        pass

    @abstractmethod
    def get_interaction(self, interaction_id: str) -> Optional[Interaction]:
        """Retrieve an interaction by ID."""
        pass

    @abstractmethod
    def list_interactions(
        self,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Interaction]:
        """List interactions with optional filtering."""
        pass

    @abstractmethod
    def update_interaction_feedback(
        self,
        interaction_id: str,
        rating: int,
        feedback: str,
    ) -> Optional[Interaction]:
        """Add user feedback to an interaction."""
        pass

    # Pattern operations
    @abstractmethod
    def create_pattern(self, pattern: Pattern) -> Pattern:
        """Create and store a pattern."""
        pass

    @abstractmethod
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Retrieve a pattern by ID."""
        pass

    @abstractmethod
    def list_patterns(
        self,
        pattern_type: Optional[str] = None,
        agent_name: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> List[Pattern]:
        """List patterns with optional filtering."""
        pass

    @abstractmethod
    def update_pattern(self, pattern: Pattern) -> Pattern:
        """Update an existing pattern."""
        pass

    # Metric operations
    @abstractmethod
    def create_metric(self, metric: Metric) -> Metric:
        """Create and store a metric."""
        pass

    @abstractmethod
    def get_metrics(
        self,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Metric]:
        """Retrieve metrics with optional filtering."""
        pass

    # Recommendation operations
    @abstractmethod
    def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Create and store a recommendation."""
        pass

    @abstractmethod
    def list_recommendations(
        self,
        agent_name: Optional[str] = None,
        priority: Optional[str] = None,
        applied: Optional[bool] = None,
        limit: int = 100,
    ) -> List[Recommendation]:
        """List recommendations with optional filtering."""
        pass

    @abstractmethod
    def update_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Update an existing recommendation."""
        pass
