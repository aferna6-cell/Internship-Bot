"""Command line interface for parsing resumes and editing preferences."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .config import (
    preferences_to_dict,
    load_preferences,
    save_preferences,
    update_preferences,
    UserPreferences,
)
from .parsing.factory import parse_resume
from .profile_optimizer import (
    LinkedInProfile,
    PortfolioArtifact,
    build_default_optimizer,
    render_cli_report,
    report_to_json,
)
from .schema import ResumeSchema


def parse_command(args: argparse.Namespace) -> None:
    schema = parse_resume(args.file)
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


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_preferences_file(path: str | None) -> UserPreferences:
    if not path:
        return load_preferences()
    payload = _load_json(path)
    return UserPreferences(
        preferred_locations=payload.get("preferred_locations", []),
        role_types=payload.get("role_types", []),
        desired_technologies=payload.get("desired_technologies", []),
    )


def optimize_profiles(args: argparse.Namespace) -> None:
    schema_data = _load_json(args.resume_schema)
    resume = ResumeSchema.from_dict(schema_data)
    preferences = _load_preferences_file(args.preferences)
    linkedin = (
        LinkedInProfile.from_dict(_load_json(args.linkedin)) if args.linkedin else None
    )
    portfolio = (
        PortfolioArtifact.from_dict(_load_json(args.portfolio)) if args.portfolio else None
    )

    optimizer = build_default_optimizer()
    report = optimizer.optimize(
        resume=resume,
        preferences=preferences,
        linkedin=linkedin,
        portfolio=portfolio,
    )

    if args.format == "json":
        payload = report_to_json(report)
    else:
        payload = render_cli_report(report)

    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


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

    optimize_parser = subparsers.add_parser(
        "optimize",
        help="Generate optimization suggestions for a resume + LinkedIn profile",
    )
    optimize_parser.add_argument(
        "--resume-schema",
        required=True,
        help="Path to a JSON document that matches the ResumeSchema",
    )
    optimize_parser.add_argument(
        "--linkedin",
        help="Optional LinkedIn artifact JSON (headline, about, skills, experiences)",
    )
    optimize_parser.add_argument(
        "--portfolio",
        help="Optional portfolio artifact JSON (url, projects, highlights)",
    )
    optimize_parser.add_argument(
        "--preferences",
        help="Optional preferences JSON; defaults to stored configuration",
    )
    optimize_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    optimize_parser.add_argument("--output", help="Optional file to store the report")
    optimize_parser.set_defaults(func=optimize_profiles)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
