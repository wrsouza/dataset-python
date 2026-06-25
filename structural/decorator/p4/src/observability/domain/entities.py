"""Entidades de domínio do processamento de pedidos."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class OrderStatus(StrEnum):
    """Status possíveis de um pedido após processamento."""

    PROCESSED = "processed"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class OrderRequest:
    """Dados de entrada para processar um pedido."""

    customer_id: str
    item_sku: str
    quantity: int
    unit_price: float

    def total_amount(self) -> float:
        """Calcula o valor total do pedido (quantidade * preço unitário)."""
        return round(self.quantity * self.unit_price, 2)


@dataclass(frozen=True, slots=True)
class OrderResult:
    """Resultado do processamento de um pedido."""

    order_id: str
    status: OrderStatus
    total_amount: float
    processed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def new_processed(total_amount: float) -> OrderResult:
        """Cria um resultado de pedido processado com sucesso."""
        return OrderResult(
            order_id=str(uuid4()),
            status=OrderStatus.PROCESSED,
            total_amount=total_amount,
        )
