"""Unit tests for analytics components."""

import tempfile
from pathlib import Path

import pytest

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
def metrics_collector(store):
    """Create a metrics collector."""
    from socratic_learning.analytics.metrics_collector import MetricsCollector
    return MetricsCollector(store)


@pytest.fixture
def pattern_detector(store):
    """Create a pattern detector."""
    from socratic_learning.analytics.pattern_detector import PatternDetector
    return PatternDetector(store)


class TestMetricsCollector:
    """Test MetricsCollector."""

    def test_empty_metrics(self, metrics_collector):
        """Test metrics with no interactions."""
        metric = metrics_collector.calculate_metrics()

        assert metric.total_interactions == 0
        assert metric.success_rate == 0.0

    def test_calculate_basic_metrics(self, logger, metrics_collector):
        """Test calculating basic metrics."""
        session = logger.create_session()
        for i in range(10):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 8,  # 8 successful, 2 failed
            )

        metric = metrics_collector.calculate_metrics()

        assert metric.total_interactions == 10
        assert metric.successful_interactions == 8
        assert metric.failed_interactions == 2
        assert metric.success_rate == 80.0

    def test_calculate_performance_metrics(self, logger, metrics_collector):
        """Test performance metric calculation."""
        session = logger.create_session()
        durations = [100.0, 200.0, 300.0, 400.0, 500.0]

        for duration in durations:
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                duration_ms=duration,
            )

        metric = metrics_collector.calculate_metrics()

        assert metric.avg_duration_ms == 300.0
        assert metric.min_duration_ms == 100.0
        assert metric.max_duration_ms == 500.0

    def test_calculate_cost_metrics(self, logger, metrics_collector):
        """Test cost metric calculation."""
        session = logger.create_session()
        for i in range(3):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                input_tokens=1000,
                output_tokens=2000,
                cost_usd=0.15,
            )

        metric = metrics_collector.calculate_metrics()

        assert metric.total_input_tokens == 3000
        assert metric.total_output_tokens == 6000
        assert abs(metric.total_cost_usd - 0.45) < 0.01  # Allow float precision

    def test_calculate_feedback_metrics(self, logger, metrics_collector):
        """Test user feedback metric calculation."""
        session = logger.create_session()
        for rating in [5, 4, 4, 3]:
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
            )
            logger.add_feedback(interaction.interaction_id, rating=rating, feedback="OK")

        metric = metrics_collector.calculate_metrics()

        assert metric.total_feedback_count == 4
        assert metric.positive_feedback_count == 3  # Ratings >= 4
        assert metric.avg_rating == 4.0

    def test_metrics_by_agent(self, logger, metrics_collector):
        """Test calculating metrics for specific agent."""
        session = logger.create_session()
        for agent in ["Agent1", "Agent2"]:
            for i in range(5):
                logger.log_interaction(
                    session_id=session.session_id,
                    agent_name=agent,
                    input_data={},
                    output_data={},
                    success=i < 4,
                )

        agent1_metric = metrics_collector.calculate_metrics(agent_name="Agent1")
        assert agent1_metric.total_interactions == 5
        assert agent1_metric.success_rate == 80.0

    def test_metrics_by_session(self, logger, metrics_collector):
        """Test calculating metrics for specific session."""
        sessions = [logger.create_session() for _ in range(2)]

        for session in sessions:
            for i in range(5):
                logger.log_interaction(
                    session_id=session.session_id,
                    agent_name="Agent",
                    input_data={},
                    output_data={},
                )

        metric1 = metrics_collector.calculate_metrics(session_id=sessions[0].session_id)
        assert metric1.total_interactions == 5

    def test_metrics_for_period(self, logger, metrics_collector):
        """Test calculating metrics for a time period."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
            )

        metric = metrics_collector.get_metrics_for_period(days=7)
        assert metric.total_interactions == 5

    def test_compare_metrics(self, logger, metrics_collector):
        """Test comparing two metrics."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                duration_ms=1000.0,
            )

        metric1 = metrics_collector.calculate_metrics()

        # Create more interactions with better performance
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                duration_ms=500.0,
            )

        metric2 = metrics_collector.calculate_metrics()
        comparison = metrics_collector.compare_metrics(metric1, metric2)

        assert "duration_improvement" in comparison
        assert comparison["duration_improvement"] > 0  # Second metric is faster


class TestPatternDetector:
    """Test PatternDetector."""

    def test_no_patterns_without_interactions(self, pattern_detector):
        """Test that no patterns detected without interactions."""
        patterns = pattern_detector.detect_all_patterns()
        assert len(patterns) == 0

    def test_detect_high_error_rate(self, logger, pattern_detector):
        """Test detecting high error rate pattern."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 5,  # 5 success, 15 failed = 75% error rate
            )

        patterns = pattern_detector.detect_error_patterns(agent_name="Agent")
        assert len(patterns) > 0
        assert patterns[0].pattern_type == "error"
        assert patterns[0].confidence > 0.7

    def test_detect_high_success_rate(self, logger, pattern_detector):
        """Test detecting high success rate pattern."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 18,  # 18 success, 2 failed = 90% success rate
            )

        patterns = pattern_detector.detect_success_patterns(agent_name="Agent")
        assert len(patterns) > 0
        assert patterns[0].pattern_type == "success"

    def test_detect_performance_pattern(self, logger, pattern_detector):
        """Test detecting performance pattern."""
        session = logger.create_session()
        for i in range(20):
            # Create pattern:
            # 6 interactions with 10000ms (> 2x average)
            # 14 interactions with 1000ms
            # Average = (6*10000 + 14*1000) / 20 = 74000/20 = 3700
            # 2x average = 7400
            # Slow > 7400 = 6 out of 20 = 30% > 20% threshold
            duration = 10000.0 if i < 6 else 1000.0
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                duration_ms=duration,
            )

        patterns = pattern_detector.detect_performance_patterns(agent_name="Agent")
        assert len(patterns) > 0
        assert patterns[0].pattern_type == "performance"

    def test_detect_high_satisfaction(self, logger, pattern_detector):
        """Test detecting high user satisfaction pattern."""
        session = logger.create_session()
        for i in range(10):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
            )
            logger.add_feedback(
                interaction.interaction_id,
                rating=5,
                feedback="Excellent!",
            )

        patterns = pattern_detector.detect_feedback_patterns(agent_name="Agent")
        assert len(patterns) > 0
        assert patterns[0].pattern_type == "feedback"
        assert "Satisfaction" in patterns[0].name

    def test_detect_low_satisfaction(self, logger, pattern_detector):
        """Test detecting low user satisfaction pattern."""
        session = logger.create_session()
        for i in range(10):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
            )
            logger.add_feedback(
                interaction.interaction_id,
                rating=2,
                feedback="Poor",
            )

        patterns = pattern_detector.detect_feedback_patterns(agent_name="Agent")
        assert len(patterns) > 0
        low_satisfaction_found = any("Low" in p.name for p in patterns)
        assert low_satisfaction_found

    def test_detect_all_patterns(self, logger, pattern_detector):
        """Test detecting all types of patterns."""
        session = logger.create_session()
        for i in range(20):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 18,  # High success rate
                duration_ms=1000.0 if i < 10 else 5000.0,  # Some slow
            )
            if i > 10:
                logger.add_feedback(interaction.interaction_id, rating=4, feedback="Good")

        patterns = pattern_detector.detect_all_patterns(agent_name="Agent")
        assert len(patterns) > 0
        pattern_types = {p.pattern_type for p in patterns}
        assert "success" in pattern_types or "feedback" in pattern_types

    def test_pattern_confidence_scoring(self, logger, pattern_detector):
        """Test that pattern confidence is properly scored."""
        session = logger.create_session()
        for i in range(20):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=True,  # Perfect success rate
            )

        patterns = pattern_detector.detect_success_patterns(agent_name="Agent")
        assert len(patterns) > 0
        assert patterns[0].confidence > 0.9

    def test_pattern_evidence_tracking(self, logger, pattern_detector):
        """Test that patterns track evidence (interaction IDs)."""
        session = logger.create_session()
        interaction_ids = []
        for i in range(15):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent",
                input_data={},
                output_data={},
                success=i < 12,  # 12 success, 3 failed
            )
            if i < 12:
                interaction_ids.append(interaction.interaction_id)

        patterns = pattern_detector.detect_success_patterns(agent_name="Agent")
        if patterns:
            assert len(patterns[0].evidence) > 0
            assert len(patterns[0].evidence) == patterns[0].occurrence_count
