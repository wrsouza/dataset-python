"""Streamlit dashboard — the Client in this Facade demo.

The UI only ever calls DataAggregatorFacade methods; it never imports a
weather/stock/crypto/news client or the cache directly.
"""

from __future__ import annotations

import streamlit as st

from aggregator.application.facade import DataAggregatorFacade
from aggregator.infrastructure.cache_manager import InMemoryCacheManager
from aggregator.infrastructure.crypto_client import MockCryptoAPIClient
from aggregator.infrastructure.news_client import MockNewsAPIClient
from aggregator.infrastructure.stock_client import MockStockAPIClient
from aggregator.infrastructure.weather_client import MockWeatherAPIClient


@st.cache_resource
def get_facade() -> DataAggregatorFacade:
    """Composition root: the only place wiring concrete clients together."""
    return DataAggregatorFacade(
        weather_client=MockWeatherAPIClient(),
        stock_client=MockStockAPIClient(),
        crypto_client=MockCryptoAPIClient(),
        news_client=MockNewsAPIClient(),
        cache=InMemoryCacheManager(),
    )


def render_market_section(facade: DataAggregatorFacade) -> None:
    st.subheader("Market Overview")
    cities = st.multiselect(
        "Cities", ["London", "Tokyo", "São Paulo", "New York"], default=["London"]
    )
    tickers = st.multiselect(
        "Stocks", ["AAPL", "GOOG", "MSFT", "AMZN"], default=["AAPL"]
    )
    cryptos = st.multiselect("Crypto", ["BTC", "ETH", "SOL"], default=["BTC"])

    if st.button("Load Market Overview") and (cities or tickers or cryptos):
        overview = facade.get_market_overview(cities, tickers, cryptos)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Weather**")
            for w in overview.weather:
                st.metric(w.city, f"{w.temperature_c}°C", w.condition)
        with col2:
            st.write("**Stocks**")
            for s in overview.stocks:
                st.metric(s.ticker, f"${s.price}", f"{s.change_pct}%")
        with col3:
            st.write("**Crypto**")
            for c in overview.cryptos:
                st.metric(c.symbol, f"${c.price_usd}", f"{c.change_pct_24h}%")

        st.write("**News**")
        for item in overview.news:
            st.write(f"- {item.title} ({item.source})")


def render_portfolio_section(facade: DataAggregatorFacade) -> None:
    st.subheader("Portfolio Summary")
    ticker = st.text_input("Ticker", value="AAPL")
    quantity = st.number_input("Quantity", min_value=0.0, value=10.0)

    if "assets" not in st.session_state:
        st.session_state["assets"] = {}

    if st.button("Add Holding") and ticker:
        st.session_state["assets"][ticker] = quantity

    if st.session_state["assets"]:
        portfolio = facade.get_portfolio_summary(st.session_state["assets"])
        for holding in portfolio.holdings:
            st.write(
                f"{holding.symbol}: {holding.quantity} @ ${holding.current_price} "
                f"= ${holding.market_value:.2f}"
            )
        st.metric("Total Portfolio Value", f"${portfolio.total_value:.2f}")


def main() -> None:
    st.title("Multi-API Aggregator — Facade Pattern")
    st.caption("DataAggregatorFacade hides 4 API clients + a cache behind 3 methods.")

    facade = get_facade()

    if st.button("Refresh All (clear cache)"):
        facade.refresh_all()
        st.success("Cache cleared — next load will re-fetch every source.")

    render_market_section(facade)
    render_portfolio_section(facade)


if __name__ == "__main__":
    main()
