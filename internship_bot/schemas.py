"""Data schemas for job listings and resume profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Sequence


@dataclass
class JobRequirement:
    """Represents a skill requirement for a job listing."""

    skill: str
    level: Optional[str] = None
    required: bool = True


@dataclass
class JobListing:
    """Canonical job listing model used across providers."""

    provider: str
    id: str
    company: str
    role: str
    location: Optional[str]
    description: str
    requirements: Sequence[JobRequirement] = field(default_factory=list)
    technologies: Sequence[str] = field(default_factory=list)
    apply_url: Optional[str] = None
    posted_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ResumeProfile:
    """Simplified schema describing a candidate's background."""

    name: str
    graduation_date: datetime
    skills: List[str]
    interests: List[str] = field(default_factory=list)
    preferred_locations: List[str] = field(default_factory=list)
    target_role_keywords: List[str] = field(default_factory=list)

    def normalized_skills(self) -> List[str]:
        """Return normalized lower-case skills for fuzzy matching."""

        return [skill.strip().lower() for skill in self.skills]


__all__ = [
    "JobRequirement",
    "JobListing",
    "ResumeProfile",
]
