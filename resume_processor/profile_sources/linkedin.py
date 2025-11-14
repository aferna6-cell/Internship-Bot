"""Parsers for LinkedIn export data."""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import zipfile

from ..schema import ProfileArtifact


def fetch_linkedin_artifacts(export_path: str | Path) -> List[ProfileArtifact]:
    """Parse a LinkedIn export and return normalized profile artifacts."""

    data = _load_export_payload(Path(export_path))
    timestamp = _now()
    artifacts: List[ProfileArtifact] = []

    profile = data.get("profile") or {}
    summary = profile.get("summary") or profile.get("about") or profile.get("headline")
    if summary:
        artifacts.append(
            ProfileArtifact(
                source="linkedin",
                artifact_type="profile_summary",
                retrieved_at=timestamp,
                url=profile.get("public_profile_url"),
                content_snippet=_truncate(summary),
                metadata={
                    "headline": profile.get("headline"),
                    "location": profile.get("location"),
                },
            )
        )

    for position in data.get("positions", []):
        snippet = position.get("description") or _format_position(position)
        if not snippet:
            continue
        artifacts.append(
            ProfileArtifact(
                source="linkedin",
                artifact_type="experience",
                retrieved_at=timestamp,
                content_snippet=_truncate(snippet),
                metadata={
                    "title": position.get("title"),
                    "company": position.get("company"),
                    "start": position.get("start"),
                    "end": position.get("end"),
                },
            )
        )

    skills = data.get("skills") or []
    if skills:
        artifacts.append(
            ProfileArtifact(
                source="linkedin",
                artifact_type="skills",
                retrieved_at=timestamp,
                content_snippet=_truncate(", ".join(skills)),
                metadata={"skills": skills},
            )
        )

    return artifacts


def _load_export_payload(path: Path) -> Dict[str, Any]:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            return _parse_zip_export(archive)
    text = path.read_text(encoding="utf-8")
    return _parse_json_or_csv(path.name, text)


def _parse_zip_export(archive: zipfile.ZipFile) -> Dict[str, Any]:
    for name in archive.namelist():
        if name.lower().endswith(".json") or name.lower().endswith(".csv"):
            payload = archive.read(name).decode("utf-8")
            try:
                return _parse_json_or_csv(name, payload)
            except ValueError:
                continue
    raise ValueError("LinkedIn export did not contain a supported file (JSON/CSV)")


def _parse_json_or_csv(filename: str, payload: str) -> Dict[str, Any]:
    if filename.lower().endswith(".json"):
        data = json.loads(payload)
        if isinstance(data, dict):
            return data
        raise ValueError("LinkedIn JSON export must be an object")
    if filename.lower().endswith(".csv"):
        reader = csv.DictReader(io.StringIO(payload))
        return {"positions": list(reader)}
    raise ValueError("Unsupported LinkedIn export format")


def _format_position(position: Dict[str, str]) -> str:
    title = position.get("title")
    company = position.get("company")
    if title and company:
        return f"{title} at {company}"
    return title or company or ""


def _truncate(value: str, limit: int = 280) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = ["fetch_linkedin_artifacts"]
