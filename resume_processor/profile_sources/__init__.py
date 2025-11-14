"""External profile fetchers used to enrich the resume schema."""

from .linkedin import fetch_linkedin_artifacts
from .portfolio import fetch_portfolio_artifacts

__all__ = ["fetch_linkedin_artifacts", "fetch_portfolio_artifacts"]
