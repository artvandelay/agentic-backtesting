from datetime import datetime, timedelta
import sqlite3
import sys

sys.path.insert(0, "src")

from nlbt.spike_reports import (
    DedupeConfig,
    PageEvidence,
    SpikeEvent,
    build_digest,
    run_scheduled_spike_digest,
    should_report_event,
)


def _event(
    term: str,
    score: float,
    direction: str,
    hours_ago: int,
    pages: list[PageEvidence],
) -> SpikeEvent:
    return SpikeEvent(
        term=term,
        score=score,
        direction=direction,
        observed_at=datetime(2024, 1, 2, 12, 0, 0) - timedelta(hours=hours_ago),
        pages=pages,
    )


def test_should_report_event_dedupe_rules() -> None:
    now = datetime(2024, 1, 2, 12, 0, 0)
    pages = [PageEvidence(url="https://a.com", title="A")]
    event = _event("term", 10.0, "up", 1, pages)
    config = DedupeConfig(
        min_hours_between_reports=6, min_score_delta=2.0, min_new_pages=1
    )

    assert should_report_event(event, None, now, config)

    last_report = {
        "created_at": now - timedelta(hours=2),
        "score": 9.5,
        "page_urls": {"https://a.com"},
    }
    assert not should_report_event(event, last_report, now, config)

    last_report = {
        "created_at": now - timedelta(hours=7),
        "score": 9.5,
        "page_urls": {"https://a.com"},
    }
    assert not should_report_event(event, last_report, now, config)

    last_report = {
        "created_at": now - timedelta(hours=7),
        "score": 7.0,
        "page_urls": {"https://a.com"},
    }
    assert not should_report_event(event, last_report, now, config)

    last_report = {
        "created_at": now - timedelta(hours=7),
        "score": 7.0,
        "page_urls": {"https://old.com"},
    }
    assert should_report_event(event, last_report, now, config)


def test_run_scheduled_spike_digest_persists_reports(tmp_path) -> None:
    now = datetime(2024, 1, 2, 12, 0, 0)
    pages = [
        PageEvidence(
            url="https://example.com/a",
            title="Example A",
            snippet="Snippet A",
            diff_link="https://example.com/diff-a",
        )
    ]
    events = [
        _event("alpha", 12.0, "up", 1, pages),
        _event("beta", 9.0, "down", 2, pages),
    ]
    db_path = tmp_path / "reports.db"

    markdown, payload = run_scheduled_spike_digest(
        events,
        str(db_path),
        window_hours=6,
        now=now,
        limit=5,
        config=DedupeConfig(
            min_hours_between_reports=6,
            min_score_delta=1.0,
            min_new_pages=1,
        ),
    )

    assert "# Spike Digest (last 6h)" in markdown
    assert payload["items"][0]["term"] == "alpha"
    assert payload["items"][0]["direction"] == "up"
    assert payload["items"][0]["top_pages"][0]["url"] == "https://example.com/a"
    assert payload["items"][0]["diff_links"][0] == "https://example.com/diff-a"
    assert payload["items"][0]["snippets"][0] == "Snippet A"

    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT term, payload_json, evidence_json FROM reports")
        rows = cur.fetchall()

    assert {row[0] for row in rows} == {"alpha", "beta"}
    assert "Snippet A" in rows[0][1] or "Snippet A" in rows[1][1]
