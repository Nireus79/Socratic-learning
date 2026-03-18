"""Core interaction model for tracking agent interactions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class Interaction:
    """Core entity tracking a single agent interaction."""

    interaction_id: str = field(default_factory=lambda: str(uuid4()))

    # Session context
    session_id: str = ""  # Groups related interactions
    agent_name: str = ""  # Which agent handled this
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Input/Output
    input_data: Dict[str, Any] = field(default_factory=dict)  # User input
    output_data: Dict[str, Any] = field(default_factory=dict)  # Agent response

    # LLM tracking (optional)
    model_name: Optional[str] = None  # e.g., "claude-opus-4"
    provider: Optional[str] = None  # e.g., "anthropic"
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    # Performance
    duration_ms: float = 0.0  # Response time
    success: bool = True  # Did it complete successfully?
    error_message: Optional[str] = None

    # User feedback (optional, added later)
    user_rating: Optional[int] = None  # 1-5 stars
    user_feedback: Optional[str] = None  # Text feedback
    feedback_timestamp: Optional[datetime] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "interaction_id": self.interaction_id,
            "session_id": self.session_id,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "input_data": self.input_data,
            "output_data": self.output_data,
            "model_name": self.model_name,
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message,
            "user_rating": self.user_rating,
            "user_feedback": self.user_feedback,
            "feedback_timestamp": (
                self.feedback_timestamp.isoformat() if self.feedback_timestamp else None
            ),
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Interaction":
        """Deserialize from storage."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if data.get("feedback_timestamp"):
            data["feedback_timestamp"] = datetime.fromisoformat(data["feedback_timestamp"])
        return cls(**data)
