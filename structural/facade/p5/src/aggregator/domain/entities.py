"""Domain entities for the Multi-API Aggregator Facade."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class WeatherInfo:
    city: str
    temperature_c: float
    condition: str
    humidity_pct: int


@dataclass(frozen=True)
class StockQuote:
    ticker: str
    price: float
    change_pct: float


@dataclass(frozen=True)
class CryptoQuote:
    symbol: str
    price_usd: float
    change_pct_24h: float


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    published_at: datetime


@dataclass(frozen=True)
class MarketData:
    weather: list[WeatherInfo]
    stocks: list[StockQuote]
    cryptos: list[CryptoQuote]
    news: list[NewsItem]
    generated_at: datetime


@dataclass(frozen=True)
class AssetHolding:
    symbol: str
    quantity: float
    current_price: float

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price


@dataclass(frozen=True)
class Portfolio:
    holdings: list[AssetHolding] = field(default_factory=list)

    @property
    def total_value(self) -> float:
        return sum(holding.market_value for holding in self.holdings)
