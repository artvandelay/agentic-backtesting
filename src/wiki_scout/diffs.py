"""Utilities for fetching and parsing MediaWiki diffs."""

from __future__ import annotations

import html
import json
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Tuple

from wiki_scout.config import ScoutConfig


class DiffTextParser(HTMLParser):
    """Extract added and removed text from MediaWiki diff HTML."""

    def __init__(self) -> None:
        super().__init__()
        self._added: list[str] = []
        self._removed: list[str] = []
        self._current: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "ins":
            self._current = self._added
        elif tag == "del":
            self._current = self._removed

    def handle_endtag(self, tag: str) -> None:
        if tag in {"ins", "del"}:
            self._current = None

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current.append(data)

    def result(self) -> Tuple[str, str]:
        added = " ".join(self._added)
        removed = " ".join(self._removed)
        return html.unescape(added), html.unescape(removed)


def fetch_diff_html(
    config: ScoutConfig,
    revision_from: int,
    revision_to: int,
) -> str:
    params = {
        "action": "compare",
        "format": "json",
        "fromrev": str(revision_from),
        "torev": str(revision_to),
        "prop": "diff",
    }
    url = f"{config.compare_api_url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": config.user_agent})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("compare", {}).get("*", "")


def parse_diff_text(diff_html: str) -> Tuple[str, str]:
    parser = DiffTextParser()
    parser.feed(diff_html)
    return parser.result()
