"""Portfolio page crawler and parser."""
from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse
from urllib.request import urlopen

from ..schema import ProfileArtifact


def fetch_portfolio_artifacts(location: str | Path) -> List[ProfileArtifact]:
    """Fetch a portfolio URL (or local file) and extract content snippets."""

    text, resolved_url = _load_text(location)
    timestamp = _now()
    sections = (
        _extract_markdown_sections(text)
        if _looks_like_markdown(resolved_url, text)
        else _extract_html_sections(text)
    )

    artifacts: List[ProfileArtifact] = []
    for title, body in sections:
        snippet = _truncate(body or title)
        if not snippet:
            continue
        metadata = {"section_title": title} if title else {}
        artifacts.append(
            ProfileArtifact(
                source="portfolio",
                artifact_type="portfolio_section",
                retrieved_at=timestamp,
                url=resolved_url,
                content_snippet=snippet,
                metadata=metadata,
            )
        )
    return artifacts


def _load_text(location: str | Path) -> Tuple[str, str]:
    value = str(location)
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https", "file"}:
        with urlopen(value) as response:  # nosec: standard library fetch
            data = response.read()
            encoding = response.headers.get_content_charset() or "utf-8"
            return data.decode(encoding, errors="replace"), response.geturl()
    path = Path(value)
    return path.read_text(encoding="utf-8"), str(path.absolute())


def _looks_like_markdown(url: str, text: str) -> bool:
    return url.lower().endswith(".md") or text.lstrip().startswith("#")


def _extract_markdown_sections(text: str) -> List[Tuple[str, str]]:
    sections: List[Tuple[str, str]] = []
    current_title = "overview"
    buffer: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if buffer:
                sections.append((current_title, "\n".join(buffer).strip()))
                buffer = []
            current_title = stripped.lstrip("# ") or current_title
        else:
            buffer.append(line)
    if buffer:
        sections.append((current_title, "\n".join(buffer).strip()))
    return sections


def _extract_html_sections(text: str) -> List[Tuple[str, str]]:
    parser = _HTMLSectionExtractor()
    parser.feed(text)
    parser.close()
    return parser.sections


class _HTMLSectionExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: List[Tuple[str, str]] = []
        self._current_heading = "overview"
        self._buffer: List[str] = []
        self._collect_heading = False
        self._collect_text = False

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag in {"h1", "h2", "h3"}:
            self._flush()
            self._collect_heading = True
        elif tag in {"p", "li", "section", "article"}:
            self._collect_text = True

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in {"h1", "h2", "h3"}:
            self._collect_heading = False
        elif tag in {"p", "li", "section", "article"}:
            self._collect_text = False
            self._flush()

    def handle_data(self, data: str):
        text = data.strip()
        if not text:
            return
        if self._collect_heading:
            self._current_heading = text
        elif self._collect_text:
            self._buffer.append(text)

    def _flush(self) -> None:
        if self._buffer:
            body = " ".join(self._buffer).strip()
            if body:
                self.sections.append((self._current_heading, body))
            self._buffer = []


def _truncate(value: str, limit: int = 280) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = ["fetch_portfolio_artifacts"]
