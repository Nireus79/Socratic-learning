"""Machine Learning-based prediction models for learning analytics."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Result of a prediction operation."""

    prediction: float  # 0.0 to 1.0 for probabilities, or continuous value
    confidence: float  # 0.0 to 1.0 confidence in the prediction
    feature_importance: Optional[Dict[str, float]] = None  # Top contributing features
    explanation: Optional[str] = None

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"PredictionResult(prediction={self.prediction:.3f}, "
            f"confidence={self.confidence:.3f})"
        )


@dataclass
class LearningOutcomePrediction(PredictionResult):
    """Prediction of user learning outcome/performance."""

    expected_score: Optional[float] = None
    skill_readiness: Optional[float] = None


@dataclass
class ChurnPrediction(PredictionResult):
    """Prediction of user churn/dropout risk."""

    churn_probability: Optional[float] = None
    days_until_churn: Optional[int] = None
    risk_level: Optional[str] = None  # "low", "medium", "high"


@dataclass
class DifficultyPrediction(PredictionResult):
    """Prediction of material/question difficulty."""

    difficulty_level: Optional[str] = None  # "easy", "medium", "hard"
    estimated_completion_time: Optional[float] = None  # in minutes


@dataclass
class SkillGapPrediction:
    """Prediction of skill gaps for a user."""

    user_id: str
    missing_skills: List[str]
    proficiency_gaps: Dict[str, float]  # skill -> gap percentage
    recommended_learning_path: Optional[List[str]] = None
    priority_score: float = 0.0  # 0.0 to 1.0


class MLPredictor:
    """Base class for ML-based predictors."""

    def __init__(self):
        """Initialize ML predictor."""
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train the prediction model.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,)
        """
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions on data.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Predictions (n_samples,)
        """
        raise NotImplementedError

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities for classification.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Probabilities (n_samples, n_classes)
        """
        raise NotImplementedError


class LearningOutcomePredictor(MLPredictor):
    """Predicts user learning outcome/performance."""

    def __init__(self):
        """Initialize learning outcome predictor."""
        super().__init__()
        try:
            from sklearn.ensemble import RandomForestRegressor

            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
            )
        except ImportError:
            self.logger.warning(
                "scikit-learn not installed. Install with: pip install scikit-learn"
            )

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train learning outcome prediction model.

        Args:
            X: Feature matrix (engagement, time, participation, etc.)
            y: Learning outcomes (scores, grades, etc.)
        """
        if self.model is None:
            raise RuntimeError("scikit-learn not installed")

        self.model.fit(X, y)
        self.is_trained = True
        self.logger.info("Learning outcome model trained")

    def predict(self, user_data: Dict[str, Any]) -> LearningOutcomePrediction:
        """
        Predict learning outcome for a user.

        Args:
            user_data: Dictionary with user features:
                - engagement_score: float (0-1)
                - time_spent: float (hours)
                - participation_count: int
                - previous_performance: float (0-100)
                - attention_span: float (0-1)
                - completion_rate: float (0-1)

        Returns:
            LearningOutcomePrediction
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        # Build feature vector
        features = np.array(
            [
                [
                    user_data.get("engagement_score", 0.5),
                    user_data.get("time_spent", 0),
                    user_data.get("participation_count", 0),
                    user_data.get("previous_performance", 50),
                    user_data.get("attention_span", 0.5),
                    user_data.get("completion_rate", 0),
                ]
            ]
        )

        # Make prediction
        predicted_score = self.model.predict(features)[0]
        predicted_score = max(0, min(100, predicted_score))  # Clip to 0-100

        # Get feature importance
        feature_names = [
            "engagement",
            "time_spent",
            "participation",
            "previous_perf",
            "attention",
            "completion",
        ]
        importance = dict(
            zip(feature_names, self.model.feature_importances_)
        )

        return LearningOutcomePrediction(
            prediction=predicted_score / 100,
            expected_score=predicted_score,
            confidence=0.75,  # Placeholder
            feature_importance=importance,
            explanation=f"Predicted score: {predicted_score:.1f}",
        )


class ChurnPredictor(MLPredictor):
    """Predicts user churn/dropout risk."""

    def __init__(self):
        """Initialize churn predictor."""
        super().__init__()
        try:
            from sklearn.ensemble import GradientBoostingClassifier

            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
            )
        except ImportError:
            self.logger.warning(
                "scikit-learn not installed. Install with: pip install scikit-learn"
            )

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train churn prediction model.

        Args:
            X: Feature matrix (activity, engagement, etc.)
            y: Churn labels (0=retained, 1=churned)
        """
        if self.model is None:
            raise RuntimeError("scikit-learn not installed")

        self.model.fit(X, y)
        self.is_trained = True
        self.logger.info("Churn prediction model trained")

    def predict(self, user_data: Dict[str, Any]) -> ChurnPrediction:
        """
        Predict churn risk for a user.

        Args:
            user_data: Dictionary with user features:
                - days_since_login: int
                - last_activity_recency: int (days)
                - engagement_trend: float (-1 to 1)
                - support_tickets: int
                - course_completion_rate: float (0-1)
                - session_frequency: int (per week)

        Returns:
            ChurnPrediction
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        # Build feature vector
        features = np.array(
            [
                [
                    user_data.get("days_since_login", 0),
                    user_data.get("last_activity_recency", 0),
                    user_data.get("engagement_trend", 0),
                    user_data.get("support_tickets", 0),
                    user_data.get("course_completion_rate", 0),
                    user_data.get("session_frequency", 0),
                ]
            ]
        )

        # Make prediction
        churn_prob = self.model.predict_proba(features)[0][1]  # Probability of churn

        # Determine risk level
        if churn_prob > 0.7:
            risk_level = "high"
        elif churn_prob > 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Estimate days until churn
        days_until = max(1, int(30 * (1 - churn_prob)))

        return ChurnPrediction(
            prediction=churn_prob,
            churn_probability=churn_prob,
            days_until_churn=days_until,
            risk_level=risk_level,
            confidence=0.8,
            explanation=f"Churn risk: {risk_level.upper()} ({churn_prob:.1%})",
        )


class DifficultyPredictor(MLPredictor):
    """Predicts material/question difficulty."""

    def __init__(self):
        """Initialize difficulty predictor."""
        super().__init__()
        try:
            from sklearn.ensemble import RandomForestClassifier

            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
            )
            self.classes_ = ["easy", "medium", "hard"]
        except ImportError:
            self.logger.warning(
                "scikit-learn not installed. Install with: pip install scikit-learn"
            )

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train difficulty prediction model.

        Args:
            X: Feature matrix (word count, concepts, etc.)
            y: Difficulty labels (0=easy, 1=medium, 2=hard)
        """
        if self.model is None:
            raise RuntimeError("scikit-learn not installed")

        self.model.fit(X, y)
        self.is_trained = True
        self.logger.info("Difficulty prediction model trained")

    def predict(self, content_data: Dict[str, Any]) -> DifficultyPrediction:
        """
        Predict difficulty of content/question.

        Args:
            content_data: Dictionary with content features:
                - word_count: int
                - concept_count: int
                - vocabulary_level: float (0-1)
                - question_type: str
                - historical_success_rate: float (0-1)

        Returns:
            DifficultyPrediction
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        # Build feature vector
        features = np.array(
            [
                [
                    content_data.get("word_count", 0),
                    content_data.get("concept_count", 0),
                    content_data.get("vocabulary_level", 0.5),
                    content_data.get("question_type_encoded", 0),
                    content_data.get("historical_success_rate", 0.5),
                ]
            ]
        )

        # Make prediction
        difficulty_idx = self.model.predict(features)[0]
        difficulty_level = self.classes_[difficulty_idx]

        # Estimate completion time (in minutes)
        if difficulty_level == "easy":
            completion_time = 5.0
        elif difficulty_level == "medium":
            completion_time = 15.0
        else:
            completion_time = 30.0

        return DifficultyPrediction(
            prediction=difficulty_idx / 2,  # Normalize to 0-1
            difficulty_level=difficulty_level,
            estimated_completion_time=completion_time,
            confidence=0.7,
            explanation=f"Predicted difficulty: {difficulty_level.upper()}",
        )


class SkillGapAnalyzer:
    """Analyzes and predicts skill gaps."""

    def __init__(self):
        """Initialize skill gap analyzer."""
        self.logger = logging.getLogger(__name__)

    def analyze_gaps(
        self,
        user_id: str,
        user_skills: Dict[str, float],
        required_skills: Dict[str, float],
    ) -> SkillGapPrediction:
        """
        Analyze skill gaps for a user.

        Args:
            user_id: User identifier
            user_skills: Dictionary of user skills with proficiency levels (0-1)
            required_skills: Dictionary of required skills with target proficiency (0-1)

        Returns:
            SkillGapPrediction with identified gaps and recommendations
        """
        missing_skills = []
        proficiency_gaps = {}

        # Identify gaps
        for skill, required_level in required_skills.items():
            user_level = user_skills.get(skill, 0.0)
            gap = max(0, required_level - user_level)

            if gap > 0.1:  # More than 10% gap
                missing_skills.append(skill)
                proficiency_gaps[skill] = gap

        # Sort by gap size
        missing_skills = sorted(
            missing_skills,
            key=lambda s: proficiency_gaps[s],
            reverse=True,
        )

        # Generate learning path
        learning_path = self._generate_learning_path(missing_skills, proficiency_gaps)

        # Calculate priority score
        priority_score = sum(proficiency_gaps.values()) / max(1, len(missing_skills))

        return SkillGapPrediction(
            user_id=user_id,
            missing_skills=missing_skills,
            proficiency_gaps=proficiency_gaps,
            recommended_learning_path=learning_path,
            priority_score=min(1.0, priority_score),
        )

    def _generate_learning_path(
        self,
        skills: List[str],
        gaps: Dict[str, float],
    ) -> List[str]:
        """
        Generate recommended learning path.

        Args:
            skills: List of skills to learn
            gaps: Dictionary of skill gaps

        Returns:
            Ordered list of skills to learn
        """
        # Order by dependency and gap size
        # This is a simplified version - could be enhanced with skill dependencies
        ordered_skills = sorted(
            skills,
            key=lambda s: gaps[s],
            reverse=True,
        )

        return ordered_skills[:5]  # Top 5 priority skills
