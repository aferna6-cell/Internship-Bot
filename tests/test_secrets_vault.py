from pathlib import Path

from internship_bot.secrets_vault import ApplicantRecord, SecretsVault


def test_secrets_vault_roundtrip(tmp_path: Path) -> None:
    key = SecretsVault.generate_key()
    vault = SecretsVault(tmp_path / "vault.json", key)
    record = ApplicantRecord(
        name="sam",
        resume_path="/tmp/resume.pdf",
        cover_letter_path="/tmp/cl.pdf",
        portal_answers={"email": "sam@example.com"},
    )
    vault.save_record(record)

    loaded = vault.get_record("sam")
    assert loaded.resume_path == record.resume_path
    assert loaded.cover_letter_path == record.cover_letter_path
    assert loaded.portal_answers == record.portal_answers

    vault.delete_record("sam")
    assert "sam" not in vault.list_profiles()
