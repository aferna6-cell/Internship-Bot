"""Utilities for parsing resumes into a structured schema and managing preferences."""

from .schema import (
    ResumeSchema,
    ResumeFact,
    Skill,
    TimelineConstraint,
    TargetIndustry,
    ProfileArtifact,
)
from .config import UserPreferences, load_preferences, save_preferences
from .parsing.factory import parse_resume
from .profile_sources import fetch_linkedin_artifacts, fetch_portfolio_artifacts

__all__ = [
    "ResumeSchema",
    "ResumeFact",
    "Skill",
    "TimelineConstraint",
    "TargetIndustry",
    "ProfileArtifact",
    "UserPreferences",
    "load_preferences",
    "save_preferences",
    "parse_resume",
    "fetch_linkedin_artifacts",
    "fetch_portfolio_artifacts",
]
