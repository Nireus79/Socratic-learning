"""Pattern model for detected patterns in agent interactions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4


@dataclass
class Pattern:
    """Detected pattern in agent interactions."""

    pattern_id: str = field(default_factory=lambda: str(uuid4()))

    # Pattern identification
    pattern_type: str = ""  # "error", "success", "topic", "behavior"
    name: str = ""  # Human-readable name
    description: str = ""  # What the pattern represents

    # Detection metadata
    first_detected: datetime = field(default_factory=datetime.utcnow)
    last_detected: datetime = field(default_factory=datetime.utcnow)
    occurrence_count: int = 1

    # Scope
    agent_names: List[str] = field(default_factory=list)  # Which agents
    session_ids: List[str] = field(default_factory=list)  # Which sessions

    # Pattern data
    confidence: float = 0.0  # 0.0-1.0 confidence score
    evidence: List[str] = field(default_factory=list)  # Interaction IDs

    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "name": self.name,
            "description": self.description,
            "first_detected": self.first_detected.isoformat(),
            "last_detected": self.last_detected.isoformat(),
            "occurrence_count": self.occurrence_count,
            "agent_names": self.agent_names,
            "session_ids": self.session_ids,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pattern":
        """Deserialize from storage."""
        data = data.copy()
        data["first_detected"] = datetime.fromisoformat(data["first_detected"])
        data["last_detected"] = datetime.fromisoformat(data["last_detected"])
        return cls(**data)
