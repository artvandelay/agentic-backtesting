import sqlite3
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from nlbt.spike_detection import (
    SpikeEvent,
    compute_hour_of_week_baseline,
    compute_political_intensity,
    compute_spike_scores,
    compute_spike_thresholds,
    compute_term_spike_scores,
    persist_spike_events,
)


def test_hour_of_week_baseline_median():
    start = datetime(2024, 1, 1)
    hours = 24 * 21
    timestamps = [start + timedelta(hours=i) for i in range(hours)]
    values = [(ts.weekday() * 24 + ts.hour) for ts in timestamps]
    df = pd.DataFrame({"timestamp": timestamps, "count": values})

    baseline = compute_hour_of_week_baseline(df, "timestamp", "count")

    assert baseline.iloc[0] == values[0]
    assert baseline.iloc[100] == values[100]
    assert baseline.iloc[-1] == values[-1]


def test_robust_z_scores_flag_spike():
    observed = np.array([10.0] * 50)
    observed[25] = 60.0
    baseline = np.array([10.0] * 50)

    scores = compute_spike_scores(observed, baseline, method="robust_z")
    spikes = compute_spike_thresholds(scores, method="robust_z", z_threshold=3.0)

    assert spikes.sum() == 1
    assert spikes[25]


def test_term_spike_log_odds_min_support():
    current = {"alpha": 20, "beta": 2}
    baseline = {"alpha": 5, "beta": 1, "gamma": 30}

    scores = compute_term_spike_scores(current, baseline, method="log_odds", min_support=3)

    assert "alpha" in scores
    assert "beta" not in scores
    assert scores["alpha"] > 0


def test_persist_spike_events(tmp_path):
    db_path = tmp_path / "spikes.db"
    event = SpikeEvent(
        event_time=datetime(2024, 1, 1, 12, 0, 0),
        entity_id="page:Example",
        score=4.2,
        direction="up",
        evidence={"baseline": 10, "observed": 25},
    )

    persist_spike_events(str(db_path), [event])

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute("SELECT entity_id, score, direction FROM spike_events")
        row = cursor.fetchone()

    assert row == ("page:Example", 4.2, "up")


def test_political_intensity_signal():
    signals = compute_political_intensity(
        categories=["Politics", "Elections"],
        wikidata_items=["Q123", "Q456"],
        revert_tags=["revert"],
        distinct_pages=5,
    )

    assert signals["score"] > 0
    assert signals["category_signal"] > 0
    assert signals["wikidata_signal"] > 0
