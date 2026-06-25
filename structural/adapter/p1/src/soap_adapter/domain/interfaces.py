"""Target interface — REST product service Protocol.

Defines the interface the client (FastAPI routes) expects.
Adaptee (LegacySoapClient) does NOT implement this directly.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from soap_adapter.domain.entities import Product, ProductCreate


@runtime_checkable
class RESTProductService(Protocol):
    """Target: unified REST-oriented product service interface.

    ISP — only three methods, one per resource operation.
    DIP — routes depend on this abstraction, not on SOAP details.
    """

    def get_product(self, product_id: str) -> Product:
        """Return a single product by ID."""
        ...

    def list_products(self) -> list[Product]:
        """Return all available products."""
        ...

    def create_product(self, data: ProductCreate) -> Product:
        """Persist a new product and return the created resource."""
        ...
