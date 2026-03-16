"""Recommendation engine for learning insights."""

from datetime import timezone
from typing import Any, Optional

from socratic_learning.analytics import MetricsCollector, PatternDetector
from socratic_learning.core import Recommendation
from socratic_learning.recommendations.rules import RecommendationRules
from socratic_learning.storage.base import BaseLearningStore


class RecommendationEngine:
    """Generates learning recommendations based on patterns and metrics."""

    def __init__(self, store: BaseLearningStore):
        """Initialize recommendation engine with storage backend."""
        self.store = store
        self.metrics_collector = MetricsCollector(store)
        self.pattern_detector = PatternDetector(store)

    def generate_recommendations(
        self,
        agent_name: Optional[str] = None,
        min_confidence: float = 0.65,
    ) -> list[Recommendation]:
        """Generate recommendations for an agent based on detected patterns.

        Args:
            agent_name: Optional agent name to focus on
            min_confidence: Minimum pattern confidence to consider

        Returns:
            List of recommendations
        """
        recommendations = []

        # Get patterns
        patterns = self.pattern_detector.detect_all_patterns(
            agent_name=agent_name,
        )

        # Generate recommendations from patterns
        for pattern in patterns:
            if pattern.confidence < min_confidence:
                continue

            if pattern.pattern_type == "error":
                rec = RecommendationRules.from_error_pattern(pattern, agent_name or "Unknown")
                if rec:
                    recommendations.append(rec)

            elif pattern.pattern_type == "performance":
                metric = self.metrics_collector.calculate_metrics(agent_name=agent_name)
                rec = RecommendationRules.from_performance_pattern(
                    pattern, metric, agent_name or "Unknown"
                )
                if rec:
                    recommendations.append(rec)

            elif pattern.pattern_type == "feedback":
                if "Low" in pattern.name:
                    rec = RecommendationRules.from_low_satisfaction(
                        pattern, agent_name or "Unknown"
                    )
                elif "High" in pattern.name or "Satisfaction" in pattern.name:
                    rec = RecommendationRules.from_high_satisfaction(
                        pattern, agent_name or "Unknown"
                    )
                else:
                    rec = None

                if rec:
                    recommendations.append(rec)

            elif pattern.pattern_type == "success":
                rec = RecommendationRules.from_success_pattern(pattern, agent_name or "Unknown")
                if rec:
                    recommendations.append(rec)

        # Also generate from metrics if no patterns found
        if not recommendations:
            metric = self.metrics_collector.calculate_metrics(agent_name=agent_name)
            metric_recs = RecommendationRules.from_metric(metric, agent_name or "Unknown")
            if metric_recs:
                recommendations.extend(metric_recs)

        # Store recommendations
        stored_recommendations = []
        for rec in recommendations:
            stored = self.store.create_recommendation(rec)
            stored_recommendations.append(stored)

        return stored_recommendations

    def get_high_priority_recommendations(
        self,
        agent_name: Optional[str] = None,
        limit: int = 10,
    ) -> list[Recommendation]:
        """Get high priority recommendations.

        Args:
            agent_name: Optional agent name to filter
            limit: Maximum number to return

        Returns:
            List of high priority recommendations
        """
        recommendations = self.store.list_recommendations(
            agent_name=agent_name,
            priority="high",
            applied=False,
            limit=limit,
        )
        return recommendations

    def get_recommendations_by_type(
        self,
        recommendation_type: str,
        agent_name: Optional[str] = None,
        limit: int = 10,
    ) -> list[Recommendation]:
        """Get recommendations of a specific type.

        Args:
            recommendation_type: Type of recommendation to get
            agent_name: Optional agent name to filter
            limit: Maximum number to return

        Returns:
            List of recommendations
        """
        all_recommendations = self.store.list_recommendations(
            agent_name=agent_name,
            limit=limit,
        )

        return [r for r in all_recommendations if r.recommendation_type == recommendation_type]

    def mark_recommendation_applied(
        self,
        recommendation_id: str,
    ) -> Optional[Recommendation]:
        """Mark a recommendation as applied.

        Args:
            recommendation_id: ID of the recommendation

        Returns:
            Updated recommendation
        """
        rec = self.store.list_recommendations(limit=10000)
        for r in rec:
            if r.recommendation_id == recommendation_id:
                r.applied = True
                from datetime import datetime

                r.applied_at = datetime.now(timezone.utc)
                return self.store.update_recommendation(r)

        return None

    def set_recommendation_effectiveness(
        self,
        recommendation_id: str,
        effectiveness_score: float,
    ) -> Optional[Recommendation]:
        """Set effectiveness score for an applied recommendation.

        Args:
            recommendation_id: ID of the recommendation
            effectiveness_score: Score from 0 to 1

        Returns:
            Updated recommendation
        """
        if not 0 <= effectiveness_score <= 1:
            raise ValueError("Effectiveness score must be between 0 and 1")

        rec = self.store.list_recommendations(limit=10000)
        for r in rec:
            if r.recommendation_id == recommendation_id:
                r.effectiveness_score = effectiveness_score
                return self.store.update_recommendation(r)

        return None

    def get_applied_recommendations(
        self,
        agent_name: Optional[str] = None,
        limit: int = 10,
    ) -> list[Recommendation]:
        """Get applied recommendations.

        Args:
            agent_name: Optional agent name to filter
            limit: Maximum number to return

        Returns:
            List of applied recommendations
        """
        return self.store.list_recommendations(
            agent_name=agent_name,
            applied=True,
            limit=limit,
        )

    def get_recommendation_summary(
        self,
        agent_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get summary of recommendations for an agent.

        Args:
            agent_name: Optional agent name to filter

        Returns:
            Summary dict
        """
        all_recs = self.store.list_recommendations(
            agent_name=agent_name,
            limit=10000,
        )

        if not all_recs:
            return {
                "total_recommendations": 0,
                "by_priority": {},
                "by_type": {},
                "applied_count": 0,
                "applied_percentage": 0.0,
            }

        by_priority = {"high": 0, "medium": 0, "low": 0}
        by_type: dict[str, int] = {}

        for rec in all_recs:
            by_priority[rec.priority] += 1
            by_type[rec.recommendation_type] = by_type.get(rec.recommendation_type, 0) + 1

        applied_count = sum(1 for r in all_recs if r.applied)

        return {
            "total_recommendations": len(all_recs),
            "by_priority": by_priority,
            "by_type": by_type,
            "applied_count": applied_count,
            "applied_percentage": (applied_count / len(all_recs) * 100 if all_recs else 0.0),
        }
