# Form State Save/Restore (Memento) — P2

Flask API que autosaiva o estado de um formulário multi-etapas a cada
chamada e permite desfazer (`undo`) ou consultar o histórico completo,
usando Redis como backend de snapshots.

## Objetivo pedagógico

Demonstrar o pattern **Memento**: `FormSession` (Originator) sabe criar e
restaurar seu próprio estado a partir de um `FormSnapshot` imutável, mas
não sabe onde nem como esses snapshots são guardados. `RedisFormCaretaker`
(Caretaker) cuida do armazenamento (lista Redis por sessão) sem nunca
inspecionar o conteúdo dos campos do formulário.

Elementos do pattern:
- **Originator:** `FormSession` (`domain/entities.py`)
- **Memento:** `FormSnapshot`, `@dataclass(frozen=True)` — imutável após criado
- **Caretaker:** `RedisFormCaretaker` (`infrastructure/caretaker.py`)

## Diagrama (ASCII)

```
Client
  │
  ▼
SaveFormStateUseCase ──create_snapshot()──► FormSnapshot (imutável)
  │                                              │
  ▼                                              ▼
FormSession (Originator)              RedisFormCaretaker.save()
                                       (Redis list: form:history:<id>)

UndoFormStateUseCase ──undo()──► RedisFormCaretaker descarta o último
                                  snapshot e retorna o anterior
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
| POST   | `/forms/<session_id>`          | Salva (autosave/manual) o estado do form    |
| GET    | `/forms/<session_id>`          | Consulta o estado atual (último snapshot)   |
| POST   | `/forms/<session_id>/undo`     | Desfaz, voltando ao snapshot anterior       |
| GET    | `/forms/<session_id>/history`  | Lista todos os snapshots da sessão          |
| GET    | `/health`                      | Healthcheck                                  |

```bash
curl -X POST http://localhost:5000/forms/session-1 \
  -H "Content-Type: application/json" \
  -d '{"fields": {"name": "Ana"}, "step": 1, "label": "manual"}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** `FormSession` só manipula seu próprio estado em memória; `RedisFormCaretaker` só persiste/recupera snapshots, sem conhecer a semântica dos campos.
- **OCP:** um novo backend de armazenamento (ex.: PostgreSQL, S3) implementa `FormCaretaker` sem alterar `FormSession` nem os use cases.
- **LSP:** qualquer implementação de `FormCaretaker` pode substituir `RedisFormCaretaker` nos use cases sem quebrar o contrato.
- **ISP:** `FormCaretaker` expõe só os quatro métodos que o Originator/use cases realmente precisam (`save`, `undo`, `latest`, `history`).
- **DIP:** os use cases dependem de `FormCaretaker` (abstração), nunca de `RedisFormCaretaker` diretamente — injeção via construtor em `create_app`.
