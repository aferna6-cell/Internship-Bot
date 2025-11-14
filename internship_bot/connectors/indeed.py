"""Indeed job search connector."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List

from ..schemas import JobListing, JobRequirement
from .base import JobConnector


class IndeedConnector(JobConnector):
    """Fetch internship listings from Indeed's search API."""

    def __init__(self) -> None:
        super().__init__(provider_name="Indeed")

    def fetch_jobs(self, query: str) -> Iterable[JobListing]:
        # Placeholder: Real implementation would call the Indeed API with API key.
        return self._mock_jobs(query)

    def _mock_jobs(self, query: str) -> List[JobListing]:
        now = datetime.utcnow()
        return [
            JobListing(
                provider=self.provider_name,
                id="mock-indeed-1",
                company="Indeed Search Labs",
                role=f"{query.title()} Research Intern",
                location="Austin, TX",
                description="Prototype search ranking improvements for job seekers.",
                requirements=[
                    JobRequirement(skill="python"),
                    JobRequirement(skill="machine learning"),
                ],
                apply_url="https://indeed.com/mock",
                posted_at=now - timedelta(days=3),
                metadata={"mock": True},
            )
        ]


__all__ = ["IndeedConnector"]
