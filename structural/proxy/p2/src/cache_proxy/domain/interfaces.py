"""Domain interfaces (Subject) for the API Cache Proxy pattern.

ExternalAPIService is the Subject role.
Both MockExternalAPIService (RealSubject) and RedisCacheProxy (Proxy)
implement this Protocol, ensuring LSP and DIP.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cache_proxy.domain.entities import StockData, WeatherData


@runtime_checkable
class ExternalAPIService(Protocol):
    """Subject: contract for external API data retrieval.

    Clients depend only on this Protocol — they are unaware whether they
    hold the real implementation or a caching proxy.
    """

    def get_weather(self, city: str) -> WeatherData:
        """Return current weather data for the given city."""
        ...

    def get_exchange_rate(self, from_cur: str, to_cur: str) -> float:
        """Return the exchange rate from from_cur to to_cur."""
        ...

    def get_stock_price(self, ticker: str) -> StockData:
        """Return current stock data for the given ticker symbol."""
        ...
