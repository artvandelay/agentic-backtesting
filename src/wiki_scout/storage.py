"""SQLite storage helpers for the Scout pipeline."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS recentchange_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE,
    server_name TEXT,
    namespace INTEGER,
    page_title TEXT,
    page_id INTEGER,
    revision_new INTEGER,
    revision_old INTEGER,
    user TEXT,
    is_bot INTEGER,
    is_minor INTEGER,
    event_ts TEXT,
    raw_event TEXT
);

CREATE TABLE IF NOT EXISTS diffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    revision_new INTEGER,
    revision_old INTEGER,
    page_id INTEGER,
    page_title TEXT,
    added_text TEXT,
    removed_text TEXT,
    fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS term_counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT,
    direction TEXT,
    bucket_ts TEXT,
    count INTEGER,
    page_count INTEGER
);

CREATE TABLE IF NOT EXISTS spike_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT,
    key TEXT,
    direction TEXT,
    score REAL,
    support_count INTEGER,
    window_start TEXT,
    window_end TEXT,
    metadata TEXT
);
"""


def connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()


def insert_recentchange(connection: sqlite3.Connection, event: dict) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO recentchange_events (
            event_id, server_name, namespace, page_title, page_id,
            revision_new, revision_old, user, is_bot, is_minor,
            event_ts, raw_event
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.get("id"),
            event.get("server_name"),
            event.get("namespace"),
            event.get("title"),
            event.get("page_id"),
            event.get("revision", {}).get("new"),
            event.get("revision", {}).get("old"),
            event.get("user"),
            int(bool(event.get("bot"))),
            int(bool(event.get("minor"))),
            datetime.utcfromtimestamp(event.get("timestamp", 0)).isoformat(),
            json.dumps(event, ensure_ascii=False),
        ),
    )
    connection.commit()


def insert_diff(
    connection: sqlite3.Connection,
    revision_new: int,
    revision_old: int,
    page_id: int,
    page_title: str,
    added_text: str,
    removed_text: str,
) -> None:
    connection.execute(
        """
        INSERT INTO diffs (
            revision_new, revision_old, page_id, page_title,
            added_text, removed_text, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            revision_new,
            revision_old,
            page_id,
            page_title,
            added_text,
            removed_text,
            datetime.utcnow().isoformat(),
        ),
    )
    connection.commit()


def upsert_term_counts(
    connection: sqlite3.Connection,
    term: str,
    direction: str,
    bucket_ts: str,
    count: int,
    page_count: int,
) -> None:
    connection.execute(
        """
        INSERT INTO term_counts (term, direction, bucket_ts, count, page_count)
        VALUES (?, ?, ?, ?, ?)
        """,
        (term, direction, bucket_ts, count, page_count),
    )
    connection.commit()


def insert_spike_events(
    connection: sqlite3.Connection,
    events: Iterable[dict],
) -> None:
    connection.executemany(
        """
        INSERT INTO spike_events (
            scope, key, direction, score, support_count, window_start,
            window_end, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                event["scope"],
                event["key"],
                event.get("direction"),
                event["score"],
                event.get("support_count", 0),
                event["window_start"],
                event["window_end"],
                json.dumps(event.get("metadata", {}), ensure_ascii=False),
            )
            for event in events
        ],
    )
    connection.commit()
