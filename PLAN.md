# Plano Mestre — Design Patterns em Python
> **Versão:** 1.0 | **Data:** 2026-06-20 | **Autor:** Claude + Usuário
> **Objetivo:** Dataset educacional com 110 projetos Python cobrindo os 22 Design Patterns do GoF em cenários reais variados, usando múltiplos frameworks, bancos de dados e serviços cloud.

---

## Visão Geral

| Dimensão           | Detalhe                                      |
|--------------------|----------------------------------------------|
| Design Patterns    | 22 (5 Creational, 7 Structural, 10 Behavioral) |
| Projetos totais    | 110 (5 por pattern)                          |
| Frameworks         | FastAPI, Flask, Django, Streamlit, CLI (Typer), gRPC |
| Bancos de dados    | PostgreSQL, MySQL, SQL Server, MongoDB, Redis, SQLite |
| Cloud / Mensageria | AWS (S3, SQS, SNS, Rekognition), GCP (Storage, PubSub), Azure (Blob), RabbitMQ, Kafka, Celery |
| Obrigatório em todos | Docker + docker-compose, Ruff, Black, mypy, pytest ≥80% cobertura |
| Padrões de código  | Clean Code + SOLID em todos os projetos      |

---

## Estrutura de Diretórios

```
dataset-python/
├── PLAN.md                        ← Este arquivo
├── STATUS.md                      ← Rastreamento de progresso
├── PROCESS.md                     ← Processo, padrões e convenções
├── docs/
│   ├── standards/
│   │   ├── clean_code.md          ← Guia Clean Code obrigatório
│   │   ├── solid_principles.md    ← Checklist SOLID por princípio
│   │   └── project_template.md    ← Template base de projeto
│   ├── decisions/
│   │   └── ADR-001-tech-stack.md  ← Decisões de arquitetura
│   └── templates/
│       ├── Dockerfile.base        ← Dockerfile base multi-stage
│       ├── docker-compose.base.yml← Compose base
│       └── pyproject.toml.base    ← pyproject.toml base
├── creational/
│   ├── abstract_factory/          ← 5 projetos (p1..p5)
│   ├── builder/
│   ├── factory_method/
│   ├── prototype/
│   └── singleton/
├── structural/
│   ├── adapter/
│   ├── bridge/
│   ├── composite/
│   ├── decorator/
│   ├── facade/
│   ├── flyweight/
│   └── proxy/
└── behavioral/
    ├── chain_of_responsibility/
    ├── command/
    ├── iterator/
    ├── mediator/
    ├── memento/
    ├── observer/
    ├── state/
    ├── strategy/
    ├── template_method/
    └── visitor/
```

Cada pattern terá subpastas `p1/` a `p5/` com projeto completo independente.

---

## Fases de Execução

```
FASE 0  →  Setup Global (1 agente orquestrador)
            ↓
FASE 1  →  Creational Patterns  (5 agentes em paralelo)
FASE 2  →  Structural Patterns  (7 agentes em paralelo)    ← podem rodar junto com F1 e F3
FASE 3  →  Behavioral Patterns  (10 agentes em paralelo)
            ↓
FASE 4  →  Revisão & Integração (1 agente revisor)
```

### Fase 0 — Setup Global
- Criar estrutura de pastas do projeto
- Escrever guias de padrões (clean_code.md, solid_principles.md)
- Criar templates base (Dockerfile, docker-compose, pyproject.toml)
- Validar ferramentas necessárias

### Fases 1-3 — Desenvolvimento dos Patterns
- 22 agentes especializados, cada um responsável por 1 pattern e seus 5 projetos
- Cada agente segue o briefing padrão documentado em PROCESS.md
- Entregáveis por projeto: código + testes + Docker + config

### Fase 4 — Revisão & Integração
- Code review SOLID em todos os projetos
- Executar `pytest --cov` em todos
- Executar `ruff check` + `mypy` em todos
- Gerar index final de projetos

---

## Conteúdo Obrigatório — Todos os 110 Projetos

| Artefato               | Especificação                                              |
|------------------------|------------------------------------------------------------|
| `Dockerfile`           | Multi-stage: `base` → `dev` → `prod`                      |
| `docker-compose.yml`   | App + todos os serviços externos necessários               |
| `pyproject.toml`       | Black, Ruff, mypy, pytest configurados                     |
| `.env.example`         | Todas as variáveis com descrição e valor de exemplo        |
| `tests/`               | pytest, cobertura ≥ 80%, fixtures, mocks where appropriate |
| `README.md`            | Objetivo pedagógico, diagrama UML ASCII, como rodar        |
| Type hints             | mypy strict em todo o código                               |
| SOLID                  | ≥ 2 princípios demonstrados e identificados no README      |
| Clean Code             | Nomes descritivos, funções ≤ 20 linhas, sem magic numbers  |

---

## Mapa Completo de Projetos

### CREATIONAL PATTERNS

#### 1. Abstract Factory
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | UI Component Factory Multiplataforma | Flask | PostgreSQL |
| P2 | Cloud Storage Factory | FastAPI | AWS S3, GCP Storage, Azure Blob |
| P3 | Message Broker Factory | CLI (Typer) | RabbitMQ, Kafka, AWS SQS |
| P4 | Chart Visualization Factory | Streamlit | — |
| P5 | Database Connector Factory | Django | PostgreSQL, MySQL, SQL Server |

#### 2. Builder
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | SQL Query Builder REST API | FastAPI | PostgreSQL |
| P2 | Report Builder (PDF/Excel/CSV) | Flask | — |
| P3 | Email Template Builder | Django | AWS SES |
| P4 | Pipeline Builder Visual | Streamlit | — |
| P5 | Docker-Compose Generator CLI | CLI (Typer) | — |

#### 3. Factory Method
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Payment Gateway Factory | FastAPI | PostgreSQL, Stripe |
| P2 | File Storage Factory | Flask | AWS S3, GCP Storage |
| P3 | Auth Provider Factory | Django | — |
| P4 | Message Consumer Factory | CLI (Typer) | Kafka, RabbitMQ |
| P5 | Serializer Factory | Streamlit | — |

#### 4. Prototype
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Game Character Template System | FastAPI | PostgreSQL |
| P2 | Document Template Cloner | Flask | MongoDB |
| P3 | E-commerce Product Variant | Django | MySQL |
| P4 | Dashboard Config Cloner | Streamlit | — |
| P5 | Infrastructure Profile Cloner | CLI (Typer) | — |

#### 5. Singleton
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Database Connection Pool | FastAPI | PostgreSQL |
| P2 | Cache Manager | Flask | Redis |
| P3 | Feature Flag Manager | Django | AWS AppConfig |
| P4 | Structured Logger | CLI (Typer) | — |
| P5 | ML Model Registry | Streamlit | — |

---

### STRUCTURAL PATTERNS

#### 6. Adapter
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | SOAP → REST Adapter | FastAPI | — |
| P2 | Multi-ORM Adapter | Flask | MySQL |
| P3 | Multi-Cloud Storage Adapter | Django | S3, GCS, Azure Blob |
| P4 | DataFrame Format Adapter | Streamlit | — |
| P5 | Messaging Protocol Adapter | CLI (Typer) | RabbitMQ, Kafka |

#### 7. Bridge
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Notification Bridge | FastAPI | AWS SNS, SES |
| P2 | Renderer Bridge | Flask | — |
| P3 | Queue Bridge | Django | Celery, Redis, RabbitMQ, SQS |
| P4 | Export Format Bridge | CLI (Typer) | — |
| P5 | Data Source Bridge | Streamlit | SQL Server, MongoDB |

#### 8. Composite
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Organization Hierarchy API | FastAPI | PostgreSQL |
| P2 | Virtual File System | Flask | AWS S3 |
| P3 | Category Tree E-commerce | Django | MySQL |
| P4 | Build Task Composite | CLI (Typer) | — |
| P5 | Nested Dashboard UI | Streamlit | — |

#### 9. Decorator
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | HTTP Middleware Pipeline | FastAPI | — |
| P2 | Cache Decorator API | Flask | Redis |
| P3 | Permission Decorator Layers | Django | PostgreSQL |
| P4 | Observability Decorator | CLI (Typer) | AWS CloudWatch |
| P5 | UI Component Decorator | Streamlit | — |

#### 10. Facade
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | E-commerce Order Facade | FastAPI | PostgreSQL, AWS SQS |
| P2 | Payment Processing Facade | Flask | Stripe, MySQL |
| P3 | Background Job Facade | Django | Celery, Redis |
| P4 | Data Migration Facade | CLI (Typer) | MySQL → PostgreSQL |
| P5 | Multi-API Aggregator Facade | Streamlit | — |

#### 11. Flyweight
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Session Token Cache | FastAPI | Redis |
| P2 | Image Thumbnail Cache | Flask | AWS S3 |
| P3 | Product Catalog Cache | Django | MySQL |
| P4 | Game Particle System | CLI (Typer) | — |
| P5 | Glyph Font Renderer | Streamlit | — |

#### 12. Proxy
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Lazy DB Proxy | FastAPI | PostgreSQL |
| P2 | API Cache Proxy | Flask | Redis |
| P3 | Access Control Proxy | Django | PostgreSQL |
| P4 | Remote File Proxy | CLI (Typer) | AWS S3 |
| P5 | Rate Limiting Proxy | gRPC | Redis |

---

### BEHAVIORAL PATTERNS

#### 13. Chain of Responsibility
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Request Validation Chain | FastAPI | — |
| P2 | Support Ticket Escalation | Flask | PostgreSQL |
| P3 | Content Moderation Pipeline | Django | AWS Rekognition |
| P4 | Message Processing Chain | CLI (Typer) | RabbitMQ |
| P5 | Data Validation Pipeline | Streamlit | — |

#### 14. Command
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Undo/Redo API | FastAPI | PostgreSQL |
| P2 | Task Queue System | Flask | RabbitMQ |
| P3 | Scheduled Command Executor | Django | Celery, Redis |
| P4 | CLI History with Replay | CLI (Typer) | SQLite |
| P5 | Event Sourcing | FastAPI | Kafka, PostgreSQL |

#### 15. Iterator
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Cursor Pagination API | FastAPI | PostgreSQL |
| P2 | S3 Bucket Iterator | Flask | AWS S3 |
| P3 | Lazy QuerySet Iterator | Django | MySQL |
| P4 | File Tree Iterator | CLI (Typer) | — |
| P5 | Stream Data Iterator | Streamlit | Kafka |

#### 16. Mediator
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | WebSocket Chat Room | FastAPI | Redis PubSub |
| P2 | Event Bus | Flask | RabbitMQ |
| P3 | Real-time Notifications | Django Channels | WebSocket, PostgreSQL |
| P4 | Service Bus Mediator | CLI (Typer) | AWS SQS |
| P5 | Dashboard Component Mediator | Streamlit | — |

#### 17. Memento
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Document Version History | FastAPI | PostgreSQL |
| P2 | Form State Save/Restore | Flask | Redis |
| P3 | Model Audit Trail | Django | SQL Server |
| P4 | Text Editor Undo/Redo | CLI (Typer) | — |
| P5 | Analysis Session Snapshots | Streamlit | MongoDB |

#### 18. Observer
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Real-time Stock Ticker | FastAPI | WebSocket, Redis |
| P2 | Event-driven Price Alert | Flask | Kafka |
| P3 | Django Signals System | Django | PostgreSQL |
| P4 | Cloud Event Notifier | CLI (Typer) | AWS SNS |
| P5 | Live Dashboard | Streamlit | GCP PubSub |

#### 19. State
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Order State Machine | FastAPI | PostgreSQL |
| P2 | User Auth Session FSM | Flask | Redis |
| P3 | Workflow Approval FSM | Django | Celery, PostgreSQL |
| P4 | Download Manager State | CLI (Typer) | AWS S3 |
| P5 | Multi-step Form Wizard | Streamlit | — |

#### 20. Strategy
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Tax Calculation Engine | FastAPI | PostgreSQL |
| P2 | Discount Strategy API | Flask | MySQL |
| P3 | Authentication Strategy | Django | — |
| P4 | Compression Strategy CLI | CLI (Typer) | — |
| P5 | ML Model Strategy | Streamlit | — |

#### 21. Template Method
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Data Import Pipeline | FastAPI | PostgreSQL |
| P2 | Report Generation Template | Flask | — |
| P3 | ETL Pipeline Template | Django | Celery, Kafka, PostgreSQL |
| P4 | Data Processing Pipeline | CLI (Typer) | AWS S3, MySQL |
| P5 | Analysis Workflow Template | Streamlit | — |

#### 22. Visitor
| # | Nome | Framework | Serviços/BD |
|---|------|-----------|-------------|
| P1 | Query AST Visitor | FastAPI | PostgreSQL |
| P2 | Shopping Cart Visitors | Flask | MySQL |
| P3 | Content Export Visitor | Django | AWS S3 |
| P4 | Code Metrics Visitor | CLI (Typer) | — |
| P5 | Data Transformation Visitor | Streamlit | — |

---

## Critérios de Conclusão

Um projeto é marcado como **DONE** no STATUS.md quando:
- [ ] Código Python implementando o pattern corretamente
- [ ] Clean Code: nomes descritivos, funções ≤ 20 linhas, type hints completos
- [ ] SOLID: ≥ 2 princípios demonstrados e identificados no README
- [ ] `Dockerfile` multi-stage funcional
- [ ] `docker-compose.yml` com todos os serviços
- [ ] `pyproject.toml` com Black, Ruff, mypy configurados
- [ ] `.env.example` completo
- [ ] `pytest` passa com cobertura ≥ 80%
- [ ] `ruff check .` sem erros
- [ ] `mypy .` sem erros críticos
- [ ] `README.md` com objetivo pedagógico + diagrama UML + como rodar

---

*Documento gerado em 2026-06-20. Atualizar PLAN.md apenas para mudanças estruturais. Progresso vai em STATUS.md.*
