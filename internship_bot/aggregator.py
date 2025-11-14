"""Job aggregation utilities."""
from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, List, Sequence

from .connectors.base import JobConnector
from .schemas import JobListing


class JobAggregator:
    """Aggregate job listings from multiple connectors."""

    def __init__(self, connectors: Sequence[JobConnector]) -> None:
        self.connectors = connectors

    def search_jobs(self, query: str) -> List[JobListing]:
        combined: "OrderedDict[str, JobListing]" = OrderedDict()
        for connector in self.connectors:
            for job in connector.fetch_jobs(query):
                combined[f"{job.provider}:{job.id}"] = job
        return list(combined.values())


__all__ = ["JobAggregator"]
