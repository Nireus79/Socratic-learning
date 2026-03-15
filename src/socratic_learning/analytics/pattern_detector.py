"""Pattern detection in interactions."""

from typing import List, Optional

from socratic_learning.core import Pattern
from socratic_learning.storage.base import BaseLearningStore


class PatternDetector:
    """Detects patterns in agent interactions."""

    def __init__(self, store: BaseLearningStore):
        """Initialize pattern detector with storage backend."""
        self.store = store

    def detect_error_patterns(
        self,
        agent_name: Optional[str] = None,
        lookback_interactions: int = 100,
    ) -> List[Pattern]:
        """Detect patterns in errors."""
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=lookback_interactions,
        )

        failed = [i for i in interactions if not i.success]
        if not failed or len(interactions) == 0:
            return []

        error_rate = len(failed) / len(interactions)
        confidence = min(0.95, error_rate * 2)

        if error_rate > 0.1:  # More than 10% error rate
            pattern = Pattern(
                pattern_type="error",
                name=f"High Error Rate ({error_rate*100:.1f}%)",
                description=f"Agent {agent_name or 'unknown'} has error rate of {error_rate*100:.1f}%",
                agent_names=[agent_name] if agent_name else [],
                confidence=confidence,
                evidence=[i.interaction_id for i in failed],
                occurrence_count=len(failed),
            )
            return [pattern]

        return []

    def detect_success_patterns(
        self,
        agent_name: Optional[str] = None,
        lookback_interactions: int = 100,
    ) -> List[Pattern]:
        """Detect patterns in successful interactions."""
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=lookback_interactions,
        )

        successful = [i for i in interactions if i.success]
        if not successful or len(interactions) == 0:
            return []

        success_rate = len(successful) / len(interactions)

        if success_rate > 0.8:  # More than 80% success rate
            pattern = Pattern(
                pattern_type="success",
                name=f"High Success Rate ({success_rate*100:.1f}%)",
                description=(
                    f"Agent {agent_name or 'unknown'} has "
                    f"success rate of {success_rate*100:.1f}%"
                ),
                agent_names=[agent_name] if agent_name else [],
                confidence=min(0.95, success_rate),
                evidence=[i.interaction_id for i in successful],
                occurrence_count=len(successful),
            )
            return [pattern]

        return []

    def detect_performance_patterns(
        self,
        agent_name: Optional[str] = None,
        lookback_interactions: int = 100,
    ) -> List[Pattern]:
        """Detect patterns in performance metrics."""
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=lookback_interactions,
        )

        if len(interactions) < 10:
            return []

        durations = [i.duration_ms for i in interactions]
        avg_duration = sum(durations) / len(durations)

        slow_interactions = [i for i in interactions if i.duration_ms > avg_duration * 2]

        if len(slow_interactions) > len(interactions) * 0.2:  # 20% are slow
            pattern = Pattern(
                pattern_type="performance",
                name="High Latency Pattern",
                description=(
                    f"20%+ of interactions exceed 2x average duration " f"({avg_duration:.0f}ms)"
                ),
                agent_names=[agent_name] if agent_name else [],
                confidence=0.75,
                evidence=[i.interaction_id for i in slow_interactions],
                occurrence_count=len(slow_interactions),
            )
            return [pattern]

        return []

    def detect_feedback_patterns(
        self,
        agent_name: Optional[str] = None,
        lookback_interactions: int = 100,
    ) -> List[Pattern]:
        """Detect patterns in user feedback."""
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=lookback_interactions,
        )

        feedback_interactions = [i for i in interactions if i.user_rating is not None]

        if len(feedback_interactions) < 5:
            return []

        avg_rating = sum(i.user_rating for i in feedback_interactions) / len(feedback_interactions)
        positive_count = sum(1 for i in feedback_interactions if i.user_rating >= 4)
        positive_rate = positive_count / len(feedback_interactions)

        patterns = []

        if avg_rating > 4.0:
            patterns.append(
                Pattern(
                    pattern_type="feedback",
                    name="High User Satisfaction",
                    description=f"Average user rating: {avg_rating:.2f}/5.0",
                    agent_names=[agent_name] if agent_name else [],
                    confidence=min(0.95, positive_rate),
                    evidence=[i.interaction_id for i in feedback_interactions],
                    occurrence_count=len(feedback_interactions),
                )
            )

        if avg_rating < 3.0:
            patterns.append(
                Pattern(
                    pattern_type="feedback",
                    name="Low User Satisfaction",
                    description=f"Average user rating: {avg_rating:.2f}/5.0",
                    agent_names=[agent_name] if agent_name else [],
                    confidence=0.8,
                    evidence=[i.interaction_id for i in feedback_interactions],
                    occurrence_count=len(feedback_interactions),
                )
            )

        return patterns

    def detect_all_patterns(
        self,
        agent_name: Optional[str] = None,
        lookback_interactions: int = 100,
    ) -> List[Pattern]:
        """Detect all types of patterns."""
        patterns = []
        patterns.extend(self.detect_error_patterns(agent_name, lookback_interactions))
        patterns.extend(self.detect_success_patterns(agent_name, lookback_interactions))
        patterns.extend(self.detect_performance_patterns(agent_name, lookback_interactions))
        patterns.extend(self.detect_feedback_patterns(agent_name, lookback_interactions))

        return patterns

    def store_pattern(self, pattern: Pattern) -> Pattern:
        """Store a detected pattern."""
        return self.store.create_pattern(pattern)
