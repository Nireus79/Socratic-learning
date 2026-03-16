"""Feedback analysis system."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from socratic_learning.storage.base import BaseLearningStore


class FeedbackAnalyzer:
    """Analyzes feedback patterns and trends."""

    def __init__(self, store: BaseLearningStore):
        """Initialize feedback analyzer with storage backend."""
        self.store = store

    def analyze_feedback_trend(
        self,
        agent_name: Optional[str] = None,
        days: int = 7,
    ) -> dict[str, Any]:
        """Analyze feedback trends over a time period.

        Args:
            agent_name: Optional agent name to filter
            days: Number of days to look back

        Returns:
            Dict with trend analysis
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)

        interactions = self.store.list_interactions(
            agent_name=agent_name,
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        feedback_interactions = [i for i in interactions if i.user_rating is not None]

        if not feedback_interactions:
            return {
                "period_days": days,
                "total_interactions": len(interactions),
                "feedback_count": 0,
                "trend": "insufficient_data",
            }

        ratings: list[int] = [i.user_rating for i in feedback_interactions]  # type: ignore
        avg_rating = sum(ratings) / len(ratings)

        # Divide into halves to detect trend
        mid = len(feedback_interactions) // 2
        if mid > 0:
            first_half_avg = sum(ratings[:mid]) / len(ratings[:mid])
            second_half_avg = sum(ratings[mid:]) / len(ratings[mid:])
            trend = (
                "improving"
                if second_half_avg > first_half_avg
                else "declining" if second_half_avg < first_half_avg else "stable"
            )
        else:
            first_half_avg = avg_rating
            second_half_avg = avg_rating
            trend = "insufficient_data"

        return {
            "period_days": days,
            "total_interactions": len(interactions),
            "feedback_count": len(feedback_interactions),
            "feedback_rate": (
                len(feedback_interactions) / len(interactions) * 100 if interactions else 0.0
            ),
            "overall_avg_rating": avg_rating,
            "first_half_avg": first_half_avg,
            "second_half_avg": second_half_avg,
            "trend": trend,
        }

    def identify_problem_areas(
        self,
        agent_name: Optional[str] = None,
        rating_threshold: int = 2,
    ) -> list[dict[str, Any]]:
        """Identify interactions with low ratings.

        Args:
            agent_name: Optional agent name to filter
            rating_threshold: Rating below which to flag

        Returns:
            List of low-rated interactions
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=10000,
        )

        problem_interactions = [
            {
                "interaction_id": i.interaction_id,
                "agent_name": i.agent_name,
                "rating": i.user_rating,
                "feedback": i.user_feedback,
                "timestamp": i.timestamp,
                "input_summary": str(i.input_data)[:100],
                "output_summary": str(i.output_data)[:100],
            }
            for i in interactions
            if i.user_rating is not None and i.user_rating <= rating_threshold
        ]

        return problem_interactions

    def identify_strengths(
        self,
        agent_name: Optional[str] = None,
        rating_threshold: int = 4,
    ) -> list[dict[str, Any]]:
        """Identify interactions with high ratings.

        Args:
            agent_name: Optional agent name to filter
            rating_threshold: Rating above which to flag

        Returns:
            List of high-rated interactions
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=10000,
        )

        strength_interactions = [
            {
                "interaction_id": i.interaction_id,
                "agent_name": i.agent_name,
                "rating": i.user_rating,
                "feedback": i.user_feedback,
                "timestamp": i.timestamp,
                "input_summary": str(i.input_data)[:100],
                "output_summary": str(i.output_data)[:100],
            }
            for i in interactions
            if i.user_rating is not None and i.user_rating >= rating_threshold
        ]

        return strength_interactions

    def sentiment_summary(
        self,
        agent_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get sentiment breakdown of feedback.

        Args:
            agent_name: Optional agent name to filter

        Returns:
            Dict with sentiment counts and percentages
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=10000,
        )

        feedback_interactions = [i for i in interactions if i.user_rating is not None]

        if not feedback_interactions:
            return {
                "total": 0,
                "positive": {"count": 0, "percentage": 0.0},
                "neutral": {"count": 0, "percentage": 0.0},
                "negative": {"count": 0, "percentage": 0.0},
            }

        total = len(feedback_interactions)
        ratings: list[int] = [i.user_rating for i in feedback_interactions]  # type: ignore
        positive = sum(1 for r in ratings if r >= 4)
        negative = sum(1 for r in ratings if r <= 2)
        neutral = total - positive - negative

        return {
            "total": total,
            "positive": {
                "count": positive,
                "percentage": positive / total * 100 if total > 0 else 0.0,
            },
            "neutral": {
                "count": neutral,
                "percentage": neutral / total * 100 if total > 0 else 0.0,
            },
            "negative": {
                "count": negative,
                "percentage": negative / total * 100 if total > 0 else 0.0,
            },
        }

    def compare_feedback(
        self,
        agent1: str,
        agent2: str,
        days: int = 7,
    ) -> dict[str, Any]:
        """Compare feedback between two agents.

        Args:
            agent1: First agent name
            agent2: Second agent name
            days: Number of days to look back

        Returns:
            Comparison dict
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)

        interactions1 = self.store.list_interactions(
            agent_name=agent1,
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        interactions2 = self.store.list_interactions(
            agent_name=agent2,
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        ratings1: list[int] = [i.user_rating for i in interactions1 if i.user_rating is not None]
        ratings2: list[int] = [i.user_rating for i in interactions2 if i.user_rating is not None]

        avg1 = sum(ratings1) / len(ratings1) if ratings1 else None
        avg2 = sum(ratings2) / len(ratings2) if ratings2 else None

        return {
            "agent1": {
                "name": agent1,
                "feedback_count": len(ratings1),
                "avg_rating": avg1,
            },
            "agent2": {
                "name": agent2,
                "feedback_count": len(ratings2),
                "avg_rating": avg2,
            },
            "rating_difference": (avg2 - avg1 if avg1 is not None and avg2 is not None else None),
            "winner": (agent2 if avg2 is not None and (avg1 is None or avg2 > avg1) else agent1),
        }
