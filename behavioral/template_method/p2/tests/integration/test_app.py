"""Integration tests for the Flask Report Generation Template API."""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_generate_csv_report(client: FlaskClient) -> None:
    response = client.post(
        "/reports",
        json={"format": "csv", "title": "Users", "rows": [{"id": 1, "name": "Ana"}]},
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["format"] == "csv"
    assert "1,Ana" in body["content"]


def test_generate_with_unknown_format_returns_400(client: FlaskClient) -> None:
    response = client.post(
        "/reports", json={"format": "pdf", "title": "Users", "rows": []}
    )

    assert response.status_code == 400


def test_get_report_after_generation(client: FlaskClient) -> None:
    generate_response = client.post(
        "/reports", json={"format": "json", "title": "Users", "rows": []}
    )
    report_id = generate_response.get_json()["report_id"]

    response = client.get(f"/reports/{report_id}")

    assert response.status_code == 200
    assert response.get_json()["report_id"] == report_id


def test_get_unknown_report_returns_404(client: FlaskClient) -> None:
    response = client.get("/reports/does-not-exist")

    assert response.status_code == 404


def test_list_formats(client: FlaskClient) -> None:
    response = client.get("/reports/formats")

    body = response.get_json()
    assert "csv" in body
    assert "html" in body
    assert "json" in body
