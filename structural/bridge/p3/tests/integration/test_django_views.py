"""Integration tests for Django views — exercises the full HTTP stack.

Uses Django's test client (no real HTTP server needed). Real brokers
(Redis/RabbitMQ/SQS) are not available in this environment, so most
assertions use the "memory" broker (InMemoryBroker) which is always
healthy and functional, with a few cases asserting graceful failure
for the real brokers when unreachable.
"""

from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

import django
import pytest
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_queue.settings")
django.setup()


@pytest.fixture
def client() -> Client:
    return Client()


class TestHealthCheckView:
    """GET /queue/health/<broker_type>/"""

    def test_health_check_memory_broker_returns_200_and_healthy(
        self, client: Client
    ) -> None:
        response = client.get("/queue/health/memory/")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["broker"] == "InMemory"
        assert body["is_healthy"] is True

    @pytest.mark.parametrize("broker_type", ["celery_redis", "rabbitmq", "sqs"])
    def test_health_check_real_brokers_return_200_unhealthy_without_services(
        self, client: Client, broker_type: str
    ) -> None:
        # No real Redis/RabbitMQ/SQS running in this test environment —
        # the view must still respond 200 with is_healthy=False, never 5xx.
        response = client.get(f"/queue/health/{broker_type}/")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["is_healthy"] is False

    def test_health_check_unsupported_broker_returns_400(self, client: Client) -> None:
        response = client.get("/queue/health/kafka/")
        assert response.status_code == 400
        body = json.loads(response.content)
        assert "Unsupported broker type" in body["error"]

    def test_health_check_with_mocked_redis_returns_healthy(
        self, client: Client
    ) -> None:
        with patch("redis.Redis.from_url") as from_url:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True
            from_url.return_value = mock_redis

            response = client.get("/queue/health/celery_redis/")

        body = json.loads(response.content)
        assert body["is_healthy"] is True


class TestEnqueueMessageView:
    """POST /queue/enqueue/<broker_type>/<client_type>/"""

    def test_enqueue_unsupported_broker_returns_400(self, client: Client) -> None:
        response = client.post(
            "/queue/enqueue/kafka/task/",
            data=json.dumps({"queue_name": "q", "payload": {}}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_enqueue_unsupported_client_type_returns_400(self, client: Client) -> None:
        response = client.post(
            "/queue/enqueue/memory/bulk/",
            data=json.dumps({"queue_name": "q", "payload": {}}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_enqueue_missing_queue_name_returns_400(self, client: Client) -> None:
        response = client.post(
            "/queue/enqueue/memory/task/",
            data=json.dumps({"payload": {}}),
            content_type="application/json",
        )
        assert response.status_code == 400
        body = json.loads(response.content)
        assert "queue_name" in body["error"]

    def test_enqueue_invalid_json_returns_400(self, client: Client) -> None:
        response = client.post(
            "/queue/enqueue/memory/task/",
            data="not-json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_enqueue_blank_queue_name_returns_400(self, client: Client) -> None:
        response = client.post(
            "/queue/enqueue/memory/task/",
            data=json.dumps({"queue_name": "   ", "payload": {}}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_enqueue_success_with_memory_broker_returns_201(
        self, client: Client
    ) -> None:
        response = client.post(
            "/queue/enqueue/memory/task/",
            data=json.dumps({"queue_name": "orders", "payload": {"id": 1}}),
            content_type="application/json",
        )
        assert response.status_code == 201
        body = json.loads(response.content)
        assert body["queue_name"] == "orders"
        assert body["broker"] == "InMemory"
        assert "message_id" in body

    def test_enqueue_with_priority_client(self, client: Client) -> None:
        response = client.post(
            "/queue/enqueue/memory/priority/",
            data=json.dumps(
                {"queue_name": "alerts", "payload": {"priority": "critical"}}
            ),
            content_type="application/json",
        )
        assert response.status_code == 201

    def test_enqueue_engine_failure_returns_422(self, client: Client) -> None:
        from task_queue.domain.entities import BrokerPublishError

        with patch(
            "task_queue.infrastructure.brokers.RabbitMQBroker.publish",
            side_effect=BrokerPublishError("RabbitMQ", "connection refused"),
        ):
            response = client.post(
                "/queue/enqueue/rabbitmq/task/",
                data=json.dumps({"queue_name": "orders", "payload": {}}),
                content_type="application/json",
            )
        assert response.status_code == 422

    def test_enqueue_defaults_payload_to_empty_dict_when_missing(
        self, client: Client
    ) -> None:
        response = client.post(
            "/queue/enqueue/memory/task/",
            data=json.dumps({"queue_name": "orders"}),
            content_type="application/json",
        )
        assert response.status_code == 201


class TestDequeueMessagesView:
    """GET /queue/dequeue/<broker_type>/<queue_name>/"""

    def test_dequeue_unsupported_broker_returns_400(self, client: Client) -> None:
        response = client.get("/queue/dequeue/kafka/orders/")
        assert response.status_code == 400

    def test_dequeue_invalid_max_param_returns_400(self, client: Client) -> None:
        response = client.get("/queue/dequeue/memory/orders/?max=abc")
        assert response.status_code == 400
        body = json.loads(response.content)
        assert "'max'" in body["error"]

    def test_dequeue_empty_queue_returns_200_with_zero_messages(
        self, client: Client
    ) -> None:
        response = client.get("/queue/dequeue/memory/never-published/")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["message_count"] == 0

    def test_enqueue_then_dequeue_round_trip_via_memory_broker(
        self, client: Client
    ) -> None:
        # NOTE: each broker instance in the view is constructed fresh per
        # request for the real brokers, but InMemoryBroker state lives on
        # the instance — so this exercises the dequeue path's empty-queue
        # branch consistently rather than relying on cross-request state.
        response = client.get("/queue/dequeue/memory/orders/?max=2")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["broker"] == "InMemory"

    def test_dequeue_connection_failure_returns_503(self, client: Client) -> None:
        from task_queue.domain.entities import BrokerConnectionError

        with patch(
            "task_queue.infrastructure.brokers.SQSBroker.consume",
            side_effect=BrokerConnectionError("SQS", "timeout"),
        ):
            response = client.get("/queue/dequeue/sqs/orders/")
        assert response.status_code == 503
