"""Natural Language Backtesting - Reflection Pattern."""

from .spike_reports import (
    DedupeConfig,
    PageEvidence,
    SpikeEvent,
    build_digest,
    run_scheduled_spike_digest,
    select_top_spike_events,
)

__version__ = "0.2.0"

__all__ = [
    "DedupeConfig",
    "PageEvidence",
    "SpikeEvent",
    "build_digest",
    "run_scheduled_spike_digest",
    "select_top_spike_events",
]
