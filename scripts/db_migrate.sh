#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL=${DATABASE_URL:?"DATABASE_URL is required"}

psql "$DATABASE_URL" -f storage/migrations/001_init.sql
