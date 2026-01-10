"""Configuration for the Wikipedia Scout pipeline."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScoutConfig:
    """Runtime configuration for the scout services."""

    eventstreams_url: str = (
        "https://stream.wikimedia.org/v2/stream/recentchange"
    )
    compare_api_url: str = "https://en.wikipedia.org/w/api.php"
    language: str = "enwiki"
    namespaces: tuple[int, ...] = (0,)
    include_talk: bool = False
    database_path: Path = Path("wiki_scout.sqlite3")
    reconnect_delay_s: float = 3.0
    user_agent: str = "wiki-scout/0.1 (contact: ops@example.com)"
