"""Adaptee — Legacy SOAP client with XML-based API.

This is the existing incompatible interface that the Adapter wraps.
The client code (routes/use-cases) never imports this class directly.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from soap_adapter.domain.entities import SoapCommunicationError


class LegacySoapClient:
    """Adaptee: communicates with the SOAP service using raw XML.

    All methods accept and return XML strings — the opposite of what
    modern REST clients need.
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _post_soap(self, action: str, body_xml: str) -> str:
        """Send a SOAP envelope and return the raw XML response body."""
        envelope = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            f"<soap:Body>{body_xml}</soap:Body>"
            "</soap:Envelope>"
        )
        try:
            response = httpx.post(
                f"{self._base_url}/soap",
                content=envelope,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": action,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as exc:
            raise SoapCommunicationError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Public Adaptee interface (XML in / XML out)
    # ------------------------------------------------------------------

    def get_product_xml(self, product_id: str) -> str:
        """Retrieve a product by ID; returns raw XML string."""
        body = f"<GetProduct><id>{product_id}</id></GetProduct>"
        return self._post_soap("GetProduct", body)

    def list_products_xml(self) -> str:
        """Retrieve all products; returns raw XML string."""
        return self._post_soap("ListProducts", "<ListProducts/>")

    def create_product_xml(self, xml_data: str) -> str:
        """Create a product from XML payload; returns raw XML string."""
        body = f"<CreateProduct>{xml_data}</CreateProduct>"
        return self._post_soap("CreateProduct", body)


# ---------------------------------------------------------------------------
# XML helpers used exclusively by SoapToRestAdapter
# ---------------------------------------------------------------------------

def parse_product_xml(xml_text: str) -> dict[str, str]:
    """Extract product fields from a SOAP response envelope."""
    root = ET.fromstring(xml_text)  # noqa: S314 — internal, controlled XML
    ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}

    body = root.find("soap:Body", ns)
    if body is None:
        raise SoapCommunicationError("Missing <soap:Body> in response")

    product_el = body.find(".//product")
    if product_el is None:
        raise SoapCommunicationError("Missing <product> element in SOAP body")

    return {child.tag: (child.text or "") for child in product_el}


def parse_product_list_xml(xml_text: str) -> list[dict[str, str]]:
    """Extract a list of products from a SOAP response envelope."""
    root = ET.fromstring(xml_text)  # noqa: S314 — internal, controlled XML
    ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}

    body = root.find("soap:Body", ns)
    if body is None:
        raise SoapCommunicationError("Missing <soap:Body> in response")

    return [
        {child.tag: (child.text or "") for child in product_el}
        for product_el in body.findall(".//product")
    ]


def product_to_xml(name: str, price: float, category: str, stock: int) -> str:
    """Serialize product fields to an XML fragment for SOAP CreateProduct."""
    return (
        f"<name>{name}</name>"
        f"<price>{price}</price>"
        f"<category>{category}</category>"
        f"<stock>{stock}</stock>"
    )
