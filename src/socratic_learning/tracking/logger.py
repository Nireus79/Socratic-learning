"""Interaction logger for tracking agent interactions."""

from typing import Any, Dict, Optional

from socratic_learning.core import Interaction
from socratic_learning.storage.base import BaseLearningStore
from socratic_learning.tracking.session import Session


class InteractionLogger:
    """Logs and tracks agent interactions with context."""

    def __init__(self, store: BaseLearningStore):
        """Initialize logger with storage backend."""
        self.store = store
        self.sessions: Dict[str, Session] = {}

    def create_session(
        self,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new tracking session."""
        session = Session(
            user_id=user_id,
            context=context or {},
        )
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID."""
        return self.sessions.get(session_id)

    def end_session(self, session_id: str) -> Optional[Session]:
        """End a session."""
        session = self.sessions.get(session_id)
        if session:
            session.end()
        return session

    def log_interaction(
        self,
        session_id: str,
        agent_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
        duration_ms: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None,
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Interaction:
        """Log an interaction to the store."""
        interaction = Interaction(
            session_id=session_id,
            agent_name=agent_name,
            input_data=input_data,
            output_data=output_data,
            model_name=model_name,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            tags=tags or [],
            metadata=metadata or {},
        )

        return self.store.create_interaction(interaction)

    def add_feedback(
        self,
        interaction_id: str,
        rating: int,
        feedback: str,
    ) -> Optional[Interaction]:
        """Add user feedback to an interaction."""
        return self.store.update_interaction_feedback(
            interaction_id,
            rating=rating,
            feedback=feedback,
        )

    def get_session_interactions(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list:
        """Get all interactions in a session."""
        return self.store.list_interactions(
            session_id=session_id,
            limit=limit,
            offset=offset,
        )
