"""Parser for plain text resumes."""
from __future__ import annotations

from .base import ResumeParser


class PlainTextResumeParser(ResumeParser):
    def extract_text(self) -> str:
        return self.path.read_text(encoding="utf-8")
