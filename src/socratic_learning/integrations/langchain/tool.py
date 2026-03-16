"""LangChain tool integration for Socratic Learning."""

from typing import Any, Dict, Optional, Union

from socratic_learning.analytics.metrics_collector import MetricsCollector
from socratic_learning.analytics.pattern_detector import PatternDetector
from socratic_learning.recommendations.engine import RecommendationEngine
from socratic_learning.storage.sqlite_store import SQLiteLearningStore
from socratic_learning.tracking.logger import InteractionLogger


class LearningTool:
    """LangChain tool for continuous learning from interactions.

    Can be used in LangChain chains and agents to automatically track,
    analyze, and improve agent performance over time.
    """

    def __init__(self, store: Optional[SQLiteLearningStore] = None) -> None:
        """Initialize the Learning Tool."""
        self.store = store or SQLiteLearningStore()
        self.logger = InteractionLogger(self.store)
        self.metrics_collector = MetricsCollector(self.store)
        self.pattern_detector = PatternDetector(self.store)
        self.recommendation_engine = RecommendationEngine(self.store)
        self._sessions: Dict[str, Any] = {}
        self._interactions: Dict[str, Any] = {}

    @property
    def tool_name(self) -> str:
        """Get the tool name for LangChain."""
        return "learning_tracker"

    @property
    def tool_description(self) -> str:
        """Get the tool description for LangChain."""
        return (
            "Tracks agent interactions and provides learning analytics. "
            "Can log interactions, detect patterns, calculate metrics, "
            "and generate recommendations for agent improvement."
        )

    def log_interaction(
        self,
        session_id: str,
        agent_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        duration_ms: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Log an agent interaction.

        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            input_data: Input to the agent
            output_data: Output from the agent
            duration_ms: Execution time
            success: Whether interaction succeeded
            error_message: Error message if failed
            **kwargs: Additional parameters

        Returns:
            Interaction details as dict
        """
        try:
            interaction = self.logger.log_interaction(
                session_id=session_id,
                agent_name=agent_name,
                input_data=input_data,
                output_data=output_data,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                **kwargs,
            )

            self._interactions[interaction.interaction_id] = interaction

            return {
                "status": "logged",
                "interaction_id": interaction.interaction_id,
                "agent": agent_name,
                "success": success,
                "duration_ms": duration_ms,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def add_feedback(
        self,
        interaction_id: str,
        rating: int,
        feedback: str = "",
    ) -> Dict[str, Any]:
        """Add feedback to an interaction.

        Args:
            interaction_id: ID of the interaction
            rating: Rating (1-5 stars)
            feedback: Text feedback

        Returns:
            Feedback status as dict
        """
        interaction = self._interactions.get(interaction_id)
        if not interaction:
            return {
                "status": "error",
                "message": f"Interaction {interaction_id} not found",
            }

        interaction.user_rating = rating
        interaction.user_feedback = feedback

        return {
            "status": "recorded",
            "interaction_id": interaction_id,
            "rating": rating,
        }

    def get_metrics(
        self,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get performance metrics.

        Args:
            agent_name: Filter by agent
            session_id: Filter by session

        Returns:
            Metrics as dict
        """
        interactions = [
            i
            for i in self._interactions.values()
            if (not agent_name or i.agent_name == agent_name)
            and (not session_id or i.session_id == session_id)
        ]

        if not interactions:
            return {"status": "no_data"}

        metric = self.metrics_collector.calculate_metrics(
            agent_name=agent_name,
            session_id=session_id,
        )

        if not metric:
            return {"status": "error", "message": "Could not calculate metrics"}

        return {
            "status": "calculated",
            "success_rate": f"{metric.success_rate:.1%}",
            "total_interactions": metric.total_interactions,
            "average_duration_ms": f"{metric.avg_duration_ms:.2f}",
            "average_rating": metric.avg_rating,
        }

    def detect_patterns(
        self,
        agent_name: Optional[str] = None,
        min_confidence: float = 0.7,
    ) -> Dict[str, Any]:
        """Detect patterns in agent behavior.

        Args:
            agent_name: Filter by agent
            min_confidence: Minimum confidence

        Returns:
            Patterns as dict
        """
        interactions = [
            i
            for i in self._interactions.values()
            if not agent_name or i.agent_name == agent_name
        ]

        if not interactions:
            return {"status": "no_data"}

        patterns = self.pattern_detector.detect_all_patterns(
            agent_name=agent_name
        )

        filtered_patterns = [
            p for p in patterns if p.confidence >= min_confidence
        ]

        return {
            "status": "detected",
            "patterns_count": len(filtered_patterns),
            "patterns": [
                {
                    "name": p.name,
                    "type": p.pattern_type,
                    "confidence": f"{p.confidence:.1%}",
                }
                for p in filtered_patterns
            ],
        }

    def get_recommendations(
        self,
        agent_name: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get learning recommendations.

        Args:
            agent_name: Filter by agent
            priority: Filter by priority

        Returns:
            Recommendations as dict
        """
        interactions = [
            i
            for i in self._interactions.values()
            if not agent_name or i.agent_name == agent_name
        ]

        if not interactions:
            return {"status": "no_data"}

        recommendations = (
            self.recommendation_engine.generate_recommendations(
                agent_name=agent_name
            )
        )

        filtered_recs = [
            r
            for r in recommendations
            if not priority or r.priority == priority
        ]

        return {
            "status": "generated",
            "total_recommendations": len(filtered_recs),
            "recommendations": [
                {
                    "title": r.title,
                    "priority": r.priority,
                    "action": r.suggested_action,
                }
                for r in filtered_recs
            ],
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics.

        Returns:
            Statistics as dict
        """
        total_interactions = len(self._interactions)
        success_count = sum(
            1 for i in self._interactions.values() if i.success
        )

        ratings = [
            i.user_rating
            for i in self._interactions.values()
            if i.user_rating is not None
        ]

        return {
            "status": "calculated",
            "total_interactions": total_interactions,
            "success_rate": (
                f"{success_count / total_interactions:.1%}"
                if total_interactions > 0
                else "0%"
            ),
            "average_rating": (
                f"{sum(ratings) / len(ratings):.1f}/5.0" if ratings else None
            ),
            "unique_agents": len(
                set(i.agent_name for i in self._interactions.values())
            ),
        }

    def invoke(
        self,
        tool_input: Union[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Invoke the tool for LangChain compatibility.

        Args:
            tool_input: Tool input as string or dict

        Returns:
            Tool output as dict
        """
        if isinstance(tool_input, str):
            return {
                "error": "Invalid input format. Expected dict with action and params."
            }

        action = tool_input.get("action")
        params = tool_input.get("params", {})

        if action == "log":
            return self.log_interaction(**params)

        elif action == "feedback":
            return self.add_feedback(**params)

        elif action == "metrics":
            return self.get_metrics(**params)

        elif action == "patterns":
            return self.detect_patterns(**params)

        elif action == "recommendations":
            return self.get_recommendations(**params)

        elif action == "statistics":
            return self.get_statistics()

        else:
            return {"error": f"Unknown action: {action}"}

    def clear(self) -> None:
        """Clear all tracked data."""
        self._sessions.clear()
        self._interactions.clear()
