"""Utility functions for extracting structured information from resume text."""
from __future__ import annotations

import re
from typing import Dict, Iterable, List

from ..schema import ResumeSchema, ResumeFact, Skill, TimelineConstraint, TargetIndustry

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


def build_schema_from_text(text: str) -> ResumeSchema:
    lines = normalise_lines(text)
    sections = extract_sections(lines)
    schema = ResumeSchema(
        name=extract_name(lines),
        contact=extract_contact(text),
        facts=extract_facts(lines),
        skills=extract_skills(sections),
        timeline_constraints=extract_timeline_constraints(text),
        target_industries=extract_target_industries(text),
        raw_text=text,
    )
    return schema
