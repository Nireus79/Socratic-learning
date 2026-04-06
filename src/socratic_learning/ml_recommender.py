"""ML-based recommendation engine for socratic-learning."""
import logging
import pickle
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """User profile with learning metrics."""
    user_id: str
    total_questions_answered: int = 0
    average_answer_quality: float = 0.0
    days_active: int = 0
    last_activity_days_ago: int = 999
    questions_per_day: float = 0.0
    skill_levels: Dict[str, float] = field(default_factory=dict)
    engagement_score: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert profile to ML feature vector."""
        features = [self.total_questions_answered, self.average_answer_quality, self.days_active, self.last_activity_days_ago, self.questions_per_day, self.engagement_score]
        skills = sorted(self.skill_levels.values())[:10]
        features.extend(skills)
        features.extend([0.0] * (10 - len(skills)))
        return np.array(features, dtype=np.float32)

class MLRecommender:
    """ML-based recommendation engine using scikit-learn."""
    MODEL_VERSION = "1.0"
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = Path(model_dir or "./models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.churn_model: Optional[RandomForestClassifier] = None
        self.scaler = StandardScaler()
        self._load_models()

    def _load_models(self) -> None:
        try:
            churn_path = self.model_dir / "churn_model.pkl"
            if churn_path.exists():
                with open(churn_path, "rb") as f:
                    self.churn_model = pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load: {e}")

    def _save_models(self) -> None:
        try:
            if self.churn_model:
                with open(self.model_dir / "churn_model.pkl", "wb") as f:
                    pickle.dump(self.churn_model, f)
        except Exception as e:
            logger.error(f"Failed to save: {e}")

    def predict_churn_risk(self, user_profile: UserProfile) -> Tuple[float, str]:
        if not self.churn_model:
            return 0.5, "unknown"
        try:
            X = user_profile.to_feature_vector().reshape(1, -1)
            X_scaled = self.scaler.transform(X)
            proba = self.churn_model.predict_proba(X_scaled)[0][1]
            risk = "critical" if proba > 0.7 else "high" if proba > 0.5 else "medium" if proba > 0.3 else "low"
            return float(proba), risk
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return 0.5, "error"
