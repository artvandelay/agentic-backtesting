#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL=${DATABASE_URL:?"DATABASE_URL is required"}
BACKUP_PATH=${BACKUP_PATH:?"BACKUP_PATH is required"}

pg_restore --clean --if-exists --dbname "$DATABASE_URL" "$BACKUP_PATH"

echo "Restored from $BACKUP_PATH"
