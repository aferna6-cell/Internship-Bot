"""Automation workflow for Lever portals."""
from __future__ import annotations

from typing import Dict

from playwright.async_api import async_playwright

from .base import PortalAutomation
from ..secrets_vault import ApplicantRecord


class LeverAutomation(PortalAutomation):
    portal_name = "lever"

    async def _with_browser(self, record: ApplicantRecord) -> None:
        posting_url = (record.portal_answers or {}).get("posting_url")
        if not posting_url:
            raise ValueError("Lever automation requires 'posting_url' in portal_answers")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(posting_url)
            selectors: Dict[str, str] = {
                "resume": "input[name='resume']",
                "cover_letter": "input[name='cover_letter']",
                "full_name": "input[name='name']",
                "email": "input[name='email']",
            }
            await self._fill_common_fields(page, record, selectors)
            await page.click("button[type='submit']")
            await page.wait_for_selector("text=Thanks for applying", timeout=15000)
            await browser.close()
