# Data Transformation Visitor (Visitor) — P5

App Streamlit que aplica diferentes transformações (normalização,
anonimização, resumo estatístico) sobre um pequeno dataset com colunas
de tipos distintos (numérica, texto, data) — sem nenhum serviço
externo. **Último projeto do dataset** (110/110).

## Objetivo pedagógico

Demonstrar o pattern **Visitor**: `DataColumn` (Element) expõe só
`accept(visitor)` — `NumericColumn`/`TextColumn`/`DateColumn` nunca
sabem qual transformação está sendo aplicada. Adicionar uma nova
transformação (ex.: "detecção de outliers") é só uma nova classe
`ColumnVisitor`, sem tocar nas colunas existentes.

Elementos do pattern:
- **Visitor (abstrato):** `ColumnVisitor` (`domain/interfaces.py`)
- **Element (abstrato):** `DataColumn`
- **Concrete Elements:** `NumericColumn`, `TextColumn`, `DateColumn`
- **Concrete Visitors:** `NormalizationVisitor`, `AnonymizationVisitor`, `SummaryVisitor` (`infrastructure/visitors/`)

## Diagrama (ASCII)

```
traverse(columns, visitor)
        │
        └─► for column in columns: column.accept(visitor)
                    │
                    ▼
        NumericColumn.accept() ──► visitor.visit_numeric(self)
        TextColumn.accept()    ──► visitor.visit_text(self)
        DateColumn.accept()    ──► visitor.visit_date(self)
                    │
                    ▼
              visitor.result (um valor transformado por coluna)
```

## Como rodar

```bash
docker-compose up --build
```

App disponível em `http://localhost:8501`.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`app.py` é excluído do cálculo de cobertura (mesmo padrão dos demais
projetos Streamlit do dataset).

## SOLID

- **SRP:** cada visitor concreto só sabe transformar seu próprio tipo de coluna; `DataColumn` só conhece sua própria estrutura.
- **OCP:** uma nova transformação é uma nova classe `ColumnVisitor` mais uma entrada em `_VISITOR_FACTORIES` — sem tocar nas colunas existentes.
- **LSP:** qualquer `ColumnVisitor` concreto pode ser usado em `traverse()` sem quebrar o contrato — todos implementam os três `visit_X`.
- **ISP:** `ColumnVisitor` expõe só os três métodos que as colunas realmente chamam; `DataColumn` expõe só `accept()`.
- **DIP:** `TransformDatasetUseCase` depende de `ColumnVisitor` (abstração) via o registro, nunca de uma classe concreta diretamente.
