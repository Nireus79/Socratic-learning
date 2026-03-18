"""Session management for tracking groups of interactions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Session:
    """A session groups related interactions together."""

    session_id: str = field(default_factory=lambda: str(uuid4()))

    # Session context
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    is_active: bool = True

    # Metadata
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "is_active": self.is_active,
            "context": self.context,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Deserialize from storage."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("ended_at"):
            data["ended_at"] = datetime.fromisoformat(data["ended_at"])
        return cls(**data)

    def end(self) -> None:
        """Mark session as ended."""
        self.ended_at = datetime.utcnow()
        self.is_active = False

    def get_duration_seconds(self) -> float:
        """Get session duration in seconds."""
        end_time = self.ended_at or datetime.utcnow()
        delta = end_time - self.created_at
        return delta.total_seconds()
