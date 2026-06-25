"""Integration tests for Django views — exercises the full HTTP stack.

Uses Django's test client (no real HTTP server needed). Real database
connections (PostgreSQL/MySQL/SQL Server) are not available in this
environment, so connection-dependent assertions only check for graceful
failure (is_healthy=False), never for exceptions/5xx leaking out.
"""

from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

import django
import pytest
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "db_factory.settings")
django.setup()


@pytest.fixture
def client() -> Client:
    return Client()


class TestHealthCheckView:
    """GET /db/health/<db_type>/"""

    @pytest.mark.parametrize("db_type", ["postgresql", "mysql", "sqlserver"])
    def test_health_check_returns_200_for_supported_engines(
        self, client: Client, db_type: str
    ) -> None:
        response = client.get(f"/db/health/{db_type}/")
        assert response.status_code == 200

    def test_health_check_response_has_expected_shape(self, client: Client) -> None:
        response = client.get("/db/health/postgresql/")
        body = json.loads(response.content)
        assert body["engine"] == "PostgreSQL"
        assert "is_healthy" in body
        assert "checked_at" in body

    def test_health_check_unhealthy_without_real_database(self, client: Client) -> None:
        # No real Postgres/MySQL/SQLServer running in this test environment.
        response = client.get("/db/health/mysql/")
        body = json.loads(response.content)
        assert body["is_healthy"] is False

    def test_health_check_unsupported_engine_returns_400(self, client: Client) -> None:
        response = client.get("/db/health/oracle/")
        assert response.status_code == 400
        body = json.loads(response.content)
        assert "Unsupported database type" in body["error"]

    def test_health_check_with_mocked_connection_returns_healthy(
        self, client: Client
    ) -> None:
        with (
            patch(
                "db_factory.infrastructure.factories.PostgreSQLConnection.ping",
                return_value=True,
            ),
            patch(
                "db_factory.infrastructure.factories.PostgreSQLConnection.get_connection_info",
                return_value={"engine": "PostgreSQL"},
            ),
        ):
            response = client.get("/db/health/postgresql/")
        body = json.loads(response.content)
        assert body["is_healthy"] is True


class TestRunQueryView:
    """POST /db/query/<db_type>/"""

    def test_run_query_unsupported_engine_returns_400(self, client: Client) -> None:
        response = client.post(
            "/db/query/oracle/",
            data=json.dumps({"sql": "SELECT 1"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_run_query_missing_sql_returns_400(self, client: Client) -> None:
        response = client.post(
            "/db/query/postgresql/",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400
        body = json.loads(response.content)
        assert "sql" in body["error"]

    def test_run_query_invalid_json_returns_400(self, client: Client) -> None:
        response = client.post(
            "/db/query/postgresql/",
            data="not-json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_run_query_blank_sql_returns_400(self, client: Client) -> None:
        response = client.post(
            "/db/query/postgresql/",
            data=json.dumps({"sql": "   "}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_run_query_success_returns_200_with_rows(self, client: Client) -> None:
        with patch(
            "db_factory.infrastructure.factories.PostgreSQLQueryBuilder.execute",
            return_value=[{"id": 1, "name": "Ada"}],
        ):
            response = client.post(
                "/db/query/postgresql/",
                data=json.dumps({"sql": "SELECT id, name FROM users;"}),
                content_type="application/json",
            )
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["row_count"] == 1
        assert body["rows"] == [{"id": 1, "name": "Ada"}]
        assert body["engine"] == "PostgreSQL"

    def test_run_query_engine_failure_returns_422(self, client: Client) -> None:
        from db_factory.domain.entities import QueryExecutionError

        with patch(
            "db_factory.infrastructure.factories.MySQLQueryBuilder.execute",
            side_effect=QueryExecutionError("MySQL", "BAD SQL", "syntax error"),
        ):
            response = client.post(
                "/db/query/mysql/",
                data=json.dumps({"sql": "BAD SQL"}),
                content_type="application/json",
            )
        assert response.status_code == 422

    def test_run_query_passes_params_through(self, client: Client) -> None:
        mock_execute = MagicMock(return_value=[])
        with patch(
            "db_factory.infrastructure.factories.PostgreSQLQueryBuilder.execute",
            mock_execute,
        ):
            client.post(
                "/db/query/postgresql/",
                data=json.dumps({"sql": "SELECT 1;", "params": {"a": 1}}),
                content_type="application/json",
            )
        mock_execute.assert_called_once_with("SELECT 1;", {"a": 1})
