"""Data aggregation and summarization."""

from datetime import datetime, timedelta
from typing import Any, Optional

from socratic_learning.storage.base import BaseLearningStore


class DataAggregator:
    """Aggregates and summarizes learning data for reporting."""

    def __init__(self, store: BaseLearningStore):
        """Initialize aggregator with storage backend."""
        self.store = store

    def get_agent_summary(self, agent_name: str) -> dict[str, Any]:
        """Get comprehensive summary for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dict with agent summary stats
        """
        interactions = self.store.list_interactions(agent_name=agent_name, limit=10000)

        if not interactions:
            return {
                "agent_name": agent_name,
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "total_cost_usd": 0.0,
                "avg_rating": None,
                "total_feedback_count": 0,
            }

        successful = sum(1 for i in interactions if i.success)
        failed = len(interactions) - successful
        durations = [i.duration_ms for i in interactions if i.duration_ms > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        total_cost = sum(i.cost_usd for i in interactions)

        feedback_items = [i for i in interactions if i.user_rating is not None]
        ratings1: list[int] = [i.user_rating for i in feedback_items]  # type: ignore
        avg_rating = (
            sum(ratings1) / len(ratings1)
            if ratings1
            else None
        )

        return {
            "agent_name": agent_name,
            "total_interactions": len(interactions),
            "successful_interactions": successful,
            "failed_interactions": failed,
            "success_rate": successful / len(interactions) * 100 if interactions else 0.0,
            "avg_duration_ms": avg_duration,
            "total_cost_usd": total_cost,
            "avg_rating": avg_rating,
            "total_feedback_count": len(feedback_items),
        }

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        """Get comprehensive summary for a session.

        Args:
            session_id: ID of the session

        Returns:
            Dict with session summary stats
        """
        interactions = self.store.list_interactions(session_id=session_id, limit=10000)

        if not interactions:
            return {
                "session_id": session_id,
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "success_rate": 0.0,
                "unique_agents": 0,
                "avg_duration_ms": 0.0,
                "total_cost_usd": 0.0,
                "avg_rating": None,
            }

        successful = sum(1 for i in interactions if i.success)
        failed = len(interactions) - successful
        unique_agents = len(set(i.agent_name for i in interactions))
        durations = [i.duration_ms for i in interactions if i.duration_ms > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        total_cost = sum(i.cost_usd for i in interactions)

        feedback_items = [i for i in interactions if i.user_rating is not None]
        ratings2: list[int] = [i.user_rating for i in feedback_items]  # type: ignore
        avg_rating = (
            sum(ratings2) / len(ratings2)
            if ratings2
            else None
        )

        return {
            "session_id": session_id,
            "total_interactions": len(interactions),
            "successful_interactions": successful,
            "failed_interactions": failed,
            "success_rate": successful / len(interactions) * 100 if interactions else 0.0,
            "unique_agents": unique_agents,
            "avg_duration_ms": avg_duration,
            "total_cost_usd": total_cost,
            "avg_rating": avg_rating,
        }

    def get_global_summary(self) -> dict[str, Any]:
        """Get overall summary across all data.

        Returns:
            Dict with global summary stats
        """
        interactions = self.store.list_interactions(limit=10000)

        if not interactions:
            return {
                "total_interactions": 0,
                "total_sessions": 0,
                "total_agents": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "total_cost_usd": 0.0,
                "avg_rating": None,
            }

        successful = sum(1 for i in interactions if i.success)
        failed = len(interactions) - successful
        unique_sessions = len(set(i.session_id for i in interactions))
        unique_agents = len(set(i.agent_name for i in interactions))
        durations = [i.duration_ms for i in interactions if i.duration_ms > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        total_cost = sum(i.cost_usd for i in interactions)

        feedback_items = [i for i in interactions if i.user_rating is not None]
        ratings3: list[int] = [i.user_rating for i in feedback_items]  # type: ignore
        avg_rating = (
            sum(ratings3) / len(ratings3)
            if ratings3
            else None
        )

        return {
            "total_interactions": len(interactions),
            "total_sessions": unique_sessions,
            "total_agents": unique_agents,
            "successful_interactions": successful,
            "failed_interactions": failed,
            "success_rate": successful / len(interactions) * 100 if interactions else 0.0,
            "avg_duration_ms": avg_duration,
            "total_cost_usd": total_cost,
            "avg_rating": avg_rating,
        }

    def compare_time_periods(
        self, agent_name: Optional[str] = None, days1: int = 7, days2: int = 7
    ) -> dict[str, Any]:
        """Compare metrics between two time periods.

        Args:
            agent_name: Optional agent name to filter
            days1: Days back for first period
            days2: Days back for second period (starting after first)

        Returns:
            Comparison dict with both periods and changes
        """
        end_time = datetime.utcnow()

        # First period
        period1_start = end_time - timedelta(days=days1 + days2)
        period1_end = end_time - timedelta(days=days2)

        interactions1 = self.store.list_interactions(
            agent_name=agent_name,
            start_time=period1_start,
            end_time=period1_end,
            limit=10000,
        )

        # Second period
        period2_start = end_time - timedelta(days=days2)
        period2_end = end_time

        interactions2 = self.store.list_interactions(
            agent_name=agent_name,
            start_time=period2_start,
            end_time=period2_end,
            limit=10000,
        )

        # Calculate metrics for each period
        def get_metrics(interactions: list[Any]) -> dict[str, Any]:
            if not interactions:
                return {
                    "count": 0,
                    "success_rate": 0.0,
                    "avg_duration": 0.0,
                    "total_cost": 0.0,
                }

            successful = sum(1 for i in interactions if i.success)
            durations = [i.duration_ms for i in interactions if i.duration_ms > 0]
            avg_duration = sum(durations) / len(durations) if durations else 0.0
            total_cost = sum(i.cost_usd for i in interactions)

            return {
                "count": len(interactions),
                "success_rate": successful / len(interactions) * 100 if interactions else 0.0,
                "avg_duration": avg_duration,
                "total_cost": total_cost,
            }

        metrics1 = get_metrics(interactions1)
        metrics2 = get_metrics(interactions2)

        return {
            "period1": {
                "days_back": days1 + days2,
                "days_ago": days2,
                **metrics1,
            },
            "period2": {
                "days_back": days2,
                "days_ago": 0,
                **metrics2,
            },
            "changes": {
                "count_change": metrics2["count"] - metrics1["count"],
                "success_rate_change": metrics2["success_rate"] - metrics1["success_rate"],
                "duration_change": metrics2["avg_duration"] - metrics1["avg_duration"],
                "cost_change": metrics2["total_cost"] - metrics1["total_cost"],
            },
        }

    def get_agent_list_with_metrics(self) -> list[dict[str, Any]]:
        """Get list of all agents with their metrics.

        Returns:
            List of agent summaries sorted by interaction count
        """
        interactions = self.store.list_interactions(limit=10000)

        if not interactions:
            return []

        # Group by agent
        agents_dict: dict[str, list[Any]] = {}
        for interaction in interactions:
            if interaction.agent_name not in agents_dict:
                agents_dict[interaction.agent_name] = []
            agents_dict[interaction.agent_name].append(interaction)

        # Calculate metrics for each agent
        agent_summaries = []
        for agent_name, agent_interactions in agents_dict.items():
            successful = sum(1 for i in agent_interactions if i.success)
            feedback_items = [i for i in agent_interactions if i.user_rating is not None]
            ratings_list: list[int] = [i.user_rating for i in feedback_items]
            avg_rating = (
                sum(ratings_list) / len(ratings_list)
                if ratings_list
                else None
            )

            agent_summaries.append(
                {
                    "agent_name": agent_name,
                    "interaction_count": len(agent_interactions),
                    "success_rate": (
                        successful / len(agent_interactions) * 100 if agent_interactions else 0.0
                    ),
                    "avg_rating": avg_rating,
                    "feedback_count": len(feedback_items),
                }
            )

        # Sort by interaction count (descending)
        return sorted(agent_summaries, key=lambda x: x["interaction_count"], reverse=True)

    def get_error_summary(self, agent_name: Optional[str] = None) -> dict[str, Any]:
        """Get summary of errors and failures.

        Args:
            agent_name: Optional agent name to filter

        Returns:
            Dict with error summary stats
        """
        interactions = self.store.list_interactions(agent_name=agent_name, limit=10000)

        failed = [i for i in interactions if not i.success]

        if not failed:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "error_types": {},
                "most_common_errors": [],
            }

        error_dict: dict[str, int] = {}
        for interaction in failed:
            error_msg = interaction.error_message or "Unknown"
            error_dict[error_msg] = error_dict.get(error_msg, 0) + 1

        # Get top 5 most common errors
        most_common = sorted(error_dict.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_errors": len(failed),
            "error_rate": len(failed) / len(interactions) * 100 if interactions else 0.0,
            "error_types": error_dict,
            "most_common_errors": [
                {"error": error, "count": count} for error, count in most_common
            ],
        }

    def get_cost_summary(self, agent_name: Optional[str] = None) -> dict[str, Any]:
        """Get cost breakdown and analysis.

        Args:
            agent_name: Optional agent name to filter

        Returns:
            Dict with cost summary stats
        """
        interactions = self.store.list_interactions(agent_name=agent_name, limit=10000)

        if not interactions:
            return {
                "total_cost": 0.0,
                "interaction_count": 0,
                "cost_per_interaction": 0.0,
                "cost_per_token": 0.0,
                "most_expensive_interactions": [],
            }

        total_cost = sum(i.cost_usd for i in interactions)
        total_tokens = sum(i.input_tokens + i.output_tokens for i in interactions)

        # Get most expensive interactions
        sorted_by_cost = sorted(interactions, key=lambda x: x.cost_usd, reverse=True)
        most_expensive = sorted_by_cost[:5]

        return {
            "total_cost": total_cost,
            "interaction_count": len(interactions),
            "cost_per_interaction": total_cost / len(interactions) if interactions else 0.0,
            "cost_per_token": (total_cost / total_tokens if total_tokens > 0 else 0.0),
            "total_tokens": total_tokens,
            "most_expensive_interactions": [
                {
                    "interaction_id": i.interaction_id,
                    "agent_name": i.agent_name,
                    "cost_usd": i.cost_usd,
                    "tokens": i.input_tokens + i.output_tokens,
                }
                for i in most_expensive
            ],
        }
