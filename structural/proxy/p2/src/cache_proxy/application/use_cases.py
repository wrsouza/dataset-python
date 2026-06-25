"""Application use cases — depend only on the ExternalAPIService Protocol.

Use cases never import MockExternalAPIService or RedisCacheProxy directly.
They receive the service via constructor injection (DIP).
"""

from __future__ import annotations

from cache_proxy.domain.entities import CacheStats, StockData, WeatherData
from cache_proxy.domain.interfaces import ExternalAPIService
from cache_proxy.infrastructure.proxy import RedisCacheProxy


class GetWeatherUseCase:
    """Retrieve current weather data for a city."""

    def __init__(self, service: ExternalAPIService) -> None:
        self._service = service

    def execute(self, city: str) -> WeatherData:
        return self._service.get_weather(city)


class GetExchangeRateUseCase:
    """Retrieve the exchange rate between two currencies."""

    def __init__(self, service: ExternalAPIService) -> None:
        self._service = service

    def execute(self, from_cur: str, to_cur: str) -> float:
        return self._service.get_exchange_rate(from_cur, to_cur)


class GetStockPriceUseCase:
    """Retrieve current stock data for a ticker symbol."""

    def __init__(self, service: ExternalAPIService) -> None:
        self._service = service

    def execute(self, ticker: str) -> StockData:
        return self._service.get_stock_price(ticker)


class GetCacheStatsUseCase:
    """Return proxy cache statistics — requires a RedisCacheProxy explicitly."""

    def __init__(self, proxy: RedisCacheProxy) -> None:
        # Stats are a proxy-specific concern, not part of ExternalAPIService.
        self._proxy = proxy

    def execute(self) -> CacheStats:
        return self._proxy.get_stats()


class FlushCacheUseCase:
    """Flush all proxy-managed keys from the Redis cache."""

    def __init__(self, proxy: RedisCacheProxy) -> None:
        self._proxy = proxy

    def execute(self) -> int:
        """Returns the number of keys removed."""
        return self._proxy.flush()
