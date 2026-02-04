import os
import subprocess

# This script is run during the Docker build process.
# It creates a fresh, migrated SQLite database in the container image.
# This "seed" database will then be copied to the persistent volume
# on the first run of the application.

DB_FILE = "literary.db"
ALEMBIC_INI = "alembic.ini"

print("Creating seed database...")

# Ensure we're starting fresh if the file somehow exists
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Set the DATABASE_URL to point to the local file for this script's execution context
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE}"

# Run alembic migrations to create the schema
try:
    subprocess.run(
        ["alembic", "-c", ALEMBIC_INI, "upgrade", "head"],
        check=True,
        capture_output=True,
        text=True,
    )
    print(f"Successfully created and migrated seed database at '{DB_FILE}'")
except subprocess.CalledProcessError as e:
    print("Error running Alembic migrations:")
    print(e.stdout)
    print(e.stderr)
    exit(1)

if not os.path.exists(DB_FILE):
    print(f"Error: Database file '{DB_FILE}' was not created.")
    exit(1)

print("Seed database creation complete.")
