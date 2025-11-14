"""Command line entry point for Internship Bot."""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Dict, Type

from .automation.base import PortalAutomation, run_sync
from .automation.greenhouse import GreenhouseAutomation
from .automation.lever import LeverAutomation
from .automation.workday import WorkdayAutomation
from .monitoring import ApplicationMonitor, StdoutNotifier
from .secrets_vault import ApplicantRecord, SecretsVault

PORTALS: Dict[str, Type[PortalAutomation]] = {
    "greenhouse": GreenhouseAutomation,
    "workday": WorkdayAutomation,
    "lever": LeverAutomation,
}


def _load_vault(args: argparse.Namespace) -> SecretsVault:
    key_path = Path(args.key)
    if not key_path.exists():
        raise SystemExit(f"Vault key not found at {key_path}. Run 'vault init' first.")
    key = key_path.read_text().strip().encode()
    return SecretsVault(Path(args.vault), key)


def cmd_vault_init(args: argparse.Namespace) -> None:
    key = SecretsVault.generate_key()
    Path(args.key).write_text(key.decode())
    print(f"Vault key stored at {args.key}")


def cmd_vault_add(args: argparse.Namespace) -> None:
    vault = _load_vault(args)
    answers = json.loads(args.answers) if args.answers else None
    record = ApplicantRecord(
        name=args.name,
        resume_path=args.resume,
        cover_letter_path=args.cover_letter,
        portal_answers=answers,
    )
    vault.save_record(record)
    print(f"Saved profile {args.name}")


def cmd_vault_list(args: argparse.Namespace) -> None:
    vault = _load_vault(args)
    profiles = vault.list_profiles()
    for name, record in profiles.items():
        print(f"- {name}: resume={record.resume_path} cover_letter={record.cover_letter_path}")


def cmd_apply(args: argparse.Namespace) -> None:
    vault = _load_vault(args)
    record = vault.get_record(args.profile)
    monitor = ApplicationMonitor([StdoutNotifier(logging.getLogger("internship_bot"))])
    automation_cls = PORTALS.get(args.portal)
    if not automation_cls:
        raise SystemExit(f"Unsupported portal '{args.portal}'")
    automation = automation_cls(monitor=monitor)
    run_sync(automation, record)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Internship Bot CLI")
    parser.add_argument("--vault", default=".internship_bot/vault.json", help="Path to encrypted vault")
    parser.add_argument("--key", default=".internship_bot/vault.key", help="Path to encryption key")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("vault-init", help="Generate a new vault key")
    init_cmd.set_defaults(func=cmd_vault_init)

    add_cmd = sub.add_parser("vault-add", help="Add or update a profile")
    add_cmd.add_argument("--name", required=True)
    add_cmd.add_argument("--resume", required=True)
    add_cmd.add_argument("--cover-letter")
    add_cmd.add_argument("--answers", help="JSON blob with portal answers")
    add_cmd.set_defaults(func=cmd_vault_add)

    list_cmd = sub.add_parser("vault-list", help="List stored profiles")
    list_cmd.set_defaults(func=cmd_vault_list)

    apply_cmd = sub.add_parser("apply", help="Submit an application")
    apply_cmd.add_argument("--portal", choices=PORTALS.keys(), required=True)
    apply_cmd.add_argument("--profile", required=True)
    apply_cmd.set_defaults(func=cmd_apply)

    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = build_parser()
    args = parser.parse_args()
    os.makedirs(Path(args.vault).parent, exist_ok=True)
    args.func(args)


if __name__ == "__main__":
    main()
