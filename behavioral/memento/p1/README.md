# P1 — Document Version History

**Pattern:** Memento | **Framework:** FastAPI + PostgreSQL

## UML — Memento Pattern

```
┌─────────────────────┐         ┌──────────────────────────┐
│   Document          │creates  │   DocumentMemento        │
│   (Originator)      │────────>│   @dataclass(frozen=True)│
│─────────────────────│         │──────────────────────────│
│ + content: str      │         │ + content: str           │
│ + metadata: dict    │         │ + metadata: dict         │
│ + current_version   │         │ + version: int           │
│─────────────────────│         │ + author: str            │
│ + create_snapshot() │         │ + created_at: datetime   │
│ + restore(memento)  │         └──────────────────────────┘
│ + apply_edit(...)   │                    ▲
└─────────────────────┘                    │ stores/retrieves
                                           │
                          ┌────────────────────────────────┐
                          │   PostgresVersionHistory       │
                          │   (Caretaker)                  │
                          │────────────────────────────────│
                          │ + save(doc_id, memento)        │
                          │ + get(doc_id, version)         │
                          │ + undo(doc_id)                 │
                          │ + list_versions(doc_id)        │
                          └────────────────────────────────┘
```

## SOLID Mapping

| Principle | Where |
|-----------|-------|
| **SRP** | `Document` only manages state; `PostgresVersionHistory` only manages persistence; `DocumentRepository` only handles CRUD |
| **OCP** | `DocumentCaretaker` ABC — add a new backend (S3, Redis) without modifying existing code |
| **DIP** | Use cases depend on `DocumentCaretaker` ABC and `DocumentRepository` protocol, not on concrete classes |

## Database Schema

```sql
document         -- current state of each document
document_version -- all historical snapshots (mementos)
```

## Quick Start

```bash
cp .env.example .env
docker compose up -d
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## API Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/documents` | Create document + initial snapshot |
| PUT | `/documents/{id}` | Edit document (saves snapshot before edit) |
| POST | `/documents/{id}/restore/{version}` | Restore to specific version |
| POST | `/documents/{id}/undo` | Revert to previous snapshot |
| GET | `/documents/{id}/history` | List all snapshots |

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/unit/          # no DB needed
DATABASE_URL=... pytest tests/integration/
```
