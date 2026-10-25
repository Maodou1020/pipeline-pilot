class Task:
    def __init__(self, task_id, name, duration, dependencies=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Task name cannot be empty.")

        if isinstance(duration, bool) or not isinstance(duration, int) or duration < 1:
            raise ValueError("Task duration must be a positive integer.")

        self.task_id = task_id
        self.name = name.strip()
        self.duration = duration
        # Copy the list so external changes cannot mutate this task's dependencies.
        self.dependencies = list(dependencies) if dependencies else []
        self.status = "PENDING"

    def to_dict(self):
        return {
            "id": self.task_id,
            "name": self.name,
            "duration": self.duration,
            "dependencies": self.dependencies,
            "status": self.status,
        }
