"""Custom HTML scraper for job boards without APIs."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Sequence

import bs4

from ..schemas import JobListing, JobRequirement
from .base import JobConnector


class CustomHTMLScraper(JobConnector):
    """Scrape job listings from arbitrary HTML sources."""

    def __init__(self, provider_name: str, html_pages: Sequence[str]) -> None:
        super().__init__(provider_name=provider_name)
        self.html_pages = html_pages

    def fetch_jobs(self, query: str) -> Iterable[JobListing]:
        listings: List[JobListing] = []
        for index, html in enumerate(self.html_pages):
            soup = bs4.BeautifulSoup(html, "html.parser")
            for card in soup.select(".job-card"):
                title = card.select_one(".job-title")
                company = card.select_one(".company")
                description = card.select_one(".description")
                apply_link = card.select_one("a.apply")
                location = card.select_one(".location")
                requirements = [
                    JobRequirement(skill=req.get_text(strip=True).lower())
                    for req in card.select(".requirements li")
                ]
                listings.append(
                    JobListing(
                        provider=self.provider_name,
                        id=f"{self.provider_name}-{index}-{len(listings)}",
                        company=company.get_text(strip=True) if company else "Unknown",
                        role=(title.get_text(strip=True) if title else "Intern"),
                        location=location.get_text(strip=True) if location else None,
                        description=description.get_text(strip=True) if description else "",
                        requirements=requirements,
                        technologies=[req.skill for req in requirements],
                        apply_url=apply_link["href"] if apply_link else None,
                        posted_at=datetime.utcnow(),
                        metadata={"scraped": True},
                    )
                )
        return listings


__all__ = ["CustomHTMLScraper"]
