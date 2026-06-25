# Background Job Facade

> **Design Pattern:** Facade
> **Categoria:** Structural
> **Framework:** Django + Celery + Redis
> **Domínio:** jobs

## Objetivo Pedagógico

Demonstra o padrão Facade simplificando o agendamento e monitoramento de
jobs assíncronos. Em vez do código cliente lidar diretamente com Celery
(`send_task`, `AsyncResult`, `control.revoke`) e com a persistência de
auditoria no banco, ele conversa com uma única classe — `JobFacade` —
que oferece quatro operações: `schedule`, `get_status`, `cancel`, `retry`.

## O Pattern Aplicado

`JobFacade` (em `src/jobs/application/facade.py`) é o Facade que esconde
três subsistemas complexos atrás de uma interface simples:

1. **Fila de tarefas** (`AbstractTaskQueue`) — Celery/Redis para enfileirar,
   cancelar e re-executar jobs.
2. **Leitura de status** (`AbstractJobStatusReader`) — consulta o
   result backend do Celery (`AsyncResult`).
3. **Auditoria persistente** (`AbstractJobRepository`) — grava o histórico
   de cada job no Postgres via Django ORM.

As views Django (`src/jobs/django_app/views.py`) e qualquer outro cliente
(comando de management, outro serviço) só precisam conhecer `JobFacade` —
nunca importam `celery.Celery` ou `AsyncResult` diretamente.

## Diagrama UML (ASCII)

```
                         ┌───────────────────────────┐
                         │      Client (Views)        │
                         └─────────────┬───────────────┘
                                        │ usa apenas
                                        ▼
                         ┌───────────────────────────┐
                         │         JobFacade          │  ← FACADE
                         │ + schedule(req): JobInfo   │
                         │ + get_status(id): JobInfo  │
                         │ + cancel(id): bool         │
                         │ + retry(id): JobInfo       │
                         └──────┬───────┬───────┬─────┘
                                │       │       │
              ┌─────────────────┘       │       └─────────────────┐
              ▼                         ▼                         ▼
  <<interface>>                 <<interface>>             <<interface>>
  AbstractTaskQueue        AbstractJobStatusReader    AbstractJobRepository
  + enqueue(req): str      + get_status(id): JobInfo  + save(job): None
  + cancel(id): bool                                  + find_by_id(id)
  + retry(id): str
        △                          △                          △
        │                          │                          │
  CeleryTaskQueue ──────────────────┘                  DjangoJobRepository
  (Celery + Redis: send_task, AsyncResult, control.revoke)  (Django ORM: JobRecord)
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** `JobFacade` só orquestra; não sabe como o
  Celery serializa tarefas nem como o Postgres persiste linhas. Cada
  adapter (`CeleryTaskQueue`, `DjangoJobRepository`) tem um único motivo
  para mudar.
- **D — Dependency Inversion:** `JobFacade.__init__` recebe três
  abstrações (`AbstractTaskQueue`, `AbstractJobStatusReader`,
  `AbstractJobRepository`) via injeção de dependência — nunca instancia
  Celery ou o ORM diretamente. Isso permite testar a facade inteira com
  fakes em memória (`tests/unit/test_facade.py`), sem Redis nem banco.
- **I — Interface Segregation:** três ABCs pequenas e focadas em vez de
  uma única interface "Deus" com 10 métodos — clientes que só leem status
  não precisam saber cancelar ou persistir.
- **O — Open/Closed:** trocar Celery por outro broker (ex.: RQ, Dramatiq)
  exige apenas uma nova implementação de `AbstractTaskQueue`; `JobFacade`
  e as views não mudam uma linha.

## Estrutura do Projeto

```
p3/
├── src/
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py          <- Django settings (Postgres + Celery/Redis)
│   │   ├── settings_test.py     <- SQLite in-memory para testes
│   │   └── urls.py
│   └── jobs/
│       ├── domain/
│       │   ├── entities.py      <- JobRequest, JobInfo, JobStatus
│       │   └── interfaces.py    <- AbstractTaskQueue/StatusReader/Repository
│       ├── application/
│       │   └── facade.py        <- JobFacade (o Facade)
│       ├── infrastructure/
│       │   ├── celery_app.py            <- instância Celery + tasks demo
│       │   ├── celery_task_queue.py      <- adapter Celery (enqueue/cancel/retry/status)
│       │   ├── django_job_repository.py <- adapter Django ORM
│       │   └── factory.py                <- composition root (build_job_facade)
│       └── django_app/
│           ├── models.py        <- JobRecord (auditoria)
│           ├── views.py         <- 4 endpoints REST
│           ├── urls.py
│           └── migrations/
├── tests/
│   ├── unit/                    <- facade + entities, fakes em memória
│   └── integration/             <- views Django + repositório real (SQLite)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Endpoints

| Método | URL                       | Descrição                              |
|--------|---------------------------|-----------------------------------------|
| POST   | `/jobs/`                  | Agenda um novo job (`task_name`, `kwargs`) |
| GET    | `/jobs/{job_id}/`         | Consulta status/resultado do job        |
| POST   | `/jobs/{job_id}/cancel/`  | Cancela um job pendente ou em execução  |
| POST   | `/jobs/{job_id}/retry/`   | Reenfileira um job que falhou           |

Tasks Celery disponíveis para o campo `task_name`: `jobs.send_report`,
`jobs.process_dataset` (ver `src/jobs/infrastructure/celery_app.py`).

## Como Rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir com Docker Compose (Postgres + Redis + Django + worker Celery)
docker-compose up --build

# API disponível em: http://localhost:8000

# Exemplos
curl -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"task_name": "jobs.send_report", "kwargs": {"recipient": "a@b.com", "report_id": "r1"}}'

curl http://localhost:8000/jobs/<job_id>/
curl -X POST http://localhost:8000/jobs/<job_id>/cancel/
curl -X POST http://localhost:8000/jobs/<job_id>/retry/
```

## Rodar Testes (sem Docker)

```bash
pip install -e ".[dev]"
pytest
```

Os testes de integração usam SQLite em memória e fazem mock do
`build_job_facade` — nenhum Redis real é necessário para rodar a suíte.

## Variáveis de Ambiente

| Variável                | Descrição                  | Padrão                     |
|--------------------------|-----------------------------|-----------------------------|
| `POSTGRES_DB`            | Nome do banco                | `jobsdb`                   |
| `POSTGRES_USER`          | Usuário Postgres             | `app`                      |
| `POSTGRES_PASSWORD`      | Senha Postgres               | `secret`                   |
| `POSTGRES_HOST`          | Host Postgres                | `db`                       |
| `CELERY_BROKER_URL`      | URL do broker Redis          | `redis://redis:6379/0`     |
| `CELERY_RESULT_BACKEND`  | URL do result backend Redis  | `redis://redis:6379/1`     |
| `DJANGO_SECRET_KEY`      | Chave secreta Django         | (obrigatória)               |
| `DEBUG`                  | Modo debug                   | `true`                     |
