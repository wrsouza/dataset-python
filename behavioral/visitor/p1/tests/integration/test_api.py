"""Integration tests for the Query AST Visitor FastAPI endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from query_ast.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_sql_endpoint_returns_select_statement() -> None:
    payload = {
        "select": {"table": "users", "columns": ["id", "name"]},
        "where": "active = true",
    }
    response = client.post("/queries/generate_sql", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["operation"] == "generate_sql"
    assert "SELECT id, name FROM users" in body["data"]["sql"]
    assert body["is_valid"] is True


def test_explain_endpoint_returns_plain_english_steps() -> None:
    payload = {"select": {"table": "orders", "columns": ["id"]}}
    response = client.post("/queries/explain", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "orders" in body["data"]["explanation"]


def test_validate_endpoint_flags_invalid_limit() -> None:
    payload = {
        "select": {"table": "users", "columns": ["id"]},
        "limit": {"limit": -1},
    }
    response = client.post("/queries/validate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["is_valid"] is False
    assert any("LIMIT must be positive" in err for err in body["errors"])


def test_optimize_endpoint_returns_hints() -> None:
    payload = {"select": {"table": "logs", "columns": []}}
    response = client.post("/queries/optimize", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["hints"]) > 0


def test_unknown_operation_returns_422_from_enum_validation() -> None:
    payload = {"select": {"table": "users", "columns": ["id"]}}
    response = client.post("/queries/not_a_real_operation", json=payload)
    assert response.status_code == 422


def test_full_query_with_joins_generates_complete_sql() -> None:
    payload = {
        "select": {"table": "users u", "columns": ["u.id", "o.total"]},
        "joins": [
            {
                "join_type": "LEFT",
                "table": "orders o",
                "on_condition": "u.id = o.user_id",
            }
        ],
        "where": "u.active = true",
        "group_by": ["u.id"],
        "order_by": [["u.id", "ASC"]],
        "limit": {"limit": 25, "offset": 0},
    }
    response = client.post("/queries/generate_sql", json=payload)
    assert response.status_code == 200
    sql = response.json()["data"]["sql"]
    assert "LEFT JOIN orders o ON u.id = o.user_id" in sql
    assert "GROUP BY u.id" in sql
    assert "ORDER BY u.id ASC" in sql
    assert "LIMIT 25" in sql
