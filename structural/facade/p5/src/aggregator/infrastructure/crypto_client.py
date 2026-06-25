"""Mock crypto-quote API — deterministic synthetic data, no real network call."""

from __future__ import annotations

from aggregator.domain.entities import CryptoQuote


def _seed(text: str) -> int:
    return sum(ord(char) for char in text)


class MockCryptoAPIClient:
    def get_quote(self, symbol: str) -> CryptoQuote:
        seed = _seed(symbol)
        price_usd = round(100 + (seed % 60000) + (seed % 100) / 100, 2)
        change_pct_24h = round(((seed % 41) - 20) / 2, 2)
        return CryptoQuote(
            symbol=symbol, price_usd=price_usd, change_pct_24h=change_pct_24h
        )
