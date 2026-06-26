# Design Patterns em Python — 110 Projetos, 22 GoF Patterns

Dataset educacional com **110 projetos Python independentes**, cobrindo os
**22 Design Patterns do Gang of Four** (5 Creational, 7 Structural, 10
Behavioral) — cada pattern demonstrado em **5 cenários reais distintos**,
usando frameworks, bancos de dados e serviços cloud variados, em vez do
clássico (e pouco memorável) `Animal.speak()`.

Pensado para aulas/estudo de design patterns onde o aluno vê o mesmo
pattern resolvendo problemas concretos diferentes — não só uma variação
acadêmica do mesmo exemplo.

## Visão geral

| Dimensão            | Detalhe |
|----------------------|---------|
| Design Patterns      | 22 (5 Creational, 7 Structural, 10 Behavioral) |
| Projetos totais      | 110 (5 por pattern) |
| Frameworks           | FastAPI, Flask, Django (+ Channels), Streamlit, CLI (Typer), gRPC |
| Bancos de dados      | PostgreSQL, MySQL, SQL Server, MongoDB, Redis, SQLite |
| Cloud / Mensageria   | AWS (S3, SQS, SNS, SES, Rekognition, AppConfig, CloudWatch), GCP (Storage, Pub/Sub), Azure Blob, RabbitMQ, Kafka, Celery |
| Qualidade obrigatória | Docker + docker-compose, Black, Ruff, mypy `--strict`, pytest com cobertura ≥80% (a maioria 90%+) |
| Princípios de código  | Clean Code + SOLID em todos os projetos |

## Estrutura do repositório

```
dataset-python/
├── PLAN.md                    # Mapa completo dos 110 projetos
├── STATUS.md                  # Histórico de progresso e decisões
├── PROCESS.md                  # Workflow e checklist de qualidade
├── docs/
│   ├── standards/              # Clean Code e SOLID — guias usados em todo o dataset
│   ├── decisions/               # ADRs (decisões de arquitetura/stack)
│   └── templates/               # Dockerfile, docker-compose e pyproject.toml base
├── creational/                  # 5 patterns × 5 projetos = 25 projetos
│   ├── abstract_factory/
│   ├── builder/
│   ├── factory_method/
│   ├── prototype/
│   └── singleton/
├── structural/                  # 7 patterns × 5 projetos = 35 projetos
│   ├── adapter/
│   ├── bridge/
│   ├── composite/
│   ├── decorator/
│   ├── facade/
│   ├── flyweight/
│   └── proxy/
├── behavioral/                  # 10 patterns × 5 projetos = 50 projetos
│   ├── chain_of_responsibility/
│   ├── command/
│   ├── iterator/
│   ├── mediator/
│   ├── memento/
│   ├── observer/
│   ├── state/
│   ├── strategy/
│   ├── template_method/
│   └── visitor/
└── extras/                      # 200 scripts independentes (1 arquivo cada)
    ├── PLAN_EXTRAS.md            # plano e convenções dos scripts extras
    ├── STATUS_EXTRAS.md          # rastreamento de progresso
    ├── data_processing/          # 50 — pandas, numpy, files (csv/json/excel)
    ├── utilities/                # 50 — strings/regex, file_io, datetime, validation, encoding
    ├── algorithms/                # 40 — sorting, searching, graphs, DP, trees
    ├── exception_handling/        # 30 — custom_exceptions, try_except, logging, error_recovery
    └── practical/                  # 30 — real_world_snippets, problem_solving, edge_cases, performance
```

Cada `pattern/pN/` é um projeto **completo e independente**: tem seu
próprio `pyproject.toml`, `Dockerfile`, `docker-compose.yml`,
`.env.example`, `README.md` (explicando o pattern naquele contexto
específico, com diagrama e mapeamento SOLID) e suite de testes em
`tests/unit` + `tests/integration`.

## Como rodar um projeto

Cada projeto é autocontido. Exemplo genérico:

```bash
cd creational/singleton/p2          # qualquer pattern/projeto
cp .env.example .env
docker-compose up --build
```

Para rodar localmente sem Docker:

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
black src tests && ruff check src tests && mypy --strict src
```

> **Nota:** os ~110 projetos foram desenvolvidos num único ambiente
> Python global (sem venv por projeto). Se for reproduzir o dataset
> inteiro numa única máquina, use um venv por projeto para evitar
> colisão de nomes de pacote entre projetos diferentes (ver `STATUS.md`
> para detalhes de ambiente).

## Os 22 patterns

### Creational
| Pattern | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Abstract Factory | UI Component Factory (Flask) | Cloud Storage Factory (FastAPI) | Message Broker Factory (CLI) | Chart Visualization Factory (Streamlit) | Database Connector Factory (Django) |
| Builder | SQL Query Builder API (FastAPI) | Report Builder PDF/Excel/CSV (Flask) | Email Template Builder (Django) | Pipeline Builder Visual (Streamlit) | Docker-Compose Generator CLI (CLI) |
| Factory Method | Payment Gateway Factory (FastAPI) | File Storage Factory (Flask) | Auth Provider Factory (Django) | Message Consumer Factory (CLI) | Serializer Factory (Streamlit) |
| Prototype | Game Character Template System (FastAPI) | Document Template Cloner (Flask) | E-commerce Product Variant (Django) | Dashboard Config Cloner (Streamlit) | Infrastructure Profile Cloner (CLI) |
| Singleton | Database Connection Pool (FastAPI) | Cache Manager (Flask) | Feature Flag Manager (Django) | Structured Logger (CLI) | ML Model Registry (Streamlit) |

### Structural
| Pattern | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Adapter | SOAP → REST Adapter (FastAPI) | Multi-ORM Adapter (Flask) | Multi-Cloud Storage Adapter (Django) | DataFrame Format Adapter (Streamlit) | Messaging Protocol Adapter (CLI) |
| Bridge | Notification Bridge (FastAPI) | Renderer Bridge (Flask) | Queue Bridge (Django) | Export Format Bridge (CLI) | Data Source Bridge (Streamlit) |
| Composite | Organization Hierarchy API (FastAPI) | Virtual File System (Flask) | Category Tree E-commerce (Django) | Build Task Composite (CLI) | Nested Dashboard UI (Streamlit) |
| Decorator | HTTP Middleware Pipeline (FastAPI) | Cache Decorator API (Flask) | Permission Decorator Layers (Django) | Observability Decorator (CLI) | UI Component Decorator (Streamlit) |
| Facade | E-commerce Order Facade (FastAPI) | Payment Processing Facade (Flask) | Background Job Facade (Django) | Data Migration Facade (CLI) | Multi-API Aggregator Facade (Streamlit) |
| Flyweight | Session Token Cache (FastAPI) | Image Thumbnail Cache (Flask) | Product Catalog Cache (Django) | Game Particle System (CLI) | Glyph Font Renderer (Streamlit) |
| Proxy | Lazy DB Proxy (FastAPI) | API Cache Proxy (Flask) | Access Control Proxy (Django) | Remote File Proxy (CLI) | Rate Limiting Proxy (gRPC) |

### Behavioral
| Pattern | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Chain of Responsibility | Request Validation Chain (FastAPI) | Support Ticket Escalation (Flask) | Content Moderation Pipeline (Django) | Message Processing Chain (CLI) | Data Validation Pipeline (Streamlit) |
| Command | Undo/Redo API (FastAPI) | Task Queue System (Flask) | Scheduled Command Executor (Django) | CLI History with Replay (CLI) | Event Sourcing (FastAPI) |
| Iterator | Cursor Pagination API (FastAPI) | S3 Bucket Iterator (Flask) | Lazy QuerySet Iterator (Django) | File Tree Iterator (CLI) | Stream Data Iterator (Streamlit) |
| Mediator | WebSocket Chat Room (FastAPI) | Event Bus (Flask) | Real-time Notifications (Django Channels) | Service Bus Mediator (CLI) | Dashboard Component Mediator (Streamlit) |
| Memento | Document Version History (FastAPI) | Form State Save/Restore (Flask) | Model Audit Trail (Django) | Text Editor Undo/Redo (CLI) | Analysis Session Snapshots (Streamlit) |
| Observer | Real-time Stock Ticker (FastAPI) | Event-driven Price Alert (Flask) | Django Signals System (Django) | Cloud Event Notifier (CLI) | Live Dashboard (Streamlit) |
| State | Order State Machine (FastAPI) | User Auth Session FSM (Flask) | Workflow Approval FSM (Django) | Download Manager State (CLI) | Multi-step Form Wizard (Streamlit) |
| Strategy | Tax Calculation Engine (FastAPI) | Discount Strategy API (Flask) | Authentication Strategy (Django) | Compression Strategy CLI (CLI) | ML Model Strategy (Streamlit) |
| Template Method | Data Import Pipeline (FastAPI) | Report Generation Template (Flask) | ETL Pipeline Template (Django) | Data Processing Pipeline (CLI) | Analysis Workflow Template (Streamlit) |
| Visitor | Query AST Visitor (FastAPI) | Shopping Cart Visitors (Flask) | Content Export Visitor (Django) | Code Metrics Visitor (CLI) | Data Transformation Visitor (Streamlit) |

## Arquitetura padrão de cada projeto

Todos os projetos seguem a mesma separação em camadas (Clean
Architecture leve):

```
src/<pacote>/
├── domain/            # entidades e interfaces — sem dependências externas
├── application/       # use cases / orquestração
├── infrastructure/     # implementações concretas (DB, cloud, fila, etc.)
└── app.py / main.py    # composition root (injeção de dependências)
```

Ver `docs/standards/clean_code.md` e `docs/standards/solid_principles.md`
para o guia completo seguido em todo o dataset, e `docs/decisions/ADR-001-tech-stack.md`
para o racional das escolhas de stack.

## Scripts extras (`extras/`)

Além dos 110 projetos de design patterns, o repositório inclui **200
scripts Python independentes** (1 arquivo cada, sem Docker/tests/SOLID —
diferente dos projetos de pattern), organizados por categoria:

| Categoria | Subpastas | Scripts |
|---|---|---|
| Data Processing | `pandas/`, `numpy/`, `files_csv_json_excel/` | 50 |
| Utilities & Helpers | `strings_regex/`, `file_io/`, `datetime/`, `validation/`, `encoding_decoding/` | 50 |
| Algoritmos | `sorting/`, `searching/`, `graphs/`, `dynamic_programming/`, `trees/` | 40 |
| Exception Handling | `custom_exceptions/`, `try_except_patterns/`, `logging_patterns/`, `error_recovery/` | 30 |
| Practical Code | `real_world_snippets/`, `problem_solving/`, `edge_cases/`, `performance/` | 30 |

Cada script segue o padrão `extras/<categoria>/<subtema>/NN_nome_descritivo.py`:
docstring com cenário e objetivo, comentários nos pontos não-óbvios, e
um bloco `if __name__ == "__main__":` executável com dados de exemplo.
Sem chamadas de rede reais e sem dependências fora de
`pandas`/`numpy`/`openpyxl` + stdlib. Ver `extras/PLAN_EXTRAS.md` para
as convenções completas e `extras/STATUS_EXTRAS.md` para o
rastreamento de progresso (200/200 concluído).

## Licença

Uso educacional.
