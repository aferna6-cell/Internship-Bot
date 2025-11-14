import json
from pathlib import Path

from resume_processor.cli import build_parser
from resume_processor.profile_sources import (
    fetch_linkedin_artifacts,
    fetch_portfolio_artifacts,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_fetch_linkedin_artifacts_parses_export():
    export = FIXTURES / "linkedin_export.json"
    artifacts = fetch_linkedin_artifacts(export)

    assert len(artifacts) >= 2
    summary = next(item for item in artifacts if item.artifact_type == "profile_summary")
    assert "backend services" in summary.content_snippet
    skills = next(item for item in artifacts if item.artifact_type == "skills")
    assert "Robotics" in ", ".join(skills.metadata["skills"])


def test_fetch_portfolio_artifacts_handles_html():
    html_file = FIXTURES / "portfolio.html"
    artifacts = fetch_portfolio_artifacts(html_file)

    assert any("volunteer matching" in art.content_snippet for art in artifacts)
    assert any(art.metadata.get("section_title") == "Writing" for art in artifacts)


def test_fetch_portfolio_artifacts_handles_markdown():
    md_file = FIXTURES / "portfolio.md"
    artifacts = fetch_portfolio_artifacts(md_file)

    assert any(art.metadata.get("section_title") == "Highlights" for art in artifacts)
    assert any("haptics" in art.content_snippet for art in artifacts)


def test_cli_profile_linkedin_command(capsys):
    parser = build_parser()
    args = parser.parse_args(["profile", "linkedin", str(FIXTURES / "linkedin_export.json"), "--pretty"])
    args.func(args)
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert any(item["artifact_type"] == "skills" for item in payload)


def test_cli_profile_portfolio_command(capsys):
    parser = build_parser()
    args = parser.parse_args(["profile", "portfolio", str(FIXTURES / "portfolio.html")])
    args.func(args)
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert any("volunteer" in item["content_snippet"].lower() for item in payload)
