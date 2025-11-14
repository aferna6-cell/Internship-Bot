"""FastAPI service exposing Internship Bot functionality."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .config import Settings, default_columns
from .models import ApplicationAttempt, ApplicationRow, DuplicateCheckResult
from .sheets_backend import SheetsBackend, rows_to_table

app = FastAPI(title="Internship Bot", version="0.1.0")


def load_settings() -> Settings:
    try:
        return Settings(
            spreadsheet_id=os.environ["SHEETS_SPREADSHEET_ID"],
            worksheet_name=os.environ.get("SHEETS_WORKSHEET", "applications"),
            service_account_file=os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        )
    except KeyError as exc:
        missing = ", ".join(exc.args)
        raise RuntimeError(
            "Missing required environment variable(s): SHEETS_SPREADSHEET_ID "
            "and GOOGLE_APPLICATION_CREDENTIALS"
        ) from exc


@lru_cache(maxsize=1)
def backend() -> SheetsBackend:
    return SheetsBackend(load_settings())


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/applications", response_model=List[ApplicationRow])
def list_applications(svc: SheetsBackend = Depends(backend)):
    return svc.list_rows()


@app.post("/applications", response_model=ApplicationRow)
def log_application(
    payload: ApplicationAttempt, svc: SheetsBackend = Depends(backend)
) -> ApplicationRow:
    duplicates = svc.find_duplicates(payload)
    if duplicates:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Duplicate application detected",
                "existing": [row.dict() for row in duplicates],
            },
        )
    return svc.log_attempt(payload)


@app.post("/applications/upsert", response_model=ApplicationRow)
def upsert_application(
    payload: ApplicationAttempt, svc: SheetsBackend = Depends(backend)
) -> ApplicationRow:
    return svc.upsert_attempt(payload)


@app.post("/applications/duplicates", response_model=DuplicateCheckResult)
def duplicates(
    payload: ApplicationAttempt, svc: SheetsBackend = Depends(backend)
) -> DuplicateCheckResult:
    matches = svc.find_duplicates(payload)
    return DuplicateCheckResult(
        duplicate=len(matches) > 0,
        match_count=len(matches),
        matching_rows=matches,
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(svc: SheetsBackend = Depends(backend)) -> str:
    rows = svc.list_rows()
    table = rows_to_table(rows)
    headers = table[0]
    body_rows = table[1:]
    head_html = "".join(f"<th>{h}</th>" for h in headers)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in body_rows
    )
    return f"""
    <html>
      <head>
        <title>Internship Bot Dashboard</title>
        <style>
          body {{ font-family: sans-serif; margin: 2rem; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
          th {{ background: #f0f0f0; }}
          tr:nth-child(even) {{ background: #fafafa; }}
        </style>
      </head>
      <body>
        <h1>Application History</h1>
        <p>Total records: {len(rows)}</p>
        <table>
          <thead><tr>{head_html}</tr></thead>
          <tbody>{body_html}</tbody>
        </table>
      </body>
    </html>
    """
