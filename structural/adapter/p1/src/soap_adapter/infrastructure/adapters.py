"""Adapter — bridges LegacySoapClient (Adaptee) to RESTProductService (Target).

SoapToRestAdapter is the only place in the codebase that knows about XML.
All consumers use RESTProductService (Protocol), so they remain decoupled
from SOAP implementation details (DIP).
"""

from __future__ import annotations

from soap_adapter.domain.entities import (
    Product,
    ProductCreate,
    ProductNotFoundError,
    SoapCommunicationError,
)
from soap_adapter.infrastructure.soap_client import (
    LegacySoapClient,
    parse_product_list_xml,
    parse_product_xml,
    product_to_xml,
)


class SoapToRestAdapter:
    """Adapter: converts RESTProductService calls into SOAP XML calls.

    Target role: implements RESTProductService (structurally via duck-typing).
    Adaptee role: holds a reference to LegacySoapClient and delegates to it.

    LSP — every method satisfies the same contract as RESTProductService:
      - get_product raises ProductNotFoundError when not found
      - list_products always returns a list (empty when none)
      - create_product returns the created Product
    """

    def __init__(self, soap_client: LegacySoapClient) -> None:
        self._client = soap_client

    def get_product(self, product_id: str) -> Product:
        """Translate REST get-by-id call into SOAP GetProduct."""
        try:
            xml_response = self._client.get_product_xml(product_id)
        except SoapCommunicationError as exc:
            # HTTP 404 from SOAP server maps to domain not-found
            if "404" in str(exc) or "not found" in str(exc).lower():
                raise ProductNotFoundError(product_id) from exc
            raise

        fields = parse_product_xml(xml_response)
        return self._fields_to_product(fields)

    def list_products(self) -> list[Product]:
        """Translate REST list call into SOAP ListProducts."""
        xml_response = self._client.list_products_xml()
        fields_list = parse_product_list_xml(xml_response)
        return [self._fields_to_product(f) for f in fields_list]

    def create_product(self, data: ProductCreate) -> Product:
        """Translate REST create call into SOAP CreateProduct."""
        xml_payload = product_to_xml(
            name=data.name,
            price=data.price,
            category=data.category,
            stock=data.stock,
        )
        xml_response = self._client.create_product_xml(xml_payload)
        fields = parse_product_xml(xml_response)
        return self._fields_to_product(fields)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fields_to_product(fields: dict[str, str]) -> Product:
        """Convert raw XML field dictionary to a typed Product entity."""
        return Product(
            id=fields.get("id", ""),
            name=fields.get("name", ""),
            price=float(fields.get("price", 0)),
            category=fields.get("category", ""),
            stock=int(fields.get("stock", 0)),
        )
