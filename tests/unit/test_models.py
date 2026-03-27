"""Unit tests for core models."""

import json
from datetime import datetime, timezone

from socratic_learning.core import Interaction, Metric, Pattern, Recommendation


class TestInteraction:
    """Test Interaction model."""

    def test_interaction_creation(self):
        """Test basic interaction creation."""
        interaction = Interaction(
            session_id="session_123",
            agent_name="TestAgent",
            input_data={"topic": "test"},
            output_data={"response": "test response"},
        )

        assert interaction.session_id == "session_123"
        assert interaction.agent_name == "TestAgent"
        assert interaction.input_data == {"topic": "test"}
        assert interaction.output_data == {"response": "test response"}
        assert interaction.success is True

    def test_interaction_with_timestamps(self):
        """Test interaction with custom timestamps."""
        now = datetime.now(timezone.utc)
        interaction = Interaction(
            session_id="session_456",
            agent_name="TestAgent",
            input_data={},
            output_data={},
            timestamp=now,
        )

        assert interaction.timestamp == now

    def test_interaction_with_feedback(self):
        """Test interaction with user feedback."""
        interaction = Interaction(
            session_id="session_789",
            agent_name="TestAgent",
            input_data={},
            output_data={},
            user_rating=5,
            user_feedback="Great response!",
        )

        assert interaction.user_rating == 5
        assert interaction.user_feedback == "Great response!"

    def test_interaction_serialization(self):
        """Test interaction to_dict and from_dict."""
        original = Interaction(
            session_id="session_123",
            agent_name="TestAgent",
            input_data={"question": "What is AI?"},
            output_data={"answer": "AI is..."},
            model_name="claude-opus-4",
            provider="anthropic",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.15,
            duration_ms=1200.5,
            success=True,
            user_rating=4,
            user_feedback="Good",
            tags=["ai", "test"],
            metadata={"version": "1.0"},
        )

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = Interaction.from_dict(data)

        # Verify all fields match
        assert restored.session_id == original.session_id
        assert restored.agent_name == original.agent_name
        assert restored.input_data == original.input_data
        assert restored.output_data == original.output_data
        assert restored.model_name == original.model_name
        assert restored.provider == original.provider
        assert restored.input_tokens == original.input_tokens
        assert restored.output_tokens == original.output_tokens
        assert restored.cost_usd == original.cost_usd
        assert restored.duration_ms == original.duration_ms
        assert restored.success == original.success
        assert restored.user_rating == original.user_rating
        assert restored.user_feedback == original.user_feedback
        assert restored.tags == original.tags
        assert restored.metadata == original.metadata

    def test_interaction_json_serializable(self):
        """Test that interaction can be serialized to JSON."""
        interaction = Interaction(
            session_id="session_123",
            agent_name="TestAgent",
            input_data={"test": "data"},
            output_data={"test": "output"},
        )

        data = interaction.to_dict()
        json_str = json.dumps(data)

        # Verify it's valid JSON
        restored_data = json.loads(json_str)
        assert restored_data["session_id"] == "session_123"


class TestPattern:
    """Test Pattern model."""

    def test_pattern_creation(self):
        """Test basic pattern creation."""
        pattern = Pattern(
            pattern_type="error",
            name="Recursion Error Pattern",
            description="Errors occur with recursive topics",
        )

        assert pattern.pattern_type == "error"
        assert pattern.name == "Recursion Error Pattern"
        assert pattern.confidence == 0.0  # Default

    def test_pattern_with_metadata(self):
        """Test pattern with occurrence tracking."""
        pattern = Pattern(
            pattern_type="success",
            name="High Rating Pattern",
            description="High user ratings with examples",
            occurrence_count=10,
            confidence=0.85,
            agent_names=["TestAgent"],
            session_ids=["session_1", "session_2"],
        )

        assert pattern.occurrence_count == 10
        assert pattern.confidence == 0.85
        assert pattern.agent_names == ["TestAgent"]
        assert len(pattern.session_ids) == 2

    def test_pattern_serialization(self):
        """Test pattern to_dict and from_dict."""
        original = Pattern(
            pattern_type="topic",
            name="Complex Topic Pattern",
            description="Complex topics get lower ratings",
            occurrence_count=5,
            confidence=0.72,
            agent_names=["Agent1", "Agent2"],
            session_ids=["s1", "s2"],
            evidence=["int1", "int2", "int3"],
            tags=["important", "actionable"],
            metadata={"threshold": 0.7},
        )

        data = original.to_dict()
        restored = Pattern.from_dict(data)

        assert restored.pattern_type == original.pattern_type
        assert restored.name == original.name
        assert restored.occurrence_count == original.occurrence_count
        assert restored.confidence == original.confidence
        assert restored.agent_names == original.agent_names
        assert restored.evidence == original.evidence


class TestMetric:
    """Test Metric model."""

    def test_metric_creation(self):
        """Test basic metric creation."""
        metric = Metric(
            agent_name="TestAgent",
            total_interactions=10,
            successful_interactions=8,
            failed_interactions=2,
            success_rate=80.0,
        )

        assert metric.agent_name == "TestAgent"
        assert metric.total_interactions == 10
        assert metric.success_rate == 80.0

    def test_metric_with_performance_data(self):
        """Test metric with performance tracking."""
        metric = Metric(
            agent_name="TestAgent",
            avg_duration_ms=1250.5,
            max_duration_ms=3000.0,
            min_duration_ms=500.0,
        )

        assert metric.avg_duration_ms == 1250.5
        assert metric.max_duration_ms == 3000.0
        assert metric.min_duration_ms == 500.0

    def test_metric_with_cost_tracking(self):
        """Test metric with cost tracking."""
        metric = Metric(
            total_input_tokens=1000,
            total_output_tokens=2000,
            total_cost_usd=0.45,
        )

        assert metric.total_input_tokens == 1000
        assert metric.total_output_tokens == 2000
        assert metric.total_cost_usd == 0.45

    def test_metric_with_feedback(self):
        """Test metric with user feedback aggregation."""
        metric = Metric(
            avg_rating=4.5,
            total_feedback_count=20,
            positive_feedback_count=18,
        )

        assert metric.avg_rating == 4.5
        assert metric.total_feedback_count == 20
        assert metric.positive_feedback_count == 18

    def test_metric_serialization(self):
        """Test metric to_dict and from_dict."""
        original = Metric(
            agent_name="TestAgent",
            session_id="session_123",
            total_interactions=10,
            successful_interactions=8,
            failed_interactions=2,
            success_rate=80.0,
            avg_duration_ms=1500.0,
            max_duration_ms=3000.0,
            min_duration_ms=500.0,
            total_input_tokens=5000,
            total_output_tokens=10000,
            total_cost_usd=1.5,
            avg_rating=4.5,
            total_feedback_count=8,
            positive_feedback_count=7,
        )

        data = original.to_dict()
        restored = Metric.from_dict(data)

        assert restored.agent_name == original.agent_name
        assert restored.total_interactions == original.total_interactions
        assert restored.success_rate == original.success_rate
        assert restored.avg_duration_ms == original.avg_duration_ms
        assert restored.total_cost_usd == original.total_cost_usd
        assert restored.avg_rating == original.avg_rating


class TestRecommendation:
    """Test Recommendation model."""

    def test_recommendation_creation(self):
        """Test basic recommendation creation."""
        rec = Recommendation(
            recommendation_type="prompt_improvement",
            priority="high",
            title="Improve Prompt Clarity",
            description="Current prompts are ambiguous",
        )

        assert rec.recommendation_type == "prompt_improvement"
        assert rec.priority == "high"
        assert rec.title == "Improve Prompt Clarity"
        assert rec.applied is False

    def test_recommendation_with_action(self):
        """Test recommendation with action guidance."""
        rec = Recommendation(
            title="Test",
            suggested_action="Add examples to prompt",
            expected_improvement="30% higher satisfaction rating",
        )

        assert rec.suggested_action == "Add examples to prompt"
        assert rec.expected_improvement == "30% higher satisfaction rating"

    def test_recommendation_with_context(self):
        """Test recommendation with pattern and metric context."""
        rec = Recommendation(
            title="Test",
            agent_name="TestAgent",
            pattern_ids=["pattern_1", "pattern_2"],
            metric_ids=["metric_1"],
        )

        assert rec.agent_name == "TestAgent"
        assert len(rec.pattern_ids) == 2
        assert len(rec.metric_ids) == 1

    def test_recommendation_applied_tracking(self):
        """Test recommendation application tracking."""
        rec = Recommendation(
            title="Test",
            applied=True,
            applied_at=datetime.now(timezone.utc),
            effectiveness_score=0.85,
        )

        assert rec.applied is True
        assert rec.applied_at is not None
        assert rec.effectiveness_score == 0.85

    def test_recommendation_serialization(self):
        """Test recommendation to_dict and from_dict."""
        now = datetime.now(timezone.utc)
        original = Recommendation(
            recommendation_type="model_change",
            priority="medium",
            title="Switch Model",
            description="Current model underperforming",
            rationale="High error rate detected",
            agent_name="TestAgent",
            pattern_ids=["p1", "p2"],
            metric_ids=["m1"],
            suggested_action="Switch to better model",
            expected_improvement="50% error reduction",
            created_at=now,
            applied=True,
            applied_at=now,
            effectiveness_score=0.9,
            metadata={"version": "1.0"},
        )

        data = original.to_dict()
        restored = Recommendation.from_dict(data)

        assert restored.recommendation_type == original.recommendation_type
        assert restored.priority == original.priority
        assert restored.title == original.title
        assert restored.agent_name == original.agent_name
        assert restored.pattern_ids == original.pattern_ids
        assert restored.applied == original.applied
        assert float(restored.effectiveness_score) == original.effectiveness_score


class TestModelEdgeCases:
    """Test edge cases and special scenarios."""

    def test_interaction_with_none_values(self):
        """Test interaction with optional None values."""
        interaction = Interaction(
            session_id="session",
            agent_name="agent",
            input_data={},
            output_data={},
            model_name=None,
            provider=None,
            error_message=None,
        )

        data = interaction.to_dict()
        restored = Interaction.from_dict(data)

        assert restored.model_name is None
        assert restored.provider is None

    def test_interaction_with_empty_collections(self):
        """Test interaction with empty tags and metadata."""
        interaction = Interaction(
            session_id="session",
            agent_name="agent",
            input_data={},
            output_data={},
            tags=[],
            metadata={},
        )

        data = interaction.to_dict()
        restored = Interaction.from_dict(data)

        assert restored.tags == []
        assert restored.metadata == {}

    def test_pattern_with_many_evidence(self):
        """Test pattern with large evidence list."""
        evidence = [f"interaction_{i}" for i in range(100)]
        pattern = Pattern(
            pattern_type="error",
            name="Test",
            description="Test",
            evidence=evidence,
        )

        assert len(pattern.evidence) == 100
        data = pattern.to_dict()
        restored = Pattern.from_dict(data)
        assert len(restored.evidence) == 100

    def test_metric_with_zero_interactions(self):
        """Test metric with zero interactions."""
        metric = Metric(
            total_interactions=0,
            successful_interactions=0,
            failed_interactions=0,
            success_rate=0.0,
        )

        assert metric.total_interactions == 0
        data = metric.to_dict()
        restored = Metric.from_dict(data)
        assert restored.total_interactions == 0

    def test_unique_ids_generated(self):
        """Test that unique IDs are generated for models."""
        i1 = Interaction(session_id="s", agent_name="a", input_data={}, output_data={})
        i2 = Interaction(session_id="s", agent_name="a", input_data={}, output_data={})

        assert i1.interaction_id != i2.interaction_id

        p1 = Pattern(pattern_type="a", name="n", description="d")
        p2 = Pattern(pattern_type="a", name="n", description="d")

        assert p1.pattern_id != p2.pattern_id

        r1 = Recommendation(title="t", recommendation_type="t", priority="h")
        r2 = Recommendation(title="t", recommendation_type="t", priority="h")

        assert r1.recommendation_id != r2.recommendation_id
