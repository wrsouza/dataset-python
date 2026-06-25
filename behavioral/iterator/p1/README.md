# Cursor Pagination API (Iterator) — P1

API FastAPI que expõe uma coleção de pedidos (`orders`) de duas formas:
paginação por cursor convencional (`GET /orders`) e exportação completa via
um Iterator GoF genuíno que busca páginas do PostgreSQL sob demanda
(`GET /orders/export`).

## Objetivo pedagógico

Demonstrar o pattern **Iterator**: o cliente percorre a coleção inteira
chamando apenas `has_next()`/`next()`, sem nunca saber que, por baixo, o
`CursorOrderIterator` está buscando lotes de `page_size` registros do
PostgreSQL com paginação por keyset (`order_id > cursor`).

Elementos do pattern:
- **Iterator (abstrato):** `OrderIterator` (`domain/interfaces.py`)
- **Concrete Iterator:** `CursorOrderIterator` — mantém um buffer interno e busca a próxima página só quando o buffer esvazia
- **Aggregate:** `OrderRepository` / `PostgresOrderRepository` — fornece os dados crus, sem saber nada sobre iteração
- **Client:** `ExportAllOrdersUseCase`, que consome o iterator com um laço `while has_next(): next()`

## Diagrama (ASCII)

```
GET /orders/export
      │
      ▼
ExportAllOrdersUseCase ──cria──► CursorOrderIterator(repository, page_size=100)
      │                                  │
      │  while iterator.has_next():      │
      │      yield iterator.next()       │
      │                                  ▼
      │                    buffer vazio? ──sim──► repository.fetch_page(cursor, 100) ──► PostgreSQL
      ▼
StreamingResponse (NDJSON, um pedido por linha, sem carregar tudo em memória)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000` (Swagger em `/docs`).

### Endpoints

| Método | Rota             | Descrição                                                  |
|--------|------------------|---------------------------------------------------------------|
| GET    | `/orders`        | Uma página de pedidos (`?cursor=&limit=`)                      |
| GET    | `/orders/export` | Stream NDJSON de todos os pedidos, via Iterator                |
| GET    | `/health`        | Healthcheck                                                    |

```bash
curl "http://localhost:8000/orders?limit=20"
curl "http://localhost:8000/orders/export"
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes de `PostgresOrderRepository` usam um fake DB-API connection
(mesmo contrato `cursor()`/`execute()`/`fetchall()`); os de
`CursorOrderIterator` e da API usam um `FakeOrderRepository` em memória —
nenhuma chamada de rede real é feita.

## SOLID

- **SRP:** `CursorOrderIterator` só sabe iterar; `PostgresOrderRepository` só sabe buscar páginas; nenhum dos dois conhece o outro além do contrato `OrderRepository`.
- **OCP:** trocar a fonte de dados (ex.: MongoDB) = criar uma nova `OrderRepository`, sem tocar no `CursorOrderIterator` nem nos use cases.
- **LSP:** qualquer `OrderIterator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `has_next`/`next`.
- **ISP:** `OrderIterator` e `OrderRepository` são interfaces pequenas e focadas.
- **DIP:** `ExportAllOrdersUseCase` e `ListOrdersPageUseCase` dependem de `OrderRepository` (abstração); a API usa `Depends()` para injetar a implementação concreta, trocada por um fake nos testes via `app.dependency_overrides`.
