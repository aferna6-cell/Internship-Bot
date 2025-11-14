"""Utility functions for extracting structured information from resume text."""
from __future__ import annotations

import re
from typing import Dict, Iterable, List

from ..schema import (
    ArtifactProfile,
    OptimizationSuggestion,
    ProjectIdea,
    ResumeFact,
    ResumeSchema,
    Skill,
    TimelineConstraint,
    TargetIndustry,
)

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_REGEX = re.compile(r"(?:(?:\+?\d{1,3})[ -]?)?(?:\(\d{3}\)|\d{3})[ -]?\d{3}[ -]?\d{4}")
YEAR_RANGE_REGEX = re.compile(r"(?P<start>20\d{2}|19\d{2})\s*(?:-|–|to)\s*(?P<end>Present|20\d{2}|19\d{2})", re.IGNORECASE)
YEAR_REGEX = re.compile(r"(19|20)\d{2}")

INDUSTRY_KEYWORDS = {
    "finance": ["finance", "fintech", "bank"],
    "healthcare": ["healthcare", "medical", "biotech"],
    "education": ["education", "edtech", "university"],
    "technology": ["technology", "software", "ai", "data"],
    "retail": ["retail", "e-commerce", "commerce"],
}

SKILL_HEADERS = {"skills", "technical skills", "technologies", "stack"}


def normalise_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def extract_name(lines: List[str]) -> str | None:
    return lines[0] if lines else None


def extract_contact(text: str) -> Dict[str, str]:
    contact: Dict[str, str] = {}
    if match := EMAIL_REGEX.search(text):
        contact["email"] = match.group(0)
    if match := PHONE_REGEX.search(text):
        contact["phone"] = match.group(0)
    websites = re.findall(r"https?://\S+", text)
    if websites:
        contact["websites"] = ", ".join(dict.fromkeys(websites))
    return contact


def extract_facts(lines: Iterable[str]) -> List[ResumeFact]:
    facts: List[ResumeFact] = []
    for line in lines:
        if ":" in line:
            label, value = line.split(":", 1)
            label = label.strip()
            value = value.strip()
            if label and value:
                facts.append(ResumeFact(label=label, value=value, confidence=0.6))
    return facts


def extract_skills(sections: Dict[str, str]) -> List[Skill]:
    for key in sections:
        if key.lower() in SKILL_HEADERS:
            values = sections[key]
            skills = [item.strip() for item in re.split(r",|\n", values) if item.strip()]
            return [Skill(name=name) for name in skills]
    return []


def extract_sections(lines: List[str]) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    current_header = ""
    for line in lines:
        lower = line.lower().rstrip(":")
        if lower in SKILL_HEADERS or lower in {"experience", "education", "summary"}:
            current_header = lower.rstrip(":")
            sections[current_header] = []
        elif current_header:
            sections[current_header].append(line)
    return {key: "\n".join(value) for key, value in sections.items()}


def extract_artifact_profiles(lines: List[str], contact: Dict[str, str]) -> List[ArtifactProfile]:
    artifacts: List[ArtifactProfile] = []
    websites = contact.get("websites")
    if websites:
        seen_links = set()
        for raw_url in websites.split(","):
            url = raw_url.strip()
            if not url or url in seen_links:
                continue
            seen_links.add(url)
            lowered = url.lower()
            tags = [tag for tag in ("github", "portfolio", "website") if tag in lowered]
            title = "GitHub Portfolio" if "github" in lowered else "Online Artifact"
            artifacts.append(
                ArtifactProfile(
                    title=title,
                    description="Link provided in contact details",
                    link=url,
                    tags=tags,
                )
            )
    for line in lines:
        lowered = line.lower()
        if "project" in lowered and len(line) > 10:
            artifacts.append(
                ArtifactProfile(
                    title=line[:60],
                    description=line,
                    tags=["project"],
                )
            )
    if not artifacts and lines:
        artifacts.append(
            ArtifactProfile(
                title=f"Profile: {lines[0]}",
                description="Placeholder artifact derived from resume heading.",
            )
        )
    return artifacts


def extract_timeline_constraints(text: str) -> List[TimelineConstraint]:
    constraints: List[TimelineConstraint] = []
    for match in YEAR_RANGE_REGEX.finditer(text):
        constraints.append(
            TimelineConstraint(
                start=match.group("start"),
                end=match.group("end"),
                description=match.group(0),
            )
        )
    if not constraints:
        years = YEAR_REGEX.findall(text)
        unique_years = sorted({"".join(year) for year in years})
        for year in unique_years:
            constraints.append(TimelineConstraint(start=year, end=year, description=year))
    return constraints


def extract_target_industries(text: str) -> List[TargetIndustry]:
    lowered = text.lower()
    industries: List[TargetIndustry] = []
    for name, keywords in INDUSTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                industries.append(TargetIndustry(name=name, motivation=f"Mentioned keyword '{keyword}'"))
                break
    return industries


def generate_project_ideas(skills: List[Skill], industries: List[TargetIndustry]) -> List[ProjectIdea]:
    if not skills:
        return []
    ideas: List[ProjectIdea] = []
    primary_skill = skills[0].name
    industry_names = [industry.name for industry in industries] or ["general"]
    for name in industry_names[:2]:
        if name == "general":
            title = f"{primary_skill} showcase project"
            summary = (
                f"Build a portfolio-ready project that highlights {primary_skill} capabilities."
            )
        else:
            title = f"{primary_skill} for {name}"
            summary = (
                f"Prototype a {name} solution demonstrating {primary_skill} expertise."
            )
        ideas.append(ProjectIdea(name=title, summary=summary, technologies=[primary_skill]))
    return ideas


def baseline_optimization_suggestions(
    skills: List[Skill], contact: Dict[str, str], artifacts: List[ArtifactProfile]
) -> List[OptimizationSuggestion]:
    suggestions: List[OptimizationSuggestion] = [
        OptimizationSuggestion(
            suggestion="Tailor the resume summary toward a specific role",
            rationale="Generic summaries are harder to match with roles.",
            priority="medium",
        )
    ]
    if not contact.get("websites"):
        suggestions.append(
            OptimizationSuggestion(
                suggestion="Add a portfolio or GitHub link",
                rationale="No web presence was detected in the contact block.",
                priority="high",
            )
        )
    if len(skills) < 3:
        suggestions.append(
            OptimizationSuggestion(
                suggestion="List at least three core skills",
                rationale="Applicant tracking systems rank resumes with explicit skill keywords.",
                priority="high",
            )
        )
    if any(not artifact.link for artifact in artifacts):
        suggestions.append(
            OptimizationSuggestion(
                suggestion="Attach URLs to described projects",
                rationale="Projects without links are harder to verify.",
                priority="medium",
            )
        )
    return suggestions


def build_schema_from_text(text: str) -> ResumeSchema:
    lines = normalise_lines(text)
    sections = extract_sections(lines)
    contact = extract_contact(text)
    skills = extract_skills(sections)
    target_industries = extract_target_industries(text)
    artifact_profiles = extract_artifact_profiles(lines, contact)
    schema = ResumeSchema(
        name=extract_name(lines),
        contact=contact,
        facts=extract_facts(lines),
        skills=skills,
        timeline_constraints=extract_timeline_constraints(text),
        target_industries=target_industries,
        artifact_profiles=artifact_profiles,
        optimization_suggestions=baseline_optimization_suggestions(skills, contact, artifact_profiles),
        project_ideas=generate_project_ideas(skills, target_industries),
        raw_text=text,
    )
    return schema
