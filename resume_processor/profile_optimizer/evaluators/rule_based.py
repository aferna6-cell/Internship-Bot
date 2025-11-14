"""Stock evaluators that run deterministic checks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .base import EvaluationContext, EvaluationResult, Suggestion


@dataclass
class MissingKeywordEvaluator:
    """Checks desired technologies are represented."""

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        missing = context.coverage.missing_desired_skills
        suggestions: List[Suggestion] = []
        for keyword in missing:
            summary = f"Add explicit mention of {keyword}"
            suggestions.append(
                Suggestion(
                    category="resume",
                    summary=summary,
                    details=(
                        "Describe where you used the technology in experience bullets "
                        "or skills so automated scanners can match you to roles."
                    ),
                    effort_hours=0.5,
                )
            )
            suggestions.append(
                Suggestion(
                    category="linkedin",
                    summary=f"Feature {keyword} on LinkedIn",
                    details=(
                        "Update the headline or About section to state hands-on "
                        "practice with the missing keyword."
                    ),
                    effort_hours=0.25,
                )
            )
        return EvaluationResult(suggestions=suggestions)


@dataclass
class FormattingEvaluator:
    """Rough heuristics for outdated formatting."""

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        resume_text = context.resume.raw_text or ""
        suggestions: List[Suggestion] = []
        if "\t" in resume_text or "Objective" in resume_text:
            suggestions.append(
                Suggestion(
                    category="resume",
                    summary="Modernise formatting",
                    details="Avoid tabs/objective statements – use succinct bullet points.",
                    effort_hours=1.0,
                )
            )
        if context.linkedin and len(context.linkedin.about.strip()) < 40:
            suggestions.append(
                Suggestion(
                    category="linkedin",
                    summary="Expand LinkedIn About section",
                    details="Provide 2-3 sentences tying skills to role goals.",
                    effort_hours=0.5,
                )
            )
        return EvaluationResult(suggestions=suggestions)


@dataclass
class ProjectIdeaEvaluator:
    """Produces deterministic project ideas for missing skills."""

    minimum_effort: float = 8.0

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        suggestions: List[Suggestion] = []
        if not context.coverage.missing_desired_skills:
            return EvaluationResult(suggestions=[])
        for skill in context.coverage.missing_desired_skills:
            details = (
                f"Prototype a small portfolio project that requires {skill}. "
                "Describe the problem, stack, and measurable results so both the resume "
                "and LinkedIn project sections can reference it."
            )
            suggestions.append(
                Suggestion(
                    category="project",
                    summary=f"Ship a weekend project using {skill}",
                    details=details,
                    effort_hours=self.minimum_effort,
                )
            )
        return EvaluationResult(suggestions=suggestions)
