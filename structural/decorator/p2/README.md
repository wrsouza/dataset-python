# P2 — Cache Decorator API

**Pattern:** Decorator (GoF) | **Categoria:** Structural
**Framework:** Flask | **Serviços:** Redis
**Domínio:** `cache_decorator`

## Objetivo Pedagógico

Demonstrar o pattern **Decorator** envolvendo um serviço de consulta de
cotações de produtos. O aluno deve conseguir identificar: o **Component**
(`DataService`), o **ConcreteComponent** (`ProductQuoteService`), o
**Decorator** abstrato (`DataServiceDecorator`) e três
**ConcreteDecorators** (`RedisCacheDecorator`, `LoggingDecorator`,
`RetryDecorator`) — todos empilháveis livremente, sem alterar o
serviço base.

## O Pattern Aplicado

A API expõe `GET /quotes/<product_id>`, que busca a cotação de um produto
através de uma cadeia de decoradores construída em
`infrastructure/factory.py`:

```
RetryDecorator(LoggingDecorator(RedisCacheDecorator(ProductQuoteService())))
```

Cada decorador adiciona um comportamento ortogonal sem tocar nos demais:

- **RedisCacheDecorator** — verifica o Redis antes de delegar; em cache
  hit, retorna o `DataResult` cacheado sem chamar o `wrapped`; em miss,
  delega, armazena o resultado com TTL configurável.
- **LoggingDecorator** — loga início, fim e duração de cada chamada
  (incluindo falhas), sem saber nada sobre cache ou retry.
- **RetryDecorator** — reexecuta a chamada ao `wrapped` em caso de
  exceção, com número de tentativas e backoff configuráveis.

O `ProductQuoteService` (ConcreteComponent) simula uma pequena latência
(`time.sleep`) para tornar o efeito do cache visível em testes/logs.

## Diagrama UML (ASCII)

```
                  ┌─────────────────────────────┐
                  │ «ABC» DataService            │
                  │ (Component)                  │
                  │───────────────────────────────│
                  │ + get_data(query) → DataResult│
                  └───────────────┬───────────────┘
                                  │ implements
            ┌─────────────────────┼─────────────────────┐
            │                                            │
┌───────────▼────────────┐         ┌──────────────────────▼─────────────┐
│ ProductQuoteService     │         │ «ABC» DataServiceDecorator         │
│ (ConcreteComponent)     │         │ (Decorator)                        │
│─────────────────────────│         │─────────────────────────────────────│
│ + get_data(query)       │◄────────┤ - _wrapped: DataService             │
│   (catálogo em memória) │  wraps  │ + get_data(query) → delega         │
└─────────────────────────┘         └──────────────────┬──────────────────┘
                                                          │ extends
                          ┌───────────────────────────────┼───────────────────────────────┐
                          │                               │                               │
              ┌───────────▼──────────┐        ┌───────────▼──────────┐        ┌───────────▼──────────┐
              │ RedisCacheDecorator  │        │ LoggingDecorator      │        │ RetryDecorator        │
              │ (ConcreteDecorator)  │        │ (ConcreteDecorator)   │        │ (ConcreteDecorator)   │
              │───────────────────────│        │───────────────────────│        │───────────────────────│
              │ - _redis: Redis       │        │ + get_data(): loga    │        │ - max_attempts        │
              │ - _ttl_seconds        │        │   início/fim/duração  │        │ - backoff_seconds     │
              │ + get_data(): cache   │        │                       │        │ + get_data(): retenta │
              │   hit/miss            │        │                       │        │   em caso de exceção  │
              └───────────────────────┘        └───────────────────────┘        └───────────────────────┘
```

Composição usada pela API (de fora para dentro):
`RetryDecorator → LoggingDecorator → RedisCacheDecorator → ProductQuoteService`

## Princípios SOLID Demonstrados

| Princípio | Onde aparece |
|-----------|--------------|
| **S — SRP** | Cada decorador tem uma única responsabilidade: `RedisCacheDecorator` só decide cache, `LoggingDecorator` só loga, `RetryDecorator` só retenta. |
| **O — OCP** | Novos decoradores (ex.: métricas) são adicionados como novas classes em `infrastructure/`, sem modificar `ProductQuoteService` nem os decoradores existentes — basta uma linha em `factory.py`. |
| **L — LSP** | `DataServiceDecorator` e todas as suas subclasses implementam `DataService`; qualquer decorador (ou pilha de decoradores) é substituível pelo `ProductQuoteService` original sem surpresas para o cliente. |
| **I — ISP** | `DataService` tem um único método (`get_data`) — interface mínima e focada, sem métodos não utilizados. |
| **D — DIP** | `GetProductQuoteUseCase` (application) depende apenas da abstração `DataService`; a composição concreta (Redis, decoradores) acontece exclusivamente em `infrastructure/factory.py` e `app.py` (composition root). |

## Nota sobre `domain/interfaces.py`

O arquivo originalmente trazia o import de `DataQuery`/`DataResult` no
**final** do módulo, com `# noqa: E402, F401`, para "evitar" um ciclo de
importação. Esse ciclo não existe de fato: `domain/entities.py` não
importa nada de `domain/interfaces.py`. O import foi movido para o topo
do arquivo (ordem convencional stdlib → local) e o `noqa` foi removido,
conforme `docs/standards/clean_code.md` (seção "Organização de
Módulos").

## Rotas

```
GET  /quotes/<product_id>   → {"product_id", "price", "currency", "fetched_at"}
GET  /health                → {"status": "ok"}
```

Catálogo de exemplo (in-memory, em
`infrastructure/product_quote_service.py`): `sku-001`, `sku-002`,
`sku-003`, `sku-004`.

## Como Rodar

```bash
# 1. Copiar e configurar variáveis de ambiente
cp .env.example .env

# 2. Subir os serviços
docker-compose up --build

# 3. Consultar a API (1ª chamada é mais lenta — miss; 2ª é cache hit)
curl http://localhost:5000/quotes/sku-001
curl http://localhost:5000/quotes/sku-001

curl http://localhost:5000/quotes/does-not-exist   # 404
curl http://localhost:5000/health
```

## Rodar os Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

Os testes de integração usam `fakeredis` injetado em `create_app()`, então
não dependem de um Redis real em execução.
