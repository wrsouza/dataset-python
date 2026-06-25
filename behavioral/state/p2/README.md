# User Auth Session FSM (State) — P2

API Flask que modela o ciclo de vida de uma sessão de autenticação como
uma máquina de estados explícita (`Anonymous` → `Active` → `Expired`/`Locked`),
persistida em Redis.

## Objetivo pedagógico

Demonstrar o pattern **State**: `AuthSession` (Context) delega todo o
comportamento (`login`, `logout`, `refresh`, `expire`, `unlock`) ao
objeto de estado atual, sem nenhum `if/elif` checando o estado.
Transições inválidas (ex.: `unlock` numa sessão `Active`) levantam
`InvalidTransitionError` automaticamente — o estado base já implementa
isso, cada estado concreto só sobrescreve as transições que permite.

Elementos do pattern:
- **Context:** `AuthSession` (`domain/entities.py`)
- **State (abstrato):** `SessionState` (`domain/interfaces.py`)
- **Concrete States:** `AnonymousState`, `ActiveState`, `LockedState`, `ExpiredState` (`infrastructure/states/`)

## Diagrama (ASCII)

```
                 login(success=False) x3
        ┌────────────────────────────────────┐
        │                                     ▼
   Anonymous ──login(success=True)──► Active ──expire──► Expired
        ▲                               │  ▲                │
        │            logout, refresh ───┘  └────login(success=True)
        └──────────────unlock────────── Locked
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota                          | Descrição                                  |
|--------|--------------------------------|---------------------------------------------|
| POST   | `/sessions/<id>/login`         | Tenta login (`{"success": true/false}`)     |
| POST   | `/sessions/<id>/logout`        | Encerra uma sessão ativa                    |
| POST   | `/sessions/<id>/refresh`       | Renova uma sessão ativa                     |
| POST   | `/sessions/<id>/expire`        | Expira uma sessão ativa                     |
| POST   | `/sessions/<id>/unlock`        | Desbloqueia uma sessão travada              |
| GET    | `/sessions/<id>`               | Consulta o estado atual da sessão           |
| GET    | `/health`                      | Healthcheck                                  |

```bash
curl -X POST http://localhost:5000/sessions/s1/login \
  -H "Content-Type: application/json" \
  -d '{"success": true}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada estado concreto só sabe lidar com suas próprias transições; `RedisSessionRepository` só persiste/recupera o nome do estado e o contador de falhas.
- **OCP:** um novo estado (ex.: `Suspended`) é uma nova classe `SessionState` mais uma entrada em `_STATE_REGISTRY` — sem tocar nos estados existentes.
- **LSP:** qualquer `SessionState` concreto pode ocupar `AuthSession._state` — todos respeitam o mesmo contrato (métodos não suportados levantam `InvalidTransitionError` por padrão, herdado do estado base).
- **ISP:** `SessionState` expõe só as cinco transições que o domínio precisa; cada estado concreto sobrescreve apenas as que permite.
- **DIP:** os use cases dependem de `RedisSessionRepository` via injeção de construtor — `create_app` decide a implementação concreta.
