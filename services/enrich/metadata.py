"""Metadata fetcher for categories and Wikidata QID."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from .http_client import HttpClient
from .storage import DiffStorage, MetadataRecord


@dataclass
class PageMetadata:
    page_id: int
    qid: Optional[str]
    categories: List[str]


class MetadataFetcher:
    def __init__(
        self,
        storage: DiffStorage,
        http_client: HttpClient,
        api_base_url: str,
        ttl: timedelta = timedelta(hours=6),
    ) -> None:
        self.storage = storage
        self.http_client = http_client
        self.api_base_url = api_base_url
        self.ttl = ttl

    def get_metadata(self, page_id: int) -> PageMetadata:
        cached = self.storage.get_cached_metadata(page_id, self.ttl)
        if cached:
            return PageMetadata(page_id=page_id, qid=cached.qid, categories=cached.categories)

        params = {
            "action": "query",
            "format": "json",
            "pageids": page_id,
            "prop": "categories|pageprops",
            "cllimit": "max",
            "redirects": 1,
        }
        response = self.http_client.get_json(self.api_base_url, params)
        pages = response.data.get("query", {}).get("pages", {})
        page = pages.get(str(page_id), {})
        categories = [
            category.get("title")
            for category in page.get("categories", [])
            if category.get("title")
        ]
        qid = page.get("pageprops", {}).get("wikibase_item")

        record = MetadataRecord(
            page_id=page_id,
            qid=qid,
            categories=categories,
            fetched_at=datetime.now(timezone.utc),
        )
        self.storage.upsert_metadata(record)
        return PageMetadata(page_id=page_id, qid=qid, categories=categories)
