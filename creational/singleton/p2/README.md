# Cache Manager

> **Design Pattern:** Singleton | **Categoria:** Creational
> **Framework:** Flask | **Serviços:** Redis

## Objetivo Pedagógico

Este projeto demonstra o padrão **Singleton** aplicado a um gerenciador de
cache Redis thread-safe, compartilhado por todos os handlers de uma
aplicação Flask. O aluno aprenderá a implementar um Singleton seguro em
ambiente multi-thread usando `__new__` + `threading.Lock`, além de um
circuit breaker simples para tolerância a falhas do backend Redis.

## O Pattern Aplicado

`CacheManager` garante que **exatamente uma instância** exista durante todo
o ciclo de vida da aplicação. A primeira chamada a `CacheManager()` cria e
configura a instância (conexão com Redis); todas as chamadas subsequentes —
em qualquer rota, use case ou thread — retornam a mesma instância. Isso
evita múltiplas conexões redundantes com o Redis e centraliza o estado do
circuit breaker (CLOSED / OPEN / HALF_OPEN) e das estatísticas de
hits/misses em um único lugar.

## Diagrama UML (ASCII)

```
                  ┌────────────────────────────┐
                  │       CacheManager         │
                  ├────────────────────────────┤
                  │ - _instance: CacheManager  │  (ClassVar, único)
                  │ - _lock: threading.Lock    │
                  │ - _redis: RedisBackend     │
                  │ - _memory: InMemoryBackend │
                  │ - _circuit_state           │
                  ├────────────────────────────┤
                  │ + __new__(cls): CacheManager│ ← thread-safe (double-checked lock)
                  │ + configure(host, port)    │
                  │ + get(key)                 │
                  │ + set(key, value, ttl)     │
                  │ + delete(key)              │
                  │ + flush()                  │
                  │ + get_stats()              │
                  └──────────────┬─────────────┘
                                 │ usa (delega via Protocol CacheBackend)
                  ┌──────────────┴─────────────┐
                  │                            │
       ┌──────────▼─────────┐      ┌───────────▼──────────┐
       │   RedisBackend      │      │   InMemoryBackend     │
       │  (produção)         │      │  (fallback)           │
       └──────────────────────┘      └───────────────────────┘

Cliente (Flask routes / use cases)
        │
        │  cache = CacheManager()   ← sempre a MESMA instância
        ▼
   [CacheManager única para todo o processo]
```

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** `CacheManager` cuida apenas de
  cache + circuit breaker. A lógica de negócio (buscar produtos, montar
  resposta HTTP) fica nos use cases (`GetProductsUseCase`,
  `FlushCacheUseCase`, `GetCacheStatsUseCase`) e nas rotas Flask
  (`src/main.py`), nunca dentro do `CacheManager`.
- **D (Dependency Inversion):** a camada de aplicação (`use_cases.py`)
  depende apenas do Protocol `CacheManager` definido em
  `cache/domain/interfaces.py`, não da implementação concreta em
  `cache/infrastructure/singleton.py`. Isso permite testar os use cases
  com qualquer objeto que satisfaça o protocolo.
- **O (Open/Closed):** novos backends de cache (ex.: Memcached) podem ser
  adicionados criando uma nova classe que satisfaça o Protocol
  `CacheBackend` — sem modificar `CacheManager`. O decorator `@cached` em
  `main.py` também permite adicionar cache a novas rotas sem alterar o
  `CacheManager`.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

A API estará disponível em `http://localhost:5000`:

- `GET /products` — lista produtos (cache-aside, TTL 60s)
- `POST /cache/flush` — limpa o cache
- `GET /cache/stats` — estatísticas de hits/misses e estado do circuit breaker

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Ou localmente, com um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```
