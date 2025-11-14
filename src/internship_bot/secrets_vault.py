"""Encrypted vault for storing applicant artifacts and profile data."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet


@dataclass
class ApplicantRecord:
    """Structured data persisted by :class:`SecretsVault`."""

    name: str
    resume_path: str
    cover_letter_path: Optional[str] = None
    portal_answers: Optional[Dict[str, Any]] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload.pop("name", None)
        return {k: v for k, v in payload.items() if v is not None}


class SecretsVault:
    """Persist applicant data encrypted at rest."""

    def __init__(self, storage_path: Path, key: bytes) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(key)

    @staticmethod
    def generate_key() -> bytes:
        return Fernet.generate_key()

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {}
        encrypted = self.storage_path.read_bytes()
        if not encrypted:
            return {}
        decrypted = self._fernet.decrypt(encrypted)
        return json.loads(decrypted)

    def _write_store(self, payload: Dict[str, Any]) -> None:
        serialized = json.dumps(payload, indent=2).encode()
        encrypted = self._fernet.encrypt(serialized)
        self.storage_path.write_bytes(encrypted)

    def list_profiles(self) -> Dict[str, ApplicantRecord]:
        store = self._read_store()
        records: Dict[str, ApplicantRecord] = {}
        for name, data in store.items():
            records[name] = ApplicantRecord(name=name, **data)
        return records

    def save_record(self, record: ApplicantRecord) -> None:
        store = self._read_store()
        store[record.name] = record.to_payload()
        self._write_store(store)

    def get_record(self, name: str) -> ApplicantRecord:
        store = self._read_store()
        if name not in store:
            raise KeyError(f"Profile '{name}' not found in vault")
        payload = store[name]
        return ApplicantRecord(name=name, **payload)

    def delete_record(self, name: str) -> None:
        store = self._read_store()
        if name in store:
            store.pop(name)
            self._write_store(store)
