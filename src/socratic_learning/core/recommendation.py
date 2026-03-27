"""Recommendation model for learning recommendations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..utils import ensure_decimals, ensure_iso_datetime


@dataclass
class Recommendation:
    """Learning recommendation based on analysis."""

    recommendation_id: str = field(default_factory=lambda: str(uuid4()))

    # Type and priority
    recommendation_type: str = ""  # "prompt_improvement", "model_change", etc
    priority: str = ""  # "high", "medium", "low"

    # Content
    title: str = ""
    description: str = ""
    rationale: str = ""  # Why this recommendation

    # Context
    agent_name: Optional[str] = None
    pattern_ids: List[str] = field(default_factory=list)  # Related patterns
    metric_ids: List[str] = field(default_factory=list)  # Related metrics

    # Action
    suggested_action: str = ""  # What to do
    expected_improvement: str = ""  # Expected outcome

    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    applied: bool = False
    applied_at: Optional[datetime] = None
    effectiveness_score: Optional[float] = None  # If applied, how effective?

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "agent_name": self.agent_name,
            "pattern_ids": self.pattern_ids,
            "metric_ids": self.metric_ids,
            "suggested_action": self.suggested_action,
            "expected_improvement": self.expected_improvement,
            "created_at": self.created_at.isoformat(),
            "applied": self.applied,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "effectiveness_score": self.effectiveness_score,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recommendation":
        """Deserialize from storage."""
        data = ensure_decimals(data, {"effectiveness_score": "0.0"})
        data = ensure_iso_datetime(data, "created_at", "applied_at")
        return cls(**data)
