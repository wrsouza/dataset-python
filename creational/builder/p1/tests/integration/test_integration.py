"""Integration tests for SQL Query Builder API endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


class TestBuildQueryEndpoint:
    def test_build_simple_query(self, client: TestClient) -> None:
        payload = {"table": "users", "columns": ["id", "name"], "conditions": []}
        response = client.post("/queries/build", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "sql" in data
        assert "FROM users" in data["sql"]

    def test_build_query_with_conditions(self, client: TestClient) -> None:
        payload = {
            "table": "orders",
            "columns": ["id", "total"],
            "conditions": ["status = 'paid'"],
            "limit": 5,
        }
        response = client.post("/queries/build", json=payload)
        assert response.status_code == 200
        sql = response.json()["sql"]
        assert "WHERE" in sql
        assert "LIMIT 5" in sql

    def test_build_query_missing_table_returns_422(self, client: TestClient) -> None:
        payload = {"table": "", "columns": []}
        response = client.post("/queries/build", json=payload)
        assert response.status_code == 422


class TestReportEndpoints:
    def test_get_sales_by_period(self, client: TestClient) -> None:
        response = client.get(
            "/queries/reports/sales_by_period",
            params={"start_date": "2024-01-01", "end_date": "2024-06-30"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["report"] == "sales_by_period"
        assert "sql" in data

    def test_get_top_customers(self, client: TestClient) -> None:
        response = client.get("/queries/reports/top_customers", params={"top_n": 5})
        assert response.status_code == 200
        assert "LIMIT 5" in response.json()["sql"]

    def test_get_low_stock_products(self, client: TestClient) -> None:
        response = client.get("/queries/reports/low_stock_products", params={"threshold": 15})
        assert response.status_code == 200
        assert "15" in response.json()["sql"]

    def test_unknown_report_returns_404(self, client: TestClient) -> None:
        response = client.get("/queries/reports/nonexistent_report")
        assert response.status_code == 404

    def test_list_reports(self, client: TestClient) -> None:
        response = client.get("/queries/reports")
        assert response.status_code == 200
        assert "reports" in response.json()

    def test_health_check(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
