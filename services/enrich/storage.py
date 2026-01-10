"""SQLite-backed storage for diff artifacts and metadata cache."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class DiffRecord:
    page_id: int
    from_rev_id: int
    to_rev_id: int
    added_text: str
    removed_text: str
    context: str


@dataclass
class MetadataRecord:
    page_id: int
    qid: Optional[str]
    categories: List[str]
    fetched_at: datetime


class DiffStorage:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id INTEGER NOT NULL,
                    from_rev_id INTEGER NOT NULL,
                    to_rev_id INTEGER NOT NULL,
                    processed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS diffs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id INTEGER NOT NULL,
                    from_rev_id INTEGER NOT NULL,
                    to_rev_id INTEGER NOT NULL,
                    added_text TEXT,
                    removed_text TEXT,
                    context TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS metadata_cache (
                    page_id INTEGER PRIMARY KEY,
                    qid TEXT,
                    categories TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                );
                """
            )

    def fetch_pending_events(self, limit: int = 100) -> List[sqlite3.Row]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, page_id, from_rev_id, to_rev_id
                FROM events
                WHERE processed_at IS NULL
                ORDER BY id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return rows

    def mark_event_processed(self, event_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE events SET processed_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), event_id),
            )

    def insert_diffs(self, records: Iterable[DiffRecord]) -> None:
        rows = [
            (
                record.page_id,
                record.from_rev_id,
                record.to_rev_id,
                record.added_text,
                record.removed_text,
                record.context,
                datetime.now(timezone.utc).isoformat(),
            )
            for record in records
        ]
        if not rows:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO diffs (
                    page_id, from_rev_id, to_rev_id,
                    added_text, removed_text, context, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def get_cached_metadata(self, page_id: int, ttl: timedelta) -> Optional[MetadataRecord]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT page_id, qid, categories, fetched_at FROM metadata_cache WHERE page_id = ?",
                (page_id,),
            ).fetchone()
        if row is None:
            return None

        fetched_at = datetime.fromisoformat(row["fetched_at"])
        if datetime.now(timezone.utc) - fetched_at > ttl:
            return None

        categories = json.loads(row["categories"]) if row["categories"] else []
        return MetadataRecord(
            page_id=row["page_id"],
            qid=row["qid"],
            categories=categories,
            fetched_at=fetched_at,
        )

    def upsert_metadata(self, record: MetadataRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO metadata_cache (page_id, qid, categories, fetched_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(page_id) DO UPDATE SET
                    qid = excluded.qid,
                    categories = excluded.categories,
                    fetched_at = excluded.fetched_at
                """,
                (
                    record.page_id,
                    record.qid,
                    json.dumps(record.categories),
                    record.fetched_at.isoformat(),
                ),
            )
