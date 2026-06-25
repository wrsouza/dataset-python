# Real-time Notifications (Mediator) — P3

App Django Channels onde publicadores HTTP e clientes WebSocket nunca se
conhecem diretamente — toda a coordenação passa pelo `ChannelsNotificationMediator`
(que delega o fan-out ao channel layer do Django Channels) e pelo
`NotificationConsumer` (que entrega ao socket conectado).

## Objetivo pedagógico

Demonstrar o pattern **Mediator** sobre a infraestrutura de channel layers
do Django Channels: uma view HTTP publica uma notificação sem saber quais
clientes WebSocket (se algum) estão ouvindo; o consumer entrega a
notificação sem saber quem a publicou. O channel layer (Redis em produção,
em memória nos testes) é o "correio" que o mediador usa por baixo.

Elementos do pattern:
- **Mediator (abstrato):** `NotificationMediator` (`domain/interfaces.py`)
- **Concrete Mediator:** `ChannelsNotificationMediator` — delega ao channel layer via `group_send`
- **Colleague (publicador):** a view `publish_notification`, via `PublishNotificationUseCase`
- **Colleague (assinante):** `NotificationConsumer`, que entra no grupo no `connect()` e repassa eventos `notification.message` ao WebSocket

## Diagrama (ASCII)

```
POST /notifications/room-1/ {"message": {"text": "hi"}}
      │
      ▼
PublishNotificationUseCase ──persiste──► PostgreSQL (NotificationModel)
      │
      ▼
ChannelsNotificationMediator.notify("room-1", message)
      │
      ▼
channel_layer.group_send("room-1", {"type": "notification.message", ...})
      │
      ▼
NotificationConsumer (todo cliente WebSocket no grupo "room-1")
      │
      ▼
notification_message(event) ──► send_json(event["message"])
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API/WebSocket disponíveis em `http://localhost:8000`.

### Endpoints

| Método    | Rota                                  | Descrição                                    |
|-----------|----------------------------------------|--------------------------------------------------|
| POST      | `/notifications/<group>/`              | Publica uma notificação para o grupo              |
| GET       | `/notifications/<group>/list/`         | Lista o histórico de notificações do grupo        |
| WebSocket | `/ws/notifications/<group>/`           | Conecta-se ao grupo e recebe notificações em tempo real |

```bash
curl -X POST http://localhost:8000/notifications/room-1/ \
  -H "Content-Type: application/json" \
  -d '{"message": {"text": "hello"}}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes usam `channels.layers.InMemoryChannelLayer` (configurado em
`config/settings_test.py`) e `channels.testing.WebsocketCommunicator`,
então nenhum Redis ou PostgreSQL real é necessário.

## SOLID

- **SRP:** `ChannelsNotificationMediator` só roteia; `NotificationConsumer` só entrega ao socket; `DjangoNotificationRepository` só persiste.
- **OCP:** trocar o transporte (ex.: SSE em vez de WebSocket) = criar um novo Colleague consumidor do mesmo channel layer, sem tocar no mediador.
- **LSP:** qualquer `NotificationMediator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `notify(group, message)`.
- **ISP:** `NotificationMediator` e `NotificationRepository` são interfaces pequenas e focadas.
- **DIP:** `PublishNotificationUseCase` depende de `NotificationMediator`/`NotificationRepository` (abstrações); a view é o único lugar que conhece `ChannelsNotificationMediator` e `get_channel_layer()`.
