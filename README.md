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
