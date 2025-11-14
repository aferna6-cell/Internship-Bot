"""Automation workflow for Greenhouse-hosted portals."""
from __future__ import annotations

from typing import Dict

from playwright.async_api import async_playwright

from .base import PortalAutomation
from ..secrets_vault import ApplicantRecord


class GreenhouseAutomation(PortalAutomation):
    portal_name = "greenhouse"

    async def _with_browser(self, record: ApplicantRecord) -> None:
        posting_url = (record.portal_answers or {}).get("posting_url")
        if not posting_url:
            raise ValueError("Greenhouse automation requires 'posting_url' in portal_answers")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(posting_url)
            selectors: Dict[str, str] = {
                "full_name": "input[name='full_name']",
                "email": "input[name='email']",
                "phone": "input[name='phone']",
                "resume": "input[type='file'][name='resume']",
                "cover_letter": "input[type='file'][name='cover_letter']",
            }
            await self._fill_common_fields(page, record, selectors)
            await page.click("button[type='submit']")
            await page.wait_for_selector("text=application submitted", timeout=10000)
            await browser.close()
