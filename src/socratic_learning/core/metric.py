"""Metric model for performance metrics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from ..utils import ensure_iso_datetime


@dataclass
class Metric:
    """Performance metric for an agent or session."""

    metric_id: str = field(default_factory=lambda: str(uuid4()))

    # Scope
    agent_name: Optional[str] = None  # Agent-specific or None for global
    session_id: Optional[str] = None  # Session-specific or None
    time_period_start: datetime = field(default_factory=datetime.utcnow)
    time_period_end: datetime = field(default_factory=datetime.utcnow)

    # Metrics
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    success_rate: float = 0.0  # Percentage

    # Performance
    avg_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    min_duration_ms: float = 0.0

    # Cost tracking
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0

    # User satisfaction (if feedback available)
    avg_rating: Optional[float] = None  # 1.0-5.0
    total_feedback_count: int = 0
    positive_feedback_count: int = 0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "metric_id": self.metric_id,
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "time_period_start": self.time_period_start.isoformat(),
            "time_period_end": self.time_period_end.isoformat(),
            "total_interactions": self.total_interactions,
            "successful_interactions": self.successful_interactions,
            "failed_interactions": self.failed_interactions,
            "success_rate": self.success_rate,
            "avg_duration_ms": self.avg_duration_ms,
            "max_duration_ms": self.max_duration_ms,
            "min_duration_ms": self.min_duration_ms,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": self.total_cost_usd,
            "avg_rating": self.avg_rating,
            "total_feedback_count": self.total_feedback_count,
            "positive_feedback_count": self.positive_feedback_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Metric":
        """Deserialize from storage."""
        data = ensure_iso_datetime(data, "time_period_start", "time_period_end")
        return cls(**data)
