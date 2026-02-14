"""Spike detection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import median
from typing import Iterable


@dataclass(frozen=True)
class SpikeResult:
    scope: str
    key: str
    direction: str
    score: float
    support_count: int
    window_start: datetime
    window_end: datetime
    metadata: dict


def robust_z_score(current: float, baseline_samples: Iterable[float]) -> float:
    samples = list(baseline_samples)
    if not samples:
        return 0.0
    med = median(samples)
    deviations = [abs(value - med) for value in samples]
    mad = median(deviations) or 1.0
    return 0.6745 * (current - med) / mad


def ratio_spike(current: float, baseline: float) -> float:
    return (current + 1.0) / (baseline + 1.0)


def window_range(hours: int) -> tuple[datetime, datetime]:
    end = datetime.utcnow()
    start = end - timedelta(hours=hours)
    return start, end
