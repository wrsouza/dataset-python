"""Schema validation handler using Pydantic."""

from __future__ import annotations

from pydantic import BaseModel, ValidationError, field_validator

from validation.domain.entities import APIRequest, APIResponse
from validation.domain.interfaces import RequestHandler


class OrderSchema(BaseModel):
    """Pydantic schema for order request body."""

    product_id: str
    quantity: int
    price: float
    customer_id: str

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be greater than 0")
        return v

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v

    @field_validator("product_id", "customer_id")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field must not be blank")
        return v


class SchemaValidationHandler(RequestHandler):
    """Validates request body against the Pydantic schema.

    SRP: only responsible for structural/type validation.
    OCP: new schemas can be added without modifying this handler.
    """

    HANDLER_NAME = "SchemaValidationHandler"

    def handle(self, request: APIRequest) -> APIResponse | None:
        try:
            OrderSchema.model_validate(request.body)
        except ValidationError as exc:
            errors = [f"{e['loc']}: {e['msg']}" for e in exc.errors()]
            return APIResponse.unprocessable(
                message=f"Schema validation failed: {'; '.join(errors)}",
                handler_name=self.HANDLER_NAME,
            )
        return self._pass_to_next(request)
