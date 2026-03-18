"""Analytics Calculator - Maturity tracking insights and recommendations."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalyticsCalculator:
    """Pure analytics computation for maturity tracking"""

    def __init__(self, project_type: str = "software"):
        """Initialize analytics calculator"""
        self.project_type = project_type
        logger.debug(f"AnalyticsCalculator initialized for {project_type}")

    def analyze_category_performance(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze category strengths and weaknesses"""
        weak_categories: List[Dict[str, Any]] = []
        strong_categories: List[Dict[str, Any]] = []
        missing_categories: List[str] = []

        category_scores = project.get("category_scores", {})

        for category, score_data in category_scores.items():
            if not isinstance(score_data, dict):
                continue

            current = score_data.get("current_score", 0.0)
            target = score_data.get("target_score", 1.0)
            percentage = (current / target * 100) if target > 0 else 0.0
            spec_count = score_data.get("spec_count", 0)

            if spec_count == 0:
                missing_categories.append(category)
            elif percentage < 30:
                weak_categories.append({
                    "category": category,
                    "percentage": percentage,
                    "current": current,
                    "target": target,
                })
            elif percentage > 70:
                strong_categories.append({
                    "category": category,
                    "percentage": percentage,
                    "current": current,
                    "target": target,
                })

        return {
            "weak_categories": sorted(weak_categories, key=lambda x: x["percentage"]),
            "strong_categories": sorted(strong_categories, key=lambda x: x["percentage"], reverse=True),
            "missing_categories": missing_categories,
        }

    def calculate_velocity(self, maturity_history: List[float]) -> float:
        """Calculate learning velocity from maturity history"""
        if len(maturity_history) < 2:
            return 0.0

        recent = maturity_history[-5:] if len(maturity_history) >= 5 else maturity_history
        if len(recent) < 2:
            return 0.0

        velocity = (recent[-1] - recent[0]) / (len(recent) - 1)
        return max(0.0, velocity)

    def identify_plateaus(self, maturity_history: List[float]) -> list[tuple[int, int]]:
        """Identify periods of stagnation in learning"""
        plateaus: list[tuple[int, int]] = []
        if len(maturity_history) < 5:
            return plateaus

        threshold = 2.0  # Less than 2% change
        plateau_start: Optional[int] = None

        for i in range(1, len(maturity_history)):
            change = abs(maturity_history[i] - maturity_history[i-1])
            if change < threshold:
                if plateau_start is None:
                    plateau_start = i - 1
            else:
                if plateau_start is not None:
                    plateaus.append((plateau_start, i))
                    plateau_start = None

        return plateaus

    def generate_recommendations(self, project: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        analysis = self.analyze_category_performance(project)

        if analysis["weak_categories"]:
            top_weak = analysis["weak_categories"][0]
            recommendations.append(
                f"Focus on strengthening {top_weak['category']} ({top_weak['percentage']:.0f}%)"
            )

        if analysis["missing_categories"]:
            recommendations.append(
                f"Complete missing categories: {', '.join(analysis['missing_categories'][:3])}"
            )

        return recommendations
