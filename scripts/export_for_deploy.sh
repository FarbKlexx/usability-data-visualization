#!/usr/bin/env bash
# Export the `smartmonitoring` schema for loading into a hosted
# Postgres + PostGIS database (e.g. Neon) — see DEPLOY.md.
#
# Produces a single self-contained SQL file: the PostGIS extension, the
# schema, every table (sensor_*, tbl_*, dashboard_*) with data, and the
# sequences. Geometry columns dump fine as long as PostGIS is installed
# on the target first (the file does that on its first line).
#
# Usage:
#   ./scripts/export_for_deploy.sh                 # -> deploy/smartmonitoring.sql
#   ./scripts/export_for_deploy.sh path/to/out.sql
#
# Load into the hosted DB with:
#   psql "$DATABASE_URL" -f deploy/smartmonitoring.sql
set -euo pipefail

OUT="${1:-deploy/smartmonitoring.sql}"
CONTAINER="${DB_CONTAINER:-usability-db}"
DB="smartmonitoring_airquality"

mkdir -p "$(dirname "$OUT")"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "error: container '$CONTAINER' is not running (try: docker compose up -d)" >&2
  exit 1
fi

{
  echo "-- Air-quality dashboard export for a hosted Postgres + PostGIS database."
  echo "-- Load with:  psql \"\$DATABASE_URL\" -f $(basename "$OUT")"
  echo "CREATE EXTENSION IF NOT EXISTS postgis;"
  echo
  docker exec "$CONTAINER" pg_dump -U "$DB" -d "$DB" \
    --schema=smartmonitoring \
    --no-owner --no-privileges --no-tablespaces
} > "$OUT"

echo "wrote $OUT ($(du -h "$OUT" | cut -f1))"
echo "next: psql \"\$DATABASE_URL\" -f $OUT   (DATABASE_URL = your Neon connection string)"
