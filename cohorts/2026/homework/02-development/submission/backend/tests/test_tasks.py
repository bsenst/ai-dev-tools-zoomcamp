from fastapi.testclient import TestClient

from app.main import create_app


def test_task_lifecycle_and_persistence(tmp_path):
    database = f"sqlite:///{tmp_path / 'test.db'}"
    client = TestClient(create_app(database))

    assert client.get("/api/tasks").json() == []
    created = client.post("/api/tasks", json={"title": "Write the demo", "priority": "high"})
    assert created.status_code == 201
    task = created.json()
    assert task["status"] == "todo"
    assert task["description"] == ""

    updated = client.patch(f"/api/tasks/{task['id']}", json={"status": "done"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    reloaded = TestClient(create_app(database))
    assert reloaded.get("/api/tasks").json()[0]["status"] == "done"
    assert reloaded.delete(f"/api/tasks/{task['id']}").status_code == 204
    assert reloaded.get("/api/tasks").json() == []


def test_task_validation_and_missing_task(tmp_path):
    client = TestClient(create_app(f"sqlite:///{tmp_path / 'validation.db'}"))

    assert client.post("/api/tasks", json={"title": "   "}).status_code == 422
    assert client.post("/api/tasks", json={"title": "x", "priority": "urgent"}).status_code == 422
    assert client.patch("/api/tasks/404", json={"status": "done"}).status_code == 404
    assert client.delete("/api/tasks/404").status_code == 404