"""Portal automation base class using Playwright."""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Optional

from tenacity import retry, stop_after_attempt, wait_fixed

from ..monitoring import ApplicationMonitor
from ..secrets_vault import ApplicantRecord


class PortalAutomation(ABC):
    """Common automation workflow for internship portals."""

    portal_name: str

    def __init__(self, monitor: Optional[ApplicationMonitor] = None) -> None:
        self.monitor = monitor

    async def run(self, record: ApplicantRecord) -> None:
        try:
            await self._execute(record)
            if self.monitor:
                self.monitor.record_success(self.portal_name, record.name)
        except Exception as exc:  # noqa: BLE001 - monitor must get the real error
            if self.monitor:
                self.monitor.record_failure(self.portal_name, record.name, exc)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _execute(self, record: ApplicantRecord) -> None:
        await self._with_browser(record)

    @abstractmethod
    async def _with_browser(self, record: ApplicantRecord) -> None:
        ...

    async def _fill_common_fields(self, page, record: ApplicantRecord, selectors: Dict[str, str]) -> None:  # type: ignore[no-untyped-def]
        """Fill name/email/resume fields shared by portals."""

        if "resume" in selectors:
            await page.set_input_files(selectors["resume"], record.resume_path)
        if record.cover_letter_path and "cover_letter" in selectors:
            await page.set_input_files(selectors["cover_letter"], record.cover_letter_path)
        if not record.portal_answers:
            return
        for question, answer in record.portal_answers.items():
            locator = selectors.get(question)
            if not locator:
                continue
            await page.fill(locator, str(answer))


async def run_automation(automation: PortalAutomation, record: ApplicantRecord) -> None:
    await automation.run(record)


def run_sync(automation: PortalAutomation, record: ApplicantRecord) -> None:
    asyncio.run(run_automation(automation, record))
