"""Automation workflow for Workday portals."""
from __future__ import annotations

from typing import Dict

from playwright.async_api import async_playwright

from .base import PortalAutomation
from ..secrets_vault import ApplicantRecord


class WorkdayAutomation(PortalAutomation):
    portal_name = "workday"

    async def _with_browser(self, record: ApplicantRecord) -> None:
        posting_url = (record.portal_answers or {}).get("posting_url")
        if not posting_url:
            raise ValueError("Workday automation requires 'posting_url' in portal_answers")
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto(posting_url)
            selectors: Dict[str, str] = {
                "resume": "input[data-automation-id='file-upload']",
                "full_name": "input[data-automation-id='name']",
                "email": "input[data-automation-id='email']",
            }
            await self._fill_common_fields(page, record, selectors)
            await page.click("button[data-automation-id='bottom-navigation-next-button']")
            await page.wait_for_selector("text=Submission complete", timeout=20000)
            await browser.close()
