from fastapi.testclient import TestClient
from src.lab_6.main import app
import pytest

client = TestClient(app)


# ---- FAKE DB ----
class FakeCursor:
    def __init__(self, data=None):
        self.data = data or []
        self.rowcount = len(self.data)

    def execute(self, query, params=None):
        pass

    def fetchall(self):
        return self.data

    def fetchone(self):
        return self.data[0] if self.data else None


class FakeDB:
    def __init__(self, data=None):
        self.data = data

    def cursor(self, dictionary=False):
        return FakeCursor(self.data)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


# ---- FIXTURE ----
@pytest.fixture
def mock_db(monkeypatch):
    def fake_get_db():
        return FakeDB([
            {"id": 1, "name": "Test", "deadline": "2025-01-01", "Client_id": 10}
        ])

    monkeypatch.setattr("src.lab_6.main.get_db", fake_get_db)


# ---- TESTS ----
def test_get_all_tasks(mock_db):
    response = client.get("/task/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == "Test"


def test_get_task_by_id(mock_db):
    response = client.get("/task/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_task_not_found(monkeypatch):
    def empty_db():
        return FakeDB([])

    monkeypatch.setattr("src.lab_6.main.get_db", empty_db)

    response = client.get("/task/999")
    assert response.status_code == 404
