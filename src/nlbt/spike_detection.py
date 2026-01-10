"""Spike detection utilities for page edit and term activity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SpikeEvent:
    event_time: datetime
    entity_id: str
    score: float
    direction: str
    evidence: Dict[str, object]

    def to_db_row(self) -> Tuple[str, str, float, str, str, str]:
        return (
            self.event_time.isoformat(),
            self.entity_id,
            float(self.score),
            self.direction,
            json.dumps(self.evidence, sort_keys=True),
            datetime.utcnow().isoformat(),
        )


def compute_hour_of_week_baseline(
    df: pd.DataFrame,
    timestamp_col: str,
    value_col: str,
    min_days: int = 14,
    max_days: int = 30,
) -> pd.Series:
    """Compute hour-of-week median baseline using a trailing window."""
    if df.empty:
        raise ValueError("No data provided for baseline computation.")

    timestamps = pd.to_datetime(df[timestamp_col], utc=True)
    end_time = timestamps.max().floor("H")
    window_start = end_time - pd.Timedelta(days=max_days)
    window_df = df.loc[timestamps >= window_start].copy()

    if window_df.empty:
        raise ValueError("Not enough data in the trailing window for baseline computation.")

    window_span = (
        pd.to_datetime(window_df[timestamp_col], utc=True).max()
        - pd.to_datetime(window_df[timestamp_col], utc=True).min()
    ).days + 1
    if window_span < min_days:
        raise ValueError("Insufficient days of data for baseline computation.")

    window_df["hour_of_week"] = pd.to_datetime(window_df[timestamp_col], utc=True).dt.dayofweek * 24
    window_df["hour_of_week"] += pd.to_datetime(window_df[timestamp_col], utc=True).dt.hour
    medians = window_df.groupby("hour_of_week")[value_col].median()

    df_hours = pd.to_datetime(df[timestamp_col], utc=True).dt.dayofweek * 24
    df_hours += pd.to_datetime(df[timestamp_col], utc=True).dt.hour
    baseline = df_hours.map(medians)

    if baseline.isna().any():
        baseline = baseline.fillna(medians.median())

    return baseline


def compute_spike_scores(
    observed: Sequence[float],
    baseline: Sequence[float],
    method: str = "robust_z",
    span: int = 24,
) -> np.ndarray:
    """Compute spike scores using robust z-score or EWMA deviation."""
    observed_arr = np.asarray(observed, dtype=float)
    baseline_arr = np.asarray(baseline, dtype=float)
    residuals = observed_arr - baseline_arr

    if method == "robust_z":
        median = np.median(residuals)
        mad = np.median(np.abs(residuals - median))
        scale = 1.4826 * mad if mad > 0 else np.std(residuals)
        if scale == 0:
            scale = 1.0
        return (residuals - median) / scale

    if method == "ewma":
        residual_series = pd.Series(residuals)
        ewma_mean = residual_series.ewm(span=span, adjust=False).mean()
        ewma_std = residual_series.ewm(span=span, adjust=False).std(bias=False).replace(0, 1.0)
        return (residual_series - ewma_mean).to_numpy() / ewma_std.to_numpy()

    raise ValueError(f"Unknown spike score method: {method}")


def compute_spike_thresholds(
    scores: Sequence[float],
    method: str = "robust_z",
    z_threshold: float = 3.5,
    ewma_threshold: float = 3.0,
) -> np.ndarray:
    """Return boolean spike flags using configured thresholds."""
    scores_arr = np.asarray(scores, dtype=float)
    threshold = z_threshold if method == "robust_z" else ewma_threshold
    return np.abs(scores_arr) >= threshold


def compute_term_spike_scores(
    current_counts: Dict[str, int],
    baseline_counts: Dict[str, int],
    method: str = "log_odds",
    prior: float = 0.5,
    min_support: int = 5,
) -> Dict[str, float]:
    """Compute term spike scores via log-odds or ratio vs baseline."""
    vocab = set(current_counts) | set(baseline_counts)
    total_current = sum(current_counts.values())
    total_baseline = sum(baseline_counts.values())
    vocab_size = max(len(vocab), 1)
    scores: Dict[str, float] = {}

    for term in vocab:
        current = current_counts.get(term, 0)
        baseline = baseline_counts.get(term, 0)
        if current + baseline < min_support:
            continue

        current_prob = (current + prior) / (total_current + prior * vocab_size)
        baseline_prob = (baseline + prior) / (total_baseline + prior * vocab_size)

        if method == "log_odds":
            scores[term] = np.log(current_prob / (1 - current_prob)) - np.log(
                baseline_prob / (1 - baseline_prob)
            )
        elif method == "ratio":
            scores[term] = np.log(current_prob / baseline_prob)
        else:
            raise ValueError(f"Unknown term spike method: {method}")

    return scores


def compute_political_intensity(
    categories: Optional[Iterable[str]] = None,
    wikidata_items: Optional[Iterable[str]] = None,
    revert_tags: Optional[Iterable[str]] = None,
    distinct_pages: int = 0,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Compute political-intensity score using metadata signals."""
    categories = list(categories or [])
    wikidata_items = list(wikidata_items or [])
    revert_tags = list(revert_tags or [])
    weights = weights or {
        "categories": 0.35,
        "wikidata": 0.35,
        "reverts": 0.2,
        "distinct_pages": 0.1,
    }

    category_signal = np.log1p(len(categories))
    wikidata_signal = np.log1p(len(wikidata_items))
    revert_signal = np.log1p(len(revert_tags))
    distinct_pages_signal = np.log1p(distinct_pages)

    score = (
        weights.get("categories", 0) * category_signal
        + weights.get("wikidata", 0) * wikidata_signal
        + weights.get("reverts", 0) * revert_signal
        + weights.get("distinct_pages", 0) * distinct_pages_signal
    )

    return {
        "score": float(score),
        "category_signal": float(category_signal),
        "wikidata_signal": float(wikidata_signal),
        "revert_signal": float(revert_signal),
        "distinct_pages_signal": float(distinct_pages_signal),
    }


def persist_spike_events(db_path: str, events: Sequence[SpikeEvent]) -> None:
    """Persist spike events to the spike_events table."""
    if not events:
        return

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS spike_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_time TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                score REAL NOT NULL,
                direction TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        rows = [event.to_db_row() for event in events]
        connection.executemany(
            """
            INSERT INTO spike_events (
                event_time,
                entity_id,
                score,
                direction,
                evidence_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
