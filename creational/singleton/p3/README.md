# Feature Flag Manager — Singleton Pattern

> **Design Pattern:** Singleton
> **Categoria:** Creational
> **Framework:** Django
> **Dominio:** feature_flags

## Objetivo Pedagogico

Demonstra o padrao Singleton aplicado a um gerenciador de feature flags.
O aluno aprende: como a metaclass SingletonMeta garante uma unica instancia
compartilhada por todos os workers Django, como implementar thread-safety com
RLock para proteger leituras e escritas concorrentes, e como os tres tipos de
flag (boolean, percentage rollout, allowlist) funcionam internamente.

## O Pattern em Acao

| Papel do Pattern           | Classe               | Arquivo                                        |
|----------------------------|----------------------|------------------------------------------------|
| Singleton (metaclasse)     | `SingletonMeta`      | `infrastructure/singleton.py`                  |
| Instancia unica            | `FeatureFlagManager` | `infrastructure/singleton.py`                  |
| Loader JSON                | `JsonFlagLoader`     | `infrastructure/loaders.py`                    |
| Abstracoes do dominio      | `FlagLoader`         | `domain/interfaces.py`                         |
| Entidades imutaveis        | `FlagConfig`         | `domain/entities.py`                           |
| Middleware Django           | `FeatureFlagMiddleware` | `middleware/feature_flag_middleware.py`      |
| Decorator de views         | `@feature_required`  | `middleware/decorators.py`                     |
| Use cases                  | `CheckFlagUseCase`   | `application/use_cases.py`                     |

## Diagrama UML (ASCII)

```
SingletonMeta (metaclass)
+ _instances: dict[type, Any]        <-- registro global
+ _lock: threading.Lock              <-- double-checked locking
+ __call__(): Any
        |
        v instancia exatamente uma vez
FeatureFlagManager
- _loader: FlagLoader                <-- injetado (DIP)
- _flags: dict[str, FlagConfig]      <-- cache em memoria
- _overrides: dict[str, bool]        <-- para testes
- _rlock: threading.RLock            <-- thread-safe reads/writes
+ is_enabled(flag, user_id) -> bool
+ get_all_flags()   -> dict
+ reload()          -> None
+ set_override(flag, value) -> None
+ get_stats()       -> RegistryStats

        ^               ^
        | depends on    | depends on
        |               |
FlagLoader (Protocol)   FlagConfig (frozen dataclass)
- load() -> dict        - name, enabled, rollout_%, allowlist, type
        ^
        | implements
JsonFlagLoader          EnvFlagLoader
(reads flags.json)      (reads FEATURE_* env vars)

Django middleware: FeatureFlagMiddleware
  -> request.flags = FeatureFlagManager()   # mesmo objeto toda requisicao

Decorator: @feature_required("flag_name")
  -> avalia o flag antes de chamar a view; retorna 403 se desabilitado
```

## Flag Types

| Tipo         | Comportamento                                            |
|--------------|----------------------------------------------------------|
| `boolean`    | Liga/desliga globalmente                                  |
| `percentage` | Hash deterministica do user_id em bucket 0-99            |
| `allowlist`  | Apenas user_ids listados recebem o feature               |

### Exemplo de flags.json

```json
{
  "dark_mode":     {"enabled": true},
  "new_checkout":  {"enabled": true,  "rollout_percentage": 50},
  "beta_search":   {"enabled": true,  "allowlist": ["user_1", "admin"]},
  "old_feature":   {"enabled": false}
}
```

## Thread-Safety: Double-Checked Locking

```python
def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:          # fast path (sem lock)
        with cls._lock:                    # slow path: adquire lock
            if cls not in cls._instances:  # re-verifica dentro do lock
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
    return cls._instances[cls]
```

Leituras e escritas de flags usam `threading.RLock` (reentrant) para
permitir que `reload()` chame `_load_flags()` no mesmo thread sem deadlock.

## Principios SOLID Demonstrados

- **S — SRP:** `FeatureFlagManager` gerencia flags; `JsonFlagLoader` le JSON;
  `FeatureFlagMiddleware` injeta na request; use cases orquestram logica.
- **O — OCP:** Novos tipos de flag adicionam um novo valor em `FlagType` e
  um metodo privado — nenhum codigo existente muda.

## Endpoints da API

| Metodo | URL                         | Descricao                              |
|--------|-----------------------------|----------------------------------------|
| GET    | `/flags/`                   | Lista todos os flags e stats           |
| POST   | `/flags/reload`             | Recarrega flags.json                   |
| GET    | `/flags/<name>/check`       | Avalia flag (query: `user_id=`)        |
| GET    | `/flags/experimental-dashboard/` | Gateado por `@feature_required` |

## Estrutura do Projeto

```
p3/
├── src/
│   ├── manage.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── flags.json                        <- configuracao dos flags
│   └── feature_flags/
│       ├── domain/
│       │   ├── entities.py              <- FlagConfig, FlagEvaluationResult
│       │   └── interfaces.py            <- FlagLoader Protocol, FlagLoadError
│       ├── application/
│       │   └── use_cases.py            <- CheckFlagUseCase, ReloadFlagsUseCase
│       ├── infrastructure/
│       │   ├── singleton.py            <- SingletonMeta + FeatureFlagManager
│       │   └── loaders.py             <- JsonFlagLoader, EnvFlagLoader
│       ├── middleware/
│       │   ├── feature_flag_middleware.py
│       │   └── decorators.py          <- @feature_required
│       └── views/
│           └── api.py                 <- list_flags, check_flag, reload_flags
├── tests/
│   ├── conftest.py
│   ├── unit/test_singleton.py         <- identidade + thread-safety + avaliacao
│   └── integration/test_api.py       <- endpoints Django test client
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API disponivel em http://localhost:8000/flags/
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/ -v
```

## Pre-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Variaveis de Ambiente

| Variavel            | Descricao                    | Padrao               |
|---------------------|------------------------------|----------------------|
| `DJANGO_SECRET_KEY` | Chave secreta Django         | dev-only (mude!)     |
| `DJANGO_DEBUG`      | Modo debug                   | `true`               |
| `FLAGS_JSON_PATH`   | Caminho para flags.json      | `./src/flags.json`   |
