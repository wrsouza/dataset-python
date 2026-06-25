# Document Editor — Undo/Redo API

> **Design Pattern:** Command
> **Categoria:** Behavioral
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Command em um editor de documentos com histórico
de undo/redo via API REST. Cada operação do usuário (inserir texto, apagar texto,
aplicar formatação) é encapsulada em um objeto Command independente, permitindo que
um Invoker centralize a execução, o desfazer e o refazer sem conhecer os detalhes
de cada operação.

## O Pattern em Ação

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Command (abstrato) | `DocumentCommand` | `src/document_editor/domain/interfaces.py` |
| ConcreteCommand | `InsertTextCommand`, `DeleteTextCommand`, `FormatCommand` | `src/document_editor/application/commands.py` |
| Receiver (abstrato) | `DocumentReceiver` | `src/document_editor/domain/interfaces.py` |
| Receiver (concreto) | `Document` | `src/document_editor/domain/entities.py` |
| Invoker (abstrato) | `CommandInvoker` | `src/document_editor/domain/interfaces.py` |
| Invoker (concreto) | `HistoryInvoker` | `src/document_editor/application/use_cases.py` |

Cada `ConcreteCommand` guarda apenas os dados necessários para executar e desfazer
a sua própria operação (ex.: `DeleteTextCommand` guarda o texto removido para
poder reinseri-lo no `undo()`). O `HistoryInvoker` não sabe o que cada comando faz
internamente — ele apenas chama `execute()`/`undo()` e mantém duas pilhas
(undo/redo). Isso permite adicionar novas operações (ex.: `ReplaceTextCommand`)
sem alterar o Invoker nem os comandos já existentes.

## Diagrama UML (ASCII)

```
<<abstract>>
DocumentCommand
+ execute(): CommandResult
+ undo(): CommandResult
+ get_description(): str
+ is_reversible(): bool
        |
        ├── InsertTextCommand ────┐
        ├── DeleteTextCommand ────┼──> usa ──> DocumentReceiver (Document)
        └── FormatCommand ────────┘            + insert(pos, text)
                                                + delete(start, end): str
                                                + apply_format(start, end, type)
                                                + remove_format(start, end, type)

<<abstract>>
CommandInvoker                          HistoryInvoker (concreto)
+ execute(command): CommandResult       - _undo_stack: list[(Command, CommandInfo)]
+ undo(): CommandResult | None          - _redo_stack: list[(Command, CommandInfo)]
+ redo(): CommandResult | None
+ get_history(): list[CommandInfo]
+ clear(): None

Cliente (main.py / API)
   --> cria ConcreteCommand(receiver=document, ...)
   --> invoker.execute(command)
   --> invoker.undo() / invoker.redo()
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** cada `ConcreteCommand` encapsula exatamente uma
  operação reversível (`InsertTextCommand` só insere/desfaz inserção,
  `DeleteTextCommand` só apaga/restaura, `FormatCommand` só formata/remove
  formatação). O `HistoryInvoker` tem a única responsabilidade de orquestrar
  histórico (pilhas de undo/redo), sem conhecer a lógica de edição de texto. O
  `Document` (Receiver) tem a única responsabilidade de manter e mutar o
  conteúdo/formatação, sem saber nada sobre histórico.
- **O — Open/Closed:** novas operações (ex.: `ReplaceTextCommand`) são adicionadas
  criando uma nova subclasse de `DocumentCommand` em `application/commands.py`,
  sem modificar `HistoryInvoker`, `DocumentCommand` ou os endpoints existentes.
- **L — Liskov Substitution:** qualquer `DocumentCommand` pode substituir outro no
  `HistoryInvoker.execute()` — todos seguem o mesmo contrato de `execute()`/`undo()`
  retornando `CommandResult`, sem lançar exceções fora do esperado pelo chamador.
- **I — Interface Segregation:** `DocumentReceiver` (operações no documento) e
  `CommandInvoker` (orquestração de histórico) são interfaces separadas e enxutas;
  `DocumentRepository`/`CommandHistoryRepository` (persistência) ficam isoladas em
  `domain/repositories.py`, sem misturar responsabilidades.
- **D — Dependency Inversion:** os comandos recebem `DocumentReceiver` via
  construtor (não instanciam `Document` internamente); `main.py` é a composição
  root onde `PostgresDocumentRepository` (implementação concreta) é injetada.

## Estrutura do Projeto

```
command/p1/
├── src/
│   └── document_editor/
│       ├── domain/
│       │   ├── interfaces.py     ← DocumentCommand, DocumentReceiver, CommandInvoker (ABCs)
│       │   ├── entities.py       ← Document (Receiver), CommandResult, CommandInfo
│       │   └── repositories.py   ← DocumentRepository, CommandHistoryRepository (ABCs)
│       ├── application/
│       │   ├── commands.py       ← InsertTextCommand, DeleteTextCommand, FormatCommand
│       │   └── use_cases.py      ← HistoryInvoker (Invoker concreto)
│       ├── infrastructure/
│       │   ├── models.py                          ← modelos SQLAlchemy
│       │   ├── database.py                        ← engine/session factory
│       │   ├── postgres_document_repository.py     ← repositórios PostgreSQL
│       │   └── in_memory_document_repository.py    ← repositórios in-memory (testes/demo)
│       └── main.py               ← FastAPI app (composição root)
├── tests/
│   ├── unit/          ← comandos, invoker (com mocks), entidades, repos in-memory
│   └── integration/   ← API completa via TestClient
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

# 3. Acessar a aplicação
# FastAPI: http://localhost:8000/docs
```

## Exemplos de Uso da API

```bash
# Inserir texto
curl -X POST http://localhost:8000/documents/doc-1/insert \
  -H "Content-Type: application/json" -d '{"position": 0, "text": "hello"}'

# Apagar um trecho
curl -X POST http://localhost:8000/documents/doc-1/delete \
  -H "Content-Type: application/json" -d '{"start": 0, "end": 2}'

# Aplicar formatação
curl -X POST http://localhost:8000/documents/doc-1/format \
  -H "Content-Type: application/json" \
  -d '{"start": 0, "end": 5, "format_type": "bold"}'

# Desfazer / refazer
curl -X POST http://localhost:8000/documents/doc-1/undo
curl -X POST http://localhost:8000/documents/doc-1/redo

# Ver estado atual e histórico
curl http://localhost:8000/documents/doc-1
curl http://localhost:8000/documents/doc-1/history
```

## Rodar os Testes

```bash
# Testes unitários (sem serviços externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (via TestClient + SQLite in-memory)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

> **Decisão de teste:** os testes de integração usam SQLite in-memory (via
> override do dependency `get_session` do FastAPI) em vez de PostgreSQL real,
> para que a suíte rode sem depender do `docker-compose up`. Os repositórios em
> `infrastructure/postgres_document_repository.py` usam apenas recursos
> portáveis do SQLAlchemy ORM, então o comportamento validado é equivalente ao
> de produção. Essa escolha está documentada em `tests/conftest.py`.

## Verificar Qualidade do Código

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `POSTGRES_USER` | Usuário do banco PostgreSQL | `app` |
| `POSTGRES_PASSWORD` | Senha do banco PostgreSQL | `secret` |
| `POSTGRES_DB` | Nome do banco PostgreSQL | `appdb` |
| `DATABASE_URL` | URL de conexão SQLAlchemy | `postgresql+psycopg2://app:secret@db:5432/appdb` |
