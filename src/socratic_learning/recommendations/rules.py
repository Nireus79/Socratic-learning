"""Rule-based recommendation generation."""

from typing import Optional

from socratic_learning.core import Metric, Pattern, Recommendation


class RecommendationRules:
    """Rule-based logic for generating recommendations."""

    # Rule thresholds
    ERROR_RATE_THRESHOLD = 0.15  # 15% error rate triggers recommendation
    SUCCESS_THRESHOLD = 0.80  # 80% success rate is good
    PERFORMANCE_THRESHOLD = 2.0  # 2x average duration is slow
    SATISFACTION_THRESHOLD_HIGH = 4.5  # 4.5+ rating is excellent
    SATISFACTION_THRESHOLD_LOW = 2.5  # 2.5- rating needs improvement
    MIN_CONFIDENCE = 0.65  # Minimum pattern confidence to act on

    @staticmethod
    def from_error_pattern(
        pattern: Pattern,
        agent_name: str,
    ) -> Optional[Recommendation]:
        """Generate recommendation from error pattern.

        Args:
            pattern: Detected error pattern
            agent_name: Name of the agent

        Returns:
            Recommendation or None if confidence too low
        """
        if pattern.confidence < RecommendationRules.MIN_CONFIDENCE:
            return None

        priority = "high" if pattern.confidence > 0.85 else "medium"

        return Recommendation(
            recommendation_type="error_reduction",
            priority=priority,
            title=f"Reduce error rate for {agent_name}",
            description=(
                f"Error rate of {pattern.occurrence_count} errors detected. "
                f"Pattern confidence: {pattern.confidence:.1%}"
            ),
            rationale=(
                f"The {agent_name} agent is experiencing errors at an elevated rate. "
                "This impacts user experience and should be investigated."
            ),
            agent_name=agent_name,
            pattern_ids=[pattern.pattern_id],
            suggested_action=(
                "1. Review error logs for common failure modes\n"
                "2. Add input validation to catch problematic requests\n"
                "3. Implement fallback handling strategies\n"
                "4. Test edge cases more thoroughly"
            ),
            expected_improvement=(
                "Reducing error rate from current level to <10% "
                "would improve user satisfaction by ~15%"
            ),
        )

    @staticmethod
    def from_performance_pattern(
        pattern: Pattern,
        metric: Metric,
        agent_name: str,
    ) -> Optional[Recommendation]:
        """Generate recommendation from performance pattern.

        Args:
            pattern: Detected performance pattern
            metric: Current metrics
            agent_name: Name of the agent

        Returns:
            Recommendation or None
        """
        if pattern.confidence < RecommendationRules.MIN_CONFIDENCE:
            return None

        return Recommendation(
            recommendation_type="performance_improvement",
            priority="medium",
            title=f"Improve response time for {agent_name}",
            description=(
                f"Average response time is {metric.avg_duration_ms:.0f}ms. "
                f"Some interactions take {metric.max_duration_ms:.0f}ms."
            ),
            rationale=(
                "Slower responses reduce user satisfaction. "
                "Optimization could improve the user experience significantly."
            ),
            agent_name=agent_name,
            pattern_ids=[pattern.pattern_id],
            metric_ids=[metric.metric_id],
            suggested_action=(
                "1. Profile the agent to find bottlenecks\n"
                "2. Implement caching for common requests\n"
                "3. Optimize database queries\n"
                "4. Consider request batching or parallelization"
            ),
            expected_improvement=(
                "50% reduction in response time would improve user satisfaction by ~20%"
            ),
        )

    @staticmethod
    def from_low_satisfaction(
        pattern: Pattern,
        agent_name: str,
    ) -> Optional[Recommendation]:
        """Generate recommendation from low satisfaction pattern.

        Args:
            pattern: Detected low satisfaction pattern
            agent_name: Name of the agent

        Returns:
            Recommendation or None
        """
        if pattern.confidence < RecommendationRules.MIN_CONFIDENCE:
            return None

        return Recommendation(
            recommendation_type="quality_improvement",
            priority="high",
            title=f"Improve response quality for {agent_name}",
            description=(
                "Users are giving low ratings to this agent's responses. "
                "This indicates quality issues that need addressing."
            ),
            rationale=(
                "User satisfaction is critical. Low ratings indicate the agent "
                "is not meeting user expectations."
            ),
            agent_name=agent_name,
            pattern_ids=[pattern.pattern_id],
            suggested_action=(
                "1. Review low-rated responses for common patterns\n"
                "2. Adjust agent prompts or parameters\n"
                "3. Add more context or examples to prompts\n"
                "4. Consider fine-tuning the underlying model\n"
                "5. Gather user feedback on what's missing"
            ),
            expected_improvement=(
                "Addressing quality issues could improve ratings from current level to 4+ stars"
            ),
        )

    @staticmethod
    def from_high_satisfaction(
        pattern: Pattern,
        agent_name: str,
    ) -> Optional[Recommendation]:
        """Generate recommendation to replicate high satisfaction.

        Args:
            pattern: Detected high satisfaction pattern
            agent_name: Name of the agent

        Returns:
            Recommendation or None
        """
        if pattern.confidence < RecommendationRules.MIN_CONFIDENCE:
            return None

        return Recommendation(
            recommendation_type="pattern_replication",
            priority="low",
            title=f"Replicate success patterns for {agent_name}",
            description=(
                "This agent is performing well with high user satisfaction. "
                "Document and replicate these success patterns."
            ),
            rationale=(
                "When something works well, it's valuable to understand and "
                "replicate those successful approaches."
            ),
            agent_name=agent_name,
            pattern_ids=[pattern.pattern_id],
            suggested_action=(
                "1. Document the successful interaction patterns\n"
                "2. Extract common characteristics from high-rated responses\n"
                "3. Update prompts to emphasize these patterns\n"
                "4. Share best practices with other agents\n"
                "5. Use as a benchmark for quality"
            ),
            expected_improvement=("Replicating success patterns could maintain or improve ratings"),
        )

    @staticmethod
    def from_metric(
        metric: Metric,
        agent_name: str,
    ) -> list[Recommendation] | None:
        """Generate recommendations from metrics alone.

        Args:
            metric: Performance metric
            agent_name: Name of the agent

        Returns:
            List of recommendations or None
        """
        recommendations = []

        # High error rate
        if metric.failed_interactions > 0:
            error_rate = metric.failed_interactions / metric.total_interactions
            if error_rate > RecommendationRules.ERROR_RATE_THRESHOLD:
                rec = Recommendation(
                    recommendation_type="error_reduction",
                    priority="high",
                    title=f"Reduce error rate for {agent_name}",
                    description=(
                        f"{agent_name} has error rate of {error_rate:.1%} "
                        f"({metric.failed_interactions} failures in {metric.total_interactions} interactions)"
                    ),
                    rationale=("Error rates above 15% indicate significant reliability issues."),
                    agent_name=agent_name,
                    suggested_action=(
                        "1. Investigate common failure causes\n"
                        "2. Add input validation\n"
                        "3. Improve error handling\n"
                        "4. Test edge cases"
                    ),
                    expected_improvement=(
                        "Reducing error rate to <10% would significantly improve reliability"
                    ),
                )
                recommendations.append(rec)

        # Low satisfaction
        if (
            metric.avg_rating is not None
            and metric.avg_rating < RecommendationRules.SATISFACTION_THRESHOLD_LOW
        ):
            rec = Recommendation(
                recommendation_type="quality_improvement",
                priority="high",
                title=f"Improve response quality for {agent_name}",
                description=(
                    f"Average user rating is {metric.avg_rating:.1f}/5 stars. "
                    f"This is below acceptable threshold."
                ),
                rationale=("Low user satisfaction indicates quality issues."),
                agent_name=agent_name,
                suggested_action=(
                    "1. Review low-rated interactions\n"
                    "2. Adjust prompts or parameters\n"
                    "3. Add examples to prompts\n"
                    "4. Consider fine-tuning"
                ),
                expected_improvement=("Improving quality could raise average rating to 4+ stars"),
            )
            recommendations.append(rec)

        # High cost
        if metric.total_cost_usd > 10.0:  # Arbitrary threshold for demo
            rec = Recommendation(
                recommendation_type="cost_optimization",
                priority="medium",
                title=f"Optimize costs for {agent_name}",
                description=(
                    f"Total cost is ${metric.total_cost_usd:.2f} for {metric.total_interactions} interactions. "
                    f"Average cost per interaction: ${metric.total_cost_usd / metric.total_interactions:.2f}"
                ),
                rationale=("High costs can be reduced through optimization strategies."),
                agent_name=agent_name,
                suggested_action=(
                    "1. Use shorter prompts\n"
                    "2. Switch to faster/cheaper models\n"
                    "3. Cache common responses\n"
                    "4. Batch requests"
                ),
                expected_improvement=("20-30% cost reduction is typical with optimization"),
            )
            recommendations.append(rec)

        return recommendations if recommendations else None

    @staticmethod
    def from_success_pattern(
        pattern: Pattern,
        agent_name: str,
    ) -> Optional[Recommendation]:
        """Generate recommendation from success pattern.

        Args:
            pattern: Detected success pattern
            agent_name: Name of the agent

        Returns:
            Recommendation or None
        """
        if pattern.confidence < RecommendationRules.MIN_CONFIDENCE:
            return None

        return Recommendation(
            recommendation_type="pattern_documentation",
            priority="low",
            title=f"Document success patterns for {agent_name}",
            description=(
                f"High success rate pattern detected with {pattern.confidence:.1%} confidence."
            ),
            rationale=("Documenting what works well helps maintain quality."),
            agent_name=agent_name,
            pattern_ids=[pattern.pattern_id],
            suggested_action=(
                "1. Analyze what makes these interactions successful\n"
                "2. Document best practices\n"
                "3. Update agent configuration to emphasize these patterns\n"
                "4. Share knowledge with other agents"
            ),
            expected_improvement=("Maintaining success patterns helps ensure consistent quality"),
        )
