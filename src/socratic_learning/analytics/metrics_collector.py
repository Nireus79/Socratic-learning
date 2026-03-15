"""Metrics collection and aggregation."""

from datetime import datetime, timedelta
from typing import Optional

from socratic_learning.core import Metric
from socratic_learning.storage.base import BaseLearningStore


class MetricsCollector:
    """Collects and aggregates metrics from interactions."""

    def __init__(self, store: BaseLearningStore):
        """Initialize metrics collector with storage backend."""
        self.store = store

    def calculate_metrics(
        self,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Metric:
        """Calculate metrics for given criteria."""
        # Get interactions
        interactions = self.store.list_interactions(
            agent_name=agent_name,
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        if not interactions:
            return Metric(
                agent_name=agent_name,
                session_id=session_id,
                time_period_start=start_time or datetime.utcnow(),
                time_period_end=end_time or datetime.utcnow(),
            )

        # Calculate metrics
        metric = Metric(
            agent_name=agent_name,
            session_id=session_id,
            time_period_start=start_time or interactions[-1].timestamp,
            time_period_end=end_time or interactions[0].timestamp,
        )

        metric.total_interactions = len(interactions)
        metric.successful_interactions = sum(1 for i in interactions if i.success)
        metric.failed_interactions = metric.total_interactions - metric.successful_interactions
        metric.success_rate = (
            (metric.successful_interactions / metric.total_interactions * 100)
            if metric.total_interactions > 0
            else 0.0
        )

        # Performance metrics
        durations = [i.duration_ms for i in interactions]
        if durations:
            metric.avg_duration_ms = sum(durations) / len(durations)
            metric.max_duration_ms = max(durations)
            metric.min_duration_ms = min(durations)

        # Cost tracking
        metric.total_input_tokens = sum(i.input_tokens for i in interactions)
        metric.total_output_tokens = sum(i.output_tokens for i in interactions)
        metric.total_cost_usd = sum(i.cost_usd for i in interactions)

        # User feedback
        feedback_interactions = [i for i in interactions if i.user_rating is not None]
        if feedback_interactions:
            metric.total_feedback_count = len(feedback_interactions)
            metric.positive_feedback_count = sum(
                1 for i in feedback_interactions if i.user_rating >= 4
            )
            metric.avg_rating = sum(i.user_rating for i in feedback_interactions) / len(
                feedback_interactions
            )

        return metric

    def get_agent_metrics(self, agent_name: str) -> Metric:
        """Get metrics for a specific agent."""
        return self.calculate_metrics(agent_name=agent_name)

    def get_session_metrics(self, session_id: str) -> Metric:
        """Get metrics for a specific session."""
        return self.calculate_metrics(session_id=session_id)

    def get_metrics_for_period(
        self,
        days: int = 7,
        agent_name: Optional[str] = None,
    ) -> Metric:
        """Get metrics for a time period (e.g., last 7 days)."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        return self.calculate_metrics(
            agent_name=agent_name,
            start_time=start_time,
            end_time=end_time,
        )

    def compare_metrics(
        self,
        metric1: Metric,
        metric2: Metric,
    ) -> dict:
        """Compare two metrics and return improvements."""
        return {
            "success_rate_change": metric2.success_rate - metric1.success_rate,
            "duration_improvement": metric1.avg_duration_ms - metric2.avg_duration_ms,
            "cost_change": metric2.total_cost_usd - metric1.total_cost_usd,
            "rating_change": (metric2.avg_rating or 0) - (metric1.avg_rating or 0),
        }

    def store_metrics(self, metric: Metric) -> Metric:
        """Store calculated metrics."""
        return self.store.create_metric(metric)
