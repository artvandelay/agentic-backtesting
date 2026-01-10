from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Set


@dataclass
class TermBucketStats:
    added: int = 0
    removed: int = 0
    pages: Set[str] = field(default_factory=set)
    editors: Set[str] = field(default_factory=set)

    def record(self, delta_added: int, delta_removed: int, page_id: str, editor_id: str) -> None:
        self.added += delta_added
        self.removed += delta_removed
        if page_id:
            self.pages.add(page_id)
        if editor_id:
            self.editors.add(editor_id)


@dataclass(frozen=True)
class TermWindowStats:
    term: str
    added: int
    removed: int
    pages: Set[str]
    editors: Set[str]


class TermCounterStore:
    """Time-bucketed counters for term additions/removals."""

    def __init__(self, bucket_size: timedelta = timedelta(hours=1)) -> None:
        if bucket_size.total_seconds() <= 0:
            raise ValueError("bucket_size must be positive")
        self.bucket_size = bucket_size
        self.table: Dict[datetime, Dict[str, TermBucketStats]] = {}

    def _bucket_start(self, timestamp: datetime) -> datetime:
        bucket_seconds = int(self.bucket_size.total_seconds())
        epoch = int(timestamp.timestamp())
        bucket_epoch = epoch - (epoch % bucket_seconds)
        return datetime.fromtimestamp(bucket_epoch, tz=timestamp.tzinfo)

    def add_terms(
        self,
        terms_added: Iterable[str],
        terms_removed: Iterable[str],
        page_id: str,
        editor_id: str,
        timestamp: datetime,
    ) -> None:
        bucket = self._bucket_start(timestamp)
        bucket_terms = self.table.setdefault(bucket, {})

        for term in terms_added:
            stats = bucket_terms.setdefault(term, TermBucketStats())
            stats.record(delta_added=1, delta_removed=0, page_id=page_id, editor_id=editor_id)

        for term in terms_removed:
            stats = bucket_terms.setdefault(term, TermBucketStats())
            stats.record(delta_added=0, delta_removed=1, page_id=page_id, editor_id=editor_id)

    def _iter_buckets(self, start: datetime, end: datetime) -> Iterable[Dict[str, TermBucketStats]]:
        for bucket_time, term_map in self.table.items():
            if start <= bucket_time <= end:
                yield term_map

    def get_window_stats(self, term: str, end: datetime, window: timedelta) -> TermWindowStats:
        start = end - window
        added = 0
        removed = 0
        pages: Set[str] = set()
        editors: Set[str] = set()
        for term_map in self._iter_buckets(start, end):
            stats = term_map.get(term)
            if stats:
                added += stats.added
                removed += stats.removed
                pages.update(stats.pages)
                editors.update(stats.editors)
        return TermWindowStats(term=term, added=added, removed=removed, pages=pages, editors=editors)

    def get_rollups(self, term: str, now: datetime) -> Dict[str, TermWindowStats]:
        return {
            "24h": self.get_window_stats(term, now, timedelta(hours=24)),
            "7d": self.get_window_stats(term, now, timedelta(days=7)),
            "30d": self.get_window_stats(term, now, timedelta(days=30)),
        }

    def list_terms(self) -> List[str]:
        terms: Set[str] = set()
        for term_map in self.table.values():
            terms.update(term_map.keys())
        return sorted(terms)
