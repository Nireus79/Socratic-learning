"""Unit tests for SQLite storage backend."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from socratic_learning.core import Interaction, Metric, Pattern, Recommendation
from socratic_learning.storage import SQLiteLearningStore


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test.db")
        yield db_path


@pytest.fixture
def store(temp_db):
    """Create a store with temporary database."""
    return SQLiteLearningStore(temp_db)


class TestInteractionStorage:
    """Test interaction storage operations."""

    def test_create_interaction(self, store):
        """Test creating an interaction."""
        interaction = Interaction(
            session_id="session_123",
            agent_name="TestAgent",
            input_data={"topic": "test"},
            output_data={"response": "test"},
        )

        created = store.create_interaction(interaction)
        assert created.interaction_id == interaction.interaction_id

    def test_get_interaction(self, store):
        """Test retrieving an interaction."""
        interaction = Interaction(
            session_id="session_123",
            agent_name="TestAgent",
            input_data={"topic": "test"},
            output_data={"response": "test"},
        )

        store.create_interaction(interaction)
        retrieved = store.get_interaction(interaction.interaction_id)

        assert retrieved is not None
        assert retrieved.session_id == "session_123"
        assert retrieved.agent_name == "TestAgent"

    def test_get_nonexistent_interaction(self, store):
        """Test retrieving a nonexistent interaction."""
        retrieved = store.get_interaction("nonexistent_id")
        assert retrieved is None

    def test_list_interactions(self, store):
        """Test listing interactions."""
        # Create 5 interactions
        for i in range(5):
            interaction = Interaction(
                session_id="session_123",
                agent_name="TestAgent",
                input_data={"index": i},
                output_data={},
            )
            store.create_interaction(interaction)

        # List all
        interactions = store.list_interactions()
        assert len(interactions) == 5

    def test_list_interactions_by_session(self, store):
        """Test filtering interactions by session."""
        # Create interactions in different sessions
        for session in ["session_1", "session_2"]:
            for i in range(3):
                interaction = Interaction(
                    session_id=session,
                    agent_name="TestAgent",
                    input_data={},
                    output_data={},
                )
                store.create_interaction(interaction)

        # List by session
        session_1_interactions = store.list_interactions(session_id="session_1")
        assert len(session_1_interactions) == 3

        session_2_interactions = store.list_interactions(session_id="session_2")
        assert len(session_2_interactions) == 3

    def test_list_interactions_by_agent(self, store):
        """Test filtering interactions by agent."""
        # Create interactions with different agents
        for agent in ["Agent1", "Agent2"]:
            for i in range(2):
                interaction = Interaction(
                    session_id="session",
                    agent_name=agent,
                    input_data={},
                    output_data={},
                )
                store.create_interaction(interaction)

        # List by agent
        agent_1_interactions = store.list_interactions(agent_name="Agent1")
        assert len(agent_1_interactions) == 2

        agent_2_interactions = store.list_interactions(agent_name="Agent2")
        assert len(agent_2_interactions) == 2

    def test_list_interactions_with_time_range(self, store):
        """Test filtering interactions by time range."""
        now = datetime.utcnow()

        # Create interaction in the past
        interaction_past = Interaction(
            session_id="session",
            agent_name="Agent",
            input_data={},
            output_data={},
            timestamp=now - timedelta(hours=2),
        )
        store.create_interaction(interaction_past)

        # Create interaction now
        interaction_now = Interaction(
            session_id="session",
            agent_name="Agent",
            input_data={},
            output_data={},
            timestamp=now,
        )
        store.create_interaction(interaction_now)

        # List with time range
        one_hour_ago = now - timedelta(hours=1)
        interactions = store.list_interactions(start_time=one_hour_ago, end_time=now)

        assert len(interactions) == 1
        assert interactions[0].interaction_id == interaction_now.interaction_id

    def test_update_interaction_feedback(self, store):
        """Test updating interaction with feedback."""
        interaction = Interaction(
            session_id="session",
            agent_name="Agent",
            input_data={},
            output_data={},
        )
        store.create_interaction(interaction)

        # Add feedback
        updated = store.update_interaction_feedback(
            interaction.interaction_id,
            rating=5,
            feedback="Excellent!",
        )

        assert updated is not None
        assert updated.user_rating == 5
        assert updated.user_feedback == "Excellent!"

    def test_list_interactions_limit_and_offset(self, store):
        """Test pagination with limit and offset."""
        # Create 10 interactions
        for i in range(10):
            interaction = Interaction(
                session_id="session",
                agent_name="Agent",
                input_data={},
                output_data={},
            )
            store.create_interaction(interaction)

        # Get first 5
        first_batch = store.list_interactions(limit=5)
        assert len(first_batch) == 5

        # Get next 5
        second_batch = store.list_interactions(limit=5, offset=5)
        assert len(second_batch) == 5


class TestPatternStorage:
    """Test pattern storage operations."""

    def test_create_pattern(self, store):
        """Test creating a pattern."""
        pattern = Pattern(
            pattern_type="error",
            name="Test Pattern",
            description="Test description",
        )

        created = store.create_pattern(pattern)
        assert created.pattern_id == pattern.pattern_id

    def test_get_pattern(self, store):
        """Test retrieving a pattern."""
        pattern = Pattern(
            pattern_type="error",
            name="Test Pattern",
            description="Test",
        )

        store.create_pattern(pattern)
        retrieved = store.get_pattern(pattern.pattern_id)

        assert retrieved is not None
        assert retrieved.name == "Test Pattern"

    def test_list_patterns(self, store):
        """Test listing patterns."""
        # Create patterns with different confidence
        for confidence in [0.5, 0.7, 0.9]:
            pattern = Pattern(
                pattern_type="error",
                name=f"Pattern_{confidence}",
                description="Test",
                confidence=confidence,
            )
            store.create_pattern(pattern)

        # List all
        patterns = store.list_patterns()
        assert len(patterns) == 3

    def test_list_patterns_by_type(self, store):
        """Test filtering patterns by type."""
        # Create patterns of different types
        for pattern_type in ["error", "success", "topic"]:
            pattern = Pattern(
                pattern_type=pattern_type,
                name=f"Pattern_{pattern_type}",
                description="Test",
            )
            store.create_pattern(pattern)

        # List by type
        error_patterns = store.list_patterns(pattern_type="error")
        assert len(error_patterns) == 1
        assert error_patterns[0].pattern_type == "error"

    def test_list_patterns_by_min_confidence(self, store):
        """Test filtering patterns by minimum confidence."""
        # Create patterns with different confidences
        for confidence in [0.3, 0.6, 0.9]:
            pattern = Pattern(
                pattern_type="error",
                name=f"Pattern_{confidence}",
                description="Test",
                confidence=confidence,
            )
            store.create_pattern(pattern)

        # List patterns with min confidence
        high_confidence = store.list_patterns(min_confidence=0.7)
        assert len(high_confidence) == 1
        assert high_confidence[0].confidence == 0.9

    def test_update_pattern(self, store):
        """Test updating a pattern."""
        pattern = Pattern(
            pattern_type="error",
            name="Original",
            description="Test",
            occurrence_count=1,
            confidence=0.5,
        )

        store.create_pattern(pattern)

        # Update pattern
        pattern.occurrence_count = 10
        pattern.confidence = 0.95
        pattern.name = "Updated"

        updated = store.update_pattern(pattern)
        assert updated.occurrence_count == 10
        assert updated.confidence == 0.95


class TestMetricStorage:
    """Test metric storage operations."""

    def test_create_metric(self, store):
        """Test creating a metric."""
        metric = Metric(
            agent_name="Agent",
            total_interactions=10,
            success_rate=80.0,
        )

        created = store.create_metric(metric)
        assert created.metric_id == metric.metric_id

    def test_get_metrics(self, store):
        """Test retrieving metrics."""
        # Create metrics for different agents
        for agent in ["Agent1", "Agent2"]:
            metric = Metric(
                agent_name=agent,
                total_interactions=10,
                success_rate=80.0,
            )
            store.create_metric(metric)

        # Get all metrics
        metrics = store.get_metrics()
        assert len(metrics) == 2

    def test_get_metrics_by_agent(self, store):
        """Test filtering metrics by agent."""
        for agent in ["Agent1", "Agent2"]:
            metric = Metric(
                agent_name=agent,
                total_interactions=10,
                success_rate=80.0,
            )
            store.create_metric(metric)

        # Get by agent
        agent1_metrics = store.get_metrics(agent_name="Agent1")
        assert len(agent1_metrics) == 1
        assert agent1_metrics[0].agent_name == "Agent1"

    def test_get_metrics_by_session(self, store):
        """Test filtering metrics by session."""
        for session in ["session_1", "session_2"]:
            metric = Metric(
                session_id=session,
                total_interactions=5,
                success_rate=90.0,
            )
            store.create_metric(metric)

        # Get by session
        session1_metrics = store.get_metrics(session_id="session_1")
        assert len(session1_metrics) == 1
        assert session1_metrics[0].session_id == "session_1"


class TestRecommendationStorage:
    """Test recommendation storage operations."""

    def test_create_recommendation(self, store):
        """Test creating a recommendation."""
        rec = Recommendation(
            recommendation_type="prompt_improvement",
            priority="high",
            title="Test",
            description="Test",
        )

        created = store.create_recommendation(rec)
        assert created.recommendation_id == rec.recommendation_id

    def test_list_recommendations(self, store):
        """Test listing recommendations."""
        # Create recommendations with different priorities
        for priority in ["high", "medium", "low"]:
            rec = Recommendation(
                recommendation_type="test",
                priority=priority,
                title=f"Rec_{priority}",
                description="Test",
            )
            store.create_recommendation(rec)

        # List all
        recommendations = store.list_recommendations()
        assert len(recommendations) == 3

    def test_list_recommendations_by_priority(self, store):
        """Test filtering recommendations by priority."""
        for priority in ["high", "medium", "low"]:
            rec = Recommendation(
                recommendation_type="test",
                priority=priority,
                title=f"Rec_{priority}",
                description="Test",
            )
            store.create_recommendation(rec)

        # Get by priority
        high_priority = store.list_recommendations(priority="high")
        assert len(high_priority) == 1
        assert high_priority[0].priority == "high"

    def test_list_recommendations_by_applied_status(self, store):
        """Test filtering recommendations by applied status."""
        # Create applied and unapplied recommendations
        applied = Recommendation(
            recommendation_type="test",
            priority="high",
            title="Applied",
            description="Test",
            applied=True,
        )
        store.create_recommendation(applied)

        unapplied = Recommendation(
            recommendation_type="test",
            priority="high",
            title="Unapplied",
            description="Test",
            applied=False,
        )
        store.create_recommendation(unapplied)

        # Get applied only
        applied_recs = store.list_recommendations(applied=True)
        assert len(applied_recs) == 1
        assert applied_recs[0].applied is True

    def test_update_recommendation(self, store):
        """Test updating a recommendation."""
        rec = Recommendation(
            recommendation_type="test",
            priority="high",
            title="Original",
            description="Test",
            applied=False,
        )

        store.create_recommendation(rec)

        # Mark as applied
        rec.applied = True
        rec.applied_at = datetime.utcnow()
        rec.effectiveness_score = 0.9

        updated = store.update_recommendation(rec)
        assert updated.applied is True
        assert updated.effectiveness_score == 0.9


class TestStorageIntegration:
    """Test integration across different entity types."""

    def test_full_workflow(self, store):
        """Test a complete workflow with all entity types."""
        # 1. Create interactions
        interaction = Interaction(
            session_id="session_1",
            agent_name="TestAgent",
            input_data={"topic": "recursion"},
            output_data={"explanation": "..."},
            user_rating=4,
            user_feedback="Good",
        )
        store.create_interaction(interaction)

        # 2. Create pattern from interactions
        pattern = Pattern(
            pattern_type="success",
            name="Recursion Success",
            description="Users rate recursion explanations highly",
            confidence=0.85,
            evidence=[interaction.interaction_id],
            agent_names=["TestAgent"],
        )
        store.create_pattern(pattern)

        # 3. Create metrics
        metric = Metric(
            agent_name="TestAgent",
            session_id="session_1",
            total_interactions=1,
            successful_interactions=1,
            success_rate=100.0,
            avg_rating=4.0,
            total_feedback_count=1,
            positive_feedback_count=1,
        )
        store.create_metric(metric)

        # 4. Create recommendation based on pattern
        recommendation = Recommendation(
            recommendation_type="prompt_improvement",
            priority="high",
            title="Leverage Success Pattern",
            description="Use recursion examples more",
            pattern_ids=[pattern.pattern_id],
            metric_ids=[metric.metric_id],
            agent_name="TestAgent",
        )
        store.create_recommendation(recommendation)

        # Verify all entities are retrievable
        assert store.get_interaction(interaction.interaction_id) is not None
        assert store.get_pattern(pattern.pattern_id) is not None
        assert len(store.get_metrics(agent_name="TestAgent")) > 0
        assert len(store.list_recommendations(agent_name="TestAgent")) > 0

    def test_multiple_sessions_isolation(self, store):
        """Test that different sessions don't interfere."""
        # Create interactions in two sessions
        for session in ["session_1", "session_2"]:
            for i in range(3):
                interaction = Interaction(
                    session_id=session,
                    agent_name="Agent",
                    input_data={"index": i},
                    output_data={},
                )
                store.create_interaction(interaction)

        # Verify isolation
        s1_interactions = store.list_interactions(session_id="session_1")
        s2_interactions = store.list_interactions(session_id="session_2")

        assert len(s1_interactions) == 3
        assert len(s2_interactions) == 3
        assert all(i.session_id == "session_1" for i in s1_interactions)
        assert all(i.session_id == "session_2" for i in s2_interactions)
