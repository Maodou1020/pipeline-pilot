from collections import deque

from .task_model import Task


class Pipeline:
    def __init__(self, pipeline_id, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Pipeline name cannot be empty.")

        self.pipeline_id = pipeline_id
        self.name = name.strip()
        self.tasks = {}

    def add_task(self, task):
        if not isinstance(task, Task):
            raise TypeError("Only Task objects can be added to a pipeline.")

        if task.task_id in self.tasks:
            raise ValueError(f"Task ID {task.task_id} already exists.")

        self.tasks[task.task_id] = task

    def valid_dependencies(self):
        error = []

        for task in self.tasks.values():
            for dependency_id in task.dependencies:
                if dependency_id == task.task_id:
                    error.append(f"Task {task.task_id} cannot depend on itself.")
                elif dependency_id not in self.tasks:
                    error.append(
                        f"Task {task.task_id} depends on missing task "
                        f"{dependency_id}."
                    )

        return error

    def has_cycle(self):
        states = {
            task_id: 0
            for task_id in self.tasks
        }

        def visit(task_id):
            if states[task_id] == 1:
                return True

            if states[task_id] == 2:
                return False

            states[task_id] = 1

            for dependency_id in self.tasks[task_id].dependencies:
                if dependency_id in self.tasks:
                    if visit(dependency_id):
                        return True

            states[task_id] = 2
            return False

        for task_id in self.tasks:
            if visit(task_id):
                return True

        return False

    def get_execution_order(self):
        dependency_errors = self.valid_dependencies()

        if dependency_errors:
            raise ValueError("Pipeline contains invalid dependencies.")

        in_degree = {
            task_id: 0
            for task_id in self.tasks
        }

        dependents = {
            task_id: []
            for task_id in self.tasks
        }

        for task in self.tasks.values():
            for dependency_id in task.dependencies:
                in_degree[task.task_id] += 1
                dependents[dependency_id].append(task.task_id)

        ready_tasks = deque(
            task_id
            for task_id, degree in in_degree.items()
            if degree == 0
        )

        execution_order = []

        while ready_tasks:
            task_id = ready_tasks.popleft()
            execution_order.append(task_id)

            for dependent_id in dependents[task_id]:
                in_degree[dependent_id] -= 1

                if in_degree[dependent_id] == 0:
                    ready_tasks.append(dependent_id)

        if len(execution_order) != len(self.tasks):
            raise ValueError("Pipeline contains a dependency cycle.")

        return execution_order

    def simulate(self, worker_count):
        if (
            isinstance(worker_count, bool)
            or not isinstance(worker_count, int)
            or worker_count < 1
        ):
            raise ValueError("Worker count must be a positive integer.")

        execution_order = self.get_execution_order()

        pending = set(self.tasks)
        completed = set()
        running = []

        available_workers = list(range(1, worker_count + 1))
        current_time = 0
        schedule = []

        while pending or running:
            ready_tasks = [
                task_id
                for task_id in execution_order
                if task_id in pending
                   and all(
                    dependency_id in completed
                    for dependency_id
                    in self.tasks[task_id].dependencies
                )
            ]

            while ready_tasks and available_workers:
                task_id = ready_tasks.pop(0)
                worker_id = available_workers.pop(0)
                task = self.tasks[task_id]

                running.append({
                    "task_id": task_id,
                    "task_name": task.name,
                    "worker_id": worker_id,
                    "start_time": current_time,
                    "end_time": current_time + task.duration,
                })

                pending.remove(task_id)

            if not running:
                raise ValueError("No tasks can be scheduled.")

            next_finish_time = min(
                item["end_time"]
                for item in running
            )

            current_time = next_finish_time

            finished_tasks = [
                item
                for item in running
                if item["end_time"] == current_time
            ]

            for item in finished_tasks:
                completed.add(item["task_id"])
                available_workers.append(item["worker_id"])
                schedule.append(item)

            running = [
                item
                for item in running
                if item["end_time"] != current_time
            ]

            available_workers.sort()

        schedule.sort(
            key=lambda item: (
                item["start_time"],
                item["worker_id"],
            )
        )

        return {
            "worker_count": worker_count,
            "total_duration": current_time,
            "schedule": schedule,
        }

    def to_dict(self):
        return {
            "id": self.pipeline_id,
            "name": self.name,
            "tasks": [
                task.to_dict()
                for task in self.tasks.values()
            ],
        }
