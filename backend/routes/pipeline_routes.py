from flask import Blueprint, jsonify, request

from auth import login_required
from database import get_database_connection
from services.pipeline_service import load_pipeline_model, validate_pipeline_model


pipeline_blueprint = Blueprint("pipelines", __name__, url_prefix="/api/pipelines")


@pipeline_blueprint.get("")
@login_required
def get_pipelines():
    connection = get_database_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                pipelines.id,
                pipelines.name,
                pipelines.created_at,
                pipelines.updated_at,
                COUNT(tasks.id) AS task_count
            FROM pipelines
            LEFT JOIN tasks ON tasks.pipeline_id = pipelines.id
            GROUP BY pipelines.id
            ORDER BY pipelines.updated_at DESC, pipelines.id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return jsonify([
        {
            "id": row["id"],
            "name": row["name"],
            "task_count": row["task_count"],
            "status": "CONFIGURED" if row["task_count"] else "DRAFT",
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ])


@pipeline_blueprint.post("")
@login_required
def create_pipeline():
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Pipeline name cannot be empty."}), 400

    connection = get_database_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO pipelines (name) VALUES (?)",
            (name.strip(),),
        )
        connection.commit()
        pipeline_id = cursor.lastrowid
        row = connection.execute(
            "SELECT created_at, updated_at FROM pipelines WHERE id = ?",
            (pipeline_id,),
        ).fetchone()
    finally:
        connection.close()

    return jsonify({
        "id": pipeline_id,
        "name": name.strip(),
        "tasks": [],
        "status": "DRAFT",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }), 201


@pipeline_blueprint.get("/<int:pipeline_id>")
@login_required
def get_pipeline(pipeline_id):
    pipeline = load_pipeline_model(pipeline_id)
    if pipeline is None:
        return jsonify({"error": "Pipeline not found."}), 404

    connection = get_database_connection()
    try:
        row = connection.execute(
            """
            SELECT created_at, updated_at
            FROM pipelines
            WHERE id = ?
            """,
            (pipeline_id,),
        ).fetchone()
    finally:
        connection.close()

    data = pipeline.to_dict()
    data["created_at"] = row["created_at"]
    data["updated_at"] = row["updated_at"]
    return jsonify(data)


@pipeline_blueprint.patch("/<int:pipeline_id>")
@login_required
def update_pipeline(pipeline_id):
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Pipeline name cannot be empty."}), 400

    connection = get_database_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE pipelines
            SET name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (name.strip(), pipeline_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Pipeline not found."}), 404
        connection.commit()
    finally:
        connection.close()

    return jsonify({"id": pipeline_id, "name": name.strip()})


@pipeline_blueprint.delete("/<int:pipeline_id>")
@login_required
def delete_pipeline(pipeline_id):
    connection = get_database_connection()
    try:
        cursor = connection.execute(
            "DELETE FROM pipelines WHERE id = ?",
            (pipeline_id,),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Pipeline not found."}), 404
        connection.commit()
    finally:
        connection.close()

    return "", 204


@pipeline_blueprint.post("/<int:pipeline_id>/validate")
@login_required
def validate_pipeline(pipeline_id):
    pipeline = load_pipeline_model(pipeline_id)
    if pipeline is None:
        return jsonify({"error": "Pipeline not found."}), 404

    result = validate_pipeline_model(pipeline)
    result["execution_order"] = [
        pipeline.tasks[task_id].to_dict()
        for task_id in result["execution_order"]
    ]
    return jsonify(result)


@pipeline_blueprint.post("/<int:pipeline_id>/simulate")
@login_required
def simulate_pipeline(pipeline_id):
    data = request.get_json(silent=True) or {}
    worker_count = data.get("worker_count")

    if (
        isinstance(worker_count, bool)
        or not isinstance(worker_count, int)
        or worker_count < 1
        or worker_count > 20
    ):
        return jsonify({
            "error": "Worker count must be an integer between 1 and 20."
        }), 400

    pipeline = load_pipeline_model(pipeline_id)
    if pipeline is None:
        return jsonify({"error": "Pipeline not found."}), 404

    validation = validate_pipeline_model(pipeline)
    if not validation["valid"]:
        return jsonify({
            "error": "Pipeline must be valid before simulation.",
            "validation": validation,
        }), 400

    return jsonify(pipeline.simulate(worker_count))
