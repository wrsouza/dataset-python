"""DataAggregatorFacade — the single entry point hiding 4 API clients + cache.

Client code (the Streamlit UI) only ever calls get_market_overview(),
get_portfolio_summary() and refresh_all() — never the individual API clients.
"""

from __future__ import annotations

from datetime import UTC, datetime

from aggregator.domain.entities import (
    AssetHolding,
    CryptoQuote,
    MarketData,
    Portfolio,
    StockQuote,
    WeatherInfo,
)
from aggregator.domain.interfaces import (
    CacheManager,
    CryptoAPIClient,
    NewsAPIClient,
    StockAPIClient,
    WeatherAPIClient,
)

_WEATHER_TTL_SECONDS = 300
_STOCK_TTL_SECONDS = 60
_CRYPTO_TTL_SECONDS = 30
_NEWS_TTL_SECONDS = 600
_NEWS_ITEMS_LIMIT = 5


class DataAggregatorFacade:
    """SRP per client, DIP at the boundary: every collaborator is injected."""

    def __init__(
        self,
        weather_client: WeatherAPIClient,
        stock_client: StockAPIClient,
        crypto_client: CryptoAPIClient,
        news_client: NewsAPIClient,
        cache: CacheManager,
    ) -> None:
        self._weather = weather_client
        self._stock = stock_client
        self._crypto = crypto_client
        self._news = news_client
        self._cache = cache

    def get_market_overview(
        self,
        cities: list[str],
        tickers: list[str],
        crypto_symbols: list[str],
        news_topic: str = "markets",
    ) -> MarketData:
        weather = [self._fetch_weather(city) for city in cities]
        stocks = [self._fetch_stock(ticker) for ticker in tickers]
        cryptos = [self._fetch_crypto(symbol) for symbol in crypto_symbols]
        news = self._cache.get_or_fetch(
            f"news:{news_topic}",
            _NEWS_TTL_SECONDS,
            lambda: self._news.get_latest(news_topic, _NEWS_ITEMS_LIMIT),
        )
        return MarketData(
            weather=weather,
            stocks=stocks,
            cryptos=cryptos,
            news=news,
            generated_at=datetime.now(UTC),
        )

    def get_portfolio_summary(self, assets: dict[str, float]) -> Portfolio:
        holdings = [
            AssetHolding(
                symbol=symbol,
                quantity=quantity,
                current_price=self._fetch_stock(symbol).price,
            )
            for symbol, quantity in assets.items()
        ]
        return Portfolio(holdings=holdings)

    def _fetch_weather(self, city: str) -> WeatherInfo:
        return self._cache.get_or_fetch(
            f"weather:{city}",
            _WEATHER_TTL_SECONDS,
            lambda: self._weather.get_weather(city),
        )

    def _fetch_stock(self, ticker: str) -> StockQuote:
        return self._cache.get_or_fetch(
            f"stock:{ticker}",
            _STOCK_TTL_SECONDS,
            lambda: self._stock.get_quote(ticker),
        )

    def _fetch_crypto(self, symbol: str) -> CryptoQuote:
        return self._cache.get_or_fetch(
            f"crypto:{symbol}",
            _CRYPTO_TTL_SECONDS,
            lambda: self._crypto.get_quote(symbol),
        )

    def refresh_all(self) -> None:
        self._cache.clear()
