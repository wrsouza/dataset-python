# Text Editor Undo/Redo (Memento) — P4

CLI Typer que implementa um editor de texto minimalista com `undo`/`redo`
completos, persistindo o histórico de snapshots em SQLite (cada comando
roda em um processo novo).

## Objetivo pedagógico

Demonstrar o pattern **Memento** num cenário de undo/redo clássico:
`TextDocument` (Originator) sabe criar e restaurar seu próprio conteúdo
a partir de um `TextSnapshot` imutável, mas não sabe como nem onde esses
snapshots são guardados. `SqliteEditorCaretaker` (Caretaker) mantém o log
de snapshots e um ponteiro de posição — `write` depois de um `undo`
descarta o ramo de redo, igual a qualquer editor de texto real.

Elementos do pattern:
- **Originator:** `TextDocument` (`domain/entities.py`)
- **Memento:** `TextSnapshot`, `@dataclass(frozen=True)` — imutável após criado
- **Caretaker:** `SqliteEditorCaretaker` (`infrastructure/sqlite_caretaker.py`)

## Diagrama (ASCII)

```
write("a") ──► snapshot v1 ──► pointer=1
write("b") ──► snapshot v2 ──► pointer=2
undo()     ──► pointer=1 (snapshot v1, "a")
redo()     ──► pointer=2 (snapshot v2, "b")
write("c") após undo ──► descarta v2, cria v2'="c", pointer=2'
```

## Como rodar

```bash
cp .env.example .env
docker-compose run --rm app python -m text_editor_memento.main write "Hello, world"
docker-compose run --rm app python -m text_editor_memento.main show
docker-compose run --rm app python -m text_editor_memento.main undo
docker-compose run --rm app python -m text_editor_memento.main redo
docker-compose run --rm app python -m text_editor_memento.main history
```

### Comandos

| Comando   | Descrição                                          |
|-----------|------------------------------------------------------|
| `write`   | Substitui o conteúdo do documento e cria um snapshot |
| `undo`    | Volta para o snapshot anterior                       |
| `redo`    | Reaplica o snapshot desfeito mais recentemente        |
| `show`    | Mostra o conteúdo atual do documento                 |
| `history` | Lista todos os snapshots já registrados              |

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** `TextDocument` só manipula seu próprio conteúdo em memória; `SqliteEditorCaretaker` só persiste snapshots e o ponteiro de posição, sem interpretar o conteúdo.
- **OCP:** um novo backend de histórico (ex.: arquivo JSON, Redis) implementa `EditorCaretaker` sem alterar `TextDocument` nem os use cases.
- **LSP:** qualquer implementação de `EditorCaretaker` pode substituir `SqliteEditorCaretaker` nos use cases sem quebrar o contrato.
- **ISP:** `EditorCaretaker` expõe só os cinco métodos que o Originator/use cases realmente precisam (`write`, `undo`, `redo`, `current`, `history`).
- **DIP:** os use cases dependem de `EditorCaretaker` (abstração), nunca de `SqliteEditorCaretaker` diretamente — injeção via construtor em `main.py`.
