"""Command line interface for parsing resumes and editing preferences."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .analysis.optimizer import optimize_schema
from .config import (
    load_preferences,
    preferences_to_dict,
    save_preferences,
    update_preferences,
)
from .parsing.factory import parse_resume


def parse_command(args: argparse.Namespace) -> None:
    schema = parse_resume(args.file)
    if getattr(args, "optimize", False):
        schema = optimize_schema(schema)
    output = schema.to_dict()
    if args.include_preferences:
        output["preferences"] = preferences_to_dict(load_preferences())
    payload = json.dumps(output, indent=2 if args.pretty else None)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


def show_preferences(_: argparse.Namespace) -> None:
    prefs = load_preferences()
    print(json.dumps(preferences_to_dict(prefs), indent=2))


def set_preferences(args: argparse.Namespace) -> None:
    roles = _split_csv(args.role_types)
    locations = _split_csv(args.locations)
    technologies = _split_csv(args.technologies)
    prefs = update_preferences(locations=locations, roles=roles, technologies=technologies)
    print("Updated preferences:")
    print(json.dumps(preferences_to_dict(prefs), indent=2))


def interactive_preferences(_: argparse.Namespace) -> None:
    prefs = load_preferences()
    print("Press enter to keep existing values. Separate list values with commas.\n")
    prefs.preferred_locations = _prompt_list("Preferred locations", prefs.preferred_locations)
    prefs.role_types = _prompt_list("Role types", prefs.role_types)
    prefs.desired_technologies = _prompt_list("Desired technologies", prefs.desired_technologies)
    save_preferences(prefs)
    print("Preferences saved.")


def _prompt_list(label: str, existing: List[str]) -> List[str]:
    prompt = f"{label} [{', '.join(existing) if existing else 'none'}]: "
    value = input(prompt).strip()
    return existing if not value else _split_csv(value)


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Internship Bot resume utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser("parse", help="Parse a resume into the schema")
    parse_parser.add_argument("file", help="Path to the resume file (pdf/docx/txt)")
    parse_parser.add_argument("--output", help="Optional file to write JSON output")
    parse_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parse_parser.add_argument(
        "--include-preferences",
        action="store_true",
        help="Include stored preference configuration in the output",
    )
    parse_parser.add_argument(
        "--optimize",
        action="store_true",
        help="Run the optimization pass and emit the enriched schema in JSON",
    )
    parse_parser.set_defaults(func=parse_command)

    prefs_parser = subparsers.add_parser("config", help="Manage preference configuration")
    prefs_sub = prefs_parser.add_subparsers(dest="config_command", required=True)

    show_parser = prefs_sub.add_parser("show", help="Display current preferences")
    show_parser.set_defaults(func=show_preferences)

    set_parser = prefs_sub.add_parser("set", help="Set preferences via CLI arguments")
    set_parser.add_argument("--locations", help="Comma separated list of preferred locations")
    set_parser.add_argument("--role-types", dest="role_types", help="Comma separated role types")
    set_parser.add_argument(
        "--technologies", help="Comma separated list of desired technologies"
    )
    set_parser.set_defaults(func=set_preferences)

    interactive_parser = prefs_sub.add_parser("interactive", help="Interactive preference editor")
    interactive_parser.set_defaults(func=interactive_preferences)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
