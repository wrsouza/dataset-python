# Session Token Cache — Flyweight Pattern

> **Design Pattern:** Flyweight | **Categoria:** Structural
> **Framework:** FastAPI | **Serviços:** Redis

## Objetivo Pedagógico

Demonstrar o padrão Flyweight em um cenário real de cache de sessões: em vez de
duplicar dados de permissão (role, permissions, mfa, etc.) em cada uma das milhares
de sessões ativas, o app compartilha um único objeto `SessionMetadata` por role —
admin, editor, viewer, moderator, analyst — entre todas as sessões daquele role.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Flyweight (estado intrínseco, imutável) | `SessionMetadata` | `src/session_cache/domain/entities.py` |
| FlyweightFactory | `RedisSessionMetadataFactory` | `src/session_cache/infrastructure/factory.py` |
| Context (estado extrínseco + referência ao Flyweight) | `UserSession` | `src/session_cache/domain/entities.py` |
| Client | `LoginUseCase`, `GetSessionUseCase` | `src/session_cache/application/use_cases.py` |

`SessionMetadata` é um `@dataclass(frozen=True)` — role, permissions, app_version,
max_session_duration, allowed_ip_ranges, requires_mfa. Esse objeto é o mesmo
(mesma referência Python, `id()` igual) para todas as sessões do mesmo role.
`UserSession` guarda apenas o que varia por usuário: user_id, token, timestamps.

## Diagrama UML (ASCII)

```
<<frozen dataclass>>
SessionMetadata (Flyweight)
  role, permissions, app_version, max_session_duration
        ▲
        │ shared reference (same object for same role)
        │
UserSession (Context)
  user_id, token, created_at, expires_at ──► metadata: SessionMetadata

RedisSessionMetadataFactory (FlyweightFactory)
  get_or_create(role) -> SessionMetadata
  ├── Level 1: in-process dict (same object across calls in this process)
  └── Level 2: Redis hash (shared across worker processes)
```

## Cache em Dois Níveis

1. **Nível 1 (in-process):** dict local na factory — garante `is` (mesma referência
   de objeto Python) entre chamadas no mesmo processo.
2. **Nível 2 (Redis):** persistência compartilhada entre workers — quando um novo
   processo reconstrói o Flyweight a partir do Redis, o objeto é **igual** (`==`)
   mas não é a **mesma instância** (`is`), porque cada processo desserializa seu
   próprio objeto Python a partir do JSON armazenado.

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** `RedisSessionMetadataFactory` só gerencia o pool
  de Flyweights; `RedisSessionRepository` só persiste o estado extrínseco da sessão.
- **D — Dependency Inversion:** os use cases (`LoginUseCase`, `GetSessionUseCase`)
  dependem de `SessionMetadataFactoryABC` e `SessionRepositoryProtocol`
  (abstrações em `domain/interfaces.py`), nunca de `redis.Redis` diretamente.

## Por que os providers usam `@lru_cache`

As dependências FastAPI (`get_redis`, `get_factory`, `get_repository`) são
decoradas com `@lru_cache` para garantir **uma única instância por processo**.
Sem isso, cada request criaria uma nova `RedisSessionMetadataFactory` com cache
em memória vazio, e o ganho de memória do Flyweight só seria visível dentro de
uma única chamada — não entre requests, que é o cenário real de produção.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000/docs`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/login` | Cria sessão; reutiliza o Flyweight do role |
| GET | `/auth/session/{token}` | Recupera sessão existente |
| GET | `/cache/stats` | Estatísticas de economia de memória do Flyweight |
| POST | `/demo/bulk-login` | Cria N sessões distribuídas entre roles (demo de escala) |

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente (com Python 3.11+ e dependências instaladas):

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes unitários usam `fakeredis` (sem necessidade de Redis real); os testes
de integração usam o `TestClient` do FastAPI com `dependency_overrides` para
substituir o cliente Redis real por um fake, mantendo a app totalmente testável
sem infraestrutura externa.
