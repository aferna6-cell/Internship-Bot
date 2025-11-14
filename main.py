"""Demonstration CLI for the Internship Bot pipeline."""
from __future__ import annotations

from datetime import datetime
from pprint import pprint

from internship_bot.aggregator import JobAggregator
from internship_bot.connectors.indeed import IndeedConnector
from internship_bot.connectors.linkedin import LinkedInConnector
from internship_bot.connectors.scraper import CustomHTMLScraper
from internship_bot.connectors.wellfound import WellfoundConnector
from internship_bot.ranker import Ranker
from internship_bot.schemas import ResumeProfile


SAMPLE_HTML = [
    """
    <div class="job-card">
        <div class="job-title">AI Research Intern</div>
        <div class="company">ML Collective</div>
        <div class="location">Remote - US</div>
        <ul class="requirements">
            <li>python</li>
            <li>pytorch</li>
        </ul>
        <div class="description">Help build open-source AI tooling for research.</div>
        <a class="apply" href="https://mlcollective.org/jobs/ai-research-intern">Apply</a>
    </div>
    """
]


def run_demo() -> None:
    connectors = [
        LinkedInConnector(),
        IndeedConnector(),
        WellfoundConnector(),
        CustomHTMLScraper(provider_name="MLCollective", html_pages=SAMPLE_HTML),
    ]
    aggregator = JobAggregator(connectors)
    ranker = Ranker()

    resume = ResumeProfile(
        name="Intern Candidate",
        graduation_date=datetime(2026, 5, 1),
        skills=["Python", "PyTorch", "React", "SQL"],
        interests=["open-source", "research"],
        preferred_locations=["Remote", "San Francisco"],
        target_role_keywords=["AI", "Platform"],
    )

    jobs = aggregator.search_jobs("software engineering")
    ranked_jobs = ranker.rank(jobs, resume)

    for ranked in ranked_jobs:
        pprint(
            {
                "provider": ranked.job.provider,
                "company": ranked.job.company,
                "role": ranked.job.role,
                "score": ranked.score,
                "explanation": ranked.explanation,
            }
        )


if __name__ == "__main__":
    run_demo()
