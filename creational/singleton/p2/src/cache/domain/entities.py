"""Domain entities for the Cache Manager project."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from cache.domain.interfaces import CircuitState


@dataclass
class CacheStatsSnapshot:
    """Immutable statistics snapshot taken at a point in time."""

    hits: int
    misses: int
    circuit_state: CircuitState
    backend: str
    sampled_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate, 4),
            "circuit_state": self.circuit_state.name,
            "backend": self.backend,
            "sampled_at": self.sampled_at.isoformat(),
        }


@dataclass(frozen=True)
class Product:
    """Sample product entity used to demonstrate cache behaviour."""

    id: int
    name: str
    price: float
    category: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
        }
