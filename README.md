# Internship Bot

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
