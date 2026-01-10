"""Worker that enriches stored events with MediaWiki diffs and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .diff_parser import DiffFragment, parse_diff_html
from .http_client import HttpClient
from .metadata import MetadataFetcher
from .storage import DiffRecord, DiffStorage


@dataclass
class Event:
    id: int
    page_id: int
    from_rev_id: int
    to_rev_id: int


class EnrichWorker:
    def __init__(
        self,
        db_path: str,
        api_base_url: str,
        user_agent: str = "nlbt-enrich/0.1",
    ) -> None:
        self.storage = DiffStorage(db_path)
        self.http_client = HttpClient(user_agent=user_agent)
        self.api_base_url = api_base_url
        self.metadata_fetcher = MetadataFetcher(
            storage=self.storage,
            http_client=self.http_client,
            api_base_url=api_base_url,
        )

    def run(self, limit: int = 100) -> int:
        events = self.storage.fetch_pending_events(limit=limit)
        processed = 0
        for row in events:
            event = Event(
                id=row["id"],
                page_id=row["page_id"],
                from_rev_id=row["from_rev_id"],
                to_rev_id=row["to_rev_id"],
            )
            self._process_event(event)
            self.storage.mark_event_processed(event.id)
            processed += 1
        return processed

    def _process_event(self, event: Event) -> None:
        diff_html = self._fetch_diff(event.from_rev_id, event.to_rev_id)
        fragments = parse_diff_html(diff_html)
        records = self._build_diff_records(event, fragments)
        self.storage.insert_diffs(records)
        self.metadata_fetcher.get_metadata(event.page_id)

    def _fetch_diff(self, from_rev_id: int, to_rev_id: int) -> str:
        params = {
            "action": "compare",
            "fromrev": from_rev_id,
            "torev": to_rev_id,
            "format": "json",
        }
        response = self.http_client.get_json(self.api_base_url, params)
        compare = response.data.get("compare", {})
        html = compare.get("*", "")
        if not html:
            html = compare.get("body", "")
        return html

    def _build_diff_records(
        self, event: Event, fragments: Iterable[DiffFragment]
    ) -> List[DiffRecord]:
        return [
            DiffRecord(
                page_id=event.page_id,
                from_rev_id=event.from_rev_id,
                to_rev_id=event.to_rev_id,
                added_text=fragment.added_text,
                removed_text=fragment.removed_text,
                context=fragment.context,
            )
            for fragment in fragments
        ]
