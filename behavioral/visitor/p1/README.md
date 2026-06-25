# Query AST Visitor

> **Design Pattern:** Visitor
> **Categoria:** Behavioral
> **Framework:** FastAPI
> **Serviços:** PostgreSQL (provisionado, não utilizado pela lógica do pattern — ver nota abaixo)

## Objetivo Pedagógico

Este projeto demonstra o padrão Visitor aplicado a uma AST (Abstract Syntax Tree) de
consultas SQL. Cada nó da AST (`SELECT`, `WHERE`, `JOIN`, ...) é um Element fixo;
novas operações sobre a árvore — explicar, otimizar, validar, gerar SQL — são
adicionadas criando novos Visitors, sem jamais tocar nos nós existentes.

## O Pattern em Ação

A AST representa uma query de forma estruturada e estável. Cada `ConcreteVisitor`
implementa uma operação completa sobre todos os tipos de nó, mantendo a lógica de
cada operação coesa em um único arquivo (em vez de espalhada como métodos `accept`
ou `if isinstance` dentro dos próprios nós).

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Visitor (abstrato) | `ASTVisitor` | `src/query_ast/domain/interfaces.py` |
| Element (abstrato) | `ASTNode` | `src/query_ast/domain/interfaces.py` |
| ConcreteElement | `SelectNode`, `WhereNode`, `JoinNode`, `OrderByNode`, `GroupByNode`, `LimitNode` | `src/query_ast/domain/interfaces.py` |
| ObjectStructure | `QueryAST` | `src/query_ast/application/structure.py` |
| ConcreteVisitor | `QueryExplainerVisitor` | `src/query_ast/infrastructure/visitors/query_explainer.py` |
| ConcreteVisitor | `QueryOptimizerVisitor` | `src/query_ast/infrastructure/visitors/query_optimizer.py` |
| ConcreteVisitor | `QueryValidatorVisitor` | `src/query_ast/infrastructure/visitors/query_validator.py` |
| ConcreteVisitor | `SQLGeneratorVisitor` | `src/query_ast/infrastructure/visitors/sql_generator.py` |

## Diagrama UML (ASCII)

```
                  <<abstract>>
                  ASTVisitor
        + visit_select(SelectNode)
        + visit_where(WhereNode)
        + visit_join(JoinNode)
        + visit_order_by(OrderByNode)
        + visit_group_by(GroupByNode)
        + visit_limit(LimitNode)
                     |
   ┌─────────────────┼──────────────────┬───────────────────┐
   |                 |                  |                   |
QueryExplainer  QueryOptimizer   QueryValidator      SQLGenerator
   Visitor          Visitor          Visitor            Visitor


                  <<abstract>>
                    ASTNode
                + accept(visitor)
                       |
   ┌──────────┬────────┼─────────┬───────────┬───────────┐
   |          |        |         |           |           |
SelectNode WhereNode JoinNode OrderByNode GroupByNode  LimitNode
   |          |        |         |           |           |
   └──────────┴────────┴─────────┴───────────┴───────────┘
        each accept() calls the matching visit_X (double dispatch)


            QueryAST (Object Structure)
        nodes: list[ASTNode]
        + accept_visitor(visitor) -> VisitorResult
        ── iterates nodes, calling node.accept(visitor) for each ──
```

Double dispatch: `QueryAST.accept_visitor(visitor)` chama `node.accept(visitor)`
para cada nó; cada nó concreto chama de volta o `visit_X` específico do visitor
(`visitor.visit_select(self)`, etc.) — o visitor nunca precisa de `isinstance`.

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Uma nova operação sobre a AST (ex.: um futuro
  `QueryCostEstimatorVisitor`) é adicionada como uma nova classe em
  `infrastructure/visitors/`, implementando `ASTVisitor`. Nenhum nó em
  `domain/interfaces.py` (`SelectNode`, `WhereNode`, etc.) precisa ser alterado.
  Inversamente, um novo tipo de nó exigiria alterar todos os visitors — essa é a
  troca consciente do Visitor: fácil adicionar operações, custoso adicionar nós.
- **D — Dependency Inversion:** `AnalyzeQueryUseCase` (em `application/use_cases.py`)
  recebe um `visitor_factory: dict[OperationType, type[ASTVisitor]]` injetado no
  construtor — depende da abstração `ASTVisitor`, nunca instancia um
  `SQLGeneratorVisitor` concreto internamente. A composição concreta acontece em
  `main.py` (composition root).
- **S — Single Responsibility:** Cada `ConcreteVisitor` tem uma única razão para
  mudar (sua operação específica); `QueryAST` só sabe percorrer nós; `AnalyzeQueryUseCase`
  só sabe traduzir um request em AST e disparar o visitor certo.
- **I — Interface Segregation:** `ASTVisitor` expõe apenas os seis `visit_X`
  necessários — nenhum cliente precisa de métodos que não usa.

## Nota sobre PostgreSQL

O padrão Visitor, por natureza, opera sobre estruturas em memória (a AST) e não
exige persistência. O serviço `db` (PostgreSQL) está provisionado no
`docker-compose.yml` para manter a consistência de infraestrutura do dataset
(todo projeto roda via `docker-compose up`), mas a lógica de negócio deste
projeto não lê nem escreve no banco — é um placeholder coerente com o briefing,
não uma dependência funcional do pattern.

## Estrutura do Projeto

```
visitor/p1/
├── src/
│   └── query_ast/
│       ├── main.py                        ← FastAPI app (composition root)
│       ├── domain/
│       │   ├── interfaces.py              ← ASTVisitor, ASTNode, ConcreteElements
│       │   └── entities.py                ← OperationType, AnalysisReport
│       ├── application/
│       │   ├── structure.py               ← QueryAST (Object Structure)
│       │   └── use_cases.py               ← AnalyzeQueryUseCase
│       └── infrastructure/
│           └── visitors/                  ← ConcreteVisitors
│               ├── query_explainer.py
│               ├── query_optimizer.py
│               ├── query_validator.py
│               └── sql_generator.py
├── tests/
│   ├── unit/                              ← um arquivo de teste por visitor
│   └── integration/                       ← API via TestClient
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

# 2. Subir todos os serviços
docker-compose up --build

# 3. Acessar a documentação interativa
# http://localhost:8000/docs
```

### Exemplo de chamada

```bash
curl -X POST http://localhost:8000/queries/generate_sql \
  -H "Content-Type: application/json" \
  -d '{
        "select": {"table": "users", "columns": ["id", "name"]},
        "where": "active = true",
        "limit": {"limit": 10}
      }'
```

Operações disponíveis em `/queries/{operation}`: `explain`, `optimize`, `validate`,
`generate_sql`.

## Rodar os Testes

```bash
# Testes unitários (sem serviços externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (via TestClient, sem precisar do Postgres no ar)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Verificar Qualidade do Código

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `DATABASE_URL` | URL de conexão PostgreSQL (não usada pela lógica atual) | `postgresql://app:secret@db:5432/appdb` |
| `POSTGRES_USER` | Usuário do PostgreSQL | `app` |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | `secret` |
| `POSTGRES_DB` | Nome do banco | `appdb` |
| `LOG_LEVEL` | Nível de log da aplicação | `INFO` |
