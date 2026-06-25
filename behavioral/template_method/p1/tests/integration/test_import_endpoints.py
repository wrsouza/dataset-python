"""Integration tests: exercise the full Template Method algorithm through
the FastAPI HTTP layer (upload -> import_data() -> status lookup).

The PostgreSQL repository is mocked at the persistence boundary (see
tests/conftest.py) so these tests run without a live database, while still
covering the real read_raw -> parse -> validate -> transform -> persist ->
generate_report pipeline for each ConcreteClass (CSV, JSON, XML).
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestCSVImportEndpoint:
    def test_import_valid_csv_returns_completed(self, client: TestClient) -> None:
        csv_content = b"id,name,value\n1,Alice,42.5\n2,Bob,10.0\n"
        response = client.post(
            "/import/csv",
            files={"file": ("data.csv", csv_content, "text/csv")},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert body["report"]["total_records"] == 2
        assert body["report"]["persisted_count"] == 2
        assert body["report"]["format"] == "CSV"

    def test_import_csv_with_missing_field_is_partial(self, client: TestClient) -> None:
        csv_content = b"id,name,value\n1,,42.5\n2,Bob,10.0\n"
        response = client.post(
            "/import/csv",
            files={"file": ("data.csv", csv_content, "text/csv")},
        )

        assert response.status_code == 207
        body = response.json()
        assert body["status"] == "partial"
        assert body["report"]["failed_count"] == 1
        assert body["report"]["persisted_count"] == 1


class TestJSONImportEndpoint:
    def test_import_valid_json_returns_completed(self, client: TestClient) -> None:
        json_content = b'[{"id": "1", "name": "Alice", "value": 42.5}]'
        response = client.post(
            "/import/json",
            files={"file": ("data.json", json_content, "application/json")},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert body["report"]["format"] == "JSON"
        assert body["report"]["persisted_count"] == 1

    def test_import_json_missing_required_field_fails(self, client: TestClient) -> None:
        json_content = b'[{"id": "1", "value": 42.5}]'
        response = client.post(
            "/import/json",
            files={"file": ("data.json", json_content, "application/json")},
        )

        # JSONImporter keeps the default (abort) hook, so validation errors
        # fail the job.
        assert response.status_code == 207
        body = response.json()
        assert body["status"] == "failed"
        assert body["report"]["persisted_count"] == 0

    def test_import_malformed_json_fails_with_error_message(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/import/json",
            files={"file": ("data.json", b"not json", "application/json")},
        )

        assert response.status_code == 207
        body = response.json()
        assert body["status"] == "failed"


class TestXMLImportEndpoint:
    def test_import_valid_xml_returns_completed(self, client: TestClient) -> None:
        xml_content = (
            b"<records><record><id>1</id><name>Alice</name>"
            b"<value>42.5</value></record></records>"
        )
        response = client.post(
            "/import/xml",
            files={"file": ("data.xml", xml_content, "application/xml")},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert body["report"]["format"] == "XML"
        assert body["report"]["persisted_count"] == 1


class TestJobStatusEndpoint:
    def test_status_lookup_after_import(self, client: TestClient) -> None:
        csv_content = b"id,name,value\n1,Alice,42.5\n"
        import_response = client.post(
            "/import/csv",
            files={"file": ("data.csv", csv_content, "text/csv")},
        )
        job_id = import_response.json()["job_id"]

        status_response = client.get(f"/import/{job_id}/status")

        assert status_response.status_code == 200
        body = status_response.json()
        assert body["job_id"] == job_id
        assert body["status"] == "completed"

    def test_status_lookup_unknown_job_returns_404(self, client: TestClient) -> None:
        response = client.get("/import/does-not-exist/status")

        assert response.status_code == 404
