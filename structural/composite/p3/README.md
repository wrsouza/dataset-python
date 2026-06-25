# Category Tree E-commerce

> **Design Pattern:** Composite
> **Categoria:** Structural
> **Framework:** Django + MySQL
> **Domínio:** categories

## Objetivo Pedagógico

Demonstra o padrão Composite em uma árvore de categorias de e-commerce.
Uma `Category` (Composite) contém filhos que podem ser outros `Category`
ou `Product` (Leaf). Operações como `get_product_count()` e
`calculate_total_value()` funcionam recursivamente em qualquer nível da
árvore sem `if/isinstance` no código cliente.

## O Pattern em Ação

| Papel        | Classe               | Arquivo                                    |
|--------------|----------------------|--------------------------------------------|
| Component    | `CatalogItem` (ABC)  | `src/catalog/domain/interfaces.py`         |
| Leaf         | `ProductLeaf`        | `src/catalog/infrastructure/composite.py`  |
| Composite    | `CategoryComposite`  | `src/catalog/infrastructure/composite.py`  |
| Client       | Views Django         | `src/catalog/views.py`                     |

## Diagrama UML — Árvore ASCII

```
<<abstract>>
CatalogItem
+ get_product_count() -> int
+ get_all_products() -> list[ProductData]
+ calculate_total_value() -> Decimal
+ to_dict(depth: int) -> dict
        |
        ├── ProductLeaf                          (Leaf)
        │     - name, price, sku, stock_qty
        │     + get_product_count() -> 1
        │     + calculate_total_value() -> price * stock_qty
        │
        └── CategoryComposite                    (Composite)
              - _children: list[CatalogItem]
              + add_child(child: CatalogItem)
              + get_product_count() -> sum(child.get_product_count())
              + calculate_total_value() -> sum(child.calculate_total_value())

Exemplo de árvore (3 níveis):

  Electronics          ← CategoryComposite (L1)
    └── Smartphones    ← CategoryComposite (L2)
          ├── Android  ← CategoryComposite (L3)
          │     ├── [ProductLeaf] Pixel 8
          │     └── [ProductLeaf] Galaxy S24
          └── iOS      ← CategoryComposite (L3)
                └── [ProductLeaf] iPhone 15
```

## Princípios SOLID Demonstrados

- **L — Liskov Substitution:** `ProductLeaf` e `CategoryComposite` são
  substituíveis por `CatalogItem` — nenhum `isinstance()` nas views.
  Uma Category com filhos e um Product individual respondem ao mesmo
  contrato: `get_product_count()`, `get_all_products()`, etc.

- **O — Open/Closed:** Adicionar `Bundle` (kit de produtos) ou
  `VirtualCategory` requer apenas nova subclasse de `CatalogItem` —
  views e use cases não precisam de alteração.

## Estrutura do Projeto

```
p3/
├── src/
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py          <- Django settings (MySQL)
│   │   ├── settings_test.py     <- SQLite in-memory para testes
│   │   └── urls.py
│   └── catalog/
│       ├── domain/
│       │   ├── interfaces.py    <- CatalogItem ABC (Component)
│       │   └── exceptions.py
│       ├── infrastructure/
│       │   ├── composite.py     <- ProductLeaf + CategoryComposite
│       │   └── repository.py    <- Constrói a árvore do ORM
│       ├── management/
│       │   └── commands/
│       │       └── populate_catalog.py
│       ├── migrations/
│       ├── models.py            <- Django ORM (adjacency list)
│       ├── views.py             <- 4 endpoints REST
│       └── urls.py
├── tests/
│   ├── unit/test_composite.py   <- Sem banco
│   └── integration/test_views.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Endpoints

| Método | URL                              | Descrição                              |
|--------|----------------------------------|----------------------------------------|
| GET    | `/categories/`                   | Árvore completa do catálogo            |
| GET    | `/categories/{slug}/`            | Subárvore a partir do slug             |
| GET    | `/categories/{slug}/products/`   | Todos os produtos (recursivo)          |
| GET    | `/categories/{slug}/stats/`      | product_count e total_value            |

## Como Rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir com Docker Compose (MySQL + Django)
docker-compose up --build

# API disponível em: http://localhost:8000

# Exemplos
curl http://localhost:8000/categories/
curl http://localhost:8000/categories/electronics/stats/
curl http://localhost:8000/categories/android/products/
```

## Rodar Testes (sem Docker)

```bash
pip install -e ".[dev]"
pytest
```

## Variáveis de Ambiente

| Variável            | Descrição               | Padrão        |
|---------------------|-------------------------|---------------|
| `MYSQL_DATABASE`    | Nome do banco           | `catalogdb`   |
| `MYSQL_USER`        | Usuário MySQL           | `app`         |
| `MYSQL_PASSWORD`    | Senha MySQL             | `secret`      |
| `MYSQL_HOST`        | Host MySQL              | `db`          |
| `DJANGO_SECRET_KEY` | Chave secreta Django    | (obrigatória) |
| `DEBUG`             | Modo debug              | `true`        |
