"""Encadeamento SHA-256 em SQLite local, com verificação contra âncora externa.

Não é WORM, assinatura digital, armazenamento distribuído ou proteção contra
administrador do host. Uma cadeia reescrita só é detectada se a âncora confiável
anterior estiver preservada fora do banco. Não armazene dados pessoais aqui.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from pydantic import AwareDatetime, Field

from .models import Digest, Identifier, StrictModel


class AuditEvent(StrictModel):
    event_id: Identifier
    tenant_id: Identifier
    execution_id: Identifier
    occurred_at: AwareDatetime
    event_type: Identifier
    payload_sha256: Digest


class Anchor(StrictModel):
    sequence: int = Field(ge=0)
    sha256: Digest


def canonical_event(event: AuditEvent) -> str:
    # Este contrato canônico é local ao pacote, não uma implementação de JCS/RFC 8785.
    return json.dumps(event.model_dump(mode="json"), sort_keys=True,
                      separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def chain_hash(sequence: int, previous: str, body: str) -> str:
    data = f"LEXGUARD-AUDIT-V1\n{sequence}\n{previous}\n{body}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


class AuditStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._connection = sqlite3.connect(str(path), timeout=10, isolation_level=None)
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute("""CREATE TABLE IF NOT EXISTS events (
            sequence INTEGER PRIMARY KEY,
            event_id TEXT NOT NULL UNIQUE,
            body TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            digest TEXT NOT NULL
        )""")

    def close(self) -> None:
        self._connection.close()

    def append(self, event: AuditEvent) -> Anchor:
        body = canonical_event(event)
        connection = self._connection
        connection.execute("BEGIN IMMEDIATE")
        try:
            existing = connection.execute(
                "SELECT sequence, body, digest FROM events WHERE event_id = ?", (event.event_id,)
            ).fetchone()
            if existing:
                if existing[1] != body:
                    raise ValueError("ID idempotente reutilizado para conteúdo diferente.")
                connection.execute("COMMIT")
                return Anchor(sequence=existing[0], sha256=existing[2])
            row = connection.execute(
                "SELECT sequence, digest FROM events ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            sequence, previous = (1, "0" * 64) if row is None else (row[0] + 1, row[1])
            digest = chain_hash(sequence, previous, body)
            connection.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)",
                               (sequence, event.event_id, body, previous, digest))
            connection.execute("COMMIT")
            return Anchor(sequence=sequence, sha256=digest)
        except BaseException:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise

    def verify(self, *, expected_anchor: Anchor | None = None) -> bool:
        """A âncora deve referir-se ao último evento, não a um prefixo da cadeia."""
        previous, expected_sequence = "0" * 64, 1
        anchor = Anchor(sequence=0, sha256=previous)
        for sequence, event_id, body, stored_previous, digest in self._connection.execute(
            "SELECT sequence, event_id, body, previous_hash, digest FROM events ORDER BY sequence"
        ):
            if sequence != expected_sequence or stored_previous != previous:
                return False
            if chain_hash(sequence, previous, body) != digest:
                return False
            try:
                event = AuditEvent.model_validate_json(body)
            except ValueError:
                return False
            if event.event_id != event_id or canonical_event(event) != body:
                return False
            anchor = Anchor(sequence=sequence, sha256=digest)
            previous, expected_sequence = digest, sequence + 1
        return expected_anchor is None or anchor == expected_anchor
