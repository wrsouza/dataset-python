"""FastAPI application entry-point for the Stock Ticker service."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from stock_ticker.application.use_cases import (
    CreateAlertRuleUseCase,
    SubscribeToTickersUseCase,
    UnsubscribeObserverUseCase,
)
from stock_ticker.infrastructure.observers import (
    AlertObserver,
    LoggingObserver,
    WebSocketObserver,
)
from stock_ticker.infrastructure.redis_subject import RedisStockMarket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Composition root: concrete subjects/observers wired here (DIP)
market = RedisStockMarket(redis_url=REDIS_URL)
logging_observer = LoggingObserver()
alert_observer = AlertObserver(rules=[])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    market.subscribe(logging_observer, ["AAPL", "MSFT", "GOOG", "AMZN", "META", "TSLA"])
    await market.start()
    yield
    await market.stop()


app = FastAPI(
    title="Real-time Stock Ticker",
    description="Observer pattern: Subject=RedisStockMarket, Observers=WebSocket/Alert/Logging",
    version="1.0.0",
    lifespan=lifespan,
)


# ── REST endpoints ────────────────────────────────────────────────────────────

class AlertRequest(BaseModel):
    ticker: str
    threshold_pct: float
    webhook_url: str | None = None


@app.get("/stocks/{ticker}/price")
async def get_price(ticker: str) -> dict[str, object]:
    price = market.get_price(ticker.upper())
    if price is None:
        return {"error": "ticker not found"}
    return {"ticker": ticker.upper(), "price": price}


@app.post("/alerts", status_code=201)
async def create_alert(request: AlertRequest) -> dict[str, object]:
    use_case = CreateAlertRuleUseCase()
    rule = use_case.execute(
        ticker=request.ticker,
        threshold_pct=request.threshold_pct,
        webhook_url=request.webhook_url,
    )
    # Extend the global alert observer's rules without changing its class (OCP)
    alert_observer._rules.append(rule)
    if alert_observer not in [
        obs
        for observers in market._subscriptions.values()
        for obs in observers
    ]:
        market.subscribe(alert_observer, [rule.ticker])
    return {"alert_id": rule.alert_id, "ticker": rule.ticker, "threshold_pct": rule.threshold_pct}


@app.get("/alerts/triggered")
async def get_triggered_alerts() -> list[dict[str, object]]:
    return alert_observer.triggered_alerts


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws/stocks")
async def websocket_stocks(websocket: WebSocket, tickers: str = "AAPL") -> None:
    await websocket.accept()
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    client_id = id(websocket)

    ws_observer = WebSocketObserver(websocket=websocket, client_id=str(client_id))
    subscribe_use_case = SubscribeToTickersUseCase(market)
    unsubscribe_use_case = UnsubscribeObserverUseCase(market)

    subscribe_use_case.execute(ws_observer, ticker_list)
    logger.info("WS client %s subscribed to %s", client_id, ticker_list)

    try:
        while True:
            # Keep connection alive; updates come via observer.update()
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WS client %s disconnected", client_id)
    finally:
        unsubscribe_use_case.execute(ws_observer)
