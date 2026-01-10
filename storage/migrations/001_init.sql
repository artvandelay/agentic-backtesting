-- Initialize core tables for ingest/enrich/detect/report pipeline.

CREATE TABLE IF NOT EXISTS ingest_events (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS enriched_events (
    id BIGSERIAL PRIMARY KEY,
    ingest_event_id BIGINT REFERENCES ingest_events(id) ON DELETE CASCADE,
    payload JSONB NOT NULL,
    enriched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS detections (
    id BIGSERIAL PRIMARY KEY,
    enriched_event_id BIGINT REFERENCES enriched_events(id) ON DELETE CASCADE,
    signal VARCHAR(128) NOT NULL,
    severity VARCHAR(32) NOT NULL,
    metadata JSONB,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
    id BIGSERIAL PRIMARY KEY,
    detection_id BIGINT REFERENCES detections(id) ON DELETE SET NULL,
    report_payload JSONB NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ingest_events_ingested_at ON ingest_events(ingested_at);
CREATE INDEX IF NOT EXISTS idx_enriched_events_enriched_at ON enriched_events(enriched_at);
CREATE INDEX IF NOT EXISTS idx_detections_detected_at ON detections(detected_at);
