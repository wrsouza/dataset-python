# WebSocket Chat Room (Mediator) — P1

API FastAPI onde clientes conectados via WebSocket trocam mensagens sem
nunca se referenciarem diretamente — toda comunicação passa por um
`RedisChatMediator`, que usa Redis Pub/Sub para sincronizar múltiplos
processos do servidor na mesma sala.

## Objetivo pedagógico

Demonstrar o pattern **Mediator**: cada `ChatParticipant` (Colleague) só
conhece o mediador, nunca os outros participantes. O mediador centraliza a
lógica de roteamento ("entregar para todo mundo, exceto o remetente"),
permitindo trocar a estratégia de roteamento sem tocar nos participantes.

Elementos do pattern:
- **Mediator (abstrato):** `ChatMediator` (`domain/interfaces.py`)
- **Concrete Mediator:** `RedisChatMediator` — publica no Redis e despacha para os participantes locais registrados
- **Colleague (abstrato):** `ChatParticipant`
- **Concrete Colleague:** `WebSocketChatParticipant` — entrega a mensagem ao cliente WebSocket
- **Client:** `SendMessageUseCase`, que nunca conhece os destinatários — só fala com o mediador

## Diagrama (ASCII)

```
Alice (WebSocket) ──send_text──► SendMessageUseCase ──► RedisChatMediator.send("alice", "hi")
                                                                  │
                                                                  ▼
                                                    Redis Pub/Sub channel "chat-room:room-1"
                                                                  │
                              ┌───────────────────────────────────┴───────────────────────────────────┐
                              ▼                                                                         ▼
                  RedisChatMediator (processo A)                                          RedisChatMediator (processo B)
                  dispatcha para participantes locais,                                     dispatcha para participantes locais,
                  exceto o remetente                                                       exceto o remetente
                              │                                                                         │
                              ▼                                                                         ▼
                       Bob (WebSocket)                                                          Carol (WebSocket)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

Conecte-se via WebSocket em `ws://localhost:8000/ws/rooms/<room_id>` —
qualquer texto enviado é entregue a todos os outros clientes conectados à
mesma sala (em qualquer processo do servidor, via Redis).

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes usam um `FakePubSubClient` em memória (baseado em
`asyncio.Queue`), incluindo um teste que simula **dois mediadores
diferentes compartilhando o mesmo canal** — provando o fan-out entre
"processos" sem precisar de um Redis real.

## SOLID

- **SRP:** `RedisChatMediator` só roteia mensagens; `WebSocketChatParticipant` só entrega ao socket; nenhum dos dois conhece a lógica do outro.
- **OCP:** trocar a estratégia de entrega (ex.: round-robin, broadcast com eco) = ajustar `RedisChatMediator._listen`, sem tocar em `ChatParticipant`.
- **LSP:** qualquer `ChatParticipant` pode ser registrado no mediador — todos respeitam o mesmo contrato `get_participant_id`/`receive`.
- **ISP:** `ChatMediator` e `ChatParticipant` são interfaces pequenas e focadas.
- **DIP:** os use cases dependem de `ChatMediator`/`ChatParticipant` (abstrações); `RedisChatMediator` depende do `Protocol` `PubSubClient`, nunca de `redis.asyncio` diretamente.
