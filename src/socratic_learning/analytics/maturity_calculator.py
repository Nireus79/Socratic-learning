"""Maturity Calculator - Phase maturity calculation and readiness assessment."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

READY_THRESHOLD = 20.0
COMPLETE_THRESHOLD = 100.0
WARNING_THRESHOLD = 10.0


class MaturityCalculator:
    """Pure maturity calculation logic for project phases"""

    def __init__(self, project_type: str = "software"):
        """Initialize maturity calculator"""
        self.project_type = project_type
        logger.debug(f"MaturityCalculator initialized for {project_type}")

    def calculate_phase_maturity(self, phase_specs: List[Dict], phase: str) -> Dict:
        """Calculate maturity for a phase using confidence-weighted algorithm"""
        if not phase_specs:
            return {
                "phase": phase,
                "maturity_percentage": 0.0,
                "total_score": 0.0,
                "category_scores": {},
                "strongest_categories": [],
                "weakest_categories": [],
                "is_ready": False,
                "warnings": [],
            }

        # Aggregate spec values by category
        category_totals = {}
        for spec in phase_specs:
            categories = spec.get("categories", [])
            value = spec.get("value", 0)
            for cat in categories:
                category_totals[cat] = category_totals.get(cat, 0) + value

        # Calculate overall maturity
        total_score = sum(category_totals.values())
        maturity_percentage = min(100.0, (total_score / 90.0) * 100)

        # Categorize
        strongest = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
        weakest = sorted(category_totals.items(), key=lambda x: x[1])[:3]

        # Generate warnings
        warnings = []
        if maturity_percentage < WARNING_THRESHOLD:
            warnings.append(f"Phase maturity critically low ({maturity_percentage:.1f}%)")
        if maturity_percentage < READY_THRESHOLD:
            warnings.append(f"Phase not ready to advance (< {READY_THRESHOLD}%)")

        return {
            "phase": phase,
            "maturity_percentage": round(maturity_percentage, 1),
            "total_score": round(total_score, 1),
            "category_scores": category_totals,
            "strongest_categories": [c for c, _ in strongest],
            "weakest_categories": [c for c, _ in weakest],
            "is_ready": maturity_percentage >= READY_THRESHOLD,
            "warnings": warnings,
        }

    def categorize_insights(self, insights: List[Dict], categories: List[str]) -> Dict[str, List]:
        """Categorize insights into phase categories"""
        categorized = {cat: [] for cat in categories}

        for insight in insights:
            insight_cats = insight.get("categories", [])
            for cat in insight_cats:
                if cat in categorized:
                    categorized[cat].append(insight)

        return categorized

    def generate_warnings(self, maturity_data: Dict) -> List[str]:
        """Generate warnings based on maturity state"""
        warnings = []

        if maturity_data.get("maturity_percentage", 0) < WARNING_THRESHOLD:
            warnings.append("CRITICAL: Phase severely underdeveloped")

        weakest = maturity_data.get("weakest_categories", [])
        if weakest:
            warnings.append(f"Address weakest areas: {', '.join(weakest[:2])}")

        return warnings
