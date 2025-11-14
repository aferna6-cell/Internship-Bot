"""Data models used by the Internship Bot."""

from __future__ import annotations

from hashlib import sha1
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from .config import timestamp


class ApplicationAttempt(BaseModel):
    """Represents a single application attempt to a job."""

    company: str
    role: str
    location: Optional[str] = None
    job_post_url: Optional[HttpUrl] = None
    source: Optional[str] = Field(
        default=None, description="Where the job was found (LinkedIn, referral, etc.)"
    )
    status: str = Field(default="Draft")
    last_attempt_outcome: str = Field(..., description="Success or failure details.")
    confirmation_id: Optional[str] = Field(
        default=None, description="Confirmation number returned by the ATS"
    )
    uploaded_materials: List[str] = Field(
        default_factory=list,
        description="Filenames or share links that were uploaded during the attempt.",
    )
    notes: Optional[str] = None
    next_follow_up: Optional[str] = Field(
        default=None, description="YYYY-MM-DD when you plan to follow up"
    )

    @validator("uploaded_materials", pre=True)
    def _normalize_materials(cls, value):  # type: ignore[override]
        if value is None:
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    def application_id(self) -> str:
        """Generate a deterministic ID to deduplicate rows."""

        hasher = sha1()
        hasher.update(self.company.lower().encode("utf-8"))
        hasher.update(self.role.lower().encode("utf-8"))
        if self.job_post_url:
            hasher.update(str(self.job_post_url).lower().encode("utf-8"))
        return hasher.hexdigest()


class ApplicationRow(BaseModel):
    """Represents the flattened row stored in Google Sheets."""

    application_id: str
    company: str
    role: str
    location: Optional[str]
    job_post_url: Optional[str]
    source: Optional[str]
    status: str
    last_attempt_outcome: str
    attempt_timestamp: str
    next_follow_up: Optional[str]
    confirmation_id: Optional[str]
    uploaded_materials: str
    notes: Optional[str]
    created_at: str
    updated_at: str

    @classmethod
    def from_attempt(cls, attempt: ApplicationAttempt) -> "ApplicationRow":
        now = timestamp()
        return cls(
            application_id=attempt.application_id(),
            company=attempt.company,
            role=attempt.role,
            location=attempt.location,
            job_post_url=str(attempt.job_post_url) if attempt.job_post_url else None,
            source=attempt.source,
            status=attempt.status,
            last_attempt_outcome=attempt.last_attempt_outcome,
            attempt_timestamp=now,
            next_follow_up=attempt.next_follow_up,
            confirmation_id=attempt.confirmation_id,
            uploaded_materials=", ".join(attempt.uploaded_materials),
            notes=attempt.notes,
            created_at=now,
            updated_at=now,
        )


class DuplicateCheckResult(BaseModel):
    """Response payload returned by the API duplicate check endpoint."""

    duplicate: bool
    match_count: int
    matching_rows: List[ApplicationRow] = Field(default_factory=list)
