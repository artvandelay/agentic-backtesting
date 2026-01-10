"""Wikipedia Scout pipeline components."""

from wiki_scout.config import ScoutConfig
from wiki_scout.ingest import consume_recentchange
from wiki_scout.report import build_digest

__all__ = ["ScoutConfig", "consume_recentchange", "build_digest"]
