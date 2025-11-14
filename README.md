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
