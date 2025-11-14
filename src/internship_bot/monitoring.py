"""Monitoring primitives for application submissions."""
from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass, field
from typing import List, Protocol


class Notifier(Protocol):
    def notify(self, message: str) -> None:
        ...


@dataclass
class StdoutNotifier:
    """Simple notifier using :mod:`logging`."""

    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("internship_bot"))

    def notify(self, message: str) -> None:
        self.logger.info(message)


@dataclass
class ApplicationMonitor:
    """Collect events emitted by :class:`PortalAutomation`."""

    notifiers: List[Notifier]

    def record_success(self, portal: str, profile: str) -> None:
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        self._broadcast(f"✅ [{timestamp}] {profile} submission to {portal} succeeded")

    def record_failure(self, portal: str, profile: str, exc: Exception) -> None:
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        self._broadcast(
            f"❌ [{timestamp}] {profile} submission to {portal} failed: {exc}"
        )

    def record_captcha(self, portal: str, profile: str) -> None:
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        self._broadcast(
            f"⚠️ [{timestamp}] Captcha encountered on {portal} for {profile}. Manual solve required"
        )

    def escalate_to_human(self, portal: str, profile: str, reason: str) -> None:
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        self._broadcast(f"🧑‍💻 [{timestamp}] Human review needed for {profile} ({portal}): {reason}")

    def _broadcast(self, message: str) -> None:
        for notifier in self.notifiers:
            notifier.notify(message)
