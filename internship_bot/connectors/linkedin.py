"""LinkedIn connector using the public Job Search API (where available)."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, List

import requests

from ..schemas import JobListing, JobRequirement
from .base import JobConnector


class LinkedInConnector(JobConnector):
    """Fetch internship listings from LinkedIn."""

    def __init__(self, base_url: str | None = None) -> None:
        super().__init__(provider_name="LinkedIn")
        self.base_url = base_url or "https://www.linkedin.com/voyager/api/jobSearch"
        self.session = requests.Session()
        self.token = os.getenv("LINKEDIN_API_TOKEN")

    def fetch_jobs(self, query: str) -> Iterable[JobListing]:
        params = {"keywords": query, "f_E": "2", "count": 25}
        if not self.token:
            return self._mock_jobs(query)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        response = self.session.get(self.base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
        return [self._to_job_listing(item) for item in payload.get("elements", [])]

    def _mock_jobs(self, query: str) -> List[JobListing]:
        requirements = [
            JobRequirement(skill="python"),
            JobRequirement(skill="data analysis", required=False),
        ]
        return [
            JobListing(
                provider=self.provider_name,
                id="mock-linkedin-1",
                company="LinkedIn Corp",
                role=f"{query.title()} Intern",
                location="Remote",
                description="Work on LinkedIn mock data integrations.",
                requirements=requirements,
                apply_url="https://linkedin.com/jobs/mock",
                posted_at=datetime.utcnow(),
                metadata={"mock": True},
            )
        ]

    def _to_job_listing(self, item: dict) -> JobListing:
        return JobListing(
            provider=self.provider_name,
            id=str(item.get("id")),
            company=item.get("companyName", "Unknown"),
            role=item.get("title", "Intern"),
            location=item.get("formattedLocation", "Unknown"),
            description=item.get("descriptionSnippet", ""),
            requirements=[],
            apply_url=item.get("applyMethod", {}).get("companyApplyUrl"),
            posted_at=None,
            metadata=item,
        )


__all__ = ["LinkedInConnector"]
