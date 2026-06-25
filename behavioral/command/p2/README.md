# Task Queue System (Command) — P2

Flask API que encapsula cada tarefa (enviar e-mail, gerar relatório) como um
objeto Command, executa-o através de um Invoker que mantém histórico, e
publica o comando em uma fila RabbitMQ para auditoria/replay.

## Objetivo pedagógico

Demonstrar o pattern **Command**: cada operação é encapsulada como um
objeto com `execute()`, desacoplando quem solicita a operação (a API) de
quem efetivamente a realiza (o Receiver). O Invoker não conhece os
detalhes de nenhuma tarefa — apenas o contrato `TaskCommand`.

Elementos do pattern:
- **Command (abstrato):** `TaskCommand` (`domain/interfaces.py`)
- **Concrete Commands:** `SendEmailCommand`, `GenerateReportCommand`
- **Receiver:** `EmailReceiver`, `ReportReceiver` (quem efetivamente realiza o trabalho)
- **Invoker:** `TaskQueueInvoker` (executa comandos e mantém histórico, sem saber o que cada um faz)
- **Client:** `EnqueueTaskUseCase`, que resolve o nome do comando via `COMMAND_REGISTRY` (OCP)

## Diagrama (ASCII)

```
POST /tasks {"command": "send_email", "payload": {...}}
      │
      ▼
EnqueueTaskUseCase ──build_command()──► COMMAND_REGISTRY ──► SendEmailCommand(receiver=EmailReceiver)
      │                                                              │
      ▼                                                              ▼
TaskQueueInvoker.execute(command) ──────────────────────────► command.execute() → EmailReceiver.send()
      │
      ▼
RabbitMQTaskPublisher.publish(name, payload)  (auditoria/replay)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota              | Descrição                                  |
|--------|-------------------|----------------------------------------------|
| POST   | `/tasks`           | Cria e executa uma tarefa (`send_email` ou `generate_report`) |
| GET    | `/tasks/<task_id>` | Consulta o resultado de uma tarefa            |
| GET    | `/health`          | Healthcheck                                   |

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"command": "send_email", "payload": {"to": "a@b.com", "subject": "Hi", "body": "Hello"}}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada `TaskCommand` concreto encapsula uma única operação; o Invoker só lida com execução e histórico; o Publisher só lida com auditoria.
- **OCP:** adicionar uma nova tarefa = criar uma nova subclasse de `TaskCommand`, um novo Receiver e uma entrada em `COMMAND_REGISTRY`, sem tocar no Invoker ou nos use cases.
- **LSP:** qualquer `TaskCommand` pode ser passado ao Invoker — todos respeitam o mesmo contrato `execute() -> str`.
- **ISP:** `TaskCommand` e `TaskPublisher` são interfaces pequenas e focadas.
- **DIP:** `EnqueueTaskUseCase` depende de `TaskPublisher` (abstração) e do `TaskQueueInvoker`; nunca importa `RabbitMQTaskPublisher` diretamente — injeção via construtor.
