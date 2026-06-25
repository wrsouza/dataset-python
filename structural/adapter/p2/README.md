# Multi-ORM Adapter

> **Design Pattern:** Adapter
> **Categoria:** Structural
> **Framework:** Flask
> **Servicos:** MySQL (via SQLAlchemy 2.0 e via pymysql cru)

## Objetivo Pedagogico

Este projeto demonstra o padrao Adapter unificando **duas formas distintas de acessar
o mesmo banco MySQL** — o ORM SQLAlchemy e queries SQL cruas via `pymysql` — sob uma
unica interface (`UserRepository`). O cliente (use cases e rotas Flask) nao sabe, e
nao precisa saber, qual tecnologia de persistencia esta sendo usada por baixo: basta
escolher o adapter via query string (`?adapter=sqlalchemy` ou `?adapter=raw`) e o
comportamento observavel e identico (LSP).

## O Pattern em Acao

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Target (interface desejada) | `UserRepository` (Protocol) | `src/orm_adapter/domain/interfaces.py` |
| Adaptee 1 (ORM) | `Session` / `UserModel` (SQLAlchemy) | `src/orm_adapter/infrastructure/sqlalchemy_adapter.py` |
| Adapter 1 | `SQLAlchemyUserAdapter` | `src/orm_adapter/infrastructure/sqlalchemy_adapter.py` |
| Adaptee 2 (driver cru) | `pymysql.connections.Connection` | `src/orm_adapter/infrastructure/raw_mysql_adapter.py` |
| Adapter 2 | `RawMySQLUserAdapter` | `src/orm_adapter/infrastructure/raw_mysql_adapter.py` |
| Client | Flask routes + Use Cases | `src/orm_adapter/main.py`, `application/use_cases.py` |

## Diagrama UML

```
                  <<Protocol>>
                  UserRepository
                  + find_by_id(id) -> User | None
                  + find_all() -> list[User]
                  + save(user) -> User
                  + delete(id) -> None
                         ^
                         |  (implementam estruturalmente)
            +------------+------------+
            |                         |
  SQLAlchemyUserAdapter      RawMySQLUserAdapter
  (Adapter 1)                (Adapter 2)
  - usa Session/ORM          - usa pymysql + SQL cru
            |                         |
            v                         v
   <<Adaptee>> SQLAlchemy     <<Adaptee>> pymysql
   Session + UserModel        Connection + cursor.execute()
            \                         /
             \                       /
              \---------------------/
                         |
                         v
                    MySQL (appdb.users)
```

## Principios SOLID Demonstrados

- **O — Open/Closed:** novos adapters (ex.: MongoDB, Django ORM) podem ser adicionados
  sem alterar `use_cases.py` ou as rotas — basta implementar `UserRepository`.
- **L — Liskov Substitution:** `SQLAlchemyUserAdapter` e `RawMySQLUserAdapter` sao
  intercambiaveis; qualquer use case funciona identicamente com ambos.
- **I — Interface Segregation:** `UserRepository` expoe apenas 4 metodos essenciais de
  persistencia, sem detalhes de ORM ou SQL.
- **D — Dependency Inversion:** `application/use_cases.py` depende exclusivamente do
  Protocol `UserRepository`; a escolha do adapter concreto e feita na composicao root
  (`main.py`), via `?adapter=` na requisicao.

## Estrutura do Projeto

```
p2/
├── src/orm_adapter/
│   ├── domain/
│   │   ├── interfaces.py        <- Target Protocol (UserRepository)
│   │   └── entities.py          <- User, UserNotFoundError, DuplicateEmailError
│   ├── application/
│   │   └── use_cases.py         <- Get/List/Create/Update/DeleteUserUseCase
│   ├── infrastructure/
│   │   ├── sqlalchemy_adapter.py  <- SQLAlchemyUserAdapter (Adapter 1)
│   │   └── raw_mysql_adapter.py   <- RawMySQLUserAdapter (Adapter 2)
│   └── main.py                  <- Flask app (composicao root)
├── tests/
│   ├── unit/                    <- mocks de UserRepository / MySQL
│   └── integration/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API: http://localhost:5001
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/unit/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variaveis de Ambiente

| Variavel | Descricao | Valor padrao |
|----------|-----------|--------------|
| `DATABASE_URL` | URL SQLAlchemy para o MySQL | `mysql+pymysql://app:secret@db:3306/appdb` |
| `MYSQL_HOST` | Host do MySQL (adapter raw) | `db` |
| `MYSQL_PORT` | Porta do MySQL | `3306` |
| `MYSQL_USER` | Usuario do MySQL | `app` |
| `MYSQL_PASSWORD` | Senha do MySQL | `secret` |
| `MYSQL_DATABASE` | Nome do banco | `appdb` |

## Endpoints REST

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/users` | Listar todos os usuarios |
| GET | `/users/{id}` | Buscar usuario por ID |
| POST | `/users` | Criar novo usuario |
| PUT | `/users/{id}` | Atualizar usuario existente |
| DELETE | `/users/{id}` | Remover usuario |
| GET | `/health` | Health check |

Todas as rotas aceitam o query param `?adapter=sqlalchemy` (padrao) ou `?adapter=raw`
para escolher qual Adapter sera injetado no use case, demonstrando a intercambiabilidade.
