from resume_processor.schema import JobPosting, ResumeSchema


def test_job_postings_round_trip():
    schema = ResumeSchema(
        name="Jane Doe",
        job_postings=[
            JobPosting(
                title="Software Engineer Intern",
                company="Acme Corp",
                location="Remote",
                technologies=["Python", "AWS"],
                url="https://example.com",
                source="manual",
            )
        ],
    )

    serialized = schema.to_dict()

    assert serialized["job_postings"][0]["title"] == "Software Engineer Intern"
    assert serialized["job_postings"][0]["technologies"] == ["Python", "AWS"]

    hydrated = ResumeSchema.from_dict(serialized)

    assert hydrated.job_postings[0].title == "Software Engineer Intern"
    assert hydrated.job_postings[0].company == "Acme Corp"
    assert hydrated.job_postings[0].technologies == ["Python", "AWS"]
