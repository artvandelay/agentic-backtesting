"""Parse MediaWiki HTML diffs into structured diff fragments."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import List, Optional


@dataclass
class DiffFragment:
    added_text: str
    removed_text: str
    context: str


class _DiffHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._rows: List[List[dict]] = []
        self._current_row: List[dict] = []
        self._current_cell: Optional[dict] = None
        self._cell_text_parts: List[str] = []

    @property
    def rows(self) -> List[List[dict]]:
        return self._rows

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attrs_dict = dict(attrs)
        if tag == "tr":
            self._current_row = []
        elif tag == "td":
            classes = attrs_dict.get("class", "")
            self._current_cell = {"class": classes, "text": ""}
            self._cell_text_parts = []
        elif tag in {"ins", "del", "span"}:
            # Preserve inline changes text; we treat them as normal text nodes.
            pass

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._current_cell is not None:
            text = "".join(self._cell_text_parts)
            self._current_cell["text"] = " ".join(text.split())
            self._current_row.append(self._current_cell)
            self._current_cell = None
            self._cell_text_parts = []
        elif tag == "tr":
            if self._current_row:
                self._rows.append(self._current_row)
            self._current_row = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._cell_text_parts.append(data)


def parse_diff_html(html: str) -> List[DiffFragment]:
    """Parse MediaWiki diff HTML and return structured diff fragments.

    The parser extracts added and removed text spans and associates them with
    the most recent context line when available.
    """
    parser = _DiffHTMLParser()
    parser.feed(html)

    fragments: List[DiffFragment] = []
    last_context = ""

    for row in parser.rows:
        context_in_row = None
        added_text = ""
        removed_text = ""

        for cell in row:
            classes = cell.get("class", "")
            text = cell.get("text", "")
            if "diff-context" in classes and text:
                context_in_row = text
            if "diff-addedline" in classes:
                added_text = text
            if "diff-deletedline" in classes:
                removed_text = text

        if context_in_row is not None:
            last_context = context_in_row

        if added_text or removed_text:
            fragments.append(
                DiffFragment(
                    added_text=added_text,
                    removed_text=removed_text,
                    context=last_context,
                )
            )

    return fragments
