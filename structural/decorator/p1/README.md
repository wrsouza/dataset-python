# HTTP Middleware Pipeline

> **Design Pattern:** Decorator (GoF Structural)
> **Categoria:** Structural
> **Framework:** FastAPI
> **Serviços:** (nenhum externo — cache em memória)

## Objetivo Pedagógico

Demonstra o padrão Decorator GoF aplicado a um pipeline de middleware HTTP real.
O aluno aprenderá como adicionar Auth, RateLimit, Cache, Logging e Compressão como
camadas independentes, reordenáveis em runtime sem alterar a lógica de negócio,
aplicando os princípios OCP e SRP.

## O Pattern em Ação

| Papel do Pattern    | Classe                    | Arquivo                                      |
|---------------------|---------------------------|----------------------------------------------|
| Component (ABC)     | `RequestHandler`          | `src/middleware/domain/interfaces.py`        |
| Decorator ABC       | `RequestHandlerDecorator` | `src/middleware/domain/interfaces.py`        |
| ConcreteComponent   | `BaseRequestHandler`      | `src/middleware/application/use_cases.py`    |
| ConcreteDecorator   | `AuthDecorator`           | `src/middleware/infrastructure/decorators.py`|
| ConcreteDecorator   | `RateLimitDecorator`      | `src/middleware/infrastructure/decorators.py`|
| ConcreteDecorator   | `LoggingDecorator`        | `src/middleware/infrastructure/decorators.py`|
| ConcreteDecorator   | `CacheDecorator`          | `src/middleware/infrastructure/decorators.py`|
| ConcreteDecorator   | `CompressionDecorator`    | `src/middleware/infrastructure/decorators.py`|

## Diagrama UML — Cadeia de Decoradores

```
<<abstract>>
RequestHandler
+ handle(request: ConcreteHTTPRequest) -> ConcreteHTTPResponse
        |
        ├── BaseRequestHandler          (ConcreteComponent)
        │     + handle(...)
        │
        └── RequestHandlerDecorator    (Decorator ABC)
              - _wrapped: RequestHandler
              + handle(...) -> delegates to _wrapped
                    |
                    ├── AuthDecorator
                    │     verifica JWT antes de delegar
                    │
                    ├── RateLimitDecorator
                    │     controla req/min por IP
                    │
                    ├── LoggingDecorator
                    │     loga req/resp com timing
                    │
                    ├── CacheDecorator
                    │     cache in-memory com TTL
                    │
                    └── CompressionDecorator
                          gzip quando cliente aceita

Composição em runtime (outer -> inner):
  CompressionDecorator(
    LoggingDecorator(
      CacheDecorator(
        RateLimitDecorator(
          AuthDecorator(
            BaseRequestHandler()
          )
        )
      )
    )
  )
```

## Composição em Código

```python
# Full pipeline (src/middleware/application/use_cases.py)
handler = BaseRequestHandler()
handler = AuthDecorator(handler)
handler = RateLimitDecorator(handler, max_requests_per_minute=60)
handler = CacheDecorator(handler, ttl_seconds=30)
handler = LoggingDecorator(handler)
handler = CompressionDecorator(handler)

# Public pipeline (sem Auth)
handler = BaseRequestHandler()
handler = RateLimitDecorator(handler, max_requests_per_minute=120)
handler = LoggingDecorator(handler)
handler = CompressionDecorator(handler)
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Novo comportamento (ex: TracingDecorator) = novo arquivo,
  sem alterar `RequestHandler`, `BaseRequestHandler` ou qualquer decorator existente.
- **S — Single Responsibility:** Cada decorator encapsula exatamente uma
  preocupação transversal (auth, rate limit, cache, log, compressão).
- **D — Dependency Inversion:** `RequestHandlerDecorator` depende da abstração
  `RequestHandler`, não de implementações concretas.

## Estrutura do Projeto

```
p1/
├── src/
│   ├── main.py                              ← FastAPI app
│   └── middleware/
│       ├── domain/
│       │   ├── interfaces.py               ← RequestHandler ABC, Decorator ABC
│       │   └── entities.py                 ← ConcreteHTTPRequest/Response, erros
│       ├── application/
│       │   └── use_cases.py               ← BaseRequestHandler, build_*_pipeline()
│       └── infrastructure/
│           └── decorators.py              ← Auth, RateLimit, Logging, Cache, Compression
├── tests/
│   ├── unit/test_decorators.py
│   └── integration/test_api.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API: http://localhost:8000/docs
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/unit/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável                  | Descrição                  | Padrão  |
|---------------------------|----------------------------|---------|
| `JWT_SECRET`              | Segredo para validar JWT   | —       |
| `RATE_LIMIT_PER_MINUTE`   | Máximo req/min por IP      | `60`    |
| `CACHE_TTL_SECONDS`       | TTL do cache em memória    | `30`    |
| `LOG_LEVEL`               | Nível de log               | `INFO`  |
