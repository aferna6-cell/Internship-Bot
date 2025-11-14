"""Artifacts that supplement the resume schema for optimization."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any


@dataclass
class LinkedInProfile:
    """Simplified representation of LinkedIn content we reason over."""

    headline: str = ""
    about: str = ""
    skills: List[str] = field(default_factory=list)
    experiences: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "LinkedInProfile":
        return cls(
            headline=payload.get("headline", ""),
            about=payload.get("about", ""),
            skills=list(payload.get("skills", [])),
            experiences=list(payload.get("experiences", [])),
        )


@dataclass
class PortfolioArtifact:
    """Represents a collection of portfolio projects or website."""

    url: str | None = None
    projects: List[str] = field(default_factory=list)
    highlights: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PortfolioArtifact":
        return cls(
            url=payload.get("url"),
            projects=list(payload.get("projects", [])),
            highlights=dict(payload.get("highlights", {})),
        )
