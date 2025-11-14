"""Base parser definitions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol

from ..schema import ResumeSchema


class ResumeParser(ABC):
    """Abstract base class for resume parsers."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    @abstractmethod
    def extract_text(self) -> str:
        """Return the textual representation of the resume."""

    def parse(self) -> ResumeSchema:
        from .extraction import build_schema_from_text

        text = self.extract_text()
        return build_schema_from_text(text)


class TextExtractor(Protocol):
    def __call__(self, path: Path) -> str:  # pragma: no cover - structural typing helper
        ...
