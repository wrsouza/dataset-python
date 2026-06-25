"""Integration tests for Report Builder Flask API."""
from __future__ import annotations


SALES_PAYLOAD = {
    "type": "sales",
    "data": {
        "period": "Q2 2024",
        "rows": [["2024-04-01", "Alice", "Widget", 2, 150.0]],
        "total": 150.0,
    },
}

INVENTORY_PAYLOAD = {
    "type": "inventory",
    "data": {
        "warehouse": "Warehouse A",
        "rows": [["SKU001", "Widget", "Electronics", 30, 5]],
    },
}


class TestCSVEndpoint:
    def test_generate_sales_csv(self, client) -> None:
        response = client.post("/reports/csv", json=SALES_PAYLOAD)
        assert response.status_code == 200
        assert "text/csv" in response.content_type

    def test_generate_inventory_csv(self, client) -> None:
        response = client.post("/reports/csv", json=INVENTORY_PAYLOAD)
        assert response.status_code == 200


class TestExcelEndpoint:
    def test_generate_sales_excel(self, client) -> None:
        response = client.post("/reports/excel", json=SALES_PAYLOAD)
        assert response.status_code == 200
        assert "spreadsheet" in response.content_type

    def test_generate_inventory_excel(self, client) -> None:
        response = client.post("/reports/excel", json=INVENTORY_PAYLOAD)
        assert response.status_code == 200


class TestPDFEndpoint:
    def test_generate_sales_pdf(self, client) -> None:
        response = client.post("/reports/pdf", json=SALES_PAYLOAD)
        assert response.status_code == 200
        assert "application/pdf" in response.content_type
        assert response.data[:4] == b"%PDF"


class TestMiscEndpoints:
    def test_unknown_format_returns_400(self, client) -> None:
        response = client.post("/reports/xml", json=SALES_PAYLOAD)
        assert response.status_code == 400

    def test_unknown_report_type_returns_400(self, client) -> None:
        response = client.post("/reports/csv", json={"type": "unknown", "data": {}})
        assert response.status_code == 400

    def test_list_templates(self, client) -> None:
        response = client.get("/reports/templates")
        assert response.status_code == 200
        data = response.get_json()
        assert "templates" in data
        assert "sales" in data["templates"]

    def test_health_check(self, client) -> None:
        response = client.get("/health")
        assert response.status_code == 200
