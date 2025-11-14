"""Configuration and column definitions for the Internship Bot."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class ColumnDefinition(BaseModel):
    """Represents the metadata for a Google Sheets column."""

    key: str = Field(..., description="Internal field key")
    header: str = Field(..., description="Column header shown in Google Sheets")
    description: str = Field(..., description="Human readable description")


def default_columns() -> List[ColumnDefinition]:
    """Return the ordered column definition list for the sheet."""

    return [
        ColumnDefinition(
            key="application_id",
            header="Application ID",
            description=(
                "Deterministic hash of company, role and job url to deduplicate entries."
            ),
        ),
        ColumnDefinition(
            key="company",
            header="Company",
            description="Company name.",
        ),
        ColumnDefinition(
            key="role",
            header="Role",
            description="Role or title applied for.",
        ),
        ColumnDefinition(
            key="location",
            header="Location",
            description="City, state, or remote designation.",
        ),
        ColumnDefinition(
            key="job_post_url",
            header="Job Post URL",
            description="Link to the job description.",
        ),
        ColumnDefinition(
            key="source",
            header="Source",
            description="Where the job posting was discovered (LinkedIn, referral, etc.).",
        ),
        ColumnDefinition(
            key="status",
            header="Status",
            description="Current status (e.g., Draft, Applied, Interviewing, Offer, Rejected).",
        ),
        ColumnDefinition(
            key="last_attempt_outcome",
            header="Last Attempt Outcome",
            description="Success/Failure/Retry along with any context.",
        ),
        ColumnDefinition(
            key="attempt_timestamp",
            header="Attempt Timestamp",
            description="UTC ISO timestamp for the most recent attempt.",
        ),
        ColumnDefinition(
            key="next_follow_up",
            header="Next Follow Up",
            description="Date for the next action or follow up.",
        ),
        ColumnDefinition(
            key="confirmation_id",
            header="Confirmation ID",
            description="Submission confirmation or tracking ID from the ATS.",
        ),
        ColumnDefinition(
            key="uploaded_materials",
            header="Uploaded Materials",
            description="Comma separated list of filenames or share links submitted.",
        ),
        ColumnDefinition(
            key="notes",
            header="Notes",
            description="Free-form notes about the interaction or recruiter feedback.",
        ),
        ColumnDefinition(
            key="created_at",
            header="Created At",
            description="Timestamp when the job was first tracked.",
        ),
        ColumnDefinition(
            key="updated_at",
            header="Updated At",
            description="Timestamp when the row was last modified.",
        ),
    ]


class Settings(BaseModel):
    """Runtime configuration values for the bot."""

    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    worksheet_name: str = Field(
        "applications", description="Worksheet name that stores applications"
    )
    service_account_file: str = Field(
        ..., description="Path to the Google service account credentials JSON"
    )


def as_header_map(columns: List[ColumnDefinition] | None = None) -> Dict[str, int]:
    """Return a mapping from column header to index for fast lookups."""

    cols = columns or default_columns()
    return {col.header: idx for idx, col in enumerate(cols)}


def timestamp() -> str:
    """Return an ISO formatted UTC timestamp."""

    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
