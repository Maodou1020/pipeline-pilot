import tempfile
import unittest
from pathlib import Path

import database


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_directory = tempfile.TemporaryDirectory()
        database.DATABASE_PATH = Path(cls.temporary_directory.name) / "test.db"

        from app import create_app

        cls.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
        })

    @classmethod
    def tearDownClass(cls):
        cls.temporary_directory.cleanup()

    def setUp(self):
        connection = database.get_database_connection()
        try:
            connection.execute("DELETE FROM pipelines")
            connection.commit()
        finally:
            connection.close()

        self.client = self.app.test_client()

    def login(self):
        return self.client.post(
            "/api/auth/login",
            json={"username": "Chris", "password": "123"},
        )

    def create_pipeline(self, name="Release"):
        response = self.client.post("/api/pipelines", json={"name": name})
        self.assertEqual(response.status_code, 201)
        return response.get_json()["id"]

    def create_task(self, pipeline_id, name, duration, dependencies=None):
        response = self.client.post(
            f"/api/pipelines/{pipeline_id}/tasks",
            json={
                "name": name,
                "duration": duration,
                "dependencies": dependencies or [],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        return response.get_json()["id"]

    def test_protected_routes_require_login(self):
        response = self.client.get("/api/pipelines")
        self.assertEqual(response.status_code, 401)

    def test_invalid_login_is_rejected(self):
        response = self.client.post(
            "/api/auth/login",
            json={"username": "Chris", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 401)

    def test_complete_pipeline_workflow(self):
        self.assertEqual(self.login().status_code, 200)
        pipeline_id = self.create_pipeline()
        install_id = self.create_task(pipeline_id, "Install", 2)
        test_id = self.create_task(pipeline_id, "Test", 4, [install_id])

        update = self.client.patch(
            f"/api/tasks/{test_id}",
            json={
                "name": "Test suite",
                "duration": 5,
                "dependencies": [install_id],
            },
        )
        self.assertEqual(update.status_code, 200)

        detail = self.client.get(f"/api/pipelines/{pipeline_id}").get_json()
        self.assertEqual(len(detail["tasks"]), 2)

        validation = self.client.post(
            f"/api/pipelines/{pipeline_id}/validate"
        ).get_json()
        self.assertTrue(validation["valid"])

        simulation = self.client.post(
            f"/api/pipelines/{pipeline_id}/simulate",
            json={"worker_count": 2},
        ).get_json()
        self.assertEqual(simulation["total_duration"], 7)

        blocked = self.client.delete(f"/api/tasks/{install_id}")
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(blocked.get_json()["dependents"], ["Test suite"])

        self.assertEqual(self.client.delete(f"/api/tasks/{test_id}").status_code, 204)
        self.assertEqual(self.client.delete(f"/api/tasks/{install_id}").status_code, 204)
        self.assertEqual(self.client.delete(f"/api/pipelines/{pipeline_id}").status_code, 204)

    def test_cross_pipeline_dependency_is_rejected(self):
        self.login()
        first_pipeline = self.create_pipeline("First")
        second_pipeline = self.create_pipeline("Second")
        other_task = self.create_task(first_pipeline, "Other", 1)

        response = self.client.post(
            f"/api/pipelines/{second_pipeline}/tasks",
            json={
                "name": "Invalid",
                "duration": 1,
                "dependencies": [other_task],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_pipeline_validation_explains_failure(self):
        self.login()
        pipeline_id = self.create_pipeline()
        response = self.client.post(f"/api/pipelines/{pipeline_id}/validate")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["valid"])
        self.assertTrue(response.get_json()["errors"])


if __name__ == "__main__":
    unittest.main()
