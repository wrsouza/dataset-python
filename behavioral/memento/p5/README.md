# Analysis Session Snapshots (Memento) — P5

App Streamlit que executa uma análise parametrizável e versiona cada
execução como um snapshot imutável em MongoDB, permitindo desfazer
(`undo`) e revisar o histórico completo de execuções da sessão.

## Objetivo pedagógico

Demonstrar o pattern **Memento**: `AnalysisSession` (Originator) sabe
criar e restaurar seu próprio estado (parâmetros + resultados) a partir
de um `AnalysisSnapshot` imutável, mas não sabe onde nem como esses
snapshots são guardados. `MongoAnalysisCaretaker` (Caretaker) persiste
cada snapshot como um documento na coleção `snapshots`, sem nunca
interpretar o que os campos `parameters`/`results` significam — o
formato livre de documentos do MongoDB é uma boa combinação com esse
requisito.

Elementos do pattern:
- **Originator:** `AnalysisSession` (`domain/entities.py`)
- **Memento:** `AnalysisSnapshot`, `@dataclass(frozen=True)` — imutável após criado
- **Caretaker:** `MongoAnalysisCaretaker` (`infrastructure/caretaker.py`)

## Diagrama (ASCII)

```
Streamlit "Executar análise"
  │
  ▼
SaveAnalysisUseCase ──create_snapshot()──► AnalysisSnapshot (imutável)
  │                                              │
  ▼                                              ▼
AnalysisSession (Originator)        MongoAnalysisCaretaker.save()
                                     (coleção snapshots, por versão)

Streamlit "Desfazer" ──UndoAnalysisUseCase──► Caretaker descarta o
                                                último snapshot e
                                                retorna o anterior
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

App disponível em `http://localhost:8501`.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`app.py` é excluído do cálculo de cobertura (mesmo padrão dos demais
projetos Streamlit do dataset, já que `streamlit run` não é exercitado
por `pytest`); a lógica pura (`run_analysis`) e o fluxo completo via
`mongomock` são cobertos em `tests/integration/test_workflow.py`.

## SOLID

- **SRP:** `AnalysisSession` só manipula seu próprio estado em memória; `MongoAnalysisCaretaker` só persiste/recupera snapshots, sem conhecer a semântica de `parameters`/`results`.
- **OCP:** um novo backend de armazenamento (ex.: PostgreSQL, S3) implementa `AnalysisCaretaker` sem alterar `AnalysisSession` nem os use cases.
- **LSP:** qualquer implementação de `AnalysisCaretaker` pode substituir `MongoAnalysisCaretaker` nos use cases sem quebrar o contrato.
- **ISP:** `AnalysisCaretaker` expõe só os quatro métodos que o Originator/use cases realmente precisam (`save`, `undo`, `latest`, `history`).
- **DIP:** os use cases dependem de `AnalysisCaretaker` (abstração), nunca de `MongoAnalysisCaretaker` diretamente — injeção via construtor em `app.py`.
