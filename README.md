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
