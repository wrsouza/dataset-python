"""Simulated legacy SOAP server (Flask).

Responds to SOAP envelopes with XML. Acts as the Adaptee's backend.
In production this would be a real SOAP service; here it is simulated
locally so the full Adapter flow can be exercised without external deps.
"""

from __future__ import annotations

import uuid
import xml.etree.ElementTree as ET
from typing import Any

from flask import Flask, Response, request

app = Flask(__name__)

# In-memory product store (simulates a legacy database)
_PRODUCTS: dict[str, dict[str, Any]] = {
    "1": {"id": "1", "name": "Widget Pro", "price": 29.99, "category": "Electronics", "stock": 150},
    "2": {"id": "2", "name": "Gadget Plus", "price": 49.99, "category": "Electronics", "stock": 75},
    "3": {"id": "3", "name": "Thingamajig", "price": 9.99, "category": "Accessories", "stock": 300},
}


def _soap_response(inner_xml: str) -> Response:
    envelope = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        f"<soap:Body>{inner_xml}</soap:Body>"
        "</soap:Envelope>"
    )
    return Response(envelope, content_type="text/xml; charset=utf-8")


def _product_xml(product: dict[str, Any]) -> str:
    return (
        f'<product>'
        f'<id>{product["id"]}</id>'
        f'<name>{product["name"]}</name>'
        f'<price>{product["price"]}</price>'
        f'<category>{product["category"]}</category>'
        f'<stock>{product["stock"]}</stock>'
        f'</product>'
    )


def _parse_soap_action(raw_xml: str) -> str:
    """Extract the first child tag of soap:Body to determine the action."""
    root = ET.fromstring(raw_xml)  # noqa: S314 — controlled test server
    ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}
    body = root.find("soap:Body", ns)
    if body is None:
        return ""
    first = list(body)
    return first[0].tag if first else ""


@app.route("/soap", methods=["POST"])
def soap_endpoint() -> Response:
    raw = request.data.decode("utf-8")
    action = _parse_soap_action(raw)

    if action == "GetProduct":
        return _handle_get_product(raw)
    if action == "ListProducts":
        return _handle_list_products()
    if action == "CreateProduct":
        return _handle_create_product(raw)

    return _soap_response("<error>Unknown action</error>"), 400  # type: ignore[return-value]


def _handle_get_product(raw: str) -> Response:
    root = ET.fromstring(raw)  # noqa: S314
    ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}
    id_el = root.find(".//id", ns)
    product_id = id_el.text if id_el is not None else ""

    product = _PRODUCTS.get(product_id or "")
    if product is None:
        return Response(
            _soap_response(f"<error>Product not found: {product_id}</error>").get_data(),
            status=404,
            content_type="text/xml",
        )
    return _soap_response(_product_xml(product))


def _handle_list_products() -> Response:
    products_xml = "".join(_product_xml(p) for p in _PRODUCTS.values())
    return _soap_response(f"<products>{products_xml}</products>")


def _handle_create_product(raw: str) -> Response:
    root = ET.fromstring(raw)  # noqa: S314
    create_el = root.find(".//CreateProduct")
    if create_el is None:
        return _soap_response("<error>Missing CreateProduct element</error>")

    def _text(tag: str) -> str:
        el = create_el.find(tag)
        return el.text or "" if el is not None else ""

    new_id = str(uuid.uuid4())[:8]
    product: dict[str, Any] = {
        "id": new_id,
        "name": _text("name"),
        "price": float(_text("price") or 0),
        "category": _text("category"),
        "stock": int(_text("stock") or 0),
    }
    _PRODUCTS[new_id] = product
    return _soap_response(_product_xml(product))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
