"""High level utilities for enriching resume schemas post extraction."""
from __future__ import annotations

from typing import List

from ..schema import (
    ArtifactProfile,
    OptimizationSuggestion,
    ProjectIdea,
    ResumeSchema,
    Skill,
    TargetIndustry,
)


def optimize_schema(schema: ResumeSchema) -> ResumeSchema:
    """Run an opinionated optimization pass over the schema in-place."""

    schema.optimization_suggestions = _deduplicate_suggestions(
        schema.optimization_suggestions + _suggest_missing_elements(schema)
    )
    schema.project_ideas = _ensure_project_ideas(schema.project_ideas, schema.skills, schema.target_industries)
    schema.artifact_profiles = _annotate_artifacts(schema.artifact_profiles, schema.skills)
    return schema


def _suggest_missing_elements(schema: ResumeSchema) -> List[OptimizationSuggestion]:
    suggestions: List[OptimizationSuggestion] = []
    if not schema.timeline_constraints:
        suggestions.append(
            OptimizationSuggestion(
                suggestion="Clarify timeline of experience",
                rationale="No explicit years or availability window detected.",
                priority="medium",
            )
        )
    if not schema.target_industries:
        suggestions.append(
            OptimizationSuggestion(
                suggestion="Mention targeted industries",
                rationale="Industry focus helps match internships more quickly.",
                priority="medium",
            )
        )
    if len(schema.skills) >= 3:
        skill_summary = ", ".join(skill.name for skill in schema.skills[:3])
        suggestions.append(
            OptimizationSuggestion(
                suggestion=f"Promote projects using {skill_summary}",
                rationale="These skills form a strong thematic focus.",
                priority="low",
            )
        )
    return suggestions


def _ensure_project_ideas(
    existing: List[ProjectIdea], skills: List[Skill], industries: List[TargetIndustry]
) -> List[ProjectIdea]:
    if existing:
        return [
            ProjectIdea(
                name=idea.name,
                summary=idea.summary,
                technologies=idea.technologies or [skill.name for skill in skills[:3]],
            )
            for idea in existing
        ]
    if not skills:
        return existing
    primary_skill = skills[0].name
    industry_hint = industries[0].name if industries else "general"
    summary = (
        f"Ship a {industry_hint} demo that exercises {primary_skill} end-to-end."
        if industries
        else f"Create an open-source toolkit to highlight {primary_skill}."
    )
    return [
        ProjectIdea(
            name=f"{primary_skill} impact project",
            summary=summary,
            technologies=[skill.name for skill in skills[:3]],
        )
    ]


def _annotate_artifacts(
    artifacts: List[ArtifactProfile], skills: List[Skill]
) -> List[ArtifactProfile]:
    if not artifacts:
        return artifacts
    inferred_tags = {skill.name.lower() for skill in skills}
    enriched: List[ArtifactProfile] = []
    for artifact in artifacts:
        tags = artifact.tags or []
        if artifact.link and "github" in artifact.link.lower() and "github" not in tags:
            tags.append("github")
        skill_hits = [skill for skill in inferred_tags if skill in (artifact.description or "").lower()]
        tags.extend(skill_hits)
        enriched.append(
            ArtifactProfile(
                title=artifact.title,
                description=artifact.description,
                link=artifact.link,
                tags=sorted({tag for tag in tags if tag}),
            )
        )
    return enriched


def _deduplicate_suggestions(suggestions: List[OptimizationSuggestion]) -> List[OptimizationSuggestion]:
    seen = set()
    deduped: List[OptimizationSuggestion] = []
    for suggestion in suggestions:
        key = (suggestion.suggestion, suggestion.priority)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(suggestion)
    return deduped
