"""Feedback collection system."""

from typing import Any, Optional

from socratic_learning.core import Interaction
from socratic_learning.storage.base import BaseLearningStore


class FeedbackCollector:
    """Collects user feedback on interactions."""

    def __init__(self, store: BaseLearningStore):
        """Initialize feedback collector with storage backend."""
        self.store = store

    def collect_feedback(
        self,
        interaction_id: str,
        rating: int,
        feedback: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Interaction]:
        """Collect feedback on an interaction.

        Args:
            interaction_id: ID of the interaction
            rating: Rating from 1 to 5
            feedback: Text feedback
            metadata: Optional metadata (source, session_type, etc.)

        Returns:
            Updated interaction with feedback, or None if not found
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        if not feedback or not isinstance(feedback, str):
            raise ValueError("Feedback must be a non-empty string")

        return self.store.update_interaction_feedback(
            interaction_id=interaction_id,
            rating=rating,
            feedback=feedback,
        )

    def batch_feedback(
        self,
        feedback_items: list[dict[str, Any]],
    ) -> list[Optional[Interaction]]:
        """Collect feedback on multiple interactions.

        Args:
            feedback_items: List of dicts with keys: interaction_id, rating, feedback

        Returns:
            List of updated interactions
        """
        results = []
        for item in feedback_items:
            try:
                result = self.collect_feedback(
                    interaction_id=item["interaction_id"],
                    rating=item["rating"],
                    feedback=item["feedback"],
                    metadata=item.get("metadata"),
                )
                results.append(result)
            except (ValueError, KeyError):
                # Log error but continue with next item
                results.append(None)

        return results

    def get_interaction_feedback(
        self,
        interaction_id: str,
    ) -> Optional[dict[str, Any]]:
        """Get feedback for a specific interaction.

        Args:
            interaction_id: ID of the interaction

        Returns:
            Dict with rating and feedback, or None if not found/no feedback
        """
        interaction = self.store.get_interaction(interaction_id)
        if not interaction or interaction.user_rating is None:
            return None

        return {
            "interaction_id": interaction_id,
            "rating": interaction.user_rating,
            "feedback": interaction.user_feedback,
            "feedback_timestamp": interaction.feedback_timestamp,
        }

    def get_session_feedback(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get all feedback in a session.

        Args:
            session_id: ID of the session
            limit: Maximum number of feedback items to return
            offset: Number of items to skip

        Returns:
            List of feedback items with interaction context
        """
        interactions = self.store.list_interactions(
            session_id=session_id,
            limit=limit,
            offset=offset,
        )

        feedback_items = []
        for interaction in interactions:
            if interaction.user_rating is not None:
                feedback_items.append(
                    {
                        "interaction_id": interaction.interaction_id,
                        "agent_name": interaction.agent_name,
                        "rating": interaction.user_rating,
                        "feedback": interaction.user_feedback,
                        "feedback_timestamp": interaction.feedback_timestamp,
                    }
                )

        return feedback_items

    def get_agent_feedback(
        self,
        agent_name: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get all feedback for a specific agent.

        Args:
            agent_name: Name of the agent
            limit: Maximum number of feedback items to return
            offset: Number of items to skip

        Returns:
            List of feedback items
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            limit=limit,
            offset=offset,
        )

        feedback_items = []
        for interaction in interactions:
            if interaction.user_rating is not None:
                feedback_items.append(
                    {
                        "interaction_id": interaction.interaction_id,
                        "rating": interaction.user_rating,
                        "feedback": interaction.user_feedback,
                        "feedback_timestamp": interaction.feedback_timestamp,
                    }
                )

        return feedback_items

    def feedback_summary(
        self,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get summary statistics of feedback.

        Args:
            agent_name: Optional agent name to filter
            session_id: Optional session ID to filter

        Returns:
            Summary dict with counts and averages
        """
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            session_id=session_id,
            limit=10000,
        )

        feedback_interactions = [i for i in interactions if i.user_rating is not None]

        if not feedback_interactions:
            return {
                "total_interactions": len(interactions),
                "feedback_count": 0,
                "feedback_rate": 0.0,
                "avg_rating": None,
                "distribution": {},
            }

        ratings: list[int] = [i.user_rating for i in feedback_interactions]  # type: ignore
        distribution: dict[int, int] = {}
        for rating in range(1, 6):
            count = sum(1 for r in ratings if r == rating)
            distribution[rating] = count

        return {
            "total_interactions": len(interactions),
            "feedback_count": len(feedback_interactions),
            "feedback_rate": (
                len(feedback_interactions) / len(interactions) * 100 if interactions else 0.0
            ),
            "avg_rating": sum(ratings) / len(ratings) if ratings else None,
            "positive_feedback_count": sum(1 for r in ratings if r >= 4),
            "negative_feedback_count": sum(1 for r in ratings if r <= 2),
            "distribution": distribution,
        }
