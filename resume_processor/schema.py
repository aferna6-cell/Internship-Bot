"""Definitions for the structured resume schema."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Type, TypeVar


@dataclass
class ResumeFact:
    """Represents an atomic fact pulled out of the resume text."""

    label: str
    value: str
    confidence: float = 0.5


@dataclass
class Skill:
    """Represents a skill and optionally its proficiency level."""

    name: str
    level: Optional[str] = None
    category: Optional[str] = None


@dataclass
class TimelineConstraint:
    """Describes availability or date constraints pulled from the resume."""

    start: Optional[str] = None
    end: Optional[str] = None
    description: Optional[str] = None


@dataclass
class TargetIndustry:
    """Represents industries the candidate is associated with or targeting."""

    name: str
    motivation: Optional[str] = None


@dataclass
class ProfileArtifact:
    """Represents supplemental profile information from external sources."""

    source: str
    artifact_type: str
    retrieved_at: str
    content_snippet: str
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
class ArtifactProfile:
    """Metadata about notable projects or portfolio artifacts."""

    title: str
    description: Optional[str] = None
    link: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class OptimizationSuggestion:
    """Represents guidance on how to improve the resume or positioning."""

    suggestion: str
    rationale: Optional[str] = None
    priority: str = "medium"


@dataclass
class ProjectIdea:
    """Potential projects tailored to the candidate's skills and interests."""

    name: str
    summary: Optional[str] = None
    technologies: List[str] = field(default_factory=list)


@dataclass
class ResumeSchema:
    """Container for all resume metadata."""

    name: Optional[str]
    contact: Dict[str, str] = field(default_factory=dict)
    facts: List[ResumeFact] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    timeline_constraints: List[TimelineConstraint] = field(default_factory=list)
    target_industries: List[TargetIndustry] = field(default_factory=list)
    profile_artifacts: List[ProfileArtifact] = field(default_factory=list)
    artifact_profiles: List[ArtifactProfile] = field(default_factory=list)
    optimization_suggestions: List[OptimizationSuggestion] = field(default_factory=list)
    project_ideas: List[ProjectIdea] = field(default_factory=list)
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-serialisable dictionary."""

        return asdict(self)

    @classmethod
    def from_dict(cls: Type["ResumeSchema"], data: Dict[str, Any]) -> "ResumeSchema":
        """Build the schema instance from a dictionary representation."""

        def build_list(key: str, item_cls):
            return [item_cls(**item) for item in data.get(key, [])]

        return cls(
            name=data.get("name"),
            contact=data.get("contact", {}),
            facts=build_list("facts", ResumeFact),
            skills=build_list("skills", Skill),
            timeline_constraints=build_list("timeline_constraints", TimelineConstraint),
            target_industries=build_list("target_industries", TargetIndustry),
            profile_artifacts=build_list("profile_artifacts", ProfileArtifact),
            artifact_profiles=build_list("artifact_profiles", ArtifactProfile),
            optimization_suggestions=build_list("optimization_suggestions", OptimizationSuggestion),
            project_ideas=build_list("project_ideas", ProjectIdea),
            raw_text=data.get("raw_text"),
        )


T = TypeVar(
    "T",
    ResumeFact,
    Skill,
    TimelineConstraint,
    TargetIndustry,
    ProfileArtifact,
    ArtifactProfile,
    OptimizationSuggestion,
    ProjectIdea,
    ResumeSchema,
)


def to_json_ready(obj: T | List[T]) -> Any:
    """Convert dataclass instances (or list of) into JSON ready structure."""

    if isinstance(obj, list):
        return [asdict(item) for item in obj]
    return asdict(obj)
