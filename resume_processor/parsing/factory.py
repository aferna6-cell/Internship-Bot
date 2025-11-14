"""Factory helpers for selecting the correct resume parser."""
from __future__ import annotations

from pathlib import Path

from .base import ResumeParser
from .docx_parser import DocxResumeParser
from .pdf_parser import PdfResumeParser
from .text_parser import PlainTextResumeParser

PARSER_MAP = {
    ".pdf": PdfResumeParser,
    ".docx": DocxResumeParser,
    ".txt": PlainTextResumeParser,
}


def get_parser_for_file(path: str | Path) -> ResumeParser:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    parser_cls = PARSER_MAP.get(suffix)
    if parser_cls is None:
        raise ValueError(f"Unsupported resume format: {suffix}")
    return parser_cls(file_path)


def parse_resume(path: str | Path):
    """Parse a resume file into the structured schema."""

    parser = get_parser_for_file(path)
    return parser.parse()
