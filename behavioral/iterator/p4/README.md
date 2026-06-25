# File Tree Iterator (Iterator) — P4

CLI Typer que percorre uma árvore de diretórios em profundidade (`tree`) ou
agrega contagens e tamanho total (`summary`), através de um Iterator GoF
genuíno que nunca carrega a árvore inteira em memória de uma vez.

## Objetivo pedagógico

Demonstrar o pattern **Iterator** sobre uma estrutura recursiva (árvore de
diretórios): o cliente percorre a árvore inteira chamando apenas
`has_next()`/`next()`, sem nunca saber que, por baixo, o
`DepthFirstFileIterator` mantém uma pilha explícita — em vez de recursão —
e só lista o conteúdo de um diretório quando de fato desce até ele.

Elementos do pattern:
- **Iterator (abstrato):** `FileTreeIterator` (`domain/interfaces.py`)
- **Concrete Iterator:** `DepthFirstFileIterator` — pilha explícita, expande um diretório só quando alcançado
- **Aggregate:** `FileSystemSource` / `OsFileSystemSource` — lista os filhos diretos de um único diretório, sem saber nada sobre a travessia
- **Client:** `SummarizeTreeUseCase`, que consome o iterator com um laço `while has_next(): next()` para agregar contagens e tamanho

## Diagrama (ASCII)

```
CLI: summary /data
      │
      ▼
SummarizeTreeUseCase ──cria──► DepthFirstFileIterator(source, "/data")
      │                                  │
      │  while iterator.has_next():      │
      │      entry = iterator.next()     │
      │      conta arquivo/dir, soma size│
      │                                  ▼
      │                    é diretório? ──sim──► source.list_children(entry.path) ──► os.scandir
      ▼
Files: N | Directories: M | Total size: X bytes
```

## Como rodar

```bash
docker-compose run --rm app python -m file_tree_iterator.main tree /app
docker-compose run --rm app python -m file_tree_iterator.main summary /app
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes unitários usam um `FakeFileSystemSource` em memória (sem tocar
o disco); os de integração usam `tmp_path` do pytest para criar uma árvore
real e validar `OsFileSystemSource` e a CLI ponta a ponta.

## SOLID

- **SRP:** `DepthFirstFileIterator` só sabe percorrer; `OsFileSystemSource` só sabe listar um diretório; nenhum dos dois conhece o outro além do contrato `FileSystemSource`.
- **OCP:** trocar a estratégia de travessia (ex.: breadth-first) = criar um novo `FileTreeIterator`, sem tocar em `FileSystemSource` nem nos use cases.
- **LSP:** qualquer `FileTreeIterator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `has_next`/`next`.
- **ISP:** `FileTreeIterator` e `FileSystemSource` são interfaces pequenas e focadas.
- **DIP:** `WalkTreeUseCase` e `SummarizeTreeUseCase` dependem de `FileSystemSource` (abstração); a CLI (`main.py`) é o único lugar que conhece `OsFileSystemSource`.
