# Report Generation Template (Template Method) — P2

API Flask que gera relatórios em diferentes formatos (CSV, JSON,
HTML) a partir do mesmo esqueleto de algoritmo, sem nenhum serviço
externo — os relatórios ficam em memória, no processo da aplicação.

## Objetivo pedagógico

Demonstrar o pattern **Template Method**: `ReportGenerator` (AbstractClass)
define o algoritmo fixo em `generate()` — cabeçalho, linhas, resumo,
montagem final — e cada formato concreto só sobrescreve os passos que
variam (`format_header`, `format_row`). O hook `include_summary()`
deixa `JSONReportGenerator` pular a linha de resumo sem alterar o
algoritmo principal, e `HTMLReportGenerator` sobrescreve `assemble()`
para montar uma tabela em vez de juntar linhas com `\n`.

Elementos do pattern:
- **AbstractClass:** `ReportGenerator` (`domain/interfaces.py`)
- **Template Method:** `ReportGenerator.generate()`
- **ConcreteClasses:** `CSVReportGenerator`, `JSONReportGenerator`, `HTMLReportGenerator` (`application/generators/`)
- **Hook:** `include_summary()`

## Diagrama (ASCII)

```
ReportGenerator.generate(title, rows)
        │
        ├─► format_header(title)         (abstrato)
        ├─► format_row(row) × N           (abstrato)
        ├─► include_summary()? ──► format_summary(n)  (hook + concreto)
        └─► assemble(header, rows, summary)            (concreto, sobrescrevível)
```

## Como rodar

```bash
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota                    | Descrição                                  |
|--------|--------------------------|-----------------------------------------------|
| POST   | `/reports`               | Gera um relatório (`format`, `title`, `rows`)  |
| GET    | `/reports/<report_id>`   | Consulta um relatório já gerado                |
| GET    | `/reports/formats`       | Lista os formatos disponíveis                  |
| GET    | `/health`                | Healthcheck                                     |

```bash
curl -X POST http://localhost:5000/reports \
  -H "Content-Type: application/json" \
  -d '{"format": "csv", "title": "Users", "rows": [{"id": 1, "name": "Ana"}]}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada gerador concreto só sabe formatar seu próprio tipo de saída; `InMemoryReportRepository` só armazena/recupera relatórios.
- **OCP:** um novo formato (ex.: Markdown) é uma nova classe `ReportGenerator` mais uma entrada em `_GENERATOR_MAP` — sem tocar no algoritmo de `generate()` nem nos formatos existentes.
- **LSP:** qualquer `ReportGenerator` concreto pode substituir outro nos use cases sem quebrar o contrato — todos retornam `ReportResult`.
- **ISP:** `ReportGenerator` expõe só os métodos abstratos que cada formato realmente precisa sobrescrever.
- **DIP:** os use cases dependem de `ReportGenerator`/`InMemoryReportRepository` (abstrações), nunca das classes concretas diretamente — injeção via construtor em `create_app`.
