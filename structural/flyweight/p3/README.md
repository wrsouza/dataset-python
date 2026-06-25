# Product Catalog Cache — Flyweight Pattern

> **Design Pattern:** Flyweight | **Categoria:** Structural
> **Framework:** Django | **Serviços:** MySQL

## Objetivo Pedagógico

Demonstrar o padrão Flyweight em um catálogo de e-commerce: ~50 combinações
de `ProductType` (categoria + marca + imposto + classe de frete) são
compartilhadas por milhares de produtos. Em vez de cada `Product` duplicar
esses dados, ele guarda apenas uma referência ao `ProductType` compartilhado.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Flyweight (estado intrínseco, imutável) | `ProductType` | `src/catalog/domain/entities.py` |
| FlyweightFactory | `ProductTypeFactory` | `src/catalog/infrastructure/factory.py` |
| Context (estado extrínseco + referência ao Flyweight) | `Product` | `src/catalog/domain/entities.py` |
| Client | `PopulateProductsUseCase`, views | `application/use_cases.py`, `views.py` |

`ProductType` é um `@dataclass(frozen=True)` — category_name, brand, tax_rate,
shipping_class, return_policy. O mesmo objeto Python é compartilhado por
todos os produtos da mesma combinação categoria/marca.

## Diagrama UML (ASCII)

```
<<frozen dataclass>>
ProductType (Flyweight)
  category_name, brand, tax_rate, shipping_class, return_policy
        ▲
        │ shared reference (same object for same type_key)
        │
Product (Context)
  name, price, sku, stock ──► product_type: ProductType

ProductTypeFactory (FlyweightFactory)
  get_or_create(...) -> ProductType   — cache em memória por type_key
  load_all_from_definitions()         — popula as ~50 combinações pré-definidas
```

## Por que ~50 tipos servem para 10.000+ produtos

`load_all_from_definitions()` pré-carrega 50 combinações reais (Electronics/
Samsung, Clothing/Nike, Books/Penguin, etc.). `PopulateProductsUseCase`
distribui N produtos *round-robin* entre essas 50 instâncias — não importa se
você cria 100 ou 100.000 produtos, o número de objetos `ProductType` em
memória continua fixo em 50. `FlyweightStats` calcula a economia estimada de
memória comparando "bytes sem Flyweight" (duplicados por produto) vs. "bytes
com Flyweight" (compartilhados + 1 ponteiro por produto).

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** `ProductTypeFactory` só gerencia o pool de
  Flyweights; `DjangoProductRepository` só faz a tradução ORM ↔ domínio.
- **O — Open/Closed:** novos tipos de produto são adicionados a
  `_PRODUCT_TYPE_DEFINITIONS` sem alterar `ProductTypeFactory`, `Product`
  ou qualquer use case.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

Isso roda as migrations, popula 1000 produtos via `populate_products` e
inicia o servidor em `http://localhost:8000`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/products/?page=&page_size=` | Lista paginada de produtos |
| GET | `/products/stats/` | Estatísticas de economia de memória do Flyweight |

## Management Commands

```bash
python src/manage.py populate_products --count 10000
python src/manage.py measure_memory
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente:

```bash
pip install -e ".[dev]"
DJANGO_SETTINGS_MODULE=config.settings_test python -m pytest --cov=src --cov-report=term-missing
```

Os testes de integração usam SQLite em memória (`config.settings_test`) —
nenhum servidor MySQL é necessário para rodar a suíte de testes.
