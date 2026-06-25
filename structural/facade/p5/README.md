# Multi-API Aggregator Facade

> **Design Pattern:** Facade | **Categoria:** Structural
> **Framework:** Streamlit | **Serviços:** —

## Objetivo Pedagógico

Demonstrar o padrão Facade agregando dados de 4 APIs externas (clima, ações,
criptomoedas, notícias) e um cache em uma interface única para o dashboard.
A UI Streamlit chama apenas `get_market_overview()`, `get_portfolio_summary()`
e `refresh_all()` — nunca os 4 clients individualmente.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Facade | `DataAggregatorFacade` | `src/aggregator/application/facade.py` |
| Subsystem: clima | `MockWeatherAPIClient` | `infrastructure/weather_client.py` |
| Subsystem: ações | `MockStockAPIClient` | `infrastructure/stock_client.py` |
| Subsystem: cripto | `MockCryptoAPIClient` | `infrastructure/crypto_client.py` |
| Subsystem: notícias | `MockNewsAPIClient` | `infrastructure/news_client.py` |
| Subsystem: cache | `InMemoryCacheManager` | `infrastructure/cache_manager.py` |
| Client | Streamlit UI | `src/main.py` |

## Diagrama UML (ASCII)

```
Client (main.py — Streamlit UI)
      │
      ▼
DataAggregatorFacade
      │  get_market_overview() / get_portfolio_summary() / refresh_all()
      ├──► WeatherAPIClient   (mock, dados sintéticos determinísticos)
      ├──► StockAPIClient     (mock)
      ├──► CryptoAPIClient    (mock)
      ├──► NewsAPIClient      (mock)
      └──► CacheManager       (TTL por fonte: clima 5min, ações 1min, cripto 30s, notícias 10min)
```

## Por que os clients são mocks determinísticos

Em produção cada provedor (OpenWeather, Alpha Vantage, CoinGecko, NewsAPI)
tem formato de resposta e regras de autenticação próprios — exatamente a
complexidade que a Facade existe para esconder. Para este dataset educacional,
os clients geram dados sintéticos a partir de um hash simples do identificador
de entrada (cidade/ticker/símbolo), garantindo resultados reprodutíveis nos
testes sem exigir chaves de API reais ou acesso à rede.

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** cada client cuida de uma única fonte de
  dados; `InMemoryCacheManager` só gerencia TTL e armazenamento.
- **D — Dependency Inversion:** `DataAggregatorFacade` depende dos `Protocol`s
  em `domain/interfaces.py`, nunca de `MockWeatherAPIClient` etc. diretamente
  — troque qualquer mock por uma implementação real sem alterar a Facade.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

Dashboard disponível em `http://localhost:8501`.

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente:

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`src/main.py` (a UI Streamlit) é excluído da cobertura — mesma convenção
usada nos demais projetos Streamlit deste dataset, já que interfaces
Streamlit não são testáveis com um test client unitário tradicional. A
lógica de agregação e cache em si tem 100% de cobertura.
