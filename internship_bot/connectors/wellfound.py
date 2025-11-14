"""Wellfound (AngelList) connector."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from ..schemas import JobListing, JobRequirement
from .base import JobConnector


class WellfoundConnector(JobConnector):
    """Fetch startup internship listings from Wellfound."""

    def __init__(self) -> None:
        super().__init__(provider_name="Wellfound")

    def fetch_jobs(self, query: str) -> Iterable[JobListing]:
        # Wellfound does not expose an official public API. In production this class would
        # use OAuth credentials plus GraphQL requests. Here we simulate the output.
        return self._mock_jobs(query)

    def _mock_jobs(self, query: str) -> List[JobListing]:
        requirements = [
            JobRequirement(skill="python"),
            JobRequirement(skill="react", required=False),
        ]
        return [
            JobListing(
                provider=self.provider_name,
                id="mock-wellfound-1",
                company="Stealth Startup",
                role=f"{query.title()} Platform Intern",
                location="San Francisco, CA",
                description="Join a seed-stage startup building AI copilots.",
                requirements=requirements,
                technologies=[req.skill for req in requirements],
                apply_url="https://wellfound.com/company/mock/jobs/1",
                posted_at=datetime.utcnow(),
                metadata={"mock": True},
            )
        ]


__all__ = ["WellfoundConnector"]
