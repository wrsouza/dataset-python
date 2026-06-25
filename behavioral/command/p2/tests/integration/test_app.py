"""Integration tests for the Flask task queue API."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from task_command_queue.app import create_app
from task_command_queue.domain.interfaces import TaskPublisher


class FakeTaskPublisher(TaskPublisher):
    def __init__(self) -> None:
        self.published: list[tuple[str, dict[str, object]]] = []

    def publish(self, command_name: str, payload: dict[str, object]) -> None:
        self.published.append((command_name, payload))


@pytest.fixture
def client() -> FlaskClient:
    app = create_app(publisher=FakeTaskPublisher())
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_enqueue_send_email_task(client: FlaskClient) -> None:
    response = client.post(
        "/tasks",
        json={
            "command": "send_email",
            "payload": {"to": "a@b.com", "subject": "Hi", "body": "Hello"},
        },
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["status"] == "completed"
    assert body["command_name"] == "send_email"


def test_enqueue_unknown_command_returns_400(client: FlaskClient) -> None:
    response = client.post("/tasks", json={"command": "nope", "payload": {}})

    assert response.status_code == 400


def test_get_task_after_enqueue(client: FlaskClient) -> None:
    enqueue_response = client.post(
        "/tasks",
        json={
            "command": "generate_report",
            "payload": {"report_type": "sales", "parameters": {}},
        },
    )
    task_id = enqueue_response.get_json()["task_id"]

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 200
    assert get_response.get_json()["task_id"] == task_id


def test_get_unknown_task_returns_404(client: FlaskClient) -> None:
    response = client.get("/tasks/does-not-exist")

    assert response.status_code == 404
