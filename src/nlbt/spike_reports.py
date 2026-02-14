"""Spike reporting job, dedupe rules, and digest assembly."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, Sequence


@dataclass(frozen=True)
class PageEvidence:
    url: str
    title: str
    snippet: str | None = None
    diff_link: str | None = None


@dataclass(frozen=True)
class SpikeEvent:
    term: str
    score: float
    direction: str
    observed_at: datetime
    pages: Sequence[PageEvidence] = field(default_factory=tuple)


@dataclass(frozen=True)
class DedupeConfig:
    min_hours_between_reports: int
    min_score_delta: float
    min_new_pages: int


def ensure_reports_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL,
            window_hours INTEGER NOT NULL,
            score REAL NOT NULL,
            direction TEXT NOT NULL,
            created_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            evidence_json TEXT NOT NULL
        )
        """
    )
    conn.commit()


def select_top_spike_events(
    events: Iterable[SpikeEvent],
    window_hours: int,
    now: datetime,
    limit: int = 20,
) -> list[SpikeEvent]:
    cutoff = now - timedelta(hours=window_hours)
    eligible = [event for event in events if event.observed_at >= cutoff]
    eligible.sort(key=lambda event: event.score, reverse=True)
    return eligible[:limit]


def _serialize_pages(pages: Sequence[PageEvidence]) -> list[dict[str, str]]:
    serialized = []
    for page in pages:
        serialized.append(
            {
                "url": page.url,
                "title": page.title,
                "snippet": page.snippet or "",
                "diff_link": page.diff_link or "",
            }
        )
    return serialized


def _page_urls(pages: Sequence[PageEvidence]) -> set[str]:
    return {page.url for page in pages}


def load_last_report(
    conn: sqlite3.Connection, term: str, window_hours: int
) -> dict[str, object] | None:
    cur = conn.execute(
        """
        SELECT score, created_at, evidence_json
        FROM reports
        WHERE term = ? AND window_hours = ?
        ORDER BY datetime(created_at) DESC
        LIMIT 1
        """,
        (term, window_hours),
    )
    row = cur.fetchone()
    if not row:
        return None
    score, created_at, evidence_json = row
    evidence = json.loads(evidence_json)
    return {
        "score": score,
        "created_at": datetime.fromisoformat(created_at),
        "page_urls": set(evidence.get("page_urls", [])),
    }


def should_report_event(
    event: SpikeEvent,
    last_report: dict[str, object] | None,
    now: datetime,
    config: DedupeConfig,
) -> bool:
    if not last_report:
        return True

    last_time = last_report["created_at"]
    if now - last_time < timedelta(hours=config.min_hours_between_reports):
        return False

    last_score = float(last_report["score"])
    if abs(event.score - last_score) < config.min_score_delta:
        return False

    last_pages = last_report.get("page_urls", set())
    new_pages = _page_urls(event.pages) - set(last_pages)
    if len(new_pages) < config.min_new_pages:
        return False

    return True


def build_digest(
    events: Sequence[SpikeEvent],
    window_hours: int,
    generated_at: datetime,
) -> tuple[str, dict[str, object]]:
    items = []
    lines = [f"# Spike Digest (last {window_hours}h)", ""]
    lines.append(f"Generated: {generated_at.isoformat()}")
    lines.append("")

    for event in events:
        top_pages = _serialize_pages(event.pages)
        item = {
            "term": event.term,
            "score": event.score,
            "direction": event.direction,
            "top_pages": [
                {"url": page["url"], "title": page["title"]}
                for page in top_pages
            ],
            "diff_links": [page["diff_link"] for page in top_pages if page["diff_link"]],
            "snippets": [page["snippet"] for page in top_pages if page["snippet"]],
        }
        items.append(item)

        lines.append(f"## {event.term} ({event.direction})")
        lines.append(f"Score: {event.score:.2f}")
        if item["top_pages"]:
            lines.append("Top pages:")
            for page in item["top_pages"]:
                lines.append(f"- {page['title']} ({page['url']})")
        if item["diff_links"]:
            lines.append("Diff links:")
            for link in item["diff_links"]:
                lines.append(f"- {link}")
        if item["snippets"]:
            lines.append("Snippets:")
            for snippet in item["snippets"]:
                lines.append(f"> {snippet}")
        lines.append("")

    payload = {
        "window_hours": window_hours,
        "generated_at": generated_at.isoformat(),
        "items": items,
    }
    return "\n".join(lines).strip() + "\n", payload


def store_report_items(
    conn: sqlite3.Connection,
    window_hours: int,
    generated_at: datetime,
    payload: dict[str, object],
    events: Sequence[SpikeEvent],
) -> None:
    for event, item in zip(events, payload.get("items", [])):
        evidence = {
            "page_urls": list(_page_urls(event.pages)),
            "pages": _serialize_pages(event.pages),
        }
        conn.execute(
            """
            INSERT INTO reports
                (term, window_hours, score, direction, created_at, payload_json, evidence_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.term,
                window_hours,
                event.score,
                event.direction,
                generated_at.isoformat(),
                json.dumps(item),
                json.dumps(evidence),
            ),
        )
    conn.commit()


def run_scheduled_spike_digest(
    events: Iterable[SpikeEvent],
    db_path: str,
    window_hours: int,
    now: datetime | None = None,
    limit: int = 20,
    config: DedupeConfig | None = None,
) -> tuple[str, dict[str, object]]:
    if now is None:
        now = datetime.utcnow()
    if config is None:
        config = DedupeConfig(
            min_hours_between_reports=window_hours,
            min_score_delta=1.0,
            min_new_pages=1,
        )

    with sqlite3.connect(db_path) as conn:
        ensure_reports_table(conn)

        candidates = select_top_spike_events(events, window_hours, now, limit=limit)
        selected: list[SpikeEvent] = []
        for event in candidates:
            last_report = load_last_report(conn, event.term, window_hours)
            if should_report_event(event, last_report, now, config):
                selected.append(event)

        markdown, payload = build_digest(selected, window_hours, now)
        if selected:
            store_report_items(conn, window_hours, now, payload, selected)

    return markdown, payload
