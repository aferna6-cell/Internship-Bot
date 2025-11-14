"""Base classes and utilities for job source connectors."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from ..schemas import JobListing


class JobConnector(ABC):
    """Abstract connector for fetching raw job listings from a provider."""

    provider_name: str

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    @abstractmethod
    def fetch_jobs(self, query: str) -> Iterable[JobListing]:
        """Return an iterable of normalized job listings for the query."""


__all__ = ["JobConnector"]
