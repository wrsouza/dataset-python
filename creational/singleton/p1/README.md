# Database Connection Pool — Singleton Pattern

> **Design Pattern:** Singleton
> **Categoria:** Creational
> **Framework:** FastAPI + asyncpg
> **Servicos:** PostgreSQL 16

## Objetivo Pedagogico

Este projeto demonstra o padrao Singleton aplicado a um pool de conexoes
async com PostgreSQL. O aluno aprende como garantir que apenas uma instancia
do pool existe em toda a aplicacao, como implementar thread-safety com
`threading.Lock` e `asyncio.Lock` combinados, e como usar FastAPI Dependency
Injection para distribuir o singleton sem acoplamento direto.

## O Pattern em Acao

| Papel do Pattern | Classe | Arquivo |
|------------------|--------|---------|
| Singleton (metaclasse) | `SingletonMeta` | `src/db_pool/infrastructure/singleton.py` |
| Instancia unica | `DatabasePool` | `src/db_pool/infrastructure/singleton.py` |
| Abstracoes do dominio | `ConnectionPool`, `UserRepository` | `src/db_pool/domain/interfaces.py` |
| Use cases | `ListUsersUseCase`, `CreateUserUseCase` | `src/db_pool/application/use_cases.py` |
| Repositorio concreto | `PostgresUserRepository` | `src/db_pool/infrastructure/repository.py` |

## Diagrama UML (ASCII)

```
SingletonMeta (metaclass)
+ _instances: dict[type, Any]
+ _lock: threading.Lock
+ __call__(): Any          <-- double-checked locking aqui
        |
        v (instancia via metaclass)
DatabasePool
- _pool: asyncpg.Pool | None
- _async_lock: asyncio.Lock
- _initialised: bool
+ initialise(dsn, min, max): Coroutine
+ acquire(): Connection
+ release(conn): Coroutine
+ connection(): AsyncContextManager   <-- uso tipico nos repositorios
+ get_stats(): PoolStatsSnapshot
+ close(): Coroutine
+ is_ready: bool

        ^
        | Depends (FastAPI DI)
        |
FastAPI endpoints (/health, /users, /db/pool/stats)
   get_pool() --> DatabasePool()  -- mesmo objeto toda vez
```

## Thread-Safety: Double-Checked Locking

```python
def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:          # fast path (sem lock)
        with cls._lock:                    # slow path: adquire lock
            if cls not in cls._instances:  # re-verifica dentro do lock
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
    return cls._instances[cls]
```

## Principios SOLID Demonstrados

- **S — SRP:** `DatabasePool` so gerencia o pool; `PostgresUserRepository`
  so faz SQL; use cases so contem logica de negocio.
- **D — DIP:** endpoints dependem de `ConnectionPool` (Protocol), nao de
  `asyncpg.Pool` diretamente. Testes injetam `FakePool` sem alterar producao.

## Estrutura do Projeto

```
p1/
├── src/
│   ├── main.py                          <- FastAPI app + lifespan
│   └── db_pool/
│       ├── domain/
│       │   ├── interfaces.py            <- ConnectionPool, UserRepository Protocols
│       │   └── entities.py             <- User, PoolStatsSnapshot, CreateUserRequest
│       ├── application/
│       │   └── use_cases.py            <- GetPoolStatsUseCase, CreateUserUseCase...
│       └── infrastructure/
│           ├── singleton.py            <- SingletonMeta + DatabasePool
│           └── repository.py          <- PostgresUserRepository
├── tests/
│   ├── unit/test_singleton.py          <- identidade + thread-safety + use cases
│   └── integration/test_api.py        <- endpoints com mocks
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Pre-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API disponivel em http://localhost:8000/docs
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/ -v
```

## Variaveis de Ambiente

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `DATABASE_URL` | DSN do PostgreSQL | `postgresql://app:secret@db:5432/appdb` |
| `POOL_MIN_SIZE` | Minimo de conexoes no pool | `2` |
| `POOL_MAX_SIZE` | Maximo de conexoes no pool | `10` |
