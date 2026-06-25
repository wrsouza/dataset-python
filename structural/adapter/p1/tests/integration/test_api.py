"""Integration tests — FastAPI endpoints with a real SOAP server stub.

Uses httpx TestClient; the SoapToRestAdapter is wired to a mock SOAP client
so no Docker is needed during CI.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from soap_adapter.main import app

PRODUCT_XML = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <product>
      <id>1</id>
      <name>Widget Pro</name>
      <price>29.99</price>
      <category>Electronics</category>
      <stock>150</stock>
    </product>
  </soap:Body>
</soap:Envelope>"""

LIST_XML = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <products>
      <product>
        <id>1</id><name>Widget Pro</name><price>29.99</price>
        <category>Electronics</category><stock>150</stock>
      </product>
    </products>
  </soap:Body>
</soap:Envelope>"""


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_soap_client() -> MagicMock:
    mock = MagicMock()
    mock.get_product_xml.return_value = PRODUCT_XML
    mock.list_products_xml.return_value = LIST_XML
    mock.create_product_xml.return_value = PRODUCT_XML
    with patch("soap_adapter.main._get_soap_client", return_value=mock):
        yield mock


class TestGetProduct:
    def test_returns_200_with_product(self, client: TestClient) -> None:
        response = client.get("/products/1")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == "1"
        assert body["name"] == "Widget Pro"

    def test_returns_correct_content_type(self, client: TestClient) -> None:
        response = client.get("/products/1")
        assert "application/json" in response.headers["content-type"]


class TestListProducts:
    def test_returns_200_with_list(self, client: TestClient) -> None:
        response = client.get("/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1


class TestCreateProduct:
    def test_returns_201_on_creation(self, client: TestClient) -> None:
        payload = {
            "name": "New Product",
            "price": 9.99,
            "category": "Misc",
            "stock": 10,
        }
        response = client.post("/products", json=payload)
        assert response.status_code == 201

    def test_validates_required_fields(self, client: TestClient) -> None:
        response = client.post("/products", json={"name": "Only name"})
        assert response.status_code == 422


class TestHealth:
    def test_health_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
