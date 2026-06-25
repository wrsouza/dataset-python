"""Domain entities — pure data classes, no infrastructure dependencies."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """Data required to create a new product."""

    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    stock: int = Field(..., ge=0)


class Product(BaseModel):
    """Full product entity as returned by the service."""

    id: str
    name: str
    price: float
    category: str
    stock: int


class ProductNotFoundError(Exception):
    """Raised when a product cannot be located by the given ID."""

    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"Product not found: {product_id}")


class SoapCommunicationError(Exception):
    """Raised when the legacy SOAP service is unreachable or returns an error."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(f"SOAP communication error: {detail}")
