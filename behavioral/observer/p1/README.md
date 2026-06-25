# P1 — Real-time Stock Ticker (Observer Pattern)

**Framework:** FastAPI + WebSocket + Redis PubSub  
**Domínio:** `stock_ticker`

## Observer Pattern UML

```
        ┌─────────────────────────────┐
        │      «interface»            │
        │       StockMarket           │
        │─────────────────────────────│
        │ +subscribe(obs, tickers)    │
        │ +unsubscribe(obs)           │
        │ +notify(ticker, price, pct) │
        └────────────┬────────────────┘
                     │ implements
        ┌────────────▼────────────────┐
        │    RedisStockMarket         │  ← ConcreteSubject
        │─────────────────────────────│
        │ - _subscriptions: dict      │
        │ - _redis_url: str           │
        │ + start() / stop()          │
        └─────────────────────────────┘
                     │ notify()
         ┌───────────┼───────────┐
         ▼           ▼           ▼
  ┌─────────────┐ ┌──────────┐ ┌──────────────┐
  │«interface»  │ │          │ │              │
  │StockObserver│ │ Alert    │ │  Logging     │
  │─────────────│ │ Observer │ │  Observer    │
  │+update(evt) │ │          │ │              │
  └──────┬──────┘ └──────────┘ └──────────────┘
         │ implements
  ┌──────▼──────────┐
  │ WebSocket       │  ← ConcreteObserver
  │ Observer        │
  └─────────────────┘
```

## SOLID Principles

| Princípio | Onde aparece |
|-----------|-------------|
| **OCP** | Novos observers estendem `StockObserver` sem alterar `RedisStockMarket` |
| **DIP** | `SubscribeToTickersUseCase` depende de `StockMarket` (ABC), não de `RedisStockMarket` |
| **SRP** | `WebSocketObserver` só faz push WS; `AlertObserver` só detecta thresholds; `LoggingObserver` só loga |
| **LSP** | Todos observers são substituíveis por `StockObserver` |

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| WS | `/ws/stocks?tickers=AAPL,MSFT` | Stream de preços em tempo real |
| GET | `/stocks/{ticker}/price` | Preço atual do ticker |
| POST | `/alerts` | Cadastrar alerta de variação |
| GET | `/alerts/triggered` | Alertas disparados |

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

Conectar via WebSocket:
```bash
wscat -c "ws://localhost:8000/ws/stocks?tickers=AAPL,TSLA"
```

## Testes

```bash
pip install -e ".[dev]"
pytest
```
