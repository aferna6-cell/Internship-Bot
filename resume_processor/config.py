"""Preference configuration utilities."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List
import json

CONFIG_DIR = Path.home() / ".internship_bot"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class UserPreferences:
    """Stores preferred locations, roles, and technologies."""

    preferred_locations: List[str]
    role_types: List[str]
    desired_technologies: List[str]

    @classmethod
    def default(cls) -> "UserPreferences":
        return cls(preferred_locations=[], role_types=[], desired_technologies=[])


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_preferences() -> UserPreferences:
    """Load stored preferences or return defaults."""

    if not CONFIG_FILE.exists():
        return UserPreferences.default()
    with CONFIG_FILE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return UserPreferences(
        preferred_locations=payload.get("preferred_locations", []),
        role_types=payload.get("role_types", []),
        desired_technologies=payload.get("desired_technologies", []),
    )


def save_preferences(prefs: UserPreferences) -> None:
    """Persist the provided preferences to disk."""

    ensure_config_dir()
    with CONFIG_FILE.open("w", encoding="utf-8") as handle:
        json.dump(asdict(prefs), handle, indent=2)


def update_preferences(
    *,
    locations: List[str] | None = None,
    roles: List[str] | None = None,
    technologies: List[str] | None = None,
) -> UserPreferences:
    """Update stored preferences with the provided fields."""

    prefs = load_preferences()
    if locations is not None:
        prefs.preferred_locations = [loc.strip() for loc in locations if loc.strip()]
    if roles is not None:
        prefs.role_types = [role.strip() for role in roles if role.strip()]
    if technologies is not None:
        prefs.desired_technologies = [tech.strip() for tech in technologies if tech.strip()]
    save_preferences(prefs)
    return prefs


def preferences_to_dict(prefs: UserPreferences) -> Dict[str, Any]:
    return asdict(prefs)
