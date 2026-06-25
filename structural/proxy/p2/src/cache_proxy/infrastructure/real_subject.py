"""RealSubject: MockExternalAPIService.

Simulates a real external API with realistic latency (time.sleep(0.5))
and randomly generated but believable data.
"""

from __future__ import annotations

import random
import time

from cache_proxy.domain.entities import StockData, WeatherData

_WEATHER_DESCRIPTIONS = [
    "Clear sky",
    "Partly cloudy",
    "Overcast",
    "Light rain",
    "Heavy thunderstorm",
    "Fog",
    "Sunny intervals",
]

_EXCHANGE_BASE_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "BRL": 5.10,
    "GBP": 0.79,
    "JPY": 149.50,
    "CAD": 1.36,
    "AUD": 1.52,
}

_STOCK_BASE_PRICES: dict[str, float] = {
    "AAPL": 178.50,
    "GOOGL": 141.20,
    "MSFT": 378.90,
    "AMZN": 182.30,
    "TSLA": 248.10,
}
_DEFAULT_STOCK_PRICE = 100.0


def _simulate_latency() -> None:
    """Simulate realistic external API response time."""
    time.sleep(0.5)


class MockExternalAPIService:
    """RealSubject: simulates an external data API.

    Every call introduces 0.5 s of artificial latency to demonstrate
    the caching proxy's value. Data is randomised around realistic base
    values so responses look plausible without requiring a live API key.
    """

    def get_weather(self, city: str) -> WeatherData:
        """Return simulated weather data for the requested city."""
        _simulate_latency()
        return WeatherData(
            city=city,
            temperature_c=round(random.uniform(-5.0, 40.0), 1),
            humidity_percent=round(random.uniform(20.0, 95.0), 1),
            description=random.choice(_WEATHER_DESCRIPTIONS),
            wind_speed_kmh=round(random.uniform(0.0, 80.0), 1),
        )

    def get_exchange_rate(self, from_cur: str, to_cur: str) -> float:
        """Return simulated exchange rate between two currencies."""
        _simulate_latency()
        from_rate = _EXCHANGE_BASE_RATES.get(from_cur.upper(), 1.0)
        to_rate = _EXCHANGE_BASE_RATES.get(to_cur.upper(), 1.0)
        # Convert via USD as base; add small random fluctuation (±0.5 %)
        base_rate = to_rate / from_rate
        fluctuation = random.uniform(-0.005, 0.005)
        return round(base_rate * (1 + fluctuation), 6)

    def get_stock_price(self, ticker: str) -> StockData:
        """Return simulated stock data for the requested ticker."""
        _simulate_latency()
        base = _STOCK_BASE_PRICES.get(ticker.upper(), _DEFAULT_STOCK_PRICE)
        price = round(base * random.uniform(0.97, 1.03), 2)
        change = round(random.uniform(-5.0, 5.0), 2)
        return StockData(
            ticker=ticker.upper(),
            price_usd=price,
            change_percent=change,
            volume=random.randint(1_000_000, 50_000_000),
            market_cap_billions=round(price * random.uniform(0.5, 10.0), 2),
        )
