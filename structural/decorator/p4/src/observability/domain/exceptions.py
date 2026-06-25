"""Exceções específicas do domínio de processamento de pedidos."""

from __future__ import annotations


class InvalidOrderError(Exception):
    """Lançada quando os dados de um pedido são inválidos para processamento."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid order: {reason}")
