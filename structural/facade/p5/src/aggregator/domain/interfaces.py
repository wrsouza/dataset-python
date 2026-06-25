"""Interfaces for the 4 external API subsystems + cache hidden by the Facade."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Protocol, TypeVar

from aggregator.domain.entities import CryptoQuote, NewsItem, StockQuote, WeatherInfo

T = TypeVar("T")


class WeatherAPIClient(Protocol):
    def get_weather(self, city: str) -> WeatherInfo: ...


class StockAPIClient(Protocol):
    def get_quote(self, ticker: str) -> StockQuote: ...


class CryptoAPIClient(Protocol):
    def get_quote(self, symbol: str) -> CryptoQuote: ...


class NewsAPIClient(Protocol):
    def get_latest(self, topic: str, limit: int) -> list[NewsItem]: ...


class CacheManager(ABC):
    """Cache Proxy hidden inside the Facade — callers never see cache hits/misses."""

    @abstractmethod
    def get_or_fetch(
        self, key: str, ttl_seconds: int, fetcher: Callable[[], T]
    ) -> T: ...

    @abstractmethod
    def clear(self) -> None: ...
