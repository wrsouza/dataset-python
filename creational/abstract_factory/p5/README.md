# Database Connector Factory

> **Design Pattern:** Abstract Factory
> **Categoria:** Creational
> **Framework:** Django
> **Serviços:** PostgreSQL, MySQL, SQL Server (opcional)

## Objetivo Pedagógico

Este projeto demonstra o padrão Abstract Factory em uma API Django que
expõe operações de banco de dados (health check, query, migration) para
três engines diferentes. O aluno aprende como uma `AbstractFactory` cria
uma **família coesa** de objetos relacionados — conexão, query builder e
migration runner — garantindo que nunca se misture, por exemplo, uma
conexão PostgreSQL com um query builder MySQL.

## O Pattern em Ação

A `DatabaseFactory` (AbstractFactory) declara três métodos de criação:
`create_connection()`, `create_query_builder()` e `create_migration_runner()`.
Cada `ConcreteFactory` (`PostgreSQLFactory`, `MySQLFactory`, `SQLServerFactory`)
produz uma família de produtos consistente com o seu engine. As views Django
são o único ponto de composição — elas resolvem a fábrica certa via
`get_factory_for_engine()` e a injetam nos use cases (Client), que nunca
sabem qual engine concreto está por baixo.

| Papel do Pattern  | Classe                                                          | Arquivo                                              |
|-------------------|------------------------------------------------------------------|-------------------------------------------------------|
| AbstractFactory   | `DatabaseFactory`                                                | `src/db_factory/domain/interfaces.py`                 |
| ConcreteFactory   | `PostgreSQLFactory`, `MySQLFactory`, `SQLServerFactory`          | `src/db_factory/infrastructure/factories.py`          |
| AbstractProduct   | `DBConnection`, `QueryBuilder`, `MigrationRunner`                | `src/db_factory/domain/interfaces.py`                 |
| ConcreteProduct   | `PostgreSQLConnection`, `MySQLQueryBuilder`, `SQLServerMigrationRunner`, etc. | `src/db_factory/infrastructure/factories.py` |
| Client            | `CheckDatabaseHealthUseCase`, `ExecuteQueryUseCase`, `RunMigrationsUseCase` | `src/db_factory/application/use_cases.py`  |

## Diagrama UML (ASCII)

```
<<abstract>>
DatabaseFactory
+ create_connection()       -> DBConnection
+ create_query_builder()    -> QueryBuilder
+ create_migration_runner() -> MigrationRunner
+ get_engine_name()         -> str
        |
        ├── PostgreSQLFactory
        │     + create_connection()       -> PostgreSQLConnection
        │     + create_query_builder()    -> PostgreSQLQueryBuilder
        │     + create_migration_runner() -> PostgreSQLMigrationRunner
        │
        ├── MySQLFactory
        │     + create_connection()       -> MySQLConnection
        │     + create_query_builder()    -> MySQLQueryBuilder
        │     + create_migration_runner() -> MySQLMigrationRunner
        │
        └── SQLServerFactory
              + create_connection()       -> SQLServerConnection
              + create_query_builder()    -> SQLServerQueryBuilder
              + create_migration_runner() -> SQLServerMigrationRunner

<<abstract>>         <<abstract>>          <<abstract>>
DBConnection          QueryBuilder         MigrationRunner
+ ping()              + select()           + run_pending()
+ get_engine_name()   + execute()          + list_applied()
+ get_connection_info()+ get_engine_name() + get_engine_name()
```

## Princípios SOLID Demonstrados

- **O (Open/Closed):** adicionar um novo engine (ex.: SQLite) significa criar
  `SQLiteConnection`, `SQLiteQueryBuilder`, `SQLiteMigrationRunner` e
  `SQLiteFactory`, e registrá-la em `DB_FACTORIES`
  (`src/db_factory/infrastructure/factories.py`). Nenhuma classe existente
  é modificada — nem as views, nem os use cases.
- **D (Dependency Inversion):** os use cases (`src/db_factory/application/use_cases.py`)
  recebem `DatabaseFactory` (abstração) via construtor. As views Django
  (`src/db_factory/views/db_views.py`) são o único lugar onde uma fábrica
  concreta é resolvida, via `get_factory_for_engine()`.
- **I (Interface Segregation):** `DBConnection`, `QueryBuilder` e
  `MigrationRunner` são interfaces pequenas e independentes
  (`src/db_factory/domain/interfaces.py`) — um cliente que só faz health
  check nunca depende dos métodos de migração.
- **S (Single Responsibility):** cada use case tem um único motivo para
  mudar: `CheckDatabaseHealthUseCase` só verifica saúde, `ExecuteQueryUseCase`
  só executa queries, `RunMigrationsUseCase` só aplica migrations.

## Estrutura do Projeto

```
p5/
├── src/
│   ├── manage.py                        ← Django management script
│   └── db_factory/
│       ├── settings.py                  ← configuração Django (3 conexões)
│       ├── urls.py                      ← rotas HTTP
│       ├── wsgi.py                      ← entrypoint WSGI/gunicorn
│       ├── domain/
│       │   ├── interfaces.py            ← DatabaseFactory + AbstractProducts (ABCs)
│       │   └── entities.py              ← HealthCheckResult, QueryResult, MigrationReport
│       ├── application/
│       │   └── use_cases.py             ← Client: orquestra a fábrica injetada
│       ├── infrastructure/
│       │   └── factories.py             ← ConcreteFactories e ConcreteProducts
│       └── views/
│           └── db_views.py              ← composition root (Django views)
├── tests/
│   ├── unit/
│   │   ├── test_use_cases.py            ← mocks de DatabaseFactory
│   │   └── test_factories.py            ← famílias de produtos por engine
│   └── integration/
│       └── test_django_views.py         ← Django test client (rotas HTTP)
├── conftest.py                          ← django.setup() para pytest
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Pré-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Como Rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir o app + bancos de dados
docker-compose up --build

# 3. Testar os endpoints
curl http://localhost:8000/db/health/postgresql/
curl http://localhost:8000/db/health/mysql/
curl -X POST http://localhost:8000/db/query/postgresql/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT 1 AS one"}'
```

## Rodar os Testes

```bash
# Testes unitários (sem banco de dados real — usam mocks)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (requer postgres/mysql via docker-compose)
docker-compose run --rm app pytest tests/integration/ -v

# Todos com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável               | Descrição                              | Padrão                    |
|-------------------------|-----------------------------------------|----------------------------|
| `DJANGO_SECRET_KEY`     | Chave secreta do Django                 | `dev-only-insecure-key...` |
| `DJANGO_DEBUG`          | Modo debug                              | `true`                     |
| `POSTGRES_DB/USER/...`  | Credenciais PostgreSQL                  | `app` / `secret` / `appdb` |
| `MYSQL_DATABASE/USER/..`| Credenciais MySQL                       | `app` / `secret` / `appdb` |
| `SQLSERVER_*`           | Credenciais SQL Server (opcional)        | `sa` / `YourStrong@Passw0rd`|
