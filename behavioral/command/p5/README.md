# Event Sourcing (Command) — P5

API FastAPI onde cada operação numa conta (`open`, `deposit`, `withdraw`) é
encapsulada como um Command, validado contra o estado atual (reconstruído
por replay do log de eventos), persistido em PostgreSQL e publicado em
Kafka para consumidores externos.

## Objetivo pedagógico

Demonstrar o pattern **Command** em sua forma mais próxima de Event
Sourcing: um Command não muta o estado diretamente — ele se valida contra
o estado replayado e retorna o `DomainEvent` resultante. O estado "vivo"
nunca é persistido; apenas o log de eventos é a fonte da verdade.

Elementos do pattern:
- **Command (abstrato):** `AccountCommand` (`domain/interfaces.py`)
- **Concrete Commands:** `OpenAccountCommand`, `DepositCommand`, `WithdrawCommand`
- **Receiver:** `AccountState` (estado replayado a partir do log; commands se validam contra ele)
- **Client/Invoker:** `DispatchCommandUseCase`, que faz replay → valida via command → persiste e publica o evento

## Diagrama (ASCII)

```
POST /accounts/acc-1/deposit {"amount": 100}
      │
      ▼
DispatchCommandUseCase
      │
      ├─ event_store.get_events("acc-1") ──► replay() ──► AccountState atual
      │                                                          │
      ▼                                                          ▼
DepositCommand.execute(state) ──valida (conta aberta? valor > 0?)──► DomainEvent("funds_deposited")
      │
      ├─► PostgresEventStore.append(event)   (fonte da verdade)
      └─► KafkaEventPublisher.publish(event)  (consumidores externos)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000` (Swagger em `/docs`).

### Endpoints

| Método | Rota                              | Descrição                                   |
|--------|-----------------------------------|------------------------------------------------|
| POST   | `/accounts/{id}/open`             | Abre uma nova conta                             |
| POST   | `/accounts/{id}/deposit`          | Deposita fundos (`{"amount": 100}`)             |
| POST   | `/accounts/{id}/withdraw`         | Retira fundos (`{"amount": 50}`)                |
| GET    | `/accounts/{id}`                  | Estado atual (reconstruído via replay)          |
| GET    | `/accounts/{id}/events`           | Histórico completo de eventos                   |
| GET    | `/health`                         | Healthcheck                                     |

```bash
curl -X POST http://localhost:8000/accounts/acc-1/open
curl -X POST http://localhost:8000/accounts/acc-1/deposit -d '{"amount": 100}' -H "Content-Type: application/json"
curl http://localhost:8000/accounts/acc-1
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes de `PostgresEventStore` usam um fake DB-API connection (mesmo
contrato `cursor()`/`execute()`/`fetchall()`), e os de `KafkaEventPublisher`
usam um fake producer — nenhuma chamada de rede real é feita.

## SOLID

- **SRP:** cada `AccountCommand` concreto valida e descreve uma única operação; o event store só persiste; o publisher só publica.
- **OCP:** adicionar uma nova operação (ex.: transferência entre contas) = criar uma nova subclasse de `AccountCommand` e um novo `EventType`, sem tocar no `DispatchCommandUseCase`.
- **LSP:** qualquer `AccountCommand` pode ser passado a `DispatchCommandUseCase` — todos respeitam o mesmo contrato `execute(state) -> DomainEvent`.
- **ISP:** `AccountCommand`, `EventStore` e `EventPublisher` são interfaces pequenas e focadas.
- **DIP:** `DispatchCommandUseCase` depende de `EventStore`/`EventPublisher` (abstrações); a API FastAPI usa `Depends()` para injetar as implementações concretas, trocadas por fakes nos testes via `app.dependency_overrides`.
