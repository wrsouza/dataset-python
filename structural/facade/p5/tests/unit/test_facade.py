"""Unit tests for DataAggregatorFacade — all 4 clients + cache mocked (DIP)."""

from __future__ import annotations

from unittest.mock import MagicMock

from aggregator.application.facade import DataAggregatorFacade
from aggregator.domain.entities import CryptoQuote, StockQuote, WeatherInfo


def _make_facade_with_mocks() -> tuple[DataAggregatorFacade, dict[str, MagicMock]]:
    mocks = {
        "weather": MagicMock(),
        "stock": MagicMock(),
        "crypto": MagicMock(),
        "news": MagicMock(),
        "cache": MagicMock(),
    }
    # Cache pass-through by default: just calls the fetcher.
    mocks["cache"].get_or_fetch.side_effect = lambda key, ttl, fetcher: fetcher()
    facade = DataAggregatorFacade(
        weather_client=mocks["weather"],
        stock_client=mocks["stock"],
        crypto_client=mocks["crypto"],
        news_client=mocks["news"],
        cache=mocks["cache"],
    )
    return facade, mocks


def test_get_market_overview_aggregates_all_sources() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["weather"].get_weather.return_value = WeatherInfo("London", 15.0, "Sunny", 50)
    mocks["stock"].get_quote.return_value = StockQuote("AAPL", 180.0, 1.2)
    mocks["crypto"].get_quote.return_value = CryptoQuote("BTC", 60000.0, 2.5)
    mocks["news"].get_latest.return_value = []

    overview = facade.get_market_overview(
        cities=["London"], tickers=["AAPL"], crypto_symbols=["BTC"]
    )

    assert overview.weather[0].city == "London"
    assert overview.stocks[0].ticker == "AAPL"
    assert overview.cryptos[0].symbol == "BTC"


def test_get_market_overview_uses_cache_for_each_source() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["weather"].get_weather.return_value = WeatherInfo("Tokyo", 20.0, "Cloudy", 60)
    mocks["stock"].get_quote.return_value = StockQuote("GOOG", 140.0, -0.5)
    mocks["crypto"].get_quote.return_value = CryptoQuote("ETH", 3000.0, 1.0)
    mocks["news"].get_latest.return_value = []

    facade.get_market_overview(
        cities=["Tokyo"], tickers=["GOOG"], crypto_symbols=["ETH"]
    )

    assert (
        mocks["cache"].get_or_fetch.call_count == 4
    )  # weather + stock + crypto + news
    cache_keys = [call.args[0] for call in mocks["cache"].get_or_fetch.call_args_list]
    assert "weather:Tokyo" in cache_keys
    assert "stock:GOOG" in cache_keys
    assert "crypto:ETH" in cache_keys


def test_get_portfolio_summary_computes_market_value() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["stock"].get_quote.return_value = StockQuote("AAPL", 100.0, 0.0)

    portfolio = facade.get_portfolio_summary({"AAPL": 10})

    assert portfolio.holdings[0].market_value == 1000.0
    assert portfolio.total_value == 1000.0


def test_get_portfolio_summary_sums_multiple_holdings() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["stock"].get_quote.side_effect = [
        StockQuote("AAPL", 100.0, 0.0),
        StockQuote("GOOG", 50.0, 0.0),
    ]

    portfolio = facade.get_portfolio_summary({"AAPL": 2, "GOOG": 4})

    assert portfolio.total_value == 400.0


def test_refresh_all_clears_the_cache() -> None:
    facade, mocks = _make_facade_with_mocks()

    facade.refresh_all()

    mocks["cache"].clear.assert_called_once()
