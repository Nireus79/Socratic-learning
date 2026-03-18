"""Openclaw skill integration for Socratic Learning."""

from typing import Any, Dict, List, Optional

from socratic_learning.analytics.metrics_collector import MetricsCollector
from socratic_learning.analytics.pattern_detector import PatternDetector
from socratic_learning.core.interaction import Interaction
from socratic_learning.recommendations.engine import RecommendationEngine
from socratic_learning.storage.sqlite_store import SQLiteLearningStore
from socratic_learning.tracking.logger import InteractionLogger
from socratic_learning.tracking.session import Session


class SocraticLearningSkill:
    """Openclaw skill for continuous learning from agent interactions.

    Provides learning tracking, analytics, and recommendations for improving
    agent performance in Openclaw workflows.
    """

    def __init__(self, store: Optional[SQLiteLearningStore] = None) -> None:
        """Initialize the Socratic Learning skill."""
        self.store = store or SQLiteLearningStore()
        self.logger = InteractionLogger(self.store)
        self.metrics_collector = MetricsCollector(self.store)
        self.pattern_detector = PatternDetector(self.store)
        self.recommendation_engine = RecommendationEngine(self.store)
        self._sessions: Dict[str, Session] = {}
        self._interactions: Dict[str, Interaction] = {}

    def create_session(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new learning session.

        Args:
            user_id: Identifier for the user/workflow
            context: Optional context information

        Returns:
            Session ID for tracking interactions
        """
        session = Session(
            user_id=user_id,
            context=context or {},
        )
        self._sessions[session.session_id] = session
        return session.session_id

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
    ) -> Optional[str]:
        """Log an agent interaction for learning.

        Args:
            session_id: Session ID for grouping interactions
            agent_name: Name of the agent
            input_data: Input to the agent
            output_data: Output from the agent
            duration_ms: Execution time in milliseconds
            success: Whether the interaction succeeded
            error_message: Error message if failed
            **kwargs: Additional parameters (model_name, tokens, cost, etc.)

        Returns:
            Interaction ID or None if session not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

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
        return interaction.interaction_id

    def add_feedback(
        self,
        interaction_id: str,
        rating: int,
        feedback: str = "",
    ) -> bool:
        """Add user feedback to an interaction.

        Args:
            interaction_id: ID of the interaction
            rating: Rating (1-5 stars)
            feedback: Text feedback

        Returns:
            True if feedback was added, False if interaction not found
        """
        interaction = self._interactions.get(interaction_id)
        if not interaction:
            return False

        interaction.user_rating = rating
        interaction.user_feedback = feedback
        return True

    def get_metrics(
        self,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get performance metrics for agents.

        Args:
            agent_name: Filter by agent name
            session_id: Filter by session ID

        Returns:
            Metrics dictionary or None if no data
        """
        interactions = [
            i
            for i in self._interactions.values()
            if (not agent_name or i.agent_name == agent_name)
            and (not session_id or i.session_id == session_id)
        ]

        if not interactions:
            return None

        metric = self.metrics_collector.calculate_metrics(
            agent_name=agent_name,
            session_id=session_id,
        )

        if not metric:
            return None

        return metric.to_dict()

    def detect_patterns(
        self,
        agent_name: Optional[str] = None,
        min_confidence: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Detect patterns in agent behavior.

        Args:
            agent_name: Filter by agent name
            min_confidence: Minimum confidence threshold

        Returns:
            List of detected patterns
        """
        interactions = [
            i for i in self._interactions.values() if not agent_name or i.agent_name == agent_name
        ]

        if not interactions:
            return []

        patterns = self.pattern_detector.detect_all_patterns(agent_name=agent_name)

        return [p.to_dict() for p in patterns if p.confidence >= min_confidence]

    def get_recommendations(
        self,
        agent_name: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get learning recommendations.

        Args:
            agent_name: Filter by agent name
            priority: Filter by priority (high, medium, low)

        Returns:
            List of recommendations
        """
        interactions = [
            i for i in self._interactions.values() if not agent_name or i.agent_name == agent_name
        ]

        if not interactions:
            return []

        recommendations = self.recommendation_engine.generate_recommendations(agent_name=agent_name)

        results = []
        for rec in recommendations:
            if priority and rec.priority != priority:
                continue
            results.append(rec.to_dict())

        return results

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a complete summary of a session.

        Args:
            session_id: Session ID

        Returns:
            Session summary or None if not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        interactions = [i for i in self._interactions.values() if i.session_id == session_id]

        agents = list(set(i.agent_name for i in interactions))
        metrics_by_agent = {}
        for agent in agents:
            metric = self.get_metrics(agent_name=agent, session_id=session_id)
            if metric:
                metrics_by_agent[agent] = metric

        patterns = self.detect_patterns()
        recommendations = self.get_recommendations()

        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "total_interactions": len(interactions),
            "agents": agents,
            "metrics_by_agent": metrics_by_agent,
            "patterns_detected": len(patterns),
            "recommendations": len(recommendations),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall learning statistics.

        Returns:
            Statistics dictionary
        """
        total_sessions = len(self._sessions)
        total_interactions = len(self._interactions)

        agents = list(set(i.agent_name for i in self._interactions.values()))
        success_count = sum(1 for i in self._interactions.values() if i.success)

        ratings = [i.user_rating for i in self._interactions.values() if i.user_rating is not None]

        return {
            "total_sessions": total_sessions,
            "total_interactions": total_interactions,
            "unique_agents": len(agents),
            "success_rate": (success_count / total_interactions if total_interactions > 0 else 0.0),
            "average_rating": (sum(ratings) / len(ratings) if ratings else None),
            "patterns_count": len(self.detect_patterns()),
            "recommendations_count": len(self.get_recommendations()),
        }

    def clear(self) -> None:
        """Clear all tracked sessions and interactions."""
        self._sessions.clear()
        self._interactions.clear()
