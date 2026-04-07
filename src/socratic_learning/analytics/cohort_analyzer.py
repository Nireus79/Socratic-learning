"""Cohort analysis tools for learning analytics."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SegmentationStrategy(str, Enum):
    """Strategies for cohort segmentation."""

    TEMPORAL = "temporal"  # By signup/start date
    BEHAVIORAL = "behavioral"  # By behavior patterns
    DEMOGRAPHIC = "demographic"  # By user attributes
    PERFORMANCE = "performance"  # By learning performance
    ENGAGEMENT = "engagement"  # By engagement level
    CUSTOM = "custom"  # Custom user function


@dataclass
class CohortMetrics:
    """Metrics for a single cohort."""

    cohort_id: str
    size: int
    avg_engagement: float
    avg_success_rate: float
    avg_learning_velocity: float
    retention_rate: float
    completion_rate: float
    dropout_rate: float
    total_interactions: int
    median_time_on_platform: float  # in hours
    churn_probability: float
    performance_percentile: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cohort_id": self.cohort_id,
            "size": self.size,
            "avg_engagement": self.avg_engagement,
            "avg_success_rate": self.avg_success_rate,
            "avg_learning_velocity": self.avg_learning_velocity,
            "retention_rate": self.retention_rate,
            "completion_rate": self.completion_rate,
            "dropout_rate": self.dropout_rate,
            "total_interactions": self.total_interactions,
            "median_time_on_platform": self.median_time_on_platform,
            "churn_probability": self.churn_probability,
            "performance_percentile": self.performance_percentile,
            "metadata": self.metadata,
        }


@dataclass
class CohortComparison:
    """Comparison between two cohorts."""

    cohort_a_id: str
    cohort_b_id: str
    engagement_delta: float
    success_rate_delta: float
    learning_velocity_delta: float
    retention_delta: float
    statistical_significance: float  # p-value
    effect_size: float  # Cohen's d or similar
    winner_cohort: str  # ID of better performing cohort

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cohort_a_id": self.cohort_a_id,
            "cohort_b_id": self.cohort_b_id,
            "engagement_delta": self.engagement_delta,
            "success_rate_delta": self.success_rate_delta,
            "learning_velocity_delta": self.learning_velocity_delta,
            "retention_delta": self.retention_delta,
            "statistical_significance": self.statistical_significance,
            "effect_size": self.effect_size,
            "winner_cohort": self.winner_cohort,
        }


@dataclass
class TrendPoint:
    """Single data point in a trend."""

    timestamp: str
    value: float
    cohort_id: str
    metric_name: str


class CohortAnalyzer:
    """Analyzes learning cohorts for comparative performance."""

    def __init__(self):
        """Initialize cohort analyzer."""
        self.cohorts: Dict[str, List[Dict[str, Any]]] = {}
        self.cohort_metrics: Dict[str, CohortMetrics] = {}
        self.logger = logging.getLogger(__name__)

    def segment_users(
        self,
        users: List[Dict[str, Any]],
        strategy: SegmentationStrategy,
        key: Optional[str] = None,
        custom_fn: Optional[Callable] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Segment users into cohorts.

        Args:
            users: List of user dictionaries with data
            strategy: Segmentation strategy to use
            key: Key for attribute-based segmentation
            custom_fn: Custom function for CUSTOM strategy

        Returns:
            Dictionary mapping cohort IDs to user lists
        """
        cohorts: Dict[str, List[Dict[str, Any]]] = {}

        if strategy == SegmentationStrategy.TEMPORAL:
            # Segment by signup date
            cohorts = self._segment_temporal(users)
        elif strategy == SegmentationStrategy.BEHAVIORAL:
            # Segment by behavior patterns
            cohorts = self._segment_behavioral(users)
        elif strategy == SegmentationStrategy.DEMOGRAPHIC:
            # Segment by demographic attribute
            cohorts = self._segment_demographic(users, key or "country")
        elif strategy == SegmentationStrategy.PERFORMANCE:
            # Segment by performance level
            cohorts = self._segment_performance(users)
        elif strategy == SegmentationStrategy.ENGAGEMENT:
            # Segment by engagement level
            cohorts = self._segment_engagement(users)
        elif strategy == SegmentationStrategy.CUSTOM:
            # Use custom function
            if custom_fn is None:
                raise ValueError("custom_fn required for CUSTOM strategy")
            cohorts = self._segment_custom(users, custom_fn)
        else:
            raise ValueError(f"Unknown segmentation strategy: {strategy}")

        self.cohorts = cohorts
        return cohorts

    def calculate_cohort_metrics(self) -> Dict[str, CohortMetrics]:
        """
        Calculate metrics for all cohorts.

        Returns:
            Dictionary mapping cohort IDs to CohortMetrics
        """
        metrics = {}

        for cohort_id, users in self.cohorts.items():
            metrics[cohort_id] = self._calculate_metrics(cohort_id, users)

        self.cohort_metrics = metrics
        return metrics

    def compare_cohorts(
        self,
        cohort_a_id: str,
        cohort_b_id: str,
    ) -> CohortComparison:
        """
        Compare two cohorts.

        Args:
            cohort_a_id: First cohort ID
            cohort_b_id: Second cohort ID

        Returns:
            CohortComparison with differences
        """
        if cohort_a_id not in self.cohort_metrics or cohort_b_id not in self.cohort_metrics:
            raise ValueError("Both cohorts must have calculated metrics")

        metrics_a = self.cohort_metrics[cohort_a_id]
        metrics_b = self.cohort_metrics[cohort_b_id]

        engagement_delta = metrics_a.avg_engagement - metrics_b.avg_engagement
        success_delta = metrics_a.avg_success_rate - metrics_b.avg_success_rate
        velocity_delta = metrics_a.avg_learning_velocity - metrics_b.avg_learning_velocity
        retention_delta = metrics_a.retention_rate - metrics_b.retention_rate

        # Determine winner
        winner = (
            cohort_a_id
            if sum([engagement_delta, success_delta, velocity_delta, retention_delta]) > 0
            else cohort_b_id
        )

        return CohortComparison(
            cohort_a_id=cohort_a_id,
            cohort_b_id=cohort_b_id,
            engagement_delta=engagement_delta,
            success_rate_delta=success_delta,
            learning_velocity_delta=velocity_delta,
            retention_delta=retention_delta,
            statistical_significance=0.05,  # Placeholder
            effect_size=abs(success_delta)
            / max(metrics_a.avg_success_rate, metrics_b.avg_success_rate, 0.1),
            winner_cohort=winner,
        )

    def get_cohort_retention_curve(
        self,
        cohort_id: str,
        time_periods: int = 12,
    ) -> List[float]:
        """
        Get retention curve for a cohort over time.

        Args:
            cohort_id: ID of cohort
            time_periods: Number of time periods to analyze

        Returns:
            List of retention rates over time
        """
        if cohort_id not in self.cohorts:
            raise ValueError(f"Cohort {cohort_id} not found")

        users = self.cohorts[cohort_id]
        retention = []

        # Simulate retention curve (would use real data in production)
        for period in range(time_periods):
            # Retention typically follows: R(t) = R0 * (1 - (t/T)^k)
            # Start at 100% and decay
            period_retention = max(0, 1.0 - (period / time_periods) ** 1.5)
            retention.append(period_retention)

        return retention

    def get_cohort_trends(
        self,
        cohort_id: str,
        metric: str = "engagement",
    ) -> List[TrendPoint]:
        """
        Get trends for a specific metric in a cohort.

        Args:
            cohort_id: ID of cohort
            metric: Metric to track (engagement, success_rate, velocity)

        Returns:
            List of TrendPoints over time
        """
        if cohort_id not in self.cohorts:
            raise ValueError(f"Cohort {cohort_id} not found")

        # Placeholder: would pull real time-series data
        trends = []
        for week in range(12):
            # Simulate varying metric over time
            value = 0.5 + (0.3 * (week / 12))
            trend = TrendPoint(
                timestamp=f"week_{week}",
                value=value,
                cohort_id=cohort_id,
                metric_name=metric,
            )
            trends.append(trend)

        return trends

    def identify_at_risk_cohorts(
        self,
        threshold: float = 0.3,
    ) -> List[Tuple[str, float]]:
        """
        Identify cohorts at risk of churn.

        Args:
            threshold: Churn probability threshold

        Returns:
            List of (cohort_id, churn_probability) tuples
        """
        at_risk = []

        for cohort_id, metrics in self.cohort_metrics.items():
            if metrics.churn_probability >= threshold:
                at_risk.append((cohort_id, metrics.churn_probability))

        return sorted(at_risk, key=lambda x: x[1], reverse=True)

    def get_top_performing_cohorts(
        self,
        metric: str = "avg_success_rate",
        top_n: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Get top performing cohorts by metric.

        Args:
            metric: Metric to rank by
            top_n: Number of cohorts to return

        Returns:
            List of (cohort_id, metric_value) tuples
        """
        ranking = []

        for cohort_id, metrics in self.cohort_metrics.items():
            if hasattr(metrics, metric):
                value = getattr(metrics, metric)
                ranking.append((cohort_id, value))

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking[:top_n]

    def _segment_temporal(self, users: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment by signup date (monthly)."""
        cohorts: Dict[str, List[Dict[str, Any]]] = {}

        for user in users:
            signup_date = user.get("signup_date", "unknown")
            month = signup_date[:7] if len(signup_date) >= 7 else "unknown"
            cohort_id = f"cohort_{month}"

            if cohort_id not in cohorts:
                cohorts[cohort_id] = []
            cohorts[cohort_id].append(user)

        return cohorts

    def _segment_behavioral(self, users: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment by behavior patterns."""
        cohorts: Dict[str, List[Dict[str, Any]]] = {
            "power_users": [],
            "regular_users": [],
            "inactive_users": [],
        }

        for user in users:
            interactions = user.get("total_interactions", 0)

            if interactions > 50:
                cohorts["power_users"].append(user)
            elif interactions > 5:
                cohorts["regular_users"].append(user)
            else:
                cohorts["inactive_users"].append(user)

        return cohorts

    def _segment_demographic(
        self,
        users: List[Dict[str, Any]],
        key: str,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Segment by demographic attribute."""
        cohorts: Dict[str, List[Dict[str, Any]]] = {}

        for user in users:
            value = user.get(key, "unknown")
            cohort_id = f"{key}_{value}"

            if cohort_id not in cohorts:
                cohorts[cohort_id] = []
            cohorts[cohort_id].append(user)

        return cohorts

    def _segment_performance(self, users: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment by performance level."""
        cohorts: Dict[str, List[Dict[str, Any]]] = {
            "high_performers": [],
            "average_performers": [],
            "low_performers": [],
        }

        for user in users:
            success_rate = user.get("success_rate", 0.5)

            if success_rate >= 0.75:
                cohorts["high_performers"].append(user)
            elif success_rate >= 0.25:
                cohorts["average_performers"].append(user)
            else:
                cohorts["low_performers"].append(user)

        return cohorts

    def _segment_engagement(self, users: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segment by engagement level."""
        cohorts: Dict[str, List[Dict[str, Any]]] = {
            "highly_engaged": [],
            "moderately_engaged": [],
            "low_engagement": [],
        }

        for user in users:
            engagement = user.get("engagement_score", 0.5)

            if engagement >= 0.75:
                cohorts["highly_engaged"].append(user)
            elif engagement >= 0.25:
                cohorts["moderately_engaged"].append(user)
            else:
                cohorts["low_engagement"].append(user)

        return cohorts

    def _segment_custom(
        self,
        users: List[Dict[str, Any]],
        custom_fn: Callable,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Segment using custom function."""
        cohorts: Dict[str, List[Dict[str, Any]]] = {}

        for user in users:
            cohort_id = custom_fn(user)

            if cohort_id not in cohorts:
                cohorts[cohort_id] = []
            cohorts[cohort_id].append(user)

        return cohorts

    def _calculate_metrics(
        self,
        cohort_id: str,
        users: List[Dict[str, Any]],
    ) -> CohortMetrics:
        """Calculate metrics for a cohort."""
        if not users:
            return CohortMetrics(
                cohort_id=cohort_id,
                size=0,
                avg_engagement=0,
                avg_success_rate=0,
                avg_learning_velocity=0,
                retention_rate=0,
                completion_rate=0,
                dropout_rate=0,
                total_interactions=0,
                median_time_on_platform=0,
                churn_probability=0,
                performance_percentile=0,
            )

        avg_engagement = sum(u.get("engagement_score", 0.5) for u in users) / len(users)
        avg_success_rate = sum(u.get("success_rate", 0.5) for u in users) / len(users)
        avg_velocity = sum(u.get("learning_velocity", 0.5) for u in users) / len(users)
        total_interactions = sum(u.get("total_interactions", 0) for u in users)

        # Calculate retention
        active_users = len([u for u in users if u.get("is_active", True)])
        retention_rate = active_users / len(users) if users else 0

        return CohortMetrics(
            cohort_id=cohort_id,
            size=len(users),
            avg_engagement=avg_engagement,
            avg_success_rate=avg_success_rate,
            avg_learning_velocity=avg_velocity,
            retention_rate=retention_rate,
            completion_rate=sum(1 for u in users if u.get("completed", False)) / len(users),
            dropout_rate=1 - retention_rate,
            total_interactions=total_interactions,
            median_time_on_platform=sum(u.get("hours_on_platform", 0) for u in users) / len(users),
            churn_probability=1 - retention_rate,
            performance_percentile=avg_success_rate * 100,
        )
