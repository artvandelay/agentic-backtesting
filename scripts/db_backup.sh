#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL=${DATABASE_URL:?"DATABASE_URL is required"}
BACKUP_PATH=${BACKUP_PATH:-backup_$(date +%Y%m%d_%H%M%S).dump}

pg_dump --format=custom --file "$BACKUP_PATH" "$DATABASE_URL"

echo "Backup written to $BACKUP_PATH"
