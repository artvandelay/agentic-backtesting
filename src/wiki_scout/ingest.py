"""EventStreams ingestion for Wikipedia recent changes."""

from __future__ import annotations

import json
import time
import urllib.request
from typing import Iterator

from wiki_scout.config import ScoutConfig
from wiki_scout.storage import connect, init_db, insert_recentchange


class EventStreamClient:
    """Lightweight SSE client for Wikimedia EventStreams."""

    def __init__(self, config: ScoutConfig) -> None:
        self._config = config
        self._last_event_id: str | None = None

    def _build_request(self) -> urllib.request.Request:
        headers = {"User-Agent": self._config.user_agent}
        if self._last_event_id:
            headers["Last-Event-ID"] = self._last_event_id
        return urllib.request.Request(self._config.eventstreams_url, headers=headers)

    def events(self) -> Iterator[dict]:
        while True:
            request = self._build_request()
            with urllib.request.urlopen(request, timeout=30) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if line.startswith("id:"):
                        self._last_event_id = line.split(":", 1)[1].strip()
                        continue
                    if not line.startswith("data:"):
                        continue
                    payload = line.split(":", 1)[1].strip()
                    if payload == "[DONE]":
                        return
                    yield json.loads(payload)
            time.sleep(self._config.reconnect_delay_s)


def _is_allowed_event(event: dict, config: ScoutConfig) -> bool:
    if event.get("server_name") != "en.wikipedia.org":
        return False
    if event.get("wiki") != config.language:
        return False
    namespace = event.get("namespace")
    allowed_namespaces = config.namespaces + ((1,) if config.include_talk else tuple())
    if namespace not in allowed_namespaces:
        return False
    if event.get("bot"):
        return False
    if event.get("minor"):
        return False
    return True


def consume_recentchange(config: ScoutConfig) -> None:
    """Consume recentchange events and write them to storage."""

    connection = connect(config.database_path)
    init_db(connection)
    client = EventStreamClient(config)
    for event in client.events():
        if not _is_allowed_event(event, config):
            continue
        insert_recentchange(connection, event)
