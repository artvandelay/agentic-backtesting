#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import logging
import os
import time
import urllib.request
from dataclasses import dataclass
from typing import Iterable, Optional

import psycopg2
import psycopg2.extras

DEFAULT_STREAM_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
LOG_INTERVAL_SECONDS = 10
RECONNECT_BASE_DELAY = 1.0
RECONNECT_MAX_DELAY = 30.0


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": dt.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        return json.dumps(payload)


def build_logger(level: str) -> logging.Logger:
    logger = logging.getLogger("recentchange_ingest")
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


@dataclass
class Metrics:
    events_total: int = 0
    reconnects: int = 0
    last_report_time: float = time.time()
    last_report_count: int = 0

    def report(self, logger: logging.Logger, lag_seconds: Optional[float]) -> None:
        now = time.time()
        elapsed = now - self.last_report_time
        if elapsed < LOG_INTERVAL_SECONDS:
            return
        delta = self.events_total - self.last_report_count
        rate = delta / elapsed if elapsed > 0 else 0.0
        logger.info(
            "metrics",
            extra={
                "extra": {
                    "events_total": self.events_total,
                    "events_per_sec": round(rate, 3),
                    "reconnects": self.reconnects,
                    "lag_seconds": lag_seconds,
                }
            },
        )
        self.last_report_time = now
        self.last_report_count = self.events_total


class RecentChangeStore:
    def __init__(self, dsn: str, logger: logging.Logger) -> None:
        self.dsn = dsn
        self.logger = logger
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self.ensure_table()

    def ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS recentchange_events (
                    id BIGSERIAL PRIMARY KEY,
                    event_id TEXT UNIQUE NOT NULL,
                    event_time TIMESTAMPTZ,
                    event JSONB NOT NULL,
                    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_recentchange_events_time ON recentchange_events (event_time)"
            )

    def insert_event(self, event_id: str, event_time: Optional[dt.datetime], event: dict) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO recentchange_events (event_id, event_time, event)
                VALUES (%s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (event_id, event_time, psycopg2.extras.Json(event)),
            )
            inserted = cur.rowcount == 1
        return inserted

    def fetch_last_event_id(self) -> Optional[str]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT event_id FROM recentchange_events ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            return row[0] if row else None


def parse_namespaces(namespaces_raw: str) -> set[int]:
    return {int(value.strip()) for value in namespaces_raw.split(",") if value.strip()}


def parse_event_time(event: dict) -> Optional[dt.datetime]:
    meta = event.get("meta") or {}
    dt_raw = meta.get("dt")
    if not dt_raw:
        return None
    try:
        return dt.datetime.fromisoformat(dt_raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def should_keep_event(event: dict, namespaces: set[int]) -> bool:
    if event.get("wiki") != "enwiki":
        return False
    if event.get("namespace") not in namespaces:
        return False
    if event.get("bot") or event.get("minor"):
        return False
    return True


def iter_sse_lines(response: Iterable[bytes]) -> Iterable[str]:
    for raw in response:
        if not raw:
            continue
        yield raw.decode("utf-8").rstrip("\r\n")


def stream_events(url: str, last_event_id: Optional[str], timeout: int) -> Iterable[dict]:
    headers = {"Accept": "text/event-stream"}
    if last_event_id:
        headers["Last-Event-ID"] = last_event_id
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        event_id = None
        data_lines: list[str] = []
        for line in iter_sse_lines(response):
            if line == "":
                if not data_lines:
                    event_id = None
                    continue
                data = "\n".join(data_lines)
                yield {"event_id": event_id, "data": data}
                event_id = None
                data_lines = []
                continue
            if line.startswith(":"):
                continue
            if line.startswith("id:"):
                event_id = line[3:].lstrip()
                continue
            if line.startswith("data:"):
                data_lines.append(line[5:].lstrip())
                continue


def ingest_loop(
    url: str,
    store: RecentChangeStore,
    namespaces: set[int],
    logger: logging.Logger,
    timeout: int,
) -> None:
    metrics = Metrics()
    last_event_id = store.fetch_last_event_id()
    if last_event_id:
        logger.info("resuming", extra={"extra": {"last_event_id": last_event_id}})
    reconnect_delay = RECONNECT_BASE_DELAY

    while True:
        try:
            for raw_event in stream_events(url, last_event_id, timeout):
                payload = json.loads(raw_event["data"])
                if not should_keep_event(payload, namespaces):
                    continue
                meta = payload.get("meta") or {}
                event_id = raw_event["event_id"] or meta.get("id")
                if not event_id:
                    continue
                event_time = parse_event_time(payload)
                inserted = store.insert_event(event_id, event_time, payload)
                if inserted:
                    metrics.events_total += 1
                    last_event_id = event_id
                    lag_seconds = None
                    if event_time is not None:
                        lag_seconds = (dt.datetime.now(dt.timezone.utc) - event_time).total_seconds()
                    metrics.report(logger, lag_seconds)
            reconnect_delay = RECONNECT_BASE_DELAY
        except Exception as exc:
            metrics.reconnects += 1
            logger.warning(
                "reconnect",
                extra={"extra": {"error": str(exc), "reconnects": metrics.reconnects}},
            )
            time.sleep(reconnect_delay)
            reconnect_delay = min(RECONNECT_MAX_DELAY, reconnect_delay * 2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest Wikimedia recentchange stream")
    parser.add_argument("--stream-url", default=os.getenv("RC_STREAM_URL", DEFAULT_STREAM_URL))
    parser.add_argument("--dsn", default=os.getenv("POSTGRES_DSN", ""))
    parser.add_argument(
        "--namespaces",
        default=os.getenv("RC_NAMESPACES", "0"),
        help="Comma-separated namespaces to allow (default: 0).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("RC_STREAM_TIMEOUT", "60")),
        help="Read timeout in seconds.",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("RC_LOG_LEVEL", "INFO"),
        help="Logging level.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.dsn:
        raise SystemExit("POSTGRES_DSN must be set")
    logger = build_logger(args.log_level)
    namespaces = parse_namespaces(args.namespaces)
    store = RecentChangeStore(args.dsn, logger)
    ingest_loop(args.stream_url, store, namespaces, logger, args.timeout)


if __name__ == "__main__":
    main()
