"""ConcreteSubject: Redis PubSub-backed stock market.

Uses Redis Pub/Sub to broadcast price ticks across multiple
app instances, then notifies local in-process observers.
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
from collections import defaultdict
from datetime import datetime, timezone

import redis.asyncio as aioredis

from stock_ticker.domain.entities import StockEvent
from stock_ticker.domain.interfaces import StockMarket, StockObserver

logger = logging.getLogger(__name__)

CHANNEL_PREFIX = "stock:"
TICKERS = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "TSLA"]


class RedisStockMarket(StockMarket):
    """ConcreteSubject: distributes events via Redis PubSub.

    - publish() serialises a StockEvent to JSON and pushes to Redis channel.
    - A subscriber loop deserialises and fans out to local StockObserver instances.
    - Each app instance holds its own observer registry; Redis decouples producers.
    """

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        # ticker -> list of observers interested in that ticker
        self._subscriptions: dict[str, list[StockObserver]] = defaultdict(list)
        self._prices: dict[str, float] = {t: 100.0 + random.uniform(-10, 10) for t in TICKERS}
        self._running = False
        self._tasks: list[asyncio.Task[None]] = []

    # ── Subject interface ────────────────────────────────────────────────────

    def subscribe(
        self,
        observer: StockObserver,
        tickers: list[str],
    ) -> None:
        for ticker in tickers:
            if observer not in self._subscriptions[ticker.upper()]:
                self._subscriptions[ticker.upper()].append(observer)

    def unsubscribe(self, observer: StockObserver) -> None:
        for observers in self._subscriptions.values():
            if observer in observers:
                observers.remove(observer)

    async def notify(self, ticker: str, price: float, change_pct: float) -> None:
        event = StockEvent(ticker=ticker, price=price, change_pct=change_pct)
        for observer in list(self._subscriptions.get(ticker, [])):
            try:
                await observer.update(event)
            except Exception:
                logger.exception("Observer %s failed for %s", observer, ticker)

    # ── Redis integration ─────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start price-generator and Redis subscriber tasks."""
        self._running = True
        self._tasks = [
            asyncio.create_task(self._price_generator()),
            asyncio.create_task(self._redis_subscriber()),
        ]

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _price_generator(self) -> None:
        """Background task: generates random price ticks every second."""
        client = aioredis.from_url(self._redis_url, decode_responses=True)
        try:
            while self._running:
                await asyncio.sleep(1.0)
                ticker = random.choice(TICKERS)
                old_price = self._prices[ticker]
                change_pct = random.uniform(-3.0, 3.0)
                new_price = round(old_price * (1 + change_pct / 100), 2)
                self._prices[ticker] = new_price

                payload = {
                    "ticker": ticker,
                    "price": new_price,
                    "change_pct": round(change_pct, 4),
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                }
                channel = f"{CHANNEL_PREFIX}{ticker}"
                await client.publish(channel, json.dumps(payload))
                logger.debug("Published %s @ %.2f (%.2f%%)", ticker, new_price, change_pct)
        finally:
            await client.aclose()

    async def _redis_subscriber(self) -> None:
        """Background task: consumes Redis PubSub and fans out to observers."""
        client = aioredis.from_url(self._redis_url, decode_responses=True)
        pubsub = client.pubsub()
        channels = [f"{CHANNEL_PREFIX}{t}" for t in TICKERS]
        await pubsub.subscribe(*channels)
        try:
            async for message in pubsub.listen():
                if not self._running:
                    break
                if message["type"] != "message":
                    continue
                data = json.loads(message["data"])
                await self.notify(
                    ticker=data["ticker"],
                    price=data["price"],
                    change_pct=data["change_pct"],
                )
        finally:
            await pubsub.unsubscribe()
            await client.aclose()

    def get_price(self, ticker: str) -> float | None:
        return self._prices.get(ticker.upper())
