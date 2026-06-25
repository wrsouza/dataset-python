# Lazy QuerySet Iterator (Iterator) — P3

Django app que expõe um catálogo de produtos via paginação por keyset
(`GET /products/`) e um agregador por categoria que percorre o catálogo
inteiro através de um Iterator GoF genuíno (`GET /products/category-summary/`),
sem nunca materializar a queryset inteira em memória.

## Objetivo pedagógico

Demonstrar o pattern **Iterator** sobre o Django ORM: o cliente percorre o
catálogo inteiro chamando apenas `has_next()`/`next()`, sem nunca saber que,
por baixo, o `LazyProductIterator` está buscando lotes de `chunk_size`
produtos via `id__gt=cursor` — uma alternativa explícita ao `OFFSET`, que
ficaria cada vez mais lento à medida que a tabela cresce.

Elementos do pattern:
- **Iterator (abstrato):** `ProductIterator` (`domain/interfaces.py`)
- **Concrete Iterator:** `LazyProductIterator` — mantém um buffer interno e busca o próximo lote só quando o buffer esvazia
- **Aggregate:** `ProductRepository` / `DjangoProductRepository` — fornece os dados crus via keyset pagination, sem saber nada sobre iteração
- **Client:** `SummarizeByCategoryUseCase`, que consome o iterator com um laço `while has_next(): next()` para agregar por categoria

## Diagrama (ASCII)

```
GET /products/category-summary/
      │
      ▼
SummarizeByCategoryUseCase ──cria──► LazyProductIterator(repository, chunk_size=500)
      │                                       │
      │  while iterator.has_next():           │
      │      p = iterator.next()              │
      │      counts[p.category] += 1          │
      │                                       ▼
      │                    buffer vazio? ──sim──► repository.fetch_chunk(cursor, 500) ──► MySQL (id > cursor)
      ▼
[{"category": "books", "product_count": 42, "total_price": 1234.5}, ...]
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                            | Descrição                                          |
|--------|----------------------------------|-------------------------------------------------------|
| GET    | `/products/`                     | Uma página de produtos (`?cursor=&limit=`)              |
| GET    | `/products/category-summary/`    | Agregação por categoria do catálogo inteiro, via Iterator |

```bash
curl "http://localhost:8000/products/?limit=50"
curl "http://localhost:8000/products/category-summary/"
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** `LazyProductIterator` só sabe iterar; `DjangoProductRepository` só sabe buscar lotes; nenhum dos dois conhece o outro além do contrato `ProductRepository`.
- **OCP:** trocar a fonte de dados (ex.: outra tabela ou view materializada) = criar uma nova `ProductRepository`, sem tocar no `LazyProductIterator` nem nos use cases.
- **LSP:** qualquer `ProductIterator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `has_next`/`next`.
- **ISP:** `ProductIterator` e `ProductRepository` são interfaces pequenas e focadas.
- **DIP:** `SummarizeByCategoryUseCase` e `ListProductsPageUseCase` dependem de `ProductRepository` (abstração), não do Django ORM diretamente.
