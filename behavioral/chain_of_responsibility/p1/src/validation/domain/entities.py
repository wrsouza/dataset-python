"""Domain entities for the request validation chain."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


@dataclass
class APIRequest:
    """Represents an incoming API request travelling through the chain."""

    body: dict[str, object]
    headers: dict[str, str] = field(default_factory=dict)
    user_id: str | None = None
    user_role: UserRole | None = None
    client_ip: str = "127.0.0.1"
    endpoint: str = "/orders"


@dataclass
class APIResponse:
    """Represents the outcome of chain processing."""

    status_code: int
    message: str
    data: dict[str, object] = field(default_factory=dict)
    handler_name: str = ""

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    @classmethod
    def ok(
        cls, message: str, data: dict[str, object] | None = None, handler_name: str = ""
    ) -> APIResponse:
        return cls(
            status_code=200, message=message, data=data or {}, handler_name=handler_name
        )

    @classmethod
    def created(
        cls, message: str, data: dict[str, object] | None = None, handler_name: str = ""
    ) -> APIResponse:
        return cls(
            status_code=201, message=message, data=data or {}, handler_name=handler_name
        )

    @classmethod
    def bad_request(cls, message: str, handler_name: str = "") -> APIResponse:
        return cls(status_code=400, message=message, handler_name=handler_name)

    @classmethod
    def unauthorized(cls, message: str, handler_name: str = "") -> APIResponse:
        return cls(status_code=401, message=message, handler_name=handler_name)

    @classmethod
    def forbidden(cls, message: str, handler_name: str = "") -> APIResponse:
        return cls(status_code=403, message=message, handler_name=handler_name)

    @classmethod
    def too_many_requests(cls, message: str, handler_name: str = "") -> APIResponse:
        return cls(status_code=429, message=message, handler_name=handler_name)

    @classmethod
    def unprocessable(cls, message: str, handler_name: str = "") -> APIResponse:
        return cls(status_code=422, message=message, handler_name=handler_name)


@dataclass
class OrderRequest:
    """Schema for the POST /orders body, validated by SchemaValidationHandler."""

    product_id: str
    quantity: int
    price: float
    customer_id: str
