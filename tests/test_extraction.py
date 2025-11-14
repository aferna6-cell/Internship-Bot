from resume_processor.parsing.extraction import build_schema_from_text


def test_build_schema_from_text_extracts_sections():
    text = """Jane Doe\nEmail: jane@example.com\nPhone: 555-555-5555\n\nSkills:\nPython, Data Analysis, SQL\nExperience\nSoftware Engineer at FinTech Corp 2020-2022\n"""
    schema = build_schema_from_text(text)

    assert schema.name == "Jane Doe"
    assert schema.contact["email"] == "jane@example.com"
    assert any(skill.name == "Python" for skill in schema.skills)
    assert schema.timeline_constraints, "Expected at least one timeline constraint"
    assert any(industry.name == "finance" for industry in schema.target_industries)
    assert schema.artifact_profiles, "Artifact profiles should be populated"
    assert schema.project_ideas and schema.project_ideas[0].technologies
    assert schema.optimization_suggestions, "Baseline suggestions should exist"
