# Download Manager State (State) — P4

CLI Typer que gerencia o ciclo de vida de um download do S3 como uma
máquina de estados explícita (`Idle` → `Downloading` → `Paused`/`Completed`/`Failed`),
persistindo o estado em SQLite (cada comando roda em um processo novo).

## Objetivo pedagógico

Demonstrar o pattern **State**: `DownloadJob` (Context) delega todo o
comportamento (`start`, `pause`, `resume`, `complete`, `fail`, `retry`)
ao objeto de estado atual, sem nenhum `if/elif` checando o estado.
`complete` é a única transição que fala com o S3 — confirma que o
objeto existe via `head_object` e grava o tamanho, simulando "a
transferência terminou".

Elementos do pattern:
- **Context:** `DownloadJob` (`domain/entities.py`)
- **State (abstrato):** `DownloadState` (`domain/interfaces.py`)
- **Concrete States:** `IdleState`, `DownloadingState`, `PausedState`, `CompletedState`, `FailedState` (`infrastructure/states/`)

## Diagrama (ASCII)

```
Idle ──start──► Downloading ──complete──► Completed (terminal)
 ▲                  │   │
 │                  │   └──fail──► Failed ──retry──┐
 │                  └──pause──► Paused ──resume──► Downloading
 └─────────────────────────retry──────────────────┘
```

## Como rodar

```bash
cp .env.example .env
docker-compose run --rm app python -m download_manager_fsm.main start job-1 my-bucket/file.zip
docker-compose run --rm app python -m download_manager_fsm.main status job-1
docker-compose run --rm app python -m download_manager_fsm.main complete job-1
```

### Comandos

| Comando    | Descrição                                                  |
|------------|---------------------------------------------------------------|
| `start`    | Inicia (ou reinicia) um download                               |
| `pause`    | Pausa um download em andamento                                 |
| `resume`   | Retoma um download pausado                                     |
| `complete` | Confirma o tamanho do objeto no S3 e marca como concluído       |
| `fail`     | Marca o download como falho, registrando um motivo             |
| `retry`    | Reseta um download falho/pausado para `Idle`                   |
| `status`   | Mostra o estado atual de um job                                 |

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`CompleteDownloadUseCase` é testado com um `FakeS3Client` em
memória nos testes unitários, e com `moto` (bucket/objeto reais
simulados) nos testes de integração da CLI.

## SOLID

- **SRP:** cada estado concreto só sabe lidar com suas próprias transições; `SqliteDownloadJobRepository` só persiste/recupera o job.
- **OCP:** um novo estado (ex.: `Verifying`, para checksum) é uma nova classe `DownloadState` mais uma entrada em `_STATE_REGISTRY` — sem tocar nos estados existentes.
- **LSP:** qualquer `DownloadState` concreto pode ocupar `DownloadJob._state` — todos respeitam o mesmo contrato (transições não suportadas levantam `InvalidTransitionError` por padrão).
- **ISP:** `DownloadState` expõe só as seis transições que o domínio precisa; cada estado concreto sobrescreve apenas as que permite.
- **DIP:** `CompleteDownloadUseCase` depende de `S3ClientLike` (Protocol), nunca do cliente boto3 concreto — injeção via construtor em `main.py`.
