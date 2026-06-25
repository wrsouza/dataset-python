# SQL Query Builder REST API

> **Design Pattern:** Builder
> **Categoria:** Creational
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Builder construindo queries SQL complexas passo a passo
com uma interface fluente (method chaining). O aluno aprende como separar a construção de
um objeto complexo (SelectQuery, InsertQuery, UpdateQuery) de sua representação final,
usando um Director para orquestrar sequências de construção reutilizáveis para relatórios.

## O Pattern em Ação

| Papel do Pattern   | Classe                        | Arquivo                                     |
|--------------------|-------------------------------|---------------------------------------------|
| Builder (interface)| `SelectQueryBuilder`          | `src/query_builder/domain/interfaces.py`    |
| Builder (interface)| `InsertQueryBuilder`          | `src/query_builder/domain/interfaces.py`    |
| Builder (interface)| `UpdateQueryBuilder`          | `src/query_builder/domain/interfaces.py`    |
| ConcreteBuilder    | `ConcreteSelectQueryBuilder`  | `src/query_builder/infrastructure/builders.py` |
| ConcreteBuilder    | `ConcreteInsertQueryBuilder`  | `src/query_builder/infrastructure/builders.py` |
| ConcreteBuilder    | `ConcreteUpdateQueryBuilder`  | `src/query_builder/infrastructure/builders.py` |
| Director           | `ReportQueryDirector`         | `src/query_builder/application/use_cases.py` |
| Product            | `SelectQuery`, `InsertQuery`  | `src/query_builder/domain/entities.py`      |

## Diagrama UML

```
<<abstract>>
SelectQueryBuilder
+ select(*columns) -> Self
+ from_table(table) -> Self
+ where(condition) -> Self
+ join(table, on, type) -> Self
+ order_by(column, dir) -> Self
+ limit(count) -> Self
+ offset(skip) -> Self
+ build() -> SelectQuery
        |
        └── ConcreteSelectQueryBuilder
              (implementa interface fluente)

ReportQueryDirector
- _builder: SelectQueryBuilder
+ build_sales_by_period(start, end) -> SelectQuery
+ build_top_customers(top_n) -> SelectQuery
+ build_low_stock_products(threshold) -> SelectQuery

SelectQuery (Product)
- columns: list[str]
- table: str
- joins: list[JoinClause]
- conditions: list[str]
- order_clauses: list[OrderClause]
+ to_sql() -> str
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** Cada Builder cuida de um único tipo de query
  (`SelectQueryBuilder`, `InsertQueryBuilder`, `UpdateQueryBuilder`). O Director
  `ReportQueryDirector` cuida apenas de orquestrar sequências de construção.
- **O — Open/Closed:** Para adicionar um novo tipo de query (ex: `DeleteQueryBuilder`),
  cria-se uma nova interface e implementação sem modificar as existentes.
- **D — Dependency Inversion:** `ReportQueryDirector` depende da abstração
  `SelectQueryBuilder`, não de `ConcreteSelectQueryBuilder`. A implementação concreta
  é injetada no construtor.

## Estrutura do Projeto

```
p1/
├── src/
│   └── query_builder/
│       ├── domain/
│       │   ├── interfaces.py    ← ABCs dos builders
│       │   └── entities.py      ← SelectQuery, InsertQuery, UpdateQuery
│       ├── application/
│       │   └── use_cases.py     ← ReportQueryDirector, BuildQueryUseCase
│       ├── infrastructure/
│       │   └── builders.py      ← ConcreteBuilders
│       └── main.py              ← FastAPI app
├── tests/
│   ├── unit/test_builders.py
│   └── integration/test_integration.py
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API: http://localhost:8000/docs
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável        | Descrição                  | Padrão                                    |
|-----------------|----------------------------|-------------------------------------------|
| `DATABASE_URL`  | URL de conexão PostgreSQL  | `postgresql://app:secret@db:5432/querydb` |
| `POSTGRES_USER` | Usuário do banco           | `app`                                     |
| `POSTGRES_PASSWORD` | Senha do banco         | `secret`                                  |
| `POSTGRES_DB`   | Nome do banco              | `querydb`                                 |

## Exemplos de Uso

```bash
# Construir query customizada
curl -X POST http://localhost:8000/queries/build \
  -H "Content-Type: application/json" \
  -d '{"table": "orders", "columns": ["id", "total"], "conditions": ["status = '\''paid'\''"], "limit": 10}'

# Relatório pré-construído pelo Director
curl "http://localhost:8000/queries/reports/sales_by_period?start_date=2024-01-01&end_date=2024-12-31"

# Top clientes
curl "http://localhost:8000/queries/reports/top_customers?top_n=5"
```
