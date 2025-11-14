"""Unit tests for the profile optimizer package."""
from __future__ import annotations

from resume_processor.config import UserPreferences
from resume_processor.profile_optimizer import (
    LinkedInProfile,
    PortfolioArtifact,
    build_default_optimizer,
    render_cli_report,
    report_to_spreadsheet_row,
)
from resume_processor.schema import ResumeSchema, Skill, ResumeFact


def build_sample_schema() -> ResumeSchema:
    return ResumeSchema(
        name="Intern",
        skills=[Skill(name="Python"), Skill(name="Pandas")],
        facts=[ResumeFact(label="role", value="Data Science Intern")],
        raw_text="Python data projects with bullets",
    )


def build_preferences() -> UserPreferences:
    return UserPreferences(
        preferred_locations=["Remote"],
        role_types=["Machine Learning Engineer"],
        desired_technologies=["Python", "TensorFlow"],
    )


def test_optimizer_generates_missing_keyword_recommendations() -> None:
    optimizer = build_default_optimizer()
    report = optimizer.optimize(
        resume=build_sample_schema(),
        preferences=build_preferences(),
        linkedin=LinkedInProfile(headline="Intern", skills=["Python"], about=""),
        portfolio=PortfolioArtifact(projects=["analysis"]),
    )

    assert report.coverage.desired_skills_covered == 1
    assert report.coverage.missing_desired_skills == ["tensorflow"]

    categories = {suggestion.category for suggestion in report.suggestions}
    assert {"resume", "linkedin", "project"}.issubset(categories)
    summaries = [suggestion.summary for suggestion in report.suggestions]
    assert any("TensorFlow" in summary or "tensorflow" in summary.lower() for summary in summaries)


def test_reporting_helpers_include_summary_information() -> None:
    optimizer = build_default_optimizer()
    report = optimizer.optimize(
        resume=build_sample_schema(),
        preferences=build_preferences(),
        linkedin=LinkedInProfile(headline="Intern", skills=["Python"], about=""),
    )
    cli_output = render_cli_report(report)
    assert "Coverage metrics" in cli_output
    assert "Missing skills" in cli_output

    row = report_to_spreadsheet_row(report)
    assert row["skill_coverage"] == "1/2"
    assert "resume:" in row["suggestions"]
