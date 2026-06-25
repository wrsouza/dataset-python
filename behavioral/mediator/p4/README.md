# Service Bus Mediator (Mediator) — P4

CLI Typer onde diferentes "serviços" trocam mensagens sem se conhecerem
diretamente — toda comunicação passa por uma fila SQS, mediada pelo
`SqsServiceBusMediator`.

## Objetivo pedagógico

Demonstrar o pattern **Mediator** num barramento de serviços distribuído:
um serviço produtor chama `send()` sem saber quem vai consumir; um
serviço consumidor chama `receive()` sem saber quem produziu. O SQS é o
"correio" físico que o mediador usa por baixo.

Elementos do pattern:
- **Mediator (abstrato):** `ServiceBusMediator` (`domain/interfaces.py`)
- **Concrete Mediator:** `SqsServiceBusMediator` — envia/recebe via SQS, removendo a mensagem após a entrega
- **Colleagues:** os "serviços" que chamam `send`/`receive` via CLI, identificados só pelo nome
- **Client:** `SendMessageUseCase`/`ReceiveMessagesUseCase`

## Diagrama (ASCII)

```
CLI: send billing-service '{"invoice_id": "i-1"}'
      │
      ▼
SendMessageUseCase ──► SqsServiceBusMediator.send("billing-service", payload)
                                  │
                                  ▼
                          fila SQS "service-bus-demo"
                                  │
CLI: receive (de qualquer outro processo) ──► SqsServiceBusMediator.receive(max_messages)
                                  │
                                  ▼
                  mensagem entregue + removida da fila (delete_message)
```

## Como rodar

```bash
cp .env.example .env
docker-compose run --rm app python -m service_bus.main send billing-service '{"invoice_id": "i-1"}'
docker-compose run --rm app python -m service_bus.main receive --max-messages 5
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes de `SqsServiceBusMediator` usam [`moto`](https://github.com/getmoto/moto)
para simular o SQS; os de use cases e CLI usam um `FakeServiceBusMediator`
em memória — nenhuma chamada de rede real é feita.

## SOLID

- **SRP:** `SqsServiceBusMediator` só roteia mensagens (envia/recebe/remove); a CLI só formata saída.
- **OCP:** trocar o transporte (ex.: SNS, EventBridge) = criar um novo `ServiceBusMediator`, sem tocar nos use cases nem na CLI.
- **LSP:** qualquer `ServiceBusMediator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `send`/`receive`.
- **ISP:** `ServiceBusMediator` é uma interface pequena e focada (dois métodos).
- **DIP:** `SendMessageUseCase`/`ReceiveMessagesUseCase` dependem de `ServiceBusMediator` (abstração); a CLI (`main.py`) é o único lugar que conhece `SqsServiceBusMediator`.
