"""Digest reporting helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from wiki_scout.storage import connect


@dataclass(frozen=True)
class DigestItem:
    term: str
    direction: str
    score: float
    pages: list[str]
    diff_links: list[str]
    snippet: str


def build_digest(database_path: str, limit: int = 20) -> list[DigestItem]:
    connection = connect(database_path)
    cursor = connection.execute(
        """
        SELECT * FROM spike_events
        WHERE scope = 'term'
        ORDER BY score DESC
        LIMIT ?
        """,
        (limit,),
    )
    items: list[DigestItem] = []
    for row in cursor.fetchall():
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        items.append(
            DigestItem(
                term=row["key"],
                direction=row["direction"] or "added",
                score=row["score"],
                pages=metadata.get("pages", []),
                diff_links=metadata.get("diff_links", []),
                snippet=metadata.get("snippet", ""),
            )
        )
    return items


def render_markdown(items: Iterable[DigestItem]) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Wikipedia Scout Digest\n\nGenerated {now}\n"]
    for item in items:
        lines.append(f"## {item.term} ({item.direction})")
        lines.append(f"Spike score: {item.score:.2f}")
        if item.pages:
            lines.append("Top pages:")
            lines.extend([f"- {page}" for page in item.pages])
        if item.diff_links:
            lines.append("Diff links:")
            lines.extend([f"- {link}" for link in item.diff_links])
        if item.snippet:
            lines.append("Snippet:")
            lines.append(f"> {item.snippet}")
        lines.append("")
    return "\n".join(lines)
