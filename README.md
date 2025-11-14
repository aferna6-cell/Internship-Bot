# Internship Bot

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

Utilities for converting resumes (PDF/DOCX/TXT) into a structured JSON schema while keeping
track of user preferences (locations, role types, technologies).

## Features

- **Structured schema** – encapsulates resume facts, skills, timeline constraints, and target
  industries.
- **Format-aware parsers** – automatically detect PDF, DOCX, or plain-text resumes and convert
  them into the schema.
- **Configuration CLI** – tweak and persist preference data that can be embedded into the parsed
  output.

## Installation

```bash
pip install -e .
```

Install the optional extras for development:

```bash
pip install -e .[dev]
```

## Usage

### Parse a resume

```bash
python -m resume_processor.cli parse /path/to/resume.pdf --pretty --output schema.json
```

Include stored preference configuration in the JSON payload:

```bash
python -m resume_processor.cli parse resume.docx --include-preferences
```

### Configure preferences

Use CLI arguments:

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

## Testing

```bash
pytest
```
