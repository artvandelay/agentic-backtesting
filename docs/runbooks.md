# Runbooks

## Service restart

**When to use**: deployment rollouts, config changes, or a stuck worker.

1. Confirm readiness endpoints return healthy:
   - `GET /healthz` and `GET /readyz`.
2. Drain traffic (remove instance from load balancer).
3. Restart the container:
   - `docker restart <container>`
4. Validate metrics are flowing:
   - `GET /metrics` returns `nlbt_requests_total`.
5. Re-add instance to the load balancer.

## Data backfill

**When to use**: missed ingest window, replay upstream data, or reprocessing.

1. Ensure storage is available and migrations are current:
   - `scripts/db_migrate.sh`
2. Temporarily raise retention window if needed (see configuration doc).
3. Run the backfill job by calling ingest with a backfill flag (or replay from storage):
   - `POST /ingest` with `{"mode": "backfill", "range": "<start>/<end>"}`
4. Monitor enrich/detect/report pipelines:
   - Check logs for `enrich_received`, `detect_received`, `report_received`.
5. Once complete, reset retention overrides and verify downstream counts.

## Backup/restore

**Backup**

```bash
DATABASE_URL=postgres://... BACKUP_PATH=backup.dump scripts/db_backup.sh
```

**Restore**

```bash
DATABASE_URL=postgres://... BACKUP_PATH=backup.dump scripts/db_restore.sh
```
