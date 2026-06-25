# Scheduled Command Executor (Command) — P3

Django app que despacha comandos (`cleanup`, `backup`) para um worker Celery
via Redis, encapsulando cada tarefa como um objeto Command, e persiste o
resultado de cada execução.

## Objetivo pedagógico

Demonstrar o pattern **Command** num cenário distribuído: o objeto Command
é serializado pelo nome + payload, enviado a um worker Celery (que pode
estar em outro processo/máquina), e só lá é desserializado de volta em um
`ScheduledCommand` concreto e executado contra seu Receiver. O Invoker
(`run_command_task`) nunca conhece os detalhes de cada tarefa.

Elementos do pattern:
- **Command (abstrato):** `ScheduledCommand` (`domain/interfaces.py`)
- **Concrete Commands:** `CleanupCommand`, `BackupCommand`
- **Receiver:** `CleanupReceiver`, `BackupReceiver`
- **Invoker:** `run_command_task` (tarefa Celery que executa o comando, sem saber o que ele faz)
- **Client:** `TriggerCommandUseCase`, que resolve o nome do comando via `COMMAND_REGISTRY` (OCP)

## Diagrama (ASCII)

```
POST /commands/trigger/ {"command_name": "backup", "payload": {"target": "orders-db"}}
      │
      ▼
TriggerCommandUseCase ──valida via build_command()──► run_command_task.delay(name, payload)
      │                                                          │
      │                                                   (worker Celery / Redis)
      │                                                          ▼
      │                                          build_command(name, payload) → BackupCommand(receiver=BackupReceiver)
      │                                                          │
      ▼                                                          ▼
DjangoExecutionRepository.save(ExecutionRecord) ◄──── command.execute() → BackupReceiver.backup()
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`. Em produção, o serviço `worker`
roda o consumidor Celery que de fato executa os comandos via Redis.

### Endpoints

| Método | Rota                        | Descrição                                   |
|--------|-----------------------------|------------------------------------------------|
| POST   | `/commands/trigger/`        | Despacha um comando (`cleanup` ou `backup`)     |
| GET    | `/commands/<job_id>/`       | Consulta o resultado de uma execução            |

```bash
curl -X POST http://localhost:8000/commands/trigger/ \
  -H "Content-Type: application/json" \
  -d '{"command_name": "backup", "payload": {"target": "orders-db"}}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes rodam com `CELERY_TASK_ALWAYS_EAGER=true` (definido em
`config/settings_test.py`), então a tarefa Celery executa de forma
síncrona, sem precisar de Redis nem de um worker real.

## SOLID

- **SRP:** cada `ScheduledCommand` concreto encapsula uma única operação; o Invoker só executa e propaga o resultado; o repositório só persiste.
- **OCP:** adicionar uma nova tarefa agendável = criar uma nova subclasse de `ScheduledCommand`, um novo Receiver e uma entrada em `COMMAND_REGISTRY`, sem tocar na tarefa Celery ou nos use cases.
- **LSP:** qualquer `ScheduledCommand` pode ser executado pela tarefa Celery — todos respeitam o mesmo contrato `execute() -> str`.
- **ISP:** `ScheduledCommand` e `ExecutionRepository` são interfaces pequenas e focadas.
- **DIP:** `TriggerCommandUseCase` depende de `CommandTask`/`ExecutionRepository` (abstrações via `Protocol`), nunca da tarefa Celery real diretamente — injeção via construtor.
