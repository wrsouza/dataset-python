"""FastAPI application — composition root.

This is the only module that wires concrete classes together.
Routes only know about use cases; use cases only know about RESTProductService.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, status

from soap_adapter.application.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsUseCase,
)
from soap_adapter.domain.entities import Product, ProductCreate, ProductNotFoundError
from soap_adapter.infrastructure.adapters import SoapToRestAdapter
from soap_adapter.infrastructure.soap_client import LegacySoapClient

app = FastAPI(
    title="SOAP → REST Adapter",
    description=(
        "Demonstrates the Adapter pattern: a FastAPI REST interface backed "
        "by a legacy SOAP service, with all XML translation hidden inside "
        "SoapToRestAdapter."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Dependency injection — composition root
# ---------------------------------------------------------------------------

def _get_soap_client() -> LegacySoapClient:
    soap_url = os.environ.get("SOAP_SERVICE_URL", "http://soap-server:5000")
    return LegacySoapClient(base_url=soap_url)


def _get_adapter(
    client: LegacySoapClient = Depends(_get_soap_client),
) -> SoapToRestAdapter:
    return SoapToRestAdapter(soap_client=client)


# ---------------------------------------------------------------------------
# Routes — depend only on use cases (high-level), not on adapters
# ---------------------------------------------------------------------------

@app.get("/products/{product_id}", response_model=Product, summary="Get product by ID")
def get_product(
    product_id: str,
    adapter: SoapToRestAdapter = Depends(_get_adapter),
) -> Product:
    use_case = GetProductUseCase(service=adapter)
    try:
        return use_case.execute(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@app.get("/products", response_model=list[Product], summary="List all products")
def list_products(
    adapter: SoapToRestAdapter = Depends(_get_adapter),
) -> list[Product]:
    use_case = ListProductsUseCase(service=adapter)
    return use_case.execute()


@app.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
def create_product(
    body: ProductCreate,
    adapter: SoapToRestAdapter = Depends(_get_adapter),
) -> Product:
    use_case = CreateProductUseCase(service=adapter)
    return use_case.execute(body)


@app.get("/health", summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}
