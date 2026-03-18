"""Framework integrations for Socratic Learning."""

from socratic_learning.integrations.langchain import LearningTool
from socratic_learning.integrations.openclaw import SocraticLearningSkill

__all__ = ["SocraticLearningSkill", "LearningTool"]
