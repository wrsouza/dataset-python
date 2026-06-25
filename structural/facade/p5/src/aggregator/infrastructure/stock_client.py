"""Mock stock-quote API — deterministic synthetic data, no real network call."""

from __future__ import annotations

from aggregator.domain.entities import StockQuote


def _seed(text: str) -> int:
    return sum(ord(char) for char in text)


class MockStockAPIClient:
    def get_quote(self, ticker: str) -> StockQuote:
        seed = _seed(ticker)
        price = round(50 + (seed % 500) + (seed % 100) / 100, 2)
        change_pct = round(((seed % 21) - 10) / 2, 2)
        return StockQuote(ticker=ticker, price=price, change_pct=change_pct)
