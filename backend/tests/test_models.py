import unittest

from models import Pipeline, Task


class PipelineModelTests(unittest.TestCase):
    def test_execution_order_and_parallel_simulation(self):
        pipeline = Pipeline(1, "Release")
        pipeline.add_task(Task(1, "Install", 2))
        pipeline.add_task(Task(2, "Test", 4, [1]))
        pipeline.add_task(Task(3, "Build", 3, [1]))
        pipeline.add_task(Task(4, "Deploy", 5, [2, 3]))

        self.assertEqual(pipeline.valid_dependencies(), [])
        self.assertFalse(pipeline.has_cycle())
        self.assertEqual(pipeline.get_execution_order()[0], 1)

        result = pipeline.simulate(2)
        self.assertEqual(result["total_duration"], 11)
        self.assertEqual(len(result["schedule"]), 4)

    def test_missing_dependency_is_rejected(self):
        pipeline = Pipeline(1, "Invalid")
        pipeline.add_task(Task(1, "Deploy", 1, [99]))

        self.assertTrue(pipeline.valid_dependencies())
        with self.assertRaises(ValueError):
            pipeline.get_execution_order()

    def test_cycle_is_detected(self):
        pipeline = Pipeline(1, "Cycle")
        pipeline.add_task(Task(1, "A", 1, [2]))
        pipeline.add_task(Task(2, "B", 1, [1]))

        self.assertTrue(pipeline.has_cycle())
        with self.assertRaises(ValueError):
            pipeline.get_execution_order()

    def test_task_rejects_invalid_duration(self):
        for value in (0, -1, 1.5, True, "2"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Task(1, "Task", value)

    def test_simulation_rejects_boolean_worker_count(self):
        pipeline = Pipeline(1, "Invalid workers")
        pipeline.add_task(Task(1, "Build", 1))

        with self.assertRaises(ValueError):
            pipeline.simulate(True)


if __name__ == "__main__":
    unittest.main()
