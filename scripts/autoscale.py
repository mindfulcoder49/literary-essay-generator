import os
import sqlite3
import subprocess

DB_PATH = "/data/literary.db"
APP_NAME = "literary-essays"
WORKER_PROCESS_GROUP = "worker"


def get_fly_machines(app_name: str, group: str) -> list:
    """Get the list of machines for a given process group."""
    result = subprocess.run(
        ["fly", "machines", "list", "--app", app_name, "--json"],
        capture_output=True,
        text=True,
    )
    result.check_returncode()
    import json
    machines = json.loads(result.stdout)
    return [m for m in machines if m.get("process_group") == group]


def get_queued_jobs_count(db_path: str) -> int:
    """Check the number of jobs with status 'queued'."""
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return 0
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'queued'")
            count = cursor.fetchone()[0]
            return count
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0


def scale_workers(app_name: str, group: str, desired_count: int):
    """Scale the number of worker machines."""
    print(f"Scaling worker group '{group}' to {desired_count} machines...")
    subprocess.run(
        ["fly", "scale", "count", str(desired_count), "--app", app_name, "--process-group", group],
        check=True,
    )


def main():
    print("Running autoscaler...")
    worker_machines = get_fly_machines(APP_NAME, WORKER_PROCESS_GROUP)
    current_worker_count = len(worker_machines)
    print(f"Current worker count: {current_worker_count}")

    queued_jobs = get_queued_jobs_count(DB_PATH)
    print(f"Queued jobs: {queued_jobs}")

    desired_worker_count = 1 if queued_jobs > 0 else 0

    if current_worker_count == desired_worker_count:
        print("Worker count is already correct. No action needed.")
    else:
        scale_workers(APP_NAME, WORKER_PROCESS_GROUP, desired_worker_count)
        print("Scaling action completed.")


if __name__ == "__main__":
    main()
