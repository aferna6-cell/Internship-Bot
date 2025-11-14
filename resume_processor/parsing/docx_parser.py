"""Docx parser implementation using python-docx."""
from __future__ import annotations

from .base import ResumeParser

try:  # pragma: no cover - optional dependency guard
    import docx
except Exception:  # pragma: no cover
    docx = None


class DocxResumeParser(ResumeParser):
    """Parser that extracts text from DOCX resumes."""

    def extract_text(self) -> str:
        if docx is None:
            raise RuntimeError(
                "python-docx is required for parsing DOCX files. Install via 'pip install python-docx'."
            )
        document = docx.Document(str(self.path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
