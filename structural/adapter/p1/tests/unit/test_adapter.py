"""Unit tests for SoapToRestAdapter.

Mocks LegacySoapClient so no network is required.
Verifies that the Adapter correctly translates between XML and domain types.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from soap_adapter.domain.entities import (
    Product,
    ProductCreate,
    ProductNotFoundError,
    SoapCommunicationError,
)
from soap_adapter.infrastructure.adapters import SoapToRestAdapter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PRODUCT_XML = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <product>
      <id>42</id>
      <name>Test Widget</name>
      <price>19.99</price>
      <category>Tools</category>
      <stock>100</stock>
    </product>
  </soap:Body>
</soap:Envelope>"""

LIST_XML = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <products>
      <product>
        <id>1</id>
        <name>Alpha</name>
        <price>10.0</price>
        <category>Misc</category>
        <stock>5</stock>
      </product>
      <product>
        <id>2</id>
        <name>Beta</name>
        <price>20.0</price>
        <category>Misc</category>
        <stock>10</stock>
      </product>
    </products>
  </soap:Body>
</soap:Envelope>"""


@pytest.fixture()
def mock_soap_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def adapter(mock_soap_client: MagicMock) -> SoapToRestAdapter:
    return SoapToRestAdapter(soap_client=mock_soap_client)


# ---------------------------------------------------------------------------
# get_product
# ---------------------------------------------------------------------------

class TestGetProduct:
    def test_returns_product_on_success(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.get_product_xml.return_value = PRODUCT_XML

        result = adapter.get_product("42")

        assert isinstance(result, Product)
        assert result.id == "42"
        assert result.name == "Test Widget"
        assert result.price == pytest.approx(19.99)
        assert result.category == "Tools"
        assert result.stock == 100

    def test_calls_adaptee_with_correct_id(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.get_product_xml.return_value = PRODUCT_XML

        adapter.get_product("42")

        mock_soap_client.get_product_xml.assert_called_once_with("42")

    def test_raises_product_not_found_on_404(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.get_product_xml.side_effect = SoapCommunicationError(
            "404 Client Error: Not Found"
        )

        with pytest.raises(ProductNotFoundError) as exc_info:
            adapter.get_product("999")

        assert exc_info.value.product_id == "999"

    def test_propagates_soap_error_on_non_404(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.get_product_xml.side_effect = SoapCommunicationError(
            "Connection refused"
        )

        with pytest.raises(SoapCommunicationError):
            adapter.get_product("1")


# ---------------------------------------------------------------------------
# list_products
# ---------------------------------------------------------------------------

class TestListProducts:
    def test_returns_list_of_products(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.list_products_xml.return_value = LIST_XML

        result = adapter.list_products()

        assert len(result) == 2
        assert all(isinstance(p, Product) for p in result)
        assert result[0].name == "Alpha"
        assert result[1].name == "Beta"

    def test_calls_adaptee_list_method(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.list_products_xml.return_value = LIST_XML

        adapter.list_products()

        mock_soap_client.list_products_xml.assert_called_once()


# ---------------------------------------------------------------------------
# create_product
# ---------------------------------------------------------------------------

class TestCreateProduct:
    def test_returns_created_product(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.create_product_xml.return_value = PRODUCT_XML
        data = ProductCreate(name="Test Widget", price=19.99, category="Tools", stock=100)

        result = adapter.create_product(data)

        assert isinstance(result, Product)
        assert result.name == "Test Widget"

    def test_sends_xml_payload_to_adaptee(
        self, adapter: SoapToRestAdapter, mock_soap_client: MagicMock
    ) -> None:
        mock_soap_client.create_product_xml.return_value = PRODUCT_XML
        data = ProductCreate(name="Widget", price=5.0, category="Misc", stock=1)

        adapter.create_product(data)

        call_args = mock_soap_client.create_product_xml.call_args[0][0]
        assert "Widget" in call_args
        assert "5.0" in call_args
        assert "Misc" in call_args
