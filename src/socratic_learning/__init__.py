from __future__ import annotations

"""
Socratic Learning - Learning Analytics and Tracking

Extracted from Socrates v1.3.3

Provides user behavior analysis, learning personalization, and question effectiveness tracking.

Main Components:
    - LearningEngine: Pure learning logic for behavior analysis and personalization
    - QuestionEffectiveness: Tracks how effective questions are for specific users
    - UserBehaviorPattern: Captures user interaction patterns and learning styles
    - KnowledgeBaseDocument: Represents documents in user's knowledge base
"""

from .learning import KnowledgeBaseDocument, QuestionEffectiveness, UserBehaviorPattern
from .learning_engine import LearningEngine

__version__ = "0.2.0"
__all__ = [
    "LearningEngine",
    "QuestionEffectiveness",
    "UserBehaviorPattern",
    "KnowledgeBaseDocument",
]
