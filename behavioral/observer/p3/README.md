# Django Signals System (Observer) — P3

API Django onde a criação/atualização de um `Order` dispara um
`OrderEvent` que se propaga, via um `django.dispatch.Signal`, para
dois observadores independentes: um log de auditoria e um log de
notificações.

> **Nota de ambiente:** o PLAN.md especifica PostgreSQL; este projeto
> usa SQLite como stand-in (mesmo precedente de outros projetos do
> dataset). Troque o `ENGINE` em `config/settings.py` por
> `django.db.backends.postgresql` para apontar para uma instância real.

## Objetivo pedagógico

Demonstrar o pattern **Observer** usando o próprio mecanismo de sinais
do Django — que já é, por si, uma implementação do Observer. `OrderSubject`
(domínio) define `subscribe`/`unsubscribe`/`notify`; `DjangoSignalOrderSubject`
(infraestrutura) adapta esse contrato para `Signal.connect`/`disconnect`/`send`,
para que o resto do código nunca dependa diretamente da API do Django.

Elementos do pattern:
- **Subject (abstrato):** `OrderSubject` (`domain/interfaces.py`)
- **ConcreteSubject:** `DjangoSignalOrderSubject` (`infrastructure/signal_subject.py`)
- **Observer (abstrato):** `OrderObserver` (`domain/interfaces.py`)
- **ConcreteObservers:** `AuditLogObserver`, `NotificationObserver` (`infrastructure/observers.py`)

## Diagrama (ASCII)

```
CreateOrderUseCase / UpdateOrderStatusUseCase
        │
        ▼ subject.notify(event)
DjangoSignalOrderSubject ──► order_event_signal.send()
        │                          │
        │              ┌───────────┴────────────┐
        ▼              ▼                         ▼
  AuditLogObserver           NotificationObserver
  (AuditLogEntryModel)       (NotificationLogModel)
```

Os observadores são inscritos **uma única vez**, na importação do
módulo `django_app/views.py` — assinar (`connect`) a cada requisição
vazaria um receiver duplicado por chamada na tabela global de
dispatch do Django, causando entradas de log duplicadas.

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                                | Descrição                                |
|--------|--------------------------------------|--------------------------------------------|
| POST   | `/orders/`                           | Cria um pedido e notifica os observadores   |
| PUT    | `/orders/<order_id>/status/`         | Atualiza o status e notifica os observadores|
| GET    | `/orders/<order_id>/audit/`          | Lista o log de auditoria do pedido          |
| GET    | `/orders/<order_id>/notifications/`  | Lista o log de notificações do pedido       |

```bash
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "o1", "total": 42.0}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes unitários de `DjangoSignalOrderSubject` usam um `Signal()`
isolado por teste (em vez do `order_event_signal` global) para que
receivers de um teste nunca vazem para outro.

## SOLID

- **SRP:** `AuditLogObserver` e `NotificationObserver` cada um só escreve em seu próprio modelo; `DjangoSignalOrderSubject` só adapta o contrato de domínio ao Django Signal.
- **OCP:** uma nova reação a eventos de pedido (ex.: cobrança) é uma nova classe `OrderObserver`, inscrita junto às demais — sem alterar `OrderSubject` nem os use cases.
- **LSP:** qualquer implementação de `OrderSubject`/`OrderObserver` pode substituir as concretas Django nos use cases sem quebrar o contrato (ver o `FakeOrderSubject` usado nos testes de use case).
- **ISP:** `OrderObserver` expõe só `on_order_event`; `OrderSubject` só os três métodos que o domínio realmente precisa.
- **DIP:** os use cases dependem de `OrderSubject` (abstração), nunca de `DjangoSignalOrderSubject` diretamente — injeção via construtor nas views.
