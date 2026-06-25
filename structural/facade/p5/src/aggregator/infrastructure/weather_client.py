"""Mock weather API — deterministic synthetic data, no real network call.

Each provider in a real aggregator has its own response shape (dict vs XML
vs nested JSON); the Facade is what normalizes all of them into WeatherInfo
etc. before the caller ever sees the data.
"""

from __future__ import annotations

from aggregator.domain.entities import WeatherInfo

_CONDITIONS = ["Sunny", "Cloudy", "Rainy", "Windy", "Snowy"]


def _seed(text: str) -> int:
    return sum(ord(char) for char in text)


class MockWeatherAPIClient:
    def get_weather(self, city: str) -> WeatherInfo:
        seed = _seed(city)
        return WeatherInfo(
            city=city,
            temperature_c=float(10 + seed % 25),
            condition=_CONDITIONS[seed % len(_CONDITIONS)],
            humidity_pct=30 + seed % 60,
        )
