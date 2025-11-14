"""Evaluator primitives used by the optimizer."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, List, Literal

from ..artifacts import LinkedInProfile, PortfolioArtifact
from ...schema import ResumeSchema
from ...config import UserPreferences


@dataclass
class Suggestion:
    """Represents a concrete action for the candidate to take."""

    category: Literal["resume", "linkedin", "portfolio", "project"]
    summary: str
    details: str
    effort_hours: float = 1.0


@dataclass
class CoverageMetrics:
    """Summarises how well the candidate covers preferences."""

    desired_skills_total: int
    desired_skills_covered: int
    missing_desired_skills: List[str] = field(default_factory=list)
    desired_roles_total: int = 0
    desired_roles_covered: int = 0
    missing_roles: List[str] = field(default_factory=list)

    @property
    def skill_coverage_ratio(self) -> float:
        if self.desired_skills_total == 0:
            return 1.0
        return self.desired_skills_covered / self.desired_skills_total

    @property
    def role_coverage_ratio(self) -> float:
        if self.desired_roles_total == 0:
            return 1.0
        return self.desired_roles_covered / max(1, self.desired_roles_total)


@dataclass
class EvaluationContext:
    """Context handed to evaluators."""

    resume: ResumeSchema
    linkedin: LinkedInProfile | None
    portfolio: PortfolioArtifact | None
    preferences: UserPreferences
    coverage: CoverageMetrics


@dataclass
class EvaluationResult:
    """Outcome returned by each evaluator."""

    suggestions: List[Suggestion]


class Evaluator(Protocol):
    """Contract shared by optimizers."""

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        ...
