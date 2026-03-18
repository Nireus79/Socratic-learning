"""
Learning Engine - Pure business logic for user behavior analysis and personalization.

Stateless computations for user profile building, learning metrics, and personalization hints.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class UserProfile:
    """User behavior profile data class"""
    def __init__(self, user_id, total_questions_asked, total_answered_well, 
                 overall_response_quality, topics_explored, projects_completed, topic_interactions):
        self.user_id = user_id
        self.total_questions_asked = total_questions_asked
        self.total_answered_well = total_answered_well
        self.overall_response_quality = overall_response_quality
        self.topics_explored = topics_explored
        self.projects_completed = projects_completed
        self.topic_interactions = topic_interactions


class LearningEngine:
    """Pure learning analytics engine for user behavior analysis"""

    def __init__(self, logger_instance: Optional[Any] = None):
        """Initialize learning engine"""
        self.logger = logger_instance or logger
        self.logger.debug("LearningEngine initialized")

    def build_user_profile(
        self,
        user_id: str,
        questions_asked: List[Dict[str, Any]],
        responses_quality: List[float],
        topic_interactions: List[str],
        projects_completed: int,
    ) -> UserProfile:
        """Build user profile from raw metrics"""
        total_questions = sum(q.get("times_asked", 0) for q in questions_asked)
        total_answered_well = sum(q.get("times_answered_well", 0) for q in questions_asked)
        overall_quality = sum(responses_quality) / len(responses_quality) if responses_quality else 0.5
        topics_explored = len(set(topic_interactions))

        return UserProfile(
            user_id=user_id,
            total_questions_asked=total_questions,
            total_answered_well=total_answered_well,
            overall_response_quality=overall_quality,
            topics_explored=topics_explored,
            projects_completed=projects_completed,
            topic_interactions=topic_interactions,
        )

    def calculate_learning_metrics(self, profile: UserProfile) -> Dict[str, Any]:
        """Calculate learning metrics from profile"""
        engagement = min(1.0, profile.total_questions_asked / 100.0)

        if profile.total_questions_asked > 0:
            success_rate = profile.total_answered_well / profile.total_questions_asked
            velocity = max(0.0, success_rate - 0.5) * 2.0
        else:
            success_rate = 0.0
            velocity = 0.0

        if profile.total_questions_asked < 10:
            level = "beginner"
        elif profile.total_questions_asked < 50:
            level = "intermediate"
        else:
            level = "advanced"

        return {
            "engagement_score": round(engagement, 2),
            "learning_velocity": round(velocity, 2),
            "experience_level": level,
            "success_rate": round(success_rate, 2),
            "topics_explored": profile.topics_explored,
            "projects_completed": profile.projects_completed,
        }

    def get_personalization_hints(self, profile: UserProfile, metrics: Dict) -> List[str]:
        """Generate personalization hints based on profile"""
        hints = []

        if metrics["experience_level"] == "beginner":
            hints.append("Start with foundational concepts")
        elif metrics["experience_level"] == "advanced":
            hints.append("Ready for complex topics")

        if metrics["learning_velocity"] > 0.7:
            hints.append("User is progressing quickly")

        if metrics["success_rate"] < 0.5:
            hints.append("Focus on challenging areas")

        return hints

    def score_question_effectiveness(self, times_asked: int, times_answered_well: int) -> float:
        """Score question effectiveness"""
        if times_asked == 0:
            return 0.0
        return (times_answered_well / times_asked) * 100.0
