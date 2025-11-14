"""PDF parser implementation using pdfminer."""
from __future__ import annotations

from pathlib import Path

from .base import ResumeParser

try:  # pragma: no cover - import guard
    from pdfminer.high_level import extract_text
except Exception:  # pragma: no cover - gracefully degrade when dependency missing
    extract_text = None


class PdfResumeParser(ResumeParser):
    """Parser that extracts text from PDF resumes."""

    def extract_text(self) -> str:
        if extract_text is None:
            raise RuntimeError(
                "pdfminer.six is required for parsing PDF files. Install via 'pip install pdfminer.six'."
            )
        return extract_text(str(self.path))
