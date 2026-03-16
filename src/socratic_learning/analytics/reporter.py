"""Report generation for learning analytics."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from socratic_learning.analytics.aggregator import DataAggregator
from socratic_learning.storage.base import BaseLearningStore


class ReportGenerator:
    """Generates comprehensive JSON reports on learning data."""

    def __init__(self, store: BaseLearningStore):
        """Initialize report generator with storage backend."""
        self.store = store
        self.aggregator = DataAggregator(store)

    def generate_executive_summary(self) -> dict[str, Any]:
        """Generate executive summary report.

        Returns:
            Dict with executive summary
        """
        global_summary = self.aggregator.get_global_summary()
        agent_list = self.aggregator.get_agent_list_with_metrics()
        error_summary = self.aggregator.get_error_summary()

        return {
            "report_type": "executive_summary",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overview": global_summary,
            "top_agents": agent_list[:10],  # Top 10 agents
            "error_summary": error_summary,
            "recommendations": self._generate_recommendations(
                global_summary, agent_list, error_summary
            ),
        }

    def generate_agent_report(self, agent_name: str) -> dict[str, Any]:
        """Generate detailed report for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dict with agent report
        """
        agent_summary = self.aggregator.get_agent_summary(agent_name)
        error_summary = self.aggregator.get_error_summary(agent_name)
        cost_summary = self.aggregator.get_cost_summary(agent_name)
        patterns = self.store.list_patterns(agent_name=agent_name, limit=100)
        recommendations = self.store.list_recommendations(agent_name=agent_name, limit=100)

        return {
            "report_type": "agent_report",
            "agent_name": agent_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": agent_summary,
            "errors": error_summary,
            "costs": cost_summary,
            "patterns": [
                {
                    "name": p.name,
                    "type": p.pattern_type,
                    "confidence": p.confidence,
                    "occurrences": p.occurrence_count,
                }
                for p in patterns
            ],
            "recommendations": [
                {
                    "title": r.title,
                    "priority": r.priority,
                    "type": r.recommendation_type,
                    "suggested_action": r.suggested_action,
                    "applied": r.applied,
                }
                for r in recommendations
            ],
        }

    def generate_comparison_report(self, agent1: str, agent2: str) -> dict[str, Any]:
        """Generate comparison report between two agents.

        Args:
            agent1: First agent name
            agent2: Second agent name

        Returns:
            Dict with comparison report
        """
        summary1 = self.aggregator.get_agent_summary(agent1)
        summary2 = self.aggregator.get_agent_summary(agent2)
        cost1 = self.aggregator.get_cost_summary(agent1)
        cost2 = self.aggregator.get_cost_summary(agent2)

        return {
            "report_type": "comparison_report",
            "agents": [agent1, agent2],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "agent1": {
                "name": agent1,
                "summary": summary1,
                "cost": cost1,
            },
            "agent2": {
                "name": agent2,
                "summary": summary2,
                "cost": cost2,
            },
            "comparison": {
                "success_rate_diff": summary2["success_rate"] - summary1["success_rate"],
                "duration_diff": summary2["avg_duration_ms"] - summary1["avg_duration_ms"],
                "cost_diff": cost2["total_cost"] - cost1["total_cost"],
                "rating_diff": (summary2["avg_rating"] or 0) - (summary1["avg_rating"] or 0),
            },
            "winner": self._determine_winner(summary1, summary2),
        }

    def generate_timeline_report(
        self, agent_name: Optional[str] = None, days: int = 30
    ) -> dict[str, Any]:
        """Generate timeline report showing trends over time.

        Args:
            agent_name: Optional agent name to filter
            days: Number of days to analyze

        Returns:
            Dict with timeline report
        """
        # Create daily buckets
        timeline: dict[str, dict[str, Any]] = {}

        now = datetime.now(timezone.utc)
        for day_offset in range(days):
            day = now - __import__("datetime").timedelta(days=day_offset)
            day_str = day.strftime("%Y-%m-%d")

            # Get interactions for this day
            start_time = day.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + __import__("datetime").timedelta(days=1)

            interactions = self.store.list_interactions(
                agent_name=agent_name,
                start_time=start_time,
                end_time=end_time,
                limit=10000,
            )

            if interactions:
                successful = sum(1 for i in interactions if i.success)
                feedback = [i for i in interactions if i.user_rating is not None]
                ratings_timeline: list[int] = [i.user_rating for i in feedback]  # type: ignore
                avg_rating = (
                    sum(ratings_timeline) / len(ratings_timeline) if ratings_timeline else None
                )

                timeline[day_str] = {
                    "interactions": len(interactions),
                    "successful": successful,
                    "failed": len(interactions) - successful,
                    "success_rate": successful / len(interactions) * 100 if interactions else 0.0,
                    "avg_rating": avg_rating,
                }

        return {
            "report_type": "timeline_report",
            "agent_name": agent_name,
            "period_days": days,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "timeline": timeline,
        }

    def generate_quality_report(self) -> dict[str, Any]:
        """Generate quality metrics report.

        Returns:
            Dict with quality report
        """
        agents = self.aggregator.get_agent_list_with_metrics()

        quality_grades = []
        for agent in agents:
            grade = self._calculate_quality_grade(agent["success_rate"], agent["avg_rating"])
            quality_grades.append(
                {
                    "agent_name": agent["agent_name"],
                    "success_rate": agent["success_rate"],
                    "avg_rating": agent["avg_rating"],
                    "grade": grade,
                    "interactions": agent["interaction_count"],
                }
            )

        # Sort by grade
        quality_grades.sort(key=lambda x: x["grade"], reverse=True)

        return {
            "report_type": "quality_report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "agents": quality_grades,
            "summary": {
                "total_agents": len(quality_grades),
                "grade_a_count": sum(1 for a in quality_grades if a["grade"] >= 90),
                "grade_b_count": sum(1 for a in quality_grades if 80 <= a["grade"] < 90),
                "grade_c_count": sum(1 for a in quality_grades if 70 <= a["grade"] < 80),
                "grade_d_count": sum(1 for a in quality_grades if a["grade"] < 70),
            },
        }

    def export_report_to_file(self, report: dict[str, Any], output_path: str) -> None:
        """Export report to JSON file.

        Args:
            report: Report dict to export
            output_path: Path to write JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

    def generate_dashboard_data(self) -> dict[str, Any]:
        """Generate data suitable for dashboard visualization.

        Returns:
            Dict with dashboard-ready data
        """
        global_summary = self.aggregator.get_global_summary()
        agent_list = self.aggregator.get_agent_list_with_metrics()
        error_summary = self.aggregator.get_error_summary()

        return {
            "dashboard_data": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics": {
                    "total_interactions": global_summary["total_interactions"],
                    "success_rate": global_summary["success_rate"],
                    "total_agents": global_summary["total_agents"],
                    "total_sessions": global_summary["total_sessions"],
                    "total_cost_usd": global_summary["total_cost_usd"],
                    "avg_rating": global_summary["avg_rating"],
                },
                "charts": {
                    "agents_by_volume": [
                        {"name": a["agent_name"], "value": a["interaction_count"]}
                        for a in agent_list[:10]
                    ],
                    "agents_by_success": sorted(
                        agent_list, key=lambda x: x["success_rate"], reverse=True
                    )[:10],
                    "error_distribution": error_summary["error_types"],
                },
                "top_performers": agent_list[:5],
                "needs_attention": [a for a in agent_list if a["success_rate"] < 70][:5],
            }
        }

    @staticmethod
    def _generate_recommendations(
        global_summary: dict[str, Any],
        agent_list: list[dict[str, Any]],
        error_summary: dict[str, Any],
    ) -> list[dict[str, str]]:
        """Generate recommendations based on data analysis.

        Args:
            global_summary: Global summary stats
            agent_list: List of agent summaries
            error_summary: Error summary stats

        Returns:
            List of recommendation dicts
        """
        recommendations = []

        # Check overall success rate
        if global_summary["success_rate"] < 80:
            recommendations.append(
                {
                    "type": "success_rate",
                    "message": f"Overall success rate is {global_summary['success_rate']:.1f}%. "
                    "Consider investigating and improving agent reliability.",
                    "priority": "high",
                }
            )

        # Check for high error rate
        if error_summary["error_rate"] > 20:
            recommendations.append(
                {
                    "type": "error_rate",
                    "message": f"Error rate is {error_summary['error_rate']:.1f}%. "
                    "Focus on error handling and input validation.",
                    "priority": "high",
                }
            )

        # Check for underperforming agents
        underperformers = [a for a in agent_list if a["success_rate"] < 70]
        if underperformers:
            recommendations.append(
                {
                    "type": "agent_performance",
                    "message": f"{len(underperformers)} agent(s) have success rate below 70%. "
                    "Consider fine-tuning or retraining.",
                    "priority": "medium",
                }
            )

        # Check for low ratings
        low_rated = [a for a in agent_list if a["avg_rating"] is not None and a["avg_rating"] < 3]
        if low_rated:
            recommendations.append(
                {
                    "type": "user_satisfaction",
                    "message": f"{len(low_rated)} agent(s) have low user ratings. "
                    "Investigate user feedback and improve responses.",
                    "priority": "high",
                }
            )

        return recommendations

    @staticmethod
    def _determine_winner(summary1: dict[str, Any], summary2: dict[str, Any]) -> str:
        """Determine which agent performed better.

        Args:
            summary1: First agent summary
            summary2: Second agent summary

        Returns:
            Name of better performing agent
        """
        score1 = (
            summary1["success_rate"]
            + (summary1["avg_rating"] or 0) * 10
            - summary1["avg_duration_ms"] / 100
        )
        score2 = (
            summary2["success_rate"]
            + (summary2["avg_rating"] or 0) * 10
            - summary2["avg_duration_ms"] / 100
        )

        winner: str = (
            str(summary2.get("agent_name", "Agent 2"))
            if score2 > score1
            else str(summary1.get("agent_name", "Agent 1"))
        )
        return winner

    @staticmethod
    def _calculate_quality_grade(success_rate: float, avg_rating: Optional[float]) -> float:
        """Calculate quality grade for an agent.

        Args:
            success_rate: Success rate percentage (0-100)
            avg_rating: Average user rating (1-5) or None

        Returns:
            Grade score (0-100)
        """
        # 60% weight on success rate, 40% on rating
        success_component = success_rate * 0.6
        rating_component = ((avg_rating or 0) / 5 * 100) * 0.4

        return success_component + rating_component
