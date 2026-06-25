# Organization Hierarchy API

> **Design Pattern:** Composite
> **Categoria:** Structural
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Composite em uma hierarquia organizacional real
(Company → Department → Team → Employee). Operações como headcount e total de
salário funcionam recursivamente em qualquer nível sem if/isinstance — o cliente
trata Employee e Department de forma idêntica via OrgUnit.

## O Pattern em Ação

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Component (abstrato) | `OrgUnit` | `src/organization/domain/interfaces.py` |
| Leaf | `EmployeeLeaf` | `src/organization/infrastructure/composite.py` |
| Composite | `CompositeOrgUnit` | `src/organization/infrastructure/composite.py` |
| Client | Routes FastAPI | `src/main.py` |

## Diagrama UML

```
<<abstract>>
OrgUnit
+ get_headcount() -> int
+ get_total_salary() -> Decimal
+ get_members() -> list[EmployeeData]
+ display(indent: int) -> str
        |
        ├── EmployeeLeaf          (Leaf)
        │     - _model: EmployeeModel
        │     + get_headcount() -> 1
        │     + get_total_salary() -> own salary
        │
        └── CompositeOrgUnit      (Composite)
              - _children: list[OrgUnit]
              + add_child(child: OrgUnit)
              + remove_child(child: OrgUnit)
              + get_headcount() -> sum(child.get_headcount())
              + get_total_salary() -> sum(child.get_total_salary())

  Company
    └── Department
          ├── Employee (Carol - VP Eng)
          └── Team
                ├── Employee (Alice - Senior Dev)
                └── Employee (Bob - Junior Dev)
```

## Princípios SOLID Demonstrados

- **L — Liskov Substitution:** `EmployeeLeaf` e `CompositeOrgUnit` são
  substituíveis por `OrgUnit` — nenhum isinstance() no código cliente.
- **O — Open/Closed:** Adicionar `Division` ou `Squad` requer criar nova
  subclasse de `CompositeOrgUnit`, sem alterar routes ou use cases.
- **D — Dependency Inversion:** `OrgUnitUseCases` depende de `OrgRepository`
  injetado via construtor, não de implementação concreta de banco.

## Estrutura do Projeto

```
p1/
├── src/
│   ├── main.py                          <- FastAPI app + routes
│   └── organization/
│       ├── domain/
│       │   ├── interfaces.py            <- OrgUnit ABC (Component)
│       │   └── entities.py              <- Pydantic schemas
│       ├── application/
│       │   └── use_cases.py             <- Orchestration
│       └── infrastructure/
│           ├── composite.py             <- EmployeeLeaf + CompositeOrgUnit
│           ├── models.py                <- SQLAlchemy ORM (adjacency list)
│           ├── repository.py            <- Data access
│           └── database.py              <- Connection factory
├── tests/
│   ├── unit/test_composite.py
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

## Exemplo de Uso

```bash
# Criar empresa
curl -X POST http://localhost:8000/org/units \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp", "unit_type": "company"}'

# Verificar headcount de qualquer nível
curl http://localhost:8000/org/1/headcount

# Ver árvore completa
curl http://localhost:8000/org/tree
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `DATABASE_URL` | URL PostgreSQL | `postgresql://app:secret@db:5432/orgdb` |
| `POSTGRES_USER` | Usuário DB | `app` |
| `POSTGRES_PASSWORD` | Senha DB | `secret` |
| `POSTGRES_DB` | Nome do banco | `orgdb` |
