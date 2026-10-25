from database import get_database_connection
from models import Pipeline, Task


def load_pipeline_model(pipeline_id):
    connection = get_database_connection()

    try:
        pipeline_row = connection.execute(
            "SELECT id, name FROM pipelines WHERE id = ?",
            (pipeline_id,),
        ).fetchone()

        if pipeline_row is None:
            return None

        task_rows = connection.execute(
            """
            SELECT id, name, duration, status
            FROM tasks
            WHERE pipeline_id = ?
            ORDER BY id
            """,
            (pipeline_id,),
        ).fetchall()

        dependency_rows = connection.execute(
            """
            SELECT td.task_id, td.dependency_task_id
            FROM task_dependencies AS td
            JOIN tasks AS task ON task.id = td.task_id
            WHERE task.pipeline_id = ?
            ORDER BY td.task_id, td.dependency_task_id
            """,
            (pipeline_id,),
        ).fetchall()
    finally:
        connection.close()

    dependencies = {row["id"]: [] for row in task_rows}
    for row in dependency_rows:
        dependencies[row["task_id"]].append(row["dependency_task_id"])

    pipeline = Pipeline(pipeline_row["id"], pipeline_row["name"])
    for row in task_rows:
        task = Task(
            row["id"],
            row["name"],
            row["duration"],
            dependencies[row["id"]],
        )
        task.status = row["status"]
        pipeline.add_task(task)

    return pipeline


def validate_pipeline_model(pipeline):
    errors = pipeline.valid_dependencies()

    if not pipeline.tasks:
        errors.append("Add at least one task before validating the pipeline.")

    if not errors and pipeline.has_cycle():
        errors.append("Pipeline contains a dependency cycle.")

    execution_order = []
    if not errors:
        execution_order = pipeline.get_execution_order()

    return {
        "valid": not errors,
        "errors": errors,
        "execution_order": execution_order,
    }
