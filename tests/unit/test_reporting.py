"""Unit tests for reporting and analytics components."""

import json
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
def aggregator(store):
    """Create a data aggregator."""
    # DataAggregator not implemented yet - placeholder
    return None


@pytest.fixture
def reporter(store):
    """Create a report generator."""
    # ReportGenerator not implemented yet - placeholder
    return None


@pytest.mark.skip(reason="DataAggregator not implemented")
class TestDataAggregator:
    """Test DataAggregator."""

    def test_agent_summary_empty(self, aggregator):
        """Test agent summary with no interactions."""
        summary = aggregator.get_agent_summary("NonExistent")
        assert summary["agent_name"] == "NonExistent"
        assert summary["total_interactions"] == 0

    def test_agent_summary(self, logger, aggregator):
        """Test agent summary with interactions."""
        session = logger.create_session()
        for i in range(10):
            interaction = logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
                success=i < 8,
                duration_ms=100.0 * (i + 1),
                cost_usd=0.1 * (i + 1),
            )
            if i < 5:
                logger.add_feedback(interaction.interaction_id, rating=4, feedback="Good")

        summary = aggregator.get_agent_summary("Agent1")
        assert summary["total_interactions"] == 10
        assert summary["successful_interactions"] == 8
        assert summary["failed_interactions"] == 2
        assert summary["success_rate"] == 80.0
        assert summary["total_feedback_count"] == 5

    def test_session_summary_empty(self, aggregator):
        """Test session summary with no interactions."""
        summary = aggregator.get_session_summary("NonExistent")
        assert summary["session_id"] == "NonExistent"
        assert summary["total_interactions"] == 0

    def test_session_summary(self, logger, aggregator):
        """Test session summary with interactions."""
        session = logger.create_session()
        for agent in ["Agent1", "Agent2"]:
            for i in range(3):
                logger.log_interaction(
                    session_id=session.session_id,
                    agent_name=agent,
                    input_data={},
                    output_data={},
                )

        summary = aggregator.get_session_summary(session.session_id)
        assert summary["total_interactions"] == 6
        assert summary["unique_agents"] == 2

    def test_global_summary(self, logger, aggregator):
        """Test global summary."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
            )

        summary = aggregator.get_global_summary()
        assert summary["total_interactions"] == 5
        assert summary["total_agents"] >= 1

    def test_compare_time_periods(self, logger, aggregator):
        """Test time period comparison."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
            )

        comparison = aggregator.compare_time_periods(agent_name="Agent1", days1=7, days2=7)
        assert "period1" in comparison
        assert "period2" in comparison
        assert "changes" in comparison

    def test_agent_list_with_metrics(self, logger, aggregator):
        """Test agent list with metrics."""
        session = logger.create_session()
        for agent in ["Agent1", "Agent2", "Agent3"]:
            for i in range(3):
                logger.log_interaction(
                    session_id=session.session_id,
                    agent_name=agent,
                    input_data={},
                    output_data={},
                    success=i < 2,
                )

        agent_list = aggregator.get_agent_list_with_metrics()
        assert len(agent_list) >= 3
        assert all("agent_name" in a for a in agent_list)
        assert all("success_rate" in a for a in agent_list)

    def test_error_summary_no_errors(self, logger, aggregator):
        """Test error summary with no errors."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
                success=True,
            )

        summary = aggregator.get_error_summary("Agent1")
        assert summary["total_errors"] == 0
        assert summary["error_rate"] == 0.0

    def test_error_summary_with_errors(self, logger, aggregator):
        """Test error summary with errors."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
                success=i < 3,
                error_message="Test error" if i >= 3 else None,
            )

        summary = aggregator.get_error_summary("Agent1")
        assert summary["total_errors"] == 2
        assert summary["error_rate"] == 40.0

    def test_cost_summary(self, logger, aggregator):
        """Test cost summary."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
                cost_usd=0.1 * (i + 1),
                input_tokens=100,
                output_tokens=200,
            )

        summary = aggregator.get_cost_summary("Agent1")
        assert summary["interaction_count"] == 5
        assert summary["total_cost"] > 0
        assert "most_expensive_interactions" in summary


@pytest.mark.skip(reason="ReportGenerator not implemented")
class TestReportGenerator:
    """Test ReportGenerator."""

    def test_executive_summary(self, logger, reporter):
        """Test executive summary generation."""
        session = logger.create_session()
        for i in range(10):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
                success=i < 8,
            )

        report = reporter.generate_executive_summary()
        assert report["report_type"] == "executive_summary"
        assert "overview" in report
        assert "top_agents" in report
        assert "error_summary" in report

    def test_agent_report(self, logger, reporter):
        """Test agent report generation."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
            )

        report = reporter.generate_agent_report("Agent1")
        assert report["report_type"] == "agent_report"
        assert report["agent_name"] == "Agent1"
        assert "summary" in report
        assert "errors" in report
        assert "costs" in report

    def test_comparison_report(self, logger, reporter):
        """Test comparison report generation."""
        session = logger.create_session()
        for agent in ["Agent1", "Agent2"]:
            for i in range(5):
                logger.log_interaction(
                    session_id=session.session_id,
                    agent_name=agent,
                    input_data={},
                    output_data={},
                    success=i < 4 if agent == "Agent1" else i < 3,
                )

        report = reporter.generate_comparison_report("Agent1", "Agent2")
        assert report["report_type"] == "comparison_report"
        assert "agent1" in report
        assert "agent2" in report
        assert "comparison" in report

    def test_timeline_report(self, logger, reporter):
        """Test timeline report generation."""
        session = logger.create_session()
        for i in range(5):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
            )

        report = reporter.generate_timeline_report(agent_name="Agent1", days=7)
        assert report["report_type"] == "timeline_report"
        assert report["agent_name"] == "Agent1"
        assert "timeline" in report

    def test_quality_report(self, logger, reporter):
        """Test quality report generation."""
        session = logger.create_session()
        for agent in ["Agent1", "Agent2"]:
            for i in range(5):
                interaction = logger.log_interaction(
                    session_id=session.session_id,
                    agent_name=agent,
                    input_data={},
                    output_data={},
                    success=i < 4,
                )
                logger.add_feedback(
                    interaction.interaction_id,
                    rating=4 if agent == "Agent1" else 2,
                    feedback="",
                )

        report = reporter.generate_quality_report()
        assert report["report_type"] == "quality_report"
        assert "agents" in report
        assert "summary" in report

    def test_export_report_to_file(self, reporter, tmp_path):
        """Test exporting report to file."""
        report = {"test": "data", "number": 42}
        output_file = tmp_path / "test_report.json"

        reporter.export_report_to_file(report, str(output_file))

        assert output_file.exists()
        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded["test"] == "data"
        assert loaded["number"] == 42

    def test_dashboard_data(self, logger, reporter):
        """Test dashboard data generation."""
        session = logger.create_session()
        for i in range(10):
            logger.log_interaction(
                session_id=session.session_id,
                agent_name="Agent1",
                input_data={},
                output_data={},
                success=i < 8,
            )

        dashboard = reporter.generate_dashboard_data()
        assert "dashboard_data" in dashboard
        assert "metrics" in dashboard["dashboard_data"]
        assert "charts" in dashboard["dashboard_data"]
        assert "top_performers" in dashboard["dashboard_data"]

    def test_dashboard_metrics(self, logger, reporter):
        """Test dashboard metrics are present."""
        session = logger.create_session()
        interaction = logger.log_interaction(
            session_id=session.session_id,
            agent_name="Agent1",
            input_data={},
            output_data={},
            cost_usd=0.5,
        )
        logger.add_feedback(interaction.interaction_id, rating=5, feedback="Good")

        dashboard = reporter.generate_dashboard_data()
        metrics = dashboard["dashboard_data"]["metrics"]

        assert metrics["total_interactions"] == 1
        assert metrics["total_agents"] >= 1
        assert metrics["success_rate"] == 100.0
