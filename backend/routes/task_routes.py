from flask import Blueprint, jsonify, request

from auth import login_required
from database import get_database_connection


task_blueprint = Blueprint("tasks", __name__, url_prefix="/api")


def _validate_task_input(data):
    name = data.get("name")
    duration = data.get("duration")
    dependencies = data.get("dependencies", [])

    if not isinstance(name, str) or not name.strip():
        return None, "Task name cannot be empty."
    if isinstance(duration, bool) or not isinstance(duration, int) or duration < 1:
        return None, "Task duration must be a positive integer."
    if not isinstance(dependencies, list):
        return None, "Dependencies must be a list."
    if any(
        isinstance(item, bool) or not isinstance(item, int)
        for item in dependencies
    ):
        return None, "Every dependency ID must be an integer."
    if len(dependencies) != len(set(dependencies)):
        return None, "Dependencies cannot contain duplicate IDs."

    return {
        "name": name.strip(),
        "duration": duration,
        "dependencies": dependencies,
    }, None


def _find_invalid_dependencies(connection, pipeline_id, dependencies, task_id=None):
    if task_id is not None and task_id in dependencies:
        return [task_id]
    if not dependencies:
        return []

    placeholders = ", ".join("?" for _ in dependencies)
    rows = connection.execute(
        f"""
        SELECT id
        FROM tasks
        WHERE pipeline_id = ? AND id IN ({placeholders})
        """,
        (pipeline_id, *dependencies),
    ).fetchall()
    valid_ids = {row["id"] for row in rows}
    return [item for item in dependencies if item not in valid_ids]


def _replace_dependencies(connection, task_id, dependencies):
    connection.execute(
        "DELETE FROM task_dependencies WHERE task_id = ?",
        (task_id,),
    )
    connection.executemany(
        """
        INSERT INTO task_dependencies (task_id, dependency_task_id)
        VALUES (?, ?)
        """,
        [(task_id, dependency_id) for dependency_id in dependencies],
    )


@task_blueprint.post("/pipelines/<int:pipeline_id>/tasks")
@login_required
def create_task(pipeline_id):
    values, error = _validate_task_input(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    connection = get_database_connection()
    try:
        pipeline = connection.execute(
            "SELECT id FROM pipelines WHERE id = ?",
            (pipeline_id,),
        ).fetchone()
        if pipeline is None:
            return jsonify({"error": "Pipeline not found."}), 404

        invalid = _find_invalid_dependencies(
            connection,
            pipeline_id,
            values["dependencies"],
        )
        if invalid:
            return jsonify({
                "error": "Every dependency must belong to this pipeline."
            }), 400

        cursor = connection.execute(
            """
            INSERT INTO tasks (pipeline_id, name, duration, status)
            VALUES (?, ?, ?, 'PENDING')
            """,
            (pipeline_id, values["name"], values["duration"]),
        )
        task_id = cursor.lastrowid
        _replace_dependencies(connection, task_id, values["dependencies"])
        connection.execute(
            "UPDATE pipelines SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (pipeline_id,),
        )
        connection.commit()
    finally:
        connection.close()

    return jsonify({
        "id": task_id,
        "name": values["name"],
        "duration": values["duration"],
        "status": "PENDING",
        "dependencies": values["dependencies"],
    }), 201


@task_blueprint.patch("/tasks/<int:task_id>")
@login_required
def update_task(task_id):
    values, error = _validate_task_input(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    connection = get_database_connection()
    try:
        task = connection.execute(
            "SELECT id, pipeline_id FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if task is None:
            return jsonify({"error": "Task not found."}), 404

        invalid = _find_invalid_dependencies(
            connection,
            task["pipeline_id"],
            values["dependencies"],
            task_id,
        )
        if invalid:
            return jsonify({
                "error": "A task cannot depend on itself or another pipeline."
            }), 400

        connection.execute(
            """
            UPDATE tasks
            SET name = ?, duration = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (values["name"], values["duration"], task_id),
        )
        _replace_dependencies(connection, task_id, values["dependencies"])
        connection.execute(
            "UPDATE pipelines SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task["pipeline_id"],),
        )
        connection.commit()
    finally:
        connection.close()

    return jsonify({
        "id": task_id,
        "name": values["name"],
        "duration": values["duration"],
        "status": "PENDING",
        "dependencies": values["dependencies"],
    })


@task_blueprint.delete("/tasks/<int:task_id>")
@login_required
def delete_task(task_id):
    connection = get_database_connection()
    try:
        task = connection.execute(
            "SELECT id, pipeline_id FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if task is None:
            return jsonify({"error": "Task not found."}), 404

        dependent_rows = connection.execute(
            """
            SELECT tasks.name
            FROM task_dependencies
            JOIN tasks ON tasks.id = task_dependencies.task_id
            WHERE task_dependencies.dependency_task_id = ?
            ORDER BY tasks.name
            """,
            (task_id,),
        ).fetchall()
        if dependent_rows:
            return jsonify({
                "error": "Remove this task from dependent tasks before deleting it.",
                "dependents": [row["name"] for row in dependent_rows],
            }), 409

        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.execute(
            "UPDATE pipelines SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task["pipeline_id"],),
        )
        connection.commit()
    finally:
        connection.close()

    return "", 204
