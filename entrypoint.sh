#!/bin/sh

# This script is the container's entrypoint.
# It first ensures the database exists on the persistent volume,
# then executes the main process.

set -e

# The seed database created during the Docker build
SEED_DB="/app/literary.db"
# The live database on the persistent volume
LIVE_DB="/data/literary.db"

# If the live database does not exist, copy the seed database to the volume.
# The `cp -n` command (no-clobber) ensures we don't overwrite an existing DB.
echo "Checking for live database at ${LIVE_DB}..."
cp -n "${SEED_DB}" "${LIVE_DB}" 2>/dev/null || true
echo "Database file is ready."

# Run any pending migrations against the live database.
# This is idempotent — Alembic checks alembic_version and only
# applies migrations that haven't been run yet.
echo "Running database migrations..."
alembic -c alembic.ini upgrade head
echo "Migrations complete."

# Instead of starting a single process, we now use honcho
# to start all processes defined in the Procfile.
echo "Starting all processes with honcho..."
exec honcho start
