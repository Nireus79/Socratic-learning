"""Unit tests for tracking components."""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from socratic_learning.storage import SQLiteLearningStore
from socratic_learning.tracking import InteractionLogger, Session


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


@pytest.fixture
def logger(store):
    """Create an interaction logger."""
    return InteractionLogger(store)


class TestSession:
    """Test Session model."""

    def test_session_creation(self):
        """Test basic session creation."""
        session = Session(user_id="user123")

        assert session.user_id == "user123"
        assert session.is_active is True
        assert session.ended_at is None

    def test_session_with_context(self):
        """Test session with context data."""
        context = {"environment": "production", "version": "1.0"}
        session = Session(user_id="user123", context=context)

        assert session.context == context

    def test_session_end(self):
        """Test ending a session."""
        session = Session()
        session.end()

        assert session.is_active is False
        assert session.ended_at is not None

    def test_session_duration(self):
        """Test session duration calculation."""
        now = datetime.now(timezone.utc)
        session = Session(created_at=now)
        session.created_at = now - timedelta(hours=1)
        session.ended_at = now

        duration = session.get_duration_seconds()
        assert 3599 < duration < 3601  # About 3600 seconds (1 hour)

    def test_session_serialization(self):
        """Test session to_dict and from_dict."""
        original = Session(
            user_id="user123",
            is_active=False,
            context={"env": "test"},
            metadata={"tag": "value"},
        )
        original.end()

        data = original.to_dict()
        restored = Session.from_dict(data)

        assert restored.user_id == original.user_id
        assert restored.is_active == original.is_active
        assert restored.context == original.context


class TestInteractionLogger:
    """Test InteractionLogger."""

    def test_create_session(self, logger):
        """Test creating a session."""
        session = logger.create_session(user_id="user123")

        assert session.user_id == "user123"
        assert session.session_id in logger.sessions

    def test_get_session(self, logger):
        """Test retrieving a session."""
        created = logger.create_session(user_id="user123")
        retrieved = logger.get_session(created.session_id)

        assert retrieved is not None
        assert retrieved.user_id == "user123"

    def test_end_session(self, logger):
        """Test ending a session."""
        session = logger.create_session(user_id="user123")
        ended = logger.end_session(session.session_id)

        assert ended is not None
        assert ended.is_active is False

    def test_log_interaction(self, logger):
        """Test logging an interaction."""
        session = logger.create_session()
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="TestAgent",
            input_data={"topic": "test"},
            output_data={"response": "test"},
            model_name="claude-opus-4",
            provider="anthropic",
            input_tokens=100,
            output_tokens=200,
            duration_ms=1000.0,
        )

        assert interaction.session_id == session.session_id
        assert interaction.agent_name == "TestAgent"
        assert interaction.model_name == "claude-opus-4"

    def test_log_failed_interaction(self, logger):
        """Test logging a failed interaction."""
        session = logger.create_session()
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="TestAgent",
            input_data={},
            output_data={},
            success=False,
            error_message="Test error",
        )

        assert interaction.success is False
        assert interaction.error_message == "Test error"

    def test_add_feedback(self, logger):
        """Test adding feedback to an interaction."""
        session = logger.create_session()
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="TestAgent",
            input_data={},
            output_data={},
        )

        updated = logger.add_feedback(
            interaction.interaction_id,
            rating=5,
            feedback="Excellent!",
        )

        assert updated is not None
        assert updated.user_rating == 5
        assert updated.user_feedback == "Excellent!"

    def test_get_session_interactions(self, logger):
        """Test retrieving all interactions in a session."""
        session = logger.create_session()

        # Log 5 interactions
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={"index": i},
                output_data={},
            )

        interactions = logger.get_session_interactions(session.session_id)
        assert len(interactions) == 5

    def test_multiple_agents_in_session(self, logger):
        """Test session with multiple agents."""
        session = logger.create_session()

        for agent in ["Agent1", "Agent2"]:
            logger.log_interaction(
                session_id=session.session_id,
                agent_name=agent,
                input_data={},
                output_data={},
            )

        interactions = logger.get_session_interactions(session.session_id)
        assert len(interactions) == 2
        agent_names = {i.agent_name for i in interactions}
        assert agent_names == {"Agent1", "Agent2"}

    def test_log_interaction_with_tags(self, logger):
        """Test logging with tags."""
        session = logger.create_session()
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="Agent",
            input_data={},
            output_data={},
            tags=["important", "test"],
        )

        assert interaction.tags == ["important", "test"]

    def test_log_interaction_with_metadata(self, logger):
        """Test logging with metadata."""
        session = logger.create_session()
        metadata = {"version": "1.0", "type": "test"}
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="Agent",
            input_data={},
            output_data={},
            metadata=metadata,
        )

        assert interaction.metadata == metadata

    def test_session_context_persistence(self, logger):
        """Test that session context is accessible."""
        context = {"user_level": "expert", "language": "en"}
        session = logger.create_session(context=context)
        retrieved = logger.get_session(session.session_id)

        assert retrieved.context == context

    def test_multiple_sessions(self, logger):
        """Test managing multiple sessions."""
        sessions = []
        for i in range(3):
            session = logger.create_session(user_id=f"user{i}")
            sessions.append(session)

            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
            )

        # Verify all sessions exist and have their own interactions
        for i, session in enumerate(sessions):
            retrieved = logger.get_session(session.session_id)
            assert retrieved is not None
            interactions = logger.get_session_interactions(session.session_id)
            assert len(interactions) == 1

    def test_interaction_cost_tracking(self, logger):
        """Test cost tracking in interactions."""
        session = logger.create_session()
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="Agent",
            input_data={},
            output_data={},
            input_tokens=1000,
            output_tokens=2000,
            cost_usd=0.15,
        )

        assert interaction.input_tokens == 1000
        assert interaction.output_tokens == 2000
        assert interaction.cost_usd == 0.15
