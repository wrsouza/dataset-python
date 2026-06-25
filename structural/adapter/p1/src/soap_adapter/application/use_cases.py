"""Application layer — use cases depend only on RESTProductService (Target).

No SOAP, no XML, no httpx here — only domain types and the Target interface.
DIP: receives RESTProductService via constructor injection.
"""

from __future__ import annotations

from soap_adapter.domain.entities import Product, ProductCreate
from soap_adapter.domain.interfaces import RESTProductService


class GetProductUseCase:
    """Retrieve a single product by its identifier."""

    def __init__(self, service: RESTProductService) -> None:
        self._service = service

    def execute(self, product_id: str) -> Product:
        return self._service.get_product(product_id)


class ListProductsUseCase:
    """Retrieve all available products."""

    def __init__(self, service: RESTProductService) -> None:
        self._service = service

    def execute(self) -> list[Product]:
        return self._service.list_products()


class CreateProductUseCase:
    """Validate and persist a new product."""

    def __init__(self, service: RESTProductService) -> None:
        self._service = service

    def execute(self, data: ProductCreate) -> Product:
        return self._service.create_product(data)
