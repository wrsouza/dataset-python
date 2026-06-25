# Support Ticket Escalation (Chain of Responsibility) — P2

Flask API that routes a support ticket through an escalation chain
(Tier 1 → Tier 2 → Tier 3 → Management) until a handler is able to resolve
it, persisting the outcome in PostgreSQL.

## Objetivo pedagógico

Demonstrar o pattern **Chain of Responsibility**: cada handler decide,
de forma independente, se consegue tratar a requisição ou se deve
encaminhá-la ao próximo elo da cadeia. O cliente (`SubmitTicketUseCase`)
não sabe nem precisa saber qual handler vai resolver o ticket.

Elementos do pattern:
- **Handler (abstrato):** `TicketHandler` (`domain/interfaces.py`)
- **Concrete Handlers:** `Tier1Handler`, `Tier2Handler`, `Tier3Handler`, `ManagementHandler`
- **Client:** `SubmitTicketUseCase`, que dispara `chain.handle(ticket)` sem conhecer a topologia da cadeia

## Diagrama (ASCII)

```
Client
  │
  ▼
SubmitTicketUseCase
  │
  ▼
Tier1Handler ──(não resolve)──► Tier2Handler ──► Tier3Handler ──► ManagementHandler
     │ resolve                        │ resolve         │ resolve         │ resolve (sempre)
     ▼                                ▼                 ▼                 ▼
  SupportTicket (resolvido, com histórico de 1 EscalationStep)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota                  | Descrição                          |
|--------|-----------------------|-------------------------------------|
| POST   | `/tickets`             | Cria e escalona um ticket           |
| GET    | `/tickets/<ticket_id>` | Consulta um ticket pelo id          |
| GET    | `/health`              | Healthcheck                         |

```bash
curl -X POST http://localhost:5000/tickets \
  -H "Content-Type: application/json" \
  -d '{"subject": "Cannot log in", "severity": "critical", "customer_email": "a@b.com"}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada `TicketHandler` concreto trata uma única severidade-limite; persistência fica isolada em `PostgresTicketRepository`.
- **OCP:** adicionar uma nova tier de suporte = criar uma nova subclasse de `TicketHandler` e religar a cadeia, sem tocar nas existentes.
- **LSP:** qualquer `TicketHandler` pode substituir outro no encadeamento — todos respeitam o mesmo contrato `handle(ticket) -> ticket`.
- **ISP:** `TicketHandler` e `TicketRepository` são interfaces pequenas e focadas (uma para tratar, outra para persistir).
- **DIP:** `SubmitTicketUseCase` depende de `TicketHandler`/`TicketRepository` (abstrações), nunca de `PostgresTicketRepository` diretamente — injeção via construtor.
