# Workflow Approval FSM (State) — P3

API Django que modela a aprovação de uma solicitação como uma máquina
de estados explícita (`Draft` → `PendingApproval` → `Approved`/`Rejected`),
notificando aprovadores/solicitantes de forma assíncrona via Celery a
cada transição.

> **Nota de ambiente:** o PLAN.md especifica PostgreSQL; este projeto
> usa SQLite como stand-in (mesmo precedente de outros projetos do
> dataset). Troque o `ENGINE` em `config/settings.py` por
> `django.db.backends.postgresql` para apontar para uma instância real.

## Objetivo pedagógico

Demonstrar o pattern **State**: `WorkflowRequest` (Context) delega todo
o comportamento (`submit`, `approve`, `reject`, `request_changes`) ao
objeto de estado atual, sem nenhum `if/elif` checando o estado.
Transições inválidas (ex.: `approve` num request `Draft`) levantam
`InvalidTransitionError` automaticamente. Cada transição válida
dispara uma task Celery (`notify_task`) que grava um log de
notificação — a lógica de FSM nunca bloqueia esperando essa notificação.

Elementos do pattern:
- **Context:** `WorkflowRequest` (`domain/entities.py`)
- **State (abstrato):** `WorkflowState` (`domain/interfaces.py`)
- **Concrete States:** `DraftState`, `PendingApprovalState`, `ApprovedState`, `RejectedState` (`infrastructure/states/`)

## Diagrama (ASCII)

```
Draft ──submit──► PendingApproval ──approve──► Approved (terminal)
  ▲                     │
  └──request_changes────┤
                         └──reject──► Rejected (terminal)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                                      | Descrição                                |
|--------|--------------------------------------------|--------------------------------------------|
| POST   | `/workflows/`                               | Cria uma solicitação em `Draft`             |
| POST   | `/workflows/<id>/submit/`                   | Envia para aprovação                        |
| POST   | `/workflows/<id>/approve/`                  | Aprova a solicitação                        |
| POST   | `/workflows/<id>/reject/`                   | Rejeita a solicitação                       |
| POST   | `/workflows/<id>/request-changes/`          | Devolve para `Draft`                        |
| GET    | `/workflows/<id>/`                          | Consulta o estado atual                     |

```bash
curl -X POST http://localhost:8000/workflows/ \
  -H "Content-Type: application/json" \
  -d '{"request_id": "r1", "title": "Buy laptops"}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`CELERY_TASK_ALWAYS_EAGER` (definido em `config/settings_test.py`) faz
a task de notificação rodar de forma síncrona nos testes, sem precisar
de um Redis real.

## SOLID

- **SRP:** cada estado concreto só sabe lidar com suas próprias transições; `notify_task` só grava o log de notificação, sem conhecer a FSM.
- **OCP:** um novo estado (ex.: `Cancelled`) é uma nova classe `WorkflowState` mais uma entrada em `_STATE_REGISTRY` — sem tocar nos estados existentes.
- **LSP:** qualquer `WorkflowState` concreto pode ocupar `WorkflowRequest._state` — todos respeitam o mesmo contrato (transições não suportadas levantam `InvalidTransitionError` por padrão).
- **ISP:** `WorkflowState` expõe só as quatro transições que o domínio precisa; cada estado concreto sobrescreve apenas as que permite.
- **DIP:** os use cases dependem de `DjangoWorkflowRepository` via injeção de construtor nas views.
