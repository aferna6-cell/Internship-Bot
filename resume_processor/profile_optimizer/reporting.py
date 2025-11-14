"""Helpers to render optimizer reports."""
from __future__ import annotations

import json
from typing import Dict, List

from .engine import OptimizationReport


def render_cli_report(report: OptimizationReport) -> str:
    """Return a human-readable summary suitable for the CLI."""

    lines: List[str] = []
    coverage = report.coverage
    lines.append("Coverage metrics:")
    lines.append(
        f"  Desired skills covered: {coverage.desired_skills_covered}/{coverage.desired_skills_total} "
        f"({coverage.skill_coverage_ratio:.0%})"
    )
    if coverage.missing_desired_skills:
        lines.append("  Missing skills: " + ", ".join(coverage.missing_desired_skills))
    lines.append(
        f"  Desired roles covered: {coverage.desired_roles_covered}/{coverage.desired_roles_total} "
        f"({coverage.role_coverage_ratio:.0%})"
    )
    if coverage.missing_roles:
        lines.append("  Missing roles: " + ", ".join(coverage.missing_roles))
    if report.suggestions:
        lines.append("\nSuggestions:")
        for suggestion in report.suggestions:
            lines.append(
                f"- [{suggestion.category}] {suggestion.summary} (~{suggestion.effort_hours}h): "
                f"{suggestion.details}"
            )
    else:
        lines.append("\nNo suggestions – great coverage! 🎉")
    return "\n".join(lines)


def report_to_json(report: OptimizationReport) -> str:
    """Serialise the report for export."""

    return json.dumps(report.to_dict(), indent=2)


def report_to_spreadsheet_row(report: OptimizationReport) -> Dict[str, str]:
    """Return a flattened dictionary useful for CSV/spreadsheets."""

    coverage = report.coverage
    summary_bits = [f"{s.category}:{s.summary}" for s in report.suggestions]
    return {
        "skill_coverage": f"{coverage.desired_skills_covered}/{coverage.desired_skills_total}",
        "role_coverage": f"{coverage.desired_roles_covered}/{coverage.desired_roles_total}",
        "missing_skills": ", ".join(coverage.missing_desired_skills),
        "missing_roles": ", ".join(coverage.missing_roles),
        "suggestions": " | ".join(summary_bits),
    }
