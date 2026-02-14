# Configuration

## Service endpoints

| Service | Endpoint | Description |
| --- | --- | --- |
| Ingest | `POST /ingest` | Pull recent changes from Wikimedia and normalize payloads. |
| Enrich | `POST /enrich` | Add metadata to ingest payloads. |
| Detect | `POST /detect` | Evaluate enriched data for signals. |
| Report | `POST /report` | Generate report records. |
| Metrics | `GET /metrics` | Prometheus metrics for each service. |
| Health | `GET /healthz` | Liveness probe. |
| Ready | `GET /readyz` | Readiness probe. |

## Environment variables

### Shared

- `LOG_LEVEL` (default: `INFO`)
- `DATABASE_URL` (required for migrations/backups)
- `RETENTION_DAYS` (default: `30`)

### Wikimedia API guards (ingest service)

- `WIKIMEDIA_BASE_URL` (default: `https://en.wikipedia.org`)
- `WIKIMEDIA_RATE_LIMIT` (default: `60`) — max requests per window.
- `WIKIMEDIA_RATE_WINDOW` (default: `60`) — seconds per window.
- `WIKIMEDIA_FAILURE_THRESHOLD` (default: `5`) — failures before circuit opens.
- `WIKIMEDIA_RECOVERY_SECONDS` (default: `30`) — cooldown before retry.

## Retention windows

- Ingest/enrich/detect/report records should be retained for `RETENTION_DAYS`.
- Recommended defaults:
  - `30` days for ingest/enrich/detect.
  - `90` days for reports.

## Thresholds

- Circuit breaker opens after `WIKIMEDIA_FAILURE_THRESHOLD` failures.
- Rate limiter defaults to `60` requests per minute.
