"""Mock news API — deterministic synthetic data, no real network call."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from aggregator.domain.entities import NewsItem

_SOURCES = ["MarketWatch", "Reuters", "Bloomberg", "FinancialTimes"]


def _seed(text: str) -> int:
    return sum(ord(char) for char in text)


class MockNewsAPIClient:
    def get_latest(self, topic: str, limit: int) -> list[NewsItem]:
        seed = _seed(topic)
        now = datetime.now(UTC)
        return [
            NewsItem(
                title=f"{topic.title()} update #{i + 1}",
                source=_SOURCES[(seed + i) % len(_SOURCES)],
                published_at=now - timedelta(hours=i),
            )
            for i in range(limit)
        ]
