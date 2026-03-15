"""Unit tests for recommendations components."""

import tempfile
from pathlib import Path

import pytest

from socratic_learning.recommendations import (
    RecommendationEngine,
    FinetuningExporter,
)
from socratic_learning.storage import SQLiteLearningStore
from socratic_learning.tracking import InteractionLogger


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


@pytest.fixture
def recommendation_engine(store):
    """Create a recommendation engine."""
    return RecommendationEngine(store)


@pytest.fixture
def finetuning_exporter(store):
    """Create a finetuning exporter."""
    return FinetuningExporter(store)


class TestRecommendationEngine:
    """Test RecommendationEngine."""

    def test_generate_recommendations_from_errors(self, logger, recommendation_engine):
        """Test generating recommendations from error patterns."""
        session = logger.create_session()

        # Create high error rate
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 5,  # 75% error rate
            )

        recommendations = recommendation_engine.generate_recommendations(agent_name="Agent")
        assert len(recommendations) > 0

    def test_generate_recommendations_from_feedback(self, logger, recommendation_engine):
        """Test generating recommendations from feedback patterns."""
        session = logger.create_session()

        # Create interactions with very low ratings
        for i in range(10):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
            )
            logger.add_feedback(interaction.interaction_id, rating=2, feedback="Poor")

        recommendations = recommendation_engine.generate_recommendations(agent_name="Agent")
        assert len(recommendations) > 0

    def test_get_high_priority_recommendations(self, logger, recommendation_engine):
        """Test getting high priority recommendations."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 5,
            )

        recommendation_engine.generate_recommendations(agent_name="Agent")
        high_priority = recommendation_engine.get_high_priority_recommendations(agent_name="Agent")
        assert all(r.priority == "high" for r in high_priority)

    def test_mark_recommendation_applied(self, logger, recommendation_engine):
        """Test marking recommendation as applied."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 5,
            )

        recommendations = recommendation_engine.generate_recommendations(agent_name="Agent")
        if recommendations:
            updated = recommendation_engine.mark_recommendation_applied(
                recommendations[0].recommendation_id
            )
            assert updated is not None
            assert updated.applied is True
            assert updated.applied_at is not None

    def test_set_recommendation_effectiveness(self, logger, recommendation_engine):
        """Test setting effectiveness score."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 5,
            )

        recommendations = recommendation_engine.generate_recommendations(agent_name="Agent")
        if recommendations:
            updated = recommendation_engine.set_recommendation_effectiveness(
                recommendations[0].recommendation_id,
                effectiveness_score=0.85,
            )
            assert updated is not None
            assert updated.effectiveness_score == 0.85

    def test_set_effectiveness_invalid_score(self, recommendation_engine):
        """Test that invalid effectiveness scores are rejected."""
        with pytest.raises(ValueError):
            recommendation_engine.set_recommendation_effectiveness(
                "rec_id", effectiveness_score=1.5
            )

        with pytest.raises(ValueError):
            recommendation_engine.set_recommendation_effectiveness(
                "rec_id", effectiveness_score=-0.1
            )

    def test_get_applied_recommendations(self, logger, recommendation_engine):
        """Test getting applied recommendations."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 5,
            )

        recommendations = recommendation_engine.generate_recommendations(agent_name="Agent")

        # Mark some as applied
        if recommendations:
            recommendation_engine.mark_recommendation_applied(recommendations[0].recommendation_id)

        applied = recommendation_engine.get_applied_recommendations(agent_name="Agent")
        assert all(r.applied is True for r in applied)

    def test_get_recommendation_summary(self, logger, recommendation_engine):
        """Test getting recommendation summary."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 5,
            )

        recommendation_engine.generate_recommendations(agent_name="Agent")
        summary = recommendation_engine.get_recommendation_summary(agent_name="Agent")

        assert "total_recommendations" in summary
        assert "by_priority" in summary
        assert "applied_count" in summary


class TestFinetuningExporter:
    """Test FinetuningExporter."""

    def test_export_jsonl(self, logger, finetuning_exporter, tmp_path):
        """Test exporting interactions to JSONL."""
        session = logger.create_session()
        for i in range(5):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={"text": f"input {i}"},
                output_data={"response": f"output {i}"},
                success=True,
            )
            logger.add_feedback(interaction.interaction_id, rating=4, feedback="")

        output_file = tmp_path / "export.jsonl"
        count = finetuning_exporter.export_jsonl(
            str(output_file),
            agent_name="Agent",
            format_type="openai",
        )

        assert count == 5
        assert output_file.exists()

        # Verify file has correct number of lines
        with open(output_file) as f:
            lines = f.readlines()
        assert len(lines) == 5

    def test_export_jsonl_with_rating_filter(self, logger, finetuning_exporter, tmp_path):
        """Test exporting only high-rated interactions."""
        session = logger.create_session()
        for i in range(5):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={"text": f"input {i}"},
                output_data={"response": f"output {i}"},
            )
            rating = 5 if i < 2 else 2
            logger.add_feedback(interaction.interaction_id, rating=rating, feedback="")

        output_file = tmp_path / "export.jsonl"
        count = finetuning_exporter.export_jsonl(
            str(output_file),
            agent_name="Agent",
            min_rating=4,
            format_type="openai",
        )

        assert count == 2

    def test_export_csv(self, logger, finetuning_exporter, tmp_path):
        """Test exporting interactions to CSV."""
        session = logger.create_session()
        for i in range(3):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={"text": f"input {i}"},
                output_data={"response": f"output {i}"},
            )
            logger.add_feedback(interaction.interaction_id, rating=4, feedback="")

        output_file = tmp_path / "export.csv"
        count = finetuning_exporter.export_csv(
            str(output_file),
            agent_name="Agent",
        )

        assert count == 3
        assert output_file.exists()

        # Verify CSV has header + 3 rows
        with open(output_file) as f:
            lines = f.readlines()
        assert len(lines) == 4  # header + 3 data rows

    def test_export_jsonl_by_quality(self, logger, finetuning_exporter, tmp_path):
        """Test exporting interactions grouped by quality."""
        session = logger.create_session()
        ratings = [5, 5, 3, 3, 1, 1]
        for rating in ratings:
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
            )
            logger.add_feedback(interaction.interaction_id, rating=rating, feedback="")

        output_file = tmp_path / "export.jsonl"
        counts = finetuning_exporter.export_jsonl_by_quality(
            str(output_file),
            agent_name="Agent",
        )

        assert counts["high_quality"] == 2
        assert counts["medium_quality"] == 2
        assert counts["low_quality"] == 2

    def test_export_empty_database(self, finetuning_exporter, tmp_path):
        """Test exporting from empty database."""
        output_file = tmp_path / "export.jsonl"
        count = finetuning_exporter.export_jsonl(str(output_file))
        assert count == 0

    def test_get_export_summary(self, logger, finetuning_exporter):
        """Test getting export summary."""
        session = logger.create_session()
        for i in range(5):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 4,  # 4 successful, 1 failed
            )
            if i < 3:  # Only rate first 3
                logger.add_feedback(
                    interaction.interaction_id,
                    rating=4 if i < 2 else 2,
                    feedback="",
                )

        summary = finetuning_exporter.get_export_summary(agent_name="Agent")
        assert summary["total_interactions"] == 5
        assert summary["successful_interactions"] == 4
        assert summary["rated_interactions"] == 3
        assert summary["rating_coverage"] == 60.0

    def test_export_format_anthropic(self, logger, finetuning_exporter, tmp_path):
        """Test exporting in Anthropic format."""
        session = logger.create_session()
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="Agent",
            input_data={"text": "hello"},
            output_data={"response": "hi"},
        )
        logger.add_feedback(interaction.interaction_id, rating=4, feedback="")

        output_file = tmp_path / "export.jsonl"
        finetuning_exporter.export_jsonl(
            str(output_file),
            agent_name="Agent",
            format_type="anthropic",
        )

        with open(output_file) as f:
            import json

            record = json.loads(f.readline())
        assert "prompt" in record
        assert "completion" in record
