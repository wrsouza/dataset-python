"""Domain entities for the API Cache Proxy project."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WeatherData:
    """Weather information for a city."""

    city: str
    temperature_c: float
    humidity_percent: float
    description: str
    wind_speed_kmh: float


@dataclass
class StockData:
    """Stock price information for a ticker symbol."""

    ticker: str
    price_usd: float
    change_percent: float
    volume: int
    market_cap_billions: float


@dataclass
class CacheStats:
    """Accumulated cache hit/miss statistics for the proxy."""

    hits: int = 0
    misses: int = 0

    @property
    def total(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Return hit rate as a value between 0.0 and 1.0."""
        if self.total == 0:
            return 0.0
        return self.hits / self.total
