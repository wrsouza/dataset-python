# ADR-001: Escolha do Tech Stack do Dataset

**Data:** 2026-06-20
**Status:** Accepted
**Decisores:** Claude + Usuário (Professor)

---

## Contexto

Precisamos definir quais tecnologias usar nos 110 projetos de forma que:
- Cada projeto seja independente e realista
- O conjunto total seja diversificado (alunos aprendem múltiplos stacks)
- As escolhas reflitam o mercado atual Python (2025-2026)

---

## Decisão

### Python
- **Versão:** 3.11+ em todos os projetos
- **Razão:** Suporte a `tomllib` nativo, melhorias de performance, `ExceptionGroup`, melhor match-case

### Frameworks Web
| Framework | Quando usar | Razão pedagógica |
|-----------|-------------|-----------------|
| FastAPI | APIs REST assíncronas | Moderno, type-safe, Pydantic v2 |
| Flask | APIs simples, adapters | Minimalismo explícito, sem magia |
| Django | Apps completas com ORM | Padrões enterprise, signals, admin |
| Streamlit | Dashboards / Data Apps | Patterns em UI de dados/ML |
| CLI Typer | Ferramentas de linha de comando | Patterns em automação/scripts |
| gRPC | Comunicação entre serviços | Patterns em microserviços |

### Bancos de Dados
| BD | Casos de uso |
|----|-------------|
| PostgreSQL | Principal relacional; JSON nativo, melhor para Python |
| MySQL | Alternativa relacional; mercado grande |
| SQL Server | Ambiente corporativo / legado |
| MongoDB | Documentos, clonagem (Prototype), snapshots (Memento) |
| Redis | Cache, sessões, pub/sub, filas simples |
| SQLite | CLI tools, testes, prototipagem leve |

### Mensageria
| Serviço | Quando usar |
|---------|------------|
| RabbitMQ | Filas tradicionais, roteamento AMQP |
| Apache Kafka | Event streaming, event sourcing, alta throughput |
| AWS SQS | Filas gerenciadas cloud, integração AWS |
| Redis Pub/Sub | Pub/sub simples, WebSocket broadcast |
| Celery | Background tasks com Django/Flask |

### Cloud
| Provider | Serviços usados |
|----------|----------------|
| AWS | S3, SQS, SNS, Rekognition, SES, AppConfig, CloudWatch |
| GCP | Cloud Storage, Pub/Sub |
| Azure | Blob Storage |

### Ferramentas de Qualidade
| Ferramenta | Função | Configuração |
|------------|--------|-------------|
| Black | Formatter | `line-length = 88` |
| Ruff | Linter (substitui flake8+isort+bandit) | `select = ["E","F","W","I","N","UP","ANN","S","B"]` |
| mypy | Type checker | `strict = true` |
| pytest | Test runner | `--cov --cov-fail-under=80` |
| pytest-cov | Cobertura | Via pytest |
| pytest-asyncio | Testes async | Para FastAPI / async code |

---

## Consequências

**Positivas:**
- Alunos veem o mesmo pattern em múltiplos stacks → compreensão mais profunda
- Cada projeto é uma referência real de como usar a tecnologia
- Diversidade de BDs ensina adaptabilidade

**Negativas / Trade-offs:**
- Curva de aprendizado maior para alunos iniciantes (múltiplos frameworks)
- Projetos com serviços cloud exigem conta AWS/GCP/Azure para rodar em produção
  - **Mitigação:** docker-compose inclui mocks locais (localstack para AWS, por exemplo)
- gRPC tem configuração mais complexa
  - **Mitigação:** Apenas 1 projeto usa gRPC (Proxy P5)

---

## Alternativas Rejeitadas

| Alternativa | Razão da rejeição |
|-------------|-------------------|
| Apenas FastAPI | Perderia diversidade pedagógica |
| Apenas PostgreSQL | Não expõe alunos a outros BDs |
| Celery substituindo Kafka/RabbitMQ | Kafka/RabbitMQ são mais comuns em sistemas reais |
| SQLAlchemy 1.x | SQLAlchemy 2.x é o padrão atual |
