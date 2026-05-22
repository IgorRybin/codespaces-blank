import unittest
from fastapi.testclient import TestClient

from app import app


class AppImportTest(unittest.TestCase):
    def test_app_imports_and_health_check(self):
        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
