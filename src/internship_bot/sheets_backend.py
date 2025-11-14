"""Google Sheets backend for logging job applications."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import gspread
from google.oauth2.service_account import Credentials

from .config import Settings, default_columns
from .models import ApplicationAttempt, ApplicationRow

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsBackend:
    """Wrapper around Google Sheets operations for the bot."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = self._create_client()
        self._worksheet = self._get_or_create_worksheet()

    def _create_client(self) -> gspread.Client:
        credentials = Credentials.from_service_account_file(
            Path(self.settings.service_account_file).expanduser(), scopes=SCOPE
        )
        return gspread.authorize(credentials)

    def _get_or_create_worksheet(self) -> gspread.Worksheet:
        spreadsheet = self._client.open_by_key(self.settings.spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet(self.settings.worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=self.settings.worksheet_name,
                rows="500",
                cols=str(len(default_columns()) + 5),
            )
            self._seed_headers(worksheet)
        else:
            if not worksheet.row_values(1):
                self._seed_headers(worksheet)
        return worksheet

    def _seed_headers(self, worksheet: gspread.Worksheet) -> None:
        headers = [col.header for col in default_columns()]
        worksheet.update("1:1", [headers])

    # ------------------------ public API ------------------------

    def log_attempt(self, attempt: ApplicationAttempt) -> ApplicationRow:
        row = ApplicationRow.from_attempt(attempt)
        self._worksheet.append_row(row.dict().values())
        return row

    def list_rows(self) -> List[ApplicationRow]:
        records = self._worksheet.get_all_records()
        return [ApplicationRow(**record) for record in records if record.get("Company")]

    def find_duplicates(self, attempt: ApplicationAttempt) -> List[ApplicationRow]:
        target_id = attempt.application_id()
        matches: List[ApplicationRow] = []
        for row in self.list_rows():
            if row.application_id == target_id:
                matches.append(row)
        return matches

    def upsert_attempt(self, attempt: ApplicationAttempt) -> ApplicationRow:
        """Update an existing row if duplicate, otherwise append a new one."""

        matches = self.find_duplicates(attempt)
        if not matches:
            return self.log_attempt(attempt)

        updated_row = ApplicationRow.from_attempt(attempt)
        target_row = matches[0]
        cell = self._worksheet.find(target_row.application_id)
        if cell is None:
            # Shouldn't happen, fallback to append
            return self.log_attempt(attempt)
        row_idx = cell.row
        values = list(updated_row.dict().values())
        self._worksheet.update(f"{row_idx}:{row_idx}", [values])
        return updated_row


def rows_to_table(rows: Iterable[ApplicationRow]) -> List[List[str]]:
    """Helper for presenting rows in tabular dashboards."""

    headers = [col.header for col in default_columns()]
    table = [headers]
    for row in rows:
        table.append(list(row.dict().values()))
    return table
