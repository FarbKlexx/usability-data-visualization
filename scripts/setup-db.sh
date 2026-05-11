#!/usr/bin/env bash
#
# One-time bootstrap: copy the immutable pgsql/ source directory into
# pgdata/, which is the working copy Docker will bind-mount. pgsql/ is
# never modified; pgdata/ is gitignored and can be deleted/regenerated.
#
# Usage:   ./scripts/setup-db.sh [--force]
#
# Idempotent: refuses to overwrite an existing pgdata/ unless --force.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/pgsql"
DST="$ROOT/pgdata"

if [[ ! -d "$SRC" ]]; then
  echo "error: source data directory not found: $SRC" >&2
  exit 1
fi

if [[ -d "$DST" ]]; then
  if [[ "${1:-}" == "--force" ]]; then
    echo "removing existing $DST (--force)..."
    rm -rf "$DST"
  else
    echo "pgdata/ already exists. Pass --force to recreate it."
    exit 0
  fi
fi

echo "copying $SRC -> $DST ..."
cp -R "$SRC" "$DST"

# Remove stale Windows-era runtime files that would confuse Postgres on
# Linux: pid lock, temp socket, log file owned by the old install.
rm -f "$DST/postmaster.pid" "$DST/postmaster.opts" "$DST/logfile"

# Patch settings baked into the dump that the Linux container can't honour:
#   - dynamic_shared_memory_type = windows   -> posix (Linux default)
#   - lc_* = 'German_Germany.1252'           -> 'C' (always available)
sed -i.bak \
  -e 's/^dynamic_shared_memory_type = windows/dynamic_shared_memory_type = posix/' \
  -e "s/^lc_messages = 'German_Germany\.1252'/lc_messages = 'C'/" \
  -e "s/^lc_monetary = 'German_Germany\.1252'/lc_monetary = 'C'/" \
  -e "s/^lc_numeric = 'German_Germany\.1252'/lc_numeric = 'C'/" \
  -e "s/^lc_time = 'German_Germany\.1252'/lc_time = 'C'/" \
  "$DST/postgresql.conf"
rm -f "$DST/postgresql.conf.bak"
echo "patched postgresql.conf (dsm + locale settings)"

# Rewrite the database-level locale baked into pg_database. The dump was
# created on Windows with 'German_Germany.1252', which glibc-based images
# (incl. imresamu/postgis) refuse to open. Run postgres in single-user
# mode against an alpine image (musl libc, permissive about the legacy
# locale name) to UPDATE the system catalog before the real container
# ever tries to open these databases.
#
# Idempotent: re-running the UPDATE on already-C rows is a no-op.
if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker is required to repair the pg_database locale" >&2
  exit 1
fi
echo "repairing pg_database locale (German_Germany.1252 -> C)..."
printf "UPDATE pg_database SET datcollate='C', datctype='C';\n" | \
  docker run -i --rm \
    -v "$DST:/var/lib/postgresql/data" \
    --user postgres \
    postgres:13-alpine \
    postgres --single -D /var/lib/postgresql/data \
      -c allow_system_table_mods=on \
      template1 >/dev/null
echo "pg_database locale repaired"

# pg_hba.conf only trusts 127.0.0.1; Docker bridges traffic through a
# different IP (e.g. 192.168.65.1 on Docker Desktop). Append a wider
# trust rule so the host can reach the container DB. This is fine for
# a local-only dev container; never do this in production.
if ! grep -q 'usability-dashboard local docker rule' "$DST/pg_hba.conf"; then
  {
    echo ""
    echo "# usability-dashboard local docker rule"
    echo "host    all             all             0.0.0.0/0               trust"
    echo "host    all             all             ::/0                    trust"
  } >> "$DST/pg_hba.conf"
  echo "patched pg_hba.conf: trust from any host"
fi

echo "done. Next: docker compose up -d"
