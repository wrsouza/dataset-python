# Message Processing Chain (Chain of Responsibility) — P4

CLI Typer que consome mensagens de uma fila RabbitMQ e as roteia por uma
cadeia de validação — schema → deduplicação → roteamento final — antes de
confirmar (`ack`) o processamento.

## Objetivo pedagógico

Demonstrar o pattern **Chain of Responsibility** num pipeline de mensageria:
cada handler decide, isoladamente, se rejeita a mensagem ou a passa adiante,
sem que o caller (`ConsumeAndProcessUseCase`) precise conhecer a ordem ou a
quantidade de verificações.

Elementos do pattern:
- **Handler (abstrato):** `MessageHandler` (`domain/interfaces.py`)
- **Concrete Handlers:** `SchemaValidationHandler`, `DeduplicationHandler`, `RoutingHandler`
- **Client:** `ProcessMessageUseCase` / `ConsumeAndProcessUseCase`, que disparam `chain.handle(message)` sem conhecer a topologia da cadeia

## Diagrama (ASCII)

```
RabbitMQ queue
      │
      ▼
ConsumeAndProcessUseCase
      │
      ▼
SchemaValidationHandler ──(campos OK)──► DeduplicationHandler ──(inédita)──► RoutingHandler
     │ rejeita                                │ rejeita (duplicada)                │ processa (sempre)
     ▼                                        ▼                                    ▼
  IncomingMessage (com 1 ProcessingStep no histórico) + ack na fila
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build

# rodar a CLI manualmente (com RabbitMQ já no ar):
docker-compose run --rm app python -m message_pipeline.main process --queue orders --limit 10

# simular uma mensagem sem precisar de broker:
docker-compose run --rm app python -m message_pipeline.main simulate \
  --message-id m-1 --payload '{"order_id": "o-1", "amount": 42}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes unitários usam um `FakeChannel` no lugar de uma conexão pika real
— nenhuma chamada de rede é feita fora dos testes de integração manuais com
`docker-compose`.

## SOLID

- **SRP:** cada handler verifica um único critério (schema, duplicidade); a leitura/ack da fila fica isolada em `RabbitMQQueueConsumer`.
- **OCP:** adicionar uma nova verificação (ex.: rate limiting por cliente) = criar uma nova subclasse de `MessageHandler` e religar a cadeia, sem tocar nas existentes.
- **LSP:** qualquer `MessageHandler` pode substituir outro no encadeamento — todos respeitam o mesmo contrato `handle(message) -> message`.
- **ISP:** `MessageHandler` e `QueueConsumer` são interfaces pequenas e focadas (uma para tratar, outra para consumir/confirmar).
- **DIP:** os use cases dependem de `MessageHandler`/`QueueConsumer` (abstrações); a CLI (`main.py`) é o único lugar que conhece `RabbitMQQueueConsumer` e o pika real.
