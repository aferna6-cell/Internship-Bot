# Internship Bot

This project wires a Google Sheets backend to a FastAPI service so that every job
application attempt is recorded with detailed metadata, confirmation IDs and the
materials that were uploaded. A lightweight dashboard and API make it easy to
review the submission history and guard against duplicate applications.

## Spreadsheet backend

Google Sheets is used as the source of truth because it is collaborative and can
be shared without granting access to infrastructure. The sheet needs the
following columns (the app will seed them automatically):

| Column | Purpose |
| --- | --- |
| `Application ID` | Deterministic hash of company + role + job URL. Used to prevent duplicates. |
| `Company` | Employer name. |
| `Role` | Title/position. |
| `Location` | City/state/remote descriptor. |
| `Job Post URL` | Link to the job posting. |
| `Source` | Where the job was found (LinkedIn, referral, etc.). |
| `Status` | Current status (Draft, Applied, Interviewing, Offer, Rejected). |
| `Last Attempt Outcome` | `Success`, `Failure`, or context for the latest attempt. |
| `Attempt Timestamp` | UTC timestamp of the most recent attempt. |
| `Next Follow Up` | Planned follow-up date. |
| `Confirmation ID` | Tracking ID returned by the ATS. |
| `Uploaded Materials` | Filenames or share links submitted with the application. |
| `Notes` | Freeform notes (recruiter feedback, interview prep). |
| `Created At` | When the job was first tracked. |
| `Updated At` | When the row was last edited. |

Each application attempt is logged with:

* success/failure context in `Last Attempt Outcome`
* ATS confirmation number in `Confirmation ID`
* resume/cover letter links in `Uploaded Materials`

## Running the API/dashboard

1. Create a Google Cloud service account with access to the spreadsheet and
   download the credentials JSON file.
2. Share the spreadsheet with the service account email.
3. Export the required environment variables:

```bash
export SHEETS_SPREADSHEET_ID="<spreadsheet-id>"
export SHEETS_WORKSHEET="applications"          # optional
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

4. Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn internship_bot.api:app --reload
```

### API endpoints

* `GET /applications` – list all logged applications
* `POST /applications` – log a new attempt (409 if duplicate exists)
* `POST /applications/upsert` – log or update an attempt in one call
* `POST /applications/duplicates` – check whether an attempt already exists
* `GET /dashboard` – HTML table summarizing the application history

These endpoints expose confirmation IDs, uploaded material references and all
timestamps so you can filter or build additional automation downstream.

## Avoiding duplicate applications

The deterministic `Application ID` is computed from the company, role and job
posting URL. Before saving a new attempt the API searches for the same hash.
Duplicates return an HTTP 409 response that includes the clashing rows and the
existing confirmation IDs/materials, helping prevent multiple submissions to the
same requisition.
Automation toolkit that keeps applicant data encrypted, auto-fills common job
portals, and surfaces monitoring events so humans can intervene quickly.

## Features

- **Playwright-powered automations** for Greenhouse, Workday, and Lever portals
  (headless Chromium/Firefox) with retries and shared form-fill helpers.
- **Encrypted secrets vault** backed by `cryptography.Fernet` for storing resume
  paths, cover letters, and custom questionnaire answers.
- **Monitoring hooks** that report successes, failures, captchas, and
  human-in-the-loop escalation needs.

## Getting Started

```bash
pip install -e .[dev]
playwright install  # once per machine
```

Generate a new vault key (stored in `.internship_bot/vault.key` by default):

```bash
python -m internship_bot.cli vault-init
```

Add a profile with resume, cover letter, and portal metadata:

```bash
python -m internship_bot.cli \
  --vault my_vault.json \
  --key my_vault.key \
  vault-add \
  --name sam_student \
  --resume /path/to/resume.pdf \
  --cover-letter /path/to/cover_letter.pdf \
  --answers '{"posting_url": "https://boards.greenhouse.io/...", "full_name": "Sam Student", "email": "sam@example.com"}'
```

List stored profiles:

```bash
python -m internship_bot.cli vault-list
```

Submit an application (automation will emit monitoring logs):

```bash
python -m internship_bot.cli apply --portal greenhouse --profile sam_student
```

## Monitoring & Alerts

`ApplicationMonitor` fans out events to the configured notifiers. The included
`StdoutNotifier` writes structured lines via the standard `logging` module, but
you can plug in Slack, email, or incident tooling by implementing the
`Notifier` protocol.

Use `monitor.record_captcha()` and `monitor.escalate_to_human()` inside custom
selectors/flows when captchas or required manual review steps appear.
This repository contains a lightweight reference implementation for aggregating internship listings
from multiple sources (LinkedIn, Indeed, Wellfound, and custom scrapers) and ranking them against a
candidate resume targeting Summer 2026 roles.

## Features

- **Connectors** – API-aware connectors for LinkedIn, Indeed, and Wellfound plus a reusable HTML
  scraper for sites without an API.
- **Canonical schema** – Every listing is normalized into a `JobListing` object with metadata such as
  company, role, requirements, and application link.
- **Resume-aware ranking** – The `Ranker` uses heuristics (skill overlap, location preferences,
  interest keywords, and recency decay) to prioritize opportunities for a candidate.

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

The `main.py` demo uses mock data when live API credentials are unavailable, producing a ranked list
of internship leads.
# Internship-Bot

Internship-Bot is a monorepo that automates the entire internship search and
application loop. It ingests your resume, finds Summer 2026 internships, applies
on your behalf, and records each submission in a centralized spreadsheet for
auditing.

## Architecture overview

| Component | Summary |
| --- | --- |
| Resume ingestion & preferences | Parse resumes (PDF/DOCX/TXT) into a structured JSON schema and store configurable preferences such as preferred locations and role types. |
| Internship discovery & filtering | Aggregate internship listings from job boards, normalize them into a canonical format, and rank them against your profile. |
| Application automation | Use browser automation to fill out and submit applications while safely handling applicant data and captchas. |
| Spreadsheet & audit logging | Persist every application attempt with metadata, confirmation IDs, and links in a spreadsheet/database for reporting. |

Each component shares the same schema definitions and configuration assets, so
keeping everything in one repository simplifies CI, testing, and deployment.

---

## 1. Resume ingestion & preference configuration

Utilities for converting resumes (PDF/DOCX/TXT) into a structured JSON schema
while keeping track of user preferences (locations, role types, technologies).

### Features

- **Structured schema** – encapsulates resume facts, skills, timeline
  constraints, and target industries.
- **Format-aware parsers** – automatically detect PDF, DOCX, or plain-text
  resumes and convert them into the schema.
- **Configuration CLI** – tweak and persist preference data that can be embedded
  into the parsed output.

### Installation

```bash
pip install -e .
```

Install the optional extras for development:

```bash
pip install -e .[dev]
```

### CLI usage

Parse a resume:

```bash
python -m resume_processor.cli parse /path/to/resume.pdf --pretty --output schema.json
```

Include stored preference configuration in the JSON payload:

```bash
python -m resume_processor.cli parse resume.docx --include-preferences
```

Configure preferences with CLI arguments:

```bash
python -m resume_processor.cli config set --locations "Remote,New York" --role-types "Intern,Full-time" --technologies "Python,TypeScript"
```

Launch the interactive editor:

```bash
python -m resume_processor.cli config interactive
```

Display current preferences:

```bash
python -m resume_processor.cli config show
```

Preferences are stored in `~/.internship_bot/config.json`.

---

## 2. Internship discovery & filtering service

The discovery layer will eventually run as a worker/service that pulls role
listings from sources such as LinkedIn, Wellfound, Greenhouse job feeds, and
custom scrapers. Every listing is normalized into a canonical `JobPosting` JSON
object with fields for company, role, requirements, location, and the original
application link.

**Planned capabilities**

- Modular provider adapters with shared retry/logging utilities.
- Matching heuristics/ML ranking that cross-reference the resume schema and
  preference config to prioritize Summer 2026 internships.
- Deduplication service to avoid submitting the same role twice across different
  job boards.
- REST/gRPC interface so other automation layers can fetch ranked job batches.

---

## 3. Application automation workflow

Browser automation (Playwright/Puppeteer) modules handle the most common ATS
portals (Greenhouse, Workday, Lever, proprietary forms). The workflow engine:

- Encrypts and stores applicant secrets (resume versions, cover letters,
  transcripts) so that form-fillers only access them when needed.
- Applies templates for repeated questions (availability, work authorization,
  diversity, etc.).
- Supports human-in-the-loop review when captchas or novel questions appear.
- Emits structured events (start, success, failure) for the logging subsystem.

Automation scripts live alongside infrastructure-as-code for provisioning the
browser runners and monitoring/alerting hooks.

---

## 4. Spreadsheet & audit logging subsystem

Every application attempt is written to a shared spreadsheet (Google Sheets or
Airtable) plus an append-only audit log. Standard columns include company, role,
source, status, timestamps, confirmation IDs, uploaded materials, and links to
automation logs/screenshots.

Additional services:

- API/dashboard for reviewing history, retrying failed submissions, and
  suppressing duplicates.
- Webhooks/notifications when applications change status.
- Data retention policies to ensure sensitive data is purged on schedule.

---

## Testing

```bash
pytest
```
