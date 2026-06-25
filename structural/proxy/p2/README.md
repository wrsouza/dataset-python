# P2 — API Cache Proxy

**Pattern:** Proxy (Cache Proxy)  
**Framework:** Flask + Redis  
**Domain:** `cache_proxy`

---

## UML — Proxy Pattern

```
┌─────────────────────────────────────┐
│  «Protocol»                         │
│  ExternalAPIService                 │
│─────────────────────────────────────│
│  + get_weather(city) → WeatherData  │
│  + get_exchange_rate(f, t) → float  │
│  + get_stock_price(ticker) → Stock  │
└──────────────┬──────────────────────┘
               │ implements
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼────────────────────┐
│ MockExternal│  │ RedisCacheProxy            │
│ APIService  │  │────────────────────────────│
│ (RealSubject│  │ - _wrapped: ExternalAPI... │
│─────────────│  │ - _redis: Redis            │
│ + get_weath │  │ - _stats: CacheStats       │
│ + get_exch  │◄─│────────────────────────────│
│ + get_stock │  │ + get_weather(city)        │
└─────────────┘  │ + get_exchange_rate(f, t)  │
                 │ + get_stock_price(ticker)  │
                 │ + get_stats() → CacheStats │
                 │ + flush() → int            │
                 └────────────────────────────┘
```

## SOLID Principles Applied

| Principle | Where |
|-----------|-------|
| **OCP** | New API methods extend `ExternalAPIService` without changing `RedisCacheProxy` logic |
| **DIP** | `RedisCacheProxy` depends on `ExternalAPIService` (Protocol), not `MockExternalAPIService` |
| **LSP** | `RedisCacheProxy` is fully substitutable for `MockExternalAPIService` — same interface, richer behavior |
| **SRP** | Proxy only manages caching; real subject only fetches data |

## Cache TTLs

| Endpoint | TTL | Reason |
|----------|-----|--------|
| `/weather/{city}` | 300 s | Weather changes every few minutes |
| `/exchange/{from}/{to}` | 3600 s | Rates fluctuate hourly |
| `/stocks/{ticker}` | 60 s | Volatile prices need fresher data |

## Routes

```
GET  /weather/{city}        → WeatherData JSON
GET  /exchange/{from}/{to}  → {"from", "to", "rate"}
GET  /stocks/{ticker}       → StockData JSON
GET  /cache/stats           → {"hits", "misses", "total", "hit_rate"}
DELETE /cache/flush         → {"keys_removed": N}
```

## How to Run

```bash
# 1. Copy and configure env
cp .env.example .env

# 2. Start services
docker-compose up --build

# 3. Hit the API (first call is slow — real subject; second is fast — cache)
curl http://localhost:5000/weather/london
curl http://localhost:5000/weather/london   # cache hit

curl http://localhost:5000/exchange/USD/BRL
curl http://localhost:5000/stocks/AAPL

# 4. Check stats
curl http://localhost:5000/cache/stats

# 5. Flush cache
curl -X DELETE http://localhost:5000/cache/flush
```

## Run Tests

```bash
pip install -e ".[dev]"
pytest
```
