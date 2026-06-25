# Event Bus (Mediator) — P2

API Flask onde publicadores e handlers de eventos nunca se conhecem
diretamente — toda coordenação passa por um `RabbitMQEventBus`, que
despacha localmente para os handlers inscritos e também publica em um
exchange fanout do RabbitMQ para fan-out entre processos.

## Objetivo pedagógico

Demonstrar o pattern **Mediator** num barramento de eventos: cada
`EventHandler` (Colleague) só conhece o `EventBus`, nunca quem publicou o
evento nem outros handlers. O bus centraliza o roteamento por tipo de
evento (ou `"*"` para todos os tipos).

Elementos do pattern:
- **Mediator (abstrato):** `EventBus` (`domain/interfaces.py`)
- **Concrete Mediator:** `RabbitMQEventBus` — despacha local + publica no RabbitMQ
- **Colleague (abstrato):** `EventHandler`
- **Concrete Colleague:** `LoggingEventHandler`
- **Client:** `PublishEventUseCase`, que nunca conhece os handlers — só fala com o bus

## Diagrama (ASCII)

```
POST /events {"event_type": "order.created", "payload": {...}}
      │
      ▼
PublishEventUseCase ──► RabbitMQEventBus.publish("order.created", payload)
                                    │
                  ┌─────────────────┼─────────────────────┐
                  ▼                                        ▼
     exchange fanout "events" (RabbitMQ)         handlers locais inscritos em
     → outros processos do servidor               "order.created" ou "*"
                                                            │
                                                            ▼
                                                  LoggingEventHandler.handle(event)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota          | Descrição                                  |
|--------|---------------|------------------------------------------------|
| POST   | `/events`     | Publica um evento (`{"event_type", "payload"}`) |
| GET    | `/events/log` | Lista os eventos recebidos pelo `LoggingEventHandler` |
| GET    | `/health`     | Healthcheck                                     |

```bash
curl -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "order.created", "payload": {"order_id": "o-1"}}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** `RabbitMQEventBus` só roteia; cada `EventHandler` só reage ao que lhe interessa.
- **OCP:** adicionar um novo handler (ex.: enviar e-mail em `order.created`) = criar uma nova subclasse de `EventHandler` e inscrevê-la, sem tocar no bus nem nos publicadores.
- **LSP:** qualquer `EventHandler` pode ser inscrito no bus — todos respeitam o mesmo contrato `get_handler_id`/`handle`.
- **ISP:** `EventBus` e `EventHandler` são interfaces pequenas e focadas.
- **DIP:** os use cases dependem de `EventBus`/`EventHandler` (abstrações); `RabbitMQEventBus` depende do `Protocol` `PikaChannel`, nunca de `pika` diretamente.
