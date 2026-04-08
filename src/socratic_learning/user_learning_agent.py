"""User Learning agent improvements for socratic-learning."""

import asyncio
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import numpy as np
from socratic_agents.agents import Agent
from socratic_agents.events import EventType

if TYPE_CHECKING:
    from socratic_agents.orchestration import AgentOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class UserLearningSession:
    """Represents a learning session."""

    session_id: str
    user_id: str
    questions_answered: int = 0
    correct_answers: int = 0
    time_spent_minutes: float = 0.0
    skills_practiced: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None

    def completion_rate(self) -> float:
        if self.questions_answered == 0:
            return 0.0
        return self.correct_answers / self.questions_answered


@dataclass
class LearningPattern:
    """Detected pattern in user learning behavior."""

    pattern_type: str
    confidence: float
    description: str
    affected_skills: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class PersonalizedLearningPath:
    """Personalized learning path for a user."""

    user_id: str
    current_level: float
    target_level: float
    estimated_completion_days: int
    phases: List[Dict[str, Any]] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class UserLearningAgent(Agent):
    """Enhanced user learning agent with pattern detection and orchestrator integration."""

    def __init__(self, name: str, orchestrator: "AgentOrchestrator"):
        """
        Initialize the user learning agent.

        Args:
            name: Display name for the agent
            orchestrator: Reference to the AgentOrchestrator for coordination
        """
        super().__init__(name, orchestrator)
        self.sessions: Dict[str, UserLearningSession] = {}
        self.user_histories: Dict[str, List[UserLearningSession]] = defaultdict(list)
        self.detected_patterns: Dict[str, List[LearningPattern]] = defaultdict(list)
        self.learning_paths: Dict[str, PersonalizedLearningPath] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a synchronous learning request.

        Routes to appropriate async method based on action type.

        Args:
            request: Dictionary with 'action' and action-specific parameters

        Returns:
            Dictionary containing the response data
        """
        action = request.get("action", "")

        try:
            if action == "start_session":
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.start_session(request.get("user_id")))
                    return {"status": "success", "session": asdict(result)}
                finally:
                    loop.close()

            elif action == "end_session":
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.end_session(request.get("session_id")))
                    return {"status": "success", "session": asdict(result) if result else None}
                finally:
                    loop.close()

            elif action == "detect_patterns":
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.detect_patterns(request.get("user_id")))
                    return {"status": "success", "patterns": [asdict(p) for p in result]}
                finally:
                    loop.close()

            elif action == "generate_learning_path":
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.generate_learning_path(
                            request.get("user_id"),
                            request.get("current_skills", {}),
                            request.get("target_skills", {}),
                            request.get("learning_velocity", 1.0),
                        )
                    )
                    return {"status": "success", "path": asdict(result)}
                finally:
                    loop.close()

            elif action == "get_user_progress":
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.get_user_progress(request.get("user_id")))
                    return {"status": "success", "progress": result}
                finally:
                    loop.close()

            else:
                return {"status": "error", "message": f"Unknown action: {action}"}

        except Exception as e:
            self.log(f"Error processing action {action}: {str(e)}", level="ERROR")
            self.emit_event(
                EventType.AGENT_ERROR,
                {"action": action, "error": str(e)},
            )
            return {"status": "error", "message": str(e)}

    async def start_session(self, user_id: str) -> UserLearningSession:
        """Start a new learning session."""
        session = UserLearningSession(
            session_id=f"{user_id}_{datetime.now().timestamp()}", user_id=user_id
        )
        self.sessions[session.session_id] = session
        self.emit_event(
            EventType.LEARNING_STARTED,
            {"user_id": user_id, "session_id": session.session_id},
        )
        return session

    async def end_session(self, session_id: str) -> UserLearningSession:
        """End a learning session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.ended_at = datetime.now()
            self.user_histories[session.user_id].append(session)
            self.emit_event(
                EventType.LEARNING_COMPLETED,
                {
                    "user_id": session.user_id,
                    "session_id": session_id,
                    "completion_rate": session.completion_rate(),
                },
            )
            return session
        return None

    async def detect_patterns(self, user_id: str) -> List[LearningPattern]:
        """Detect learning patterns for a user."""
        patterns = []

        if user_id not in self.user_histories:
            return patterns

        sessions = self.user_histories[user_id]
        if len(sessions) < 3:
            return patterns

        recent_sessions = sessions[-5:]
        completion_rates = [s.completion_rate() for s in recent_sessions]
        if len(completion_rates) > 1:
            improvement = completion_rates[-1] - completion_rates[0]
            if improvement > 0.15:
                patterns.append(
                    LearningPattern(
                        pattern_type="consistent_improvement",
                        confidence=min(0.95, abs(improvement)),
                        description="User shows consistent improvement over sessions",
                        recommendations=["Increase difficulty", "Expand topic coverage"],
                    )
                )

        self.detected_patterns[user_id] = patterns

        if patterns:
            self.emit_event(
                EventType.PATTERN_DETECTED,
                {
                    "user_id": user_id,
                    "pattern_count": len(patterns),
                    "patterns": [asdict(p) for p in patterns],
                },
            )

        return patterns

    async def generate_learning_path(
        self,
        user_id: str,
        current_skills: Dict[str, float],
        target_skills: Dict[str, float],
        learning_velocity: float = 1.0,
    ) -> PersonalizedLearningPath:
        """Generate personalized learning path."""
        skill_gaps = {}
        for skill, target in target_skills.items():
            current = current_skills.get(skill, 0.0)
            gap = max(0.0, target - current)
            skill_gaps[skill] = gap

        total_gap = sum(skill_gaps.values())
        current_avg = np.mean(list(current_skills.values())) if current_skills else 0.0
        target_avg = np.mean(list(target_skills.values())) if target_skills else 0.0

        estimated_days = max(1, int(total_gap * 30 / learning_velocity))

        path = PersonalizedLearningPath(
            user_id=user_id,
            current_level=current_avg,
            target_level=target_avg,
            estimated_completion_days=estimated_days,
        )

        self.learning_paths[user_id] = path

        self.emit_event(
            EventType.RECOMMENDATION_GENERATED,
            {
                "user_id": user_id,
                "current_level": current_avg,
                "target_level": target_avg,
                "estimated_days": estimated_days,
            },
        )

        return path

    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive progress report."""
        if user_id not in self.user_histories:
            return {"total_sessions": 0, "progress": 0.0}

        sessions = self.user_histories[user_id]
        total_answered = sum(s.questions_answered for s in sessions)
        total_correct = sum(s.correct_answers for s in sessions)

        progress_data = {
            "total_sessions": len(sessions),
            "total_questions_answered": total_answered,
            "overall_completion_rate": (
                total_correct / total_answered if total_answered > 0 else 0.0
            ),
            "patterns_detected": len(self.detected_patterns.get(user_id, [])),
        }

        self.emit_event(
            EventType.BEHAVIOR_ANALYZED,
            {"user_id": user_id, "progress": progress_data},
        )

        return progress_data
