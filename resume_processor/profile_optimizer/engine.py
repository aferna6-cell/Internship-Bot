"""Profile optimizer orchestration."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Iterable, List

from ..schema import ResumeSchema
from ..config import UserPreferences, load_preferences
from .artifacts import LinkedInProfile, PortfolioArtifact
from .evaluators.base import (
    CoverageMetrics,
    EvaluationContext,
    Evaluator,
    EvaluationResult,
    Suggestion,
)
from .evaluators.rule_based import (
    FormattingEvaluator,
    MissingKeywordEvaluator,
    ProjectIdeaEvaluator,
)


@dataclass
class OptimizationReport:
    """Aggregated view produced by the optimizer."""

    coverage: CoverageMetrics
    suggestions: List[Suggestion] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "coverage": asdict(self.coverage),
            "suggestions": [asdict(item) for item in self.suggestions],
        }


class ProfileOptimizer:
    """Runs a configurable set of evaluators."""

    def __init__(self, evaluators: Iterable[Evaluator]):
        self._evaluators = list(evaluators)

    def optimize(
        self,
        *,
        resume: ResumeSchema,
        preferences: UserPreferences | None = None,
        linkedin: LinkedInProfile | None = None,
        portfolio: PortfolioArtifact | None = None,
    ) -> OptimizationReport:
        prefs = preferences or load_preferences()
        coverage = compute_coverage_metrics(resume, linkedin, prefs)
        context = EvaluationContext(
            resume=resume,
            linkedin=linkedin,
            portfolio=portfolio,
            preferences=prefs,
            coverage=coverage,
        )
        suggestions: List[Suggestion] = []
        for evaluator in self._evaluators:
            result = evaluator.evaluate(context)
            suggestions.extend(result.suggestions)
        return OptimizationReport(coverage=coverage, suggestions=suggestions)


def compute_coverage_metrics(
    resume: ResumeSchema,
    linkedin: LinkedInProfile | None,
    preferences: UserPreferences,
) -> CoverageMetrics:
    desired_skills = {skill.lower() for skill in preferences.desired_technologies}
    mentioned_skills = set()
    mentioned_skills.update(skill.name.lower() for skill in resume.skills)
    if linkedin:
        mentioned_skills.update(skill.lower() for skill in linkedin.skills)
        for text in linkedin.experiences:
            mentioned_skills.update(token.lower() for token in text.split())
    if resume.raw_text:
        mentioned_skills.update(token.lower() for token in resume.raw_text.split())

    missing_skills = sorted(skill for skill in desired_skills if skill not in mentioned_skills)
    covered_skills = len(desired_skills) - len(missing_skills)

    desired_roles = {role.lower() for role in preferences.role_types}
    mentioned_roles = set()
    for fact in resume.facts:
        if fact.label.lower() in {"role", "title", "target role"}:
            mentioned_roles.add(fact.value.lower())
    if resume.raw_text:
        text_lower = resume.raw_text.lower()
        for role in desired_roles:
            if role in text_lower:
                mentioned_roles.add(role)
    missing_roles = sorted(role for role in desired_roles if role not in mentioned_roles)
    covered_roles = len(desired_roles) - len(missing_roles)

    return CoverageMetrics(
        desired_skills_total=len(desired_skills),
        desired_skills_covered=covered_skills,
        missing_desired_skills=missing_skills,
        desired_roles_total=len(desired_roles),
        desired_roles_covered=covered_roles,
        missing_roles=missing_roles,
    )


def build_default_optimizer() -> ProfileOptimizer:
    """Factory returning a configured optimizer with stock evaluators."""

    return ProfileOptimizer(
        [
            MissingKeywordEvaluator(),
            FormattingEvaluator(),
            ProjectIdeaEvaluator(),
        ]
    )
