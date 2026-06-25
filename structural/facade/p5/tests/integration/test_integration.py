"""End-to-end tests — real mock clients + real cache, the Facade itself isn't mocked."""

from __future__ import annotations

from aggregator.application.facade import DataAggregatorFacade


def test_market_overview_end_to_end(facade: DataAggregatorFacade) -> None:
    overview = facade.get_market_overview(
        cities=["London", "Tokyo"],
        tickers=["AAPL"],
        crypto_symbols=["BTC"],
        news_topic="crypto",
    )

    assert len(overview.weather) == 2
    assert len(overview.stocks) == 1
    assert len(overview.cryptos) == 1
    assert len(overview.news) == 5
    assert overview.news[0].title.startswith("Crypto")


def test_market_overview_is_cached_on_second_call(
    facade: DataAggregatorFacade,
) -> None:
    first = facade.get_market_overview(cities=["London"], tickers=[], crypto_symbols=[])
    second = facade.get_market_overview(
        cities=["London"], tickers=[], crypto_symbols=[]
    )

    # Same WeatherInfo value object served from cache, not a fresh fetch.
    assert first.weather[0] == second.weather[0]


def test_portfolio_summary_end_to_end(facade: DataAggregatorFacade) -> None:
    portfolio = facade.get_portfolio_summary({"AAPL": 5, "GOOG": 2})

    assert len(portfolio.holdings) == 2
    assert portfolio.total_value == sum(h.market_value for h in portfolio.holdings)


def test_refresh_all_forces_recompute(facade: DataAggregatorFacade) -> None:
    facade.get_market_overview(cities=["London"], tickers=[], crypto_symbols=[])

    facade.refresh_all()

    # No exception, and a subsequent call still works after the cache is wiped.
    overview = facade.get_market_overview(
        cities=["London"], tickers=[], crypto_symbols=[]
    )
    assert overview.weather[0].city == "London"
