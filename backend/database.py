import os
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(
    os.environ.get(
        "PIPELINE_PILOT_DB_PATH",
        Path(__file__).parent / "pipeline_pilot.db",
    )
)


def get_database_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    connection = get_database_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS pipelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pipeline_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                duration INTEGER NOT NULL CHECK (duration > 0),
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pipeline_id)
                    REFERENCES pipelines (id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS task_dependencies (
                task_id INTEGER NOT NULL,
                dependency_task_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, dependency_task_id),
                FOREIGN KEY (task_id)
                    REFERENCES tasks (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (dependency_task_id)
                    REFERENCES tasks (id)
                    ON DELETE CASCADE,
                CHECK (task_id != dependency_task_id)
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_pipeline_id
                ON tasks (pipeline_id);

            CREATE INDEX IF NOT EXISTS idx_dependencies_dependency_id
                ON task_dependencies (dependency_task_id);
            """
        )

        _add_timestamp_columns(connection, "pipelines")
        _add_timestamp_columns(connection, "tasks")

        connection.execute(
            """
            UPDATE pipelines
            SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
                updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
            """
        )
        connection.execute(
            """
            UPDATE tasks
            SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
                updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
            """
        )

        connection.commit()
    finally:
        connection.close()


def _add_timestamp_columns(connection, table_name):
    columns = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table_name})")
    }

    if "created_at" not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN created_at TEXT")

    if "updated_at" not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN updated_at TEXT")


if __name__ == "__main__":
    initialize_database()
    print(f"Database created at: {DATABASE_PATH}")
