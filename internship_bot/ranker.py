"""Ranking heuristics for internship listings."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import exp
from typing import Iterable, List, Sequence, Tuple

from .schemas import JobListing, ResumeProfile


@dataclass
class RankedJob:
    job: JobListing
    score: float
    explanation: str


class Ranker:
    """Apply matching heuristics/ML-inspired scoring."""

    def __init__(self, decay_half_life_days: float = 15.0) -> None:
        self.decay_half_life_days = decay_half_life_days

    def rank(self, jobs: Sequence[JobListing], resume: ResumeProfile) -> List[RankedJob]:
        ranked: List[RankedJob] = []
        for job in jobs:
            score, explanation = self._score_job(job, resume)
            ranked.append(RankedJob(job=job, score=score, explanation=explanation))
        return sorted(ranked, key=lambda item: item.score, reverse=True)

    def _score_job(self, job: JobListing, resume: ResumeProfile) -> Tuple[float, str]:
        score = 0.0
        reasons: List[str] = []

        normalized_skills = resume.normalized_skills()
        job_requirements = [req.skill.lower() for req in job.requirements]
        job_technologies = [tech.lower() for tech in job.technologies]
        job_skill_pool = set(job_requirements + job_technologies)
        skill_matches = len(set(normalized_skills) & job_skill_pool)
        if skill_matches:
            points = skill_matches * 5
            score += points
            reasons.append(f"{skill_matches} skill matches (+{points})")

        for keyword in resume.target_role_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in job.role.lower() or keyword_lower in job.description.lower():
                score += 3
                reasons.append(f"Role keyword '{keyword}' (+3)")

        if resume.preferred_locations and job.location:
            if any(loc.lower() in job.location.lower() for loc in resume.preferred_locations):
                score += 4
                reasons.append("Preferred location match (+4)")

        if resume.interests and job.description:
            for interest in resume.interests:
                if interest.lower() in job.description.lower():
                    score += 1.5
                    reasons.append(f"Interest '{interest}' (+1.5)")
                    break

        score += self._recency_bonus(job)
        reasons.append("Recency bonus applied")

        return score, "; ".join(reasons)

    def _recency_bonus(self, job: JobListing) -> float:
        if not job.posted_at:
            return 0.0
        days_old = max((datetime.utcnow() - job.posted_at).days, 0)
        decay_factor = 0.5 ** (days_old / self.decay_half_life_days)
        return 10 * decay_factor


__all__ = ["Ranker", "RankedJob"]
