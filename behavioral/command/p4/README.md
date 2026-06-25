# CLI History with Replay (Command) — P4

CLI Typer que mantém uma lista de tarefas, registra cada operação executada
em um log SQLite append-only, e é capaz de reconstruir o estado inteiro a
partir desse log (replay) — além de suportar `undo`.

## Objetivo pedagógico

Demonstrar o pattern **Command** com foco em **persistência e replay**: cada
comando sabe se descrever (`to_payload()` + `get_command_name()`), o que
permite reconstituí-lo a partir do log e reaplicá-lo, sem que o log precise
conhecer nada sobre a lógica de cada operação.

Elementos do pattern:
- **Command (abstrato):** `TodoCommand` (`domain/interfaces.py`)
- **Concrete Commands:** `AddItemCommand`, `RemoveItemCommand`
- **Receiver:** `TodoList` (sabe apenas `add`/`remove`, nada sobre histórico)
- **Client/Invoker:** `ExecuteCommandUseCase` (executa e loga), `UndoLastCommandUseCase` (reverte), `ReplayHistoryUseCase` (reconstrói do zero a partir do log)

## Diagrama (ASCII)

```
CLI: add "Buy milk"
      │
      ▼
ExecuteCommandUseCase ──build_command()──► AddItemCommand
      │                                          │
      ▼                                          ▼
SqliteStateRepository.load() ──► TodoList ──► command.execute(state) ──► SqliteStateRepository.save()
                                                  │
                                                  ▼
                                  SqliteCommandLogRepository.append("add", {"item": "Buy milk"})

CLI: replay
      │
      ▼
ReplayHistoryUseCase ──► TodoList() vazio ──► para cada entrada do log: build_command(name, payload).execute(state)
```

## Como rodar

```bash
cp .env.example .env
docker-compose run --rm app python -m cli_history.main add "Buy milk"
docker-compose run --rm app python -m cli_history.main add "Walk dog"
docker-compose run --rm app python -m cli_history.main list
docker-compose run --rm app python -m cli_history.main undo
docker-compose run --rm app python -m cli_history.main history
docker-compose run --rm app python -m cli_history.main replay
```

O estado e o log vivem em um arquivo SQLite local (`cli_history.db`, ver
`.env.example`), persistido entre execuções via volume do Docker Compose.

**Nota:** `undo` não remove a entrada correspondente do log — o log é um
registro de auditoria imutável de tudo que foi executado. Por isso,
`replay` reconstrói o estado *antes* de qualquer `undo`; é um trade-off
didático para manter o log simples como fonte de replay.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada `TodoCommand` concreto encapsula uma única operação reversível; os repositórios SQLite só persistem, sem regra de negócio.
- **OCP:** adicionar uma nova operação (ex.: renomear item) = criar uma nova subclasse de `TodoCommand` e uma entrada em `COMMAND_REGISTRY`, sem tocar nos use cases.
- **LSP:** qualquer `TodoCommand` pode ser executado/desfeito/repetido pelos use cases — todos respeitam o mesmo contrato `execute`/`undo`/`to_payload`.
- **ISP:** `TodoCommand`, `StateRepository` e `CommandLogRepository` são interfaces pequenas e focadas.
- **DIP:** todos os use cases dependem das abstrações de domínio; a CLI (`main.py`) é o único lugar que conhece as implementações SQLite concretas.
