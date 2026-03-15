"""SQLite-based storage for learning data."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from socratic_learning.core import Interaction, Metric, Pattern, Recommendation
from socratic_learning.storage.base import BaseLearningStore


class SQLiteLearningStore(BaseLearningStore):
    """SQLite-based storage for learning data."""

    def __init__(self, db_path: str = "learning.db"):
        """Initialize SQLite store."""
        self.db_path = Path(db_path)
        self._init_database()

    def _init_database(self) -> None:
        """Create tables with indexes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Interactions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                interaction_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                model_name TEXT,
                provider TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                duration_ms REAL DEFAULT 0.0,
                success INTEGER DEFAULT 1,
                error_message TEXT,
                user_rating INTEGER,
                user_feedback TEXT,
                feedback_timestamp TEXT,
                tags TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """
        )

        # Indexes for fast queries
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_interaction_session " "ON interactions(session_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_interaction_agent " "ON interactions(agent_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_interaction_timestamp " "ON interactions(timestamp)"
        )

        # Patterns table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                first_detected TEXT NOT NULL,
                last_detected TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                agent_names TEXT NOT NULL,
                session_ids TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                evidence TEXT NOT NULL,
                tags TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """
        )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pattern_type " "ON patterns(pattern_type)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pattern_confidence " "ON patterns(confidence)"
        )

        # Metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                metric_id TEXT PRIMARY KEY,
                agent_name TEXT,
                session_id TEXT,
                time_period_start TEXT NOT NULL,
                time_period_end TEXT NOT NULL,
                total_interactions INTEGER DEFAULT 0,
                successful_interactions INTEGER DEFAULT 0,
                failed_interactions INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                avg_duration_ms REAL DEFAULT 0.0,
                max_duration_ms REAL DEFAULT 0.0,
                min_duration_ms REAL DEFAULT 0.0,
                total_input_tokens INTEGER DEFAULT 0,
                total_output_tokens INTEGER DEFAULT 0,
                total_cost_usd REAL DEFAULT 0.0,
                avg_rating REAL,
                total_feedback_count INTEGER DEFAULT 0,
                positive_feedback_count INTEGER DEFAULT 0,
                metadata TEXT NOT NULL
            )
        """
        )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_agent " "ON metrics(agent_name)")

        # Recommendations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id TEXT PRIMARY KEY,
                recommendation_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                rationale TEXT,
                agent_name TEXT,
                pattern_ids TEXT NOT NULL,
                metric_ids TEXT NOT NULL,
                suggested_action TEXT,
                expected_improvement TEXT,
                created_at TEXT NOT NULL,
                applied INTEGER DEFAULT 0,
                applied_at TEXT,
                effectiveness_score REAL,
                metadata TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recommendation_priority " "ON recommendations(priority)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recommendation_applied " "ON recommendations(applied)"
        )

        conn.commit()
        conn.close()

    def create_interaction(self, interaction: Interaction) -> Interaction:
        """Create and store an interaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO interactions VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                interaction.interaction_id,
                interaction.session_id,
                interaction.agent_name,
                interaction.timestamp.isoformat(),
                json.dumps(interaction.input_data),
                json.dumps(interaction.output_data),
                interaction.model_name,
                interaction.provider,
                interaction.input_tokens,
                interaction.output_tokens,
                interaction.cost_usd,
                interaction.duration_ms,
                1 if interaction.success else 0,
                interaction.error_message,
                interaction.user_rating,
                interaction.user_feedback,
                (
                    interaction.feedback_timestamp.isoformat()
                    if interaction.feedback_timestamp
                    else None
                ),
                json.dumps(interaction.tags),
                json.dumps(interaction.metadata),
            ),
        )

        conn.commit()
        conn.close()
        return interaction

    def get_interaction(self, interaction_id: str) -> Optional[Interaction]:
        """Retrieve an interaction by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM interactions WHERE interaction_id = ?", (interaction_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_interaction(row)

    def list_interactions(
        self,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Interaction]:
        """List interactions with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM interactions WHERE 1=1"
        params: List[Any] = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_interaction(row) for row in rows]

    def update_interaction_feedback(
        self,
        interaction_id: str,
        rating: int,
        feedback: str,
    ) -> Optional[Interaction]:
        """Add user feedback to an interaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE interactions
            SET user_rating = ?, user_feedback = ?, feedback_timestamp = ?
            WHERE interaction_id = ?
        """,
            (rating, feedback, datetime.utcnow().isoformat(), interaction_id),
        )

        conn.commit()
        conn.close()

        return self.get_interaction(interaction_id)

    def create_pattern(self, pattern: Pattern) -> Pattern:
        """Create and store a pattern."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO patterns VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                pattern.pattern_id,
                pattern.pattern_type,
                pattern.name,
                pattern.description,
                pattern.first_detected.isoformat(),
                pattern.last_detected.isoformat(),
                pattern.occurrence_count,
                json.dumps(pattern.agent_names),
                json.dumps(pattern.session_ids),
                pattern.confidence,
                json.dumps(pattern.evidence),
                json.dumps(pattern.tags),
                json.dumps(pattern.metadata),
            ),
        )

        conn.commit()
        conn.close()
        return pattern

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Retrieve a pattern by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM patterns WHERE pattern_id = ?", (pattern_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_pattern(row)

    def list_patterns(
        self,
        pattern_type: Optional[str] = None,
        agent_name: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> List[Pattern]:
        """List patterns with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM patterns WHERE confidence >= ?"
        params: List[Any] = [min_confidence]

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)

        if agent_name:
            query += " AND agent_names LIKE ?"
            params.append(f'%"{agent_name}"%')

        query += " ORDER BY confidence DESC, last_detected DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_pattern(row) for row in rows]

    def update_pattern(self, pattern: Pattern) -> Pattern:
        """Update an existing pattern."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE patterns
            SET pattern_type = ?, name = ?, description = ?,
                first_detected = ?, last_detected = ?,
                occurrence_count = ?, agent_names = ?,
                session_ids = ?, confidence = ?,
                evidence = ?, tags = ?, metadata = ?
            WHERE pattern_id = ?
        """,
            (
                pattern.pattern_type,
                pattern.name,
                pattern.description,
                pattern.first_detected.isoformat(),
                pattern.last_detected.isoformat(),
                pattern.occurrence_count,
                json.dumps(pattern.agent_names),
                json.dumps(pattern.session_ids),
                pattern.confidence,
                json.dumps(pattern.evidence),
                json.dumps(pattern.tags),
                json.dumps(pattern.metadata),
                pattern.pattern_id,
            ),
        )

        conn.commit()
        conn.close()
        return pattern

    def create_metric(self, metric: Metric) -> Metric:
        """Create and store a metric."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO metrics VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metric.metric_id,
                metric.agent_name,
                metric.session_id,
                metric.time_period_start.isoformat(),
                metric.time_period_end.isoformat(),
                metric.total_interactions,
                metric.successful_interactions,
                metric.failed_interactions,
                metric.success_rate,
                metric.avg_duration_ms,
                metric.max_duration_ms,
                metric.min_duration_ms,
                metric.total_input_tokens,
                metric.total_output_tokens,
                metric.total_cost_usd,
                metric.avg_rating,
                metric.total_feedback_count,
                metric.positive_feedback_count,
                json.dumps(metric.metadata),
            ),
        )

        conn.commit()
        conn.close()
        return metric

    def get_metrics(
        self,
        agent_name: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Metric]:
        """Retrieve metrics with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM metrics WHERE 1=1"
        params: List[Any] = []

        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        if start_time:
            query += " AND time_period_start >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND time_period_end <= ?"
            params.append(end_time.isoformat())

        query += " ORDER BY time_period_end DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_metric(row) for row in rows]

    def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Create and store a recommendation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO recommendations VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                recommendation.recommendation_id,
                recommendation.recommendation_type,
                recommendation.priority,
                recommendation.title,
                recommendation.description,
                recommendation.rationale,
                recommendation.agent_name,
                json.dumps(recommendation.pattern_ids),
                json.dumps(recommendation.metric_ids),
                recommendation.suggested_action,
                recommendation.expected_improvement,
                recommendation.created_at.isoformat(),
                1 if recommendation.applied else 0,
                (recommendation.applied_at.isoformat() if recommendation.applied_at else None),
                recommendation.effectiveness_score,
                json.dumps(recommendation.metadata),
            ),
        )

        conn.commit()
        conn.close()
        return recommendation

    def list_recommendations(
        self,
        agent_name: Optional[str] = None,
        priority: Optional[str] = None,
        applied: Optional[bool] = None,
        limit: int = 100,
    ) -> List[Recommendation]:
        """List recommendations with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM recommendations WHERE 1=1"
        params: List[Any] = []

        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        if applied is not None:
            query += " AND applied = ?"
            params.append(1 if applied else 0)

        query += " ORDER BY priority DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_recommendation(row) for row in rows]

    def update_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Update an existing recommendation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE recommendations
            SET recommendation_type = ?, priority = ?,
                title = ?, description = ?, rationale = ?,
                agent_name = ?, pattern_ids = ?,
                metric_ids = ?, suggested_action = ?,
                expected_improvement = ?, applied = ?,
                applied_at = ?, effectiveness_score = ?, metadata = ?
            WHERE recommendation_id = ?
        """,
            (
                recommendation.recommendation_type,
                recommendation.priority,
                recommendation.title,
                recommendation.description,
                recommendation.rationale,
                recommendation.agent_name,
                json.dumps(recommendation.pattern_ids),
                json.dumps(recommendation.metric_ids),
                recommendation.suggested_action,
                recommendation.expected_improvement,
                1 if recommendation.applied else 0,
                (recommendation.applied_at.isoformat() if recommendation.applied_at else None),
                recommendation.effectiveness_score,
                json.dumps(recommendation.metadata),
                recommendation.recommendation_id,
            ),
        )

        conn.commit()
        conn.close()
        return recommendation

    # Helper methods to convert rows to objects
    @staticmethod
    def _row_to_interaction(row: tuple) -> Interaction:
        """Convert database row to Interaction object."""
        return Interaction(
            interaction_id=row[0],
            session_id=row[1],
            agent_name=row[2],
            timestamp=datetime.fromisoformat(row[3]),
            input_data=json.loads(row[4]),
            output_data=json.loads(row[5]),
            model_name=row[6],
            provider=row[7],
            input_tokens=row[8],
            output_tokens=row[9],
            cost_usd=row[10],
            duration_ms=row[11],
            success=bool(row[12]),
            error_message=row[13],
            user_rating=row[14],
            user_feedback=row[15],
            feedback_timestamp=(datetime.fromisoformat(row[16]) if row[16] else None),
            tags=json.loads(row[17]),
            metadata=json.loads(row[18]),
        )

    @staticmethod
    def _row_to_pattern(row: tuple) -> Pattern:
        """Convert database row to Pattern object."""
        return Pattern(
            pattern_id=row[0],
            pattern_type=row[1],
            name=row[2],
            description=row[3],
            first_detected=datetime.fromisoformat(row[4]),
            last_detected=datetime.fromisoformat(row[5]),
            occurrence_count=row[6],
            agent_names=json.loads(row[7]),
            session_ids=json.loads(row[8]),
            confidence=row[9],
            evidence=json.loads(row[10]),
            tags=json.loads(row[11]),
            metadata=json.loads(row[12]),
        )

    @staticmethod
    def _row_to_metric(row: tuple) -> Metric:
        """Convert database row to Metric object."""
        return Metric(
            metric_id=row[0],
            agent_name=row[1],
            session_id=row[2],
            time_period_start=datetime.fromisoformat(row[3]),
            time_period_end=datetime.fromisoformat(row[4]),
            total_interactions=row[5],
            successful_interactions=row[6],
            failed_interactions=row[7],
            success_rate=row[8],
            avg_duration_ms=row[9],
            max_duration_ms=row[10],
            min_duration_ms=row[11],
            total_input_tokens=row[12],
            total_output_tokens=row[13],
            total_cost_usd=row[14],
            avg_rating=row[15],
            total_feedback_count=row[16],
            positive_feedback_count=row[17],
            metadata=json.loads(row[18]),
        )

    @staticmethod
    def _row_to_recommendation(row: tuple) -> Recommendation:
        """Convert database row to Recommendation object."""
        return Recommendation(
            recommendation_id=row[0],
            recommendation_type=row[1],
            priority=row[2],
            title=row[3],
            description=row[4],
            rationale=row[5],
            agent_name=row[6],
            pattern_ids=json.loads(row[7]),
            metric_ids=json.loads(row[8]),
            suggested_action=row[9],
            expected_improvement=row[10],
            created_at=datetime.fromisoformat(row[11]),
            applied=bool(row[12]),
            applied_at=(datetime.fromisoformat(row[13]) if row[13] else None),
            effectiveness_score=row[14],
            metadata=json.loads(row[15]),
        )
