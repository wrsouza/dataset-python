# Data Processing Pipeline (Template Method) — P4

CLI Typer que processa objetos do S3 (CSV ou JSON Lines) através do
mesmo esqueleto fetch→parse→clean→persist, salvando os registros
limpos em MySQL.

## Objetivo pedagógico

Demonstrar o pattern **Template Method**: `DataProcessingPipeline`
(AbstractClass) define o algoritmo fixo em `process()` — buscar no S3,
parsear, limpar, persistir — e cada formato concreto só sobrescreve
`fetch_input`/`parse`/`clean`, lendo seu próprio objeto do S3. O hook
`on_empty_input()` deixa o pipeline decidir se persiste zero registros
ou aborta quando o objeto vem vazio.

Elementos do pattern:
- **AbstractClass:** `DataProcessingPipeline` (`domain/interfaces.py`)
- **Template Method:** `DataProcessingPipeline.process()`
- **ConcreteClasses:** `CSVDataProcessingPipeline`, `JSONDataProcessingPipeline` (`application/pipelines/`)
- **Hook:** `on_empty_input()`

## Diagrama (ASCII)

```
DataProcessingPipeline.process()
        │
        ├─► fetch_input()                  (abstrato — lê o objeto certo do S3)
        ├─► parse(raw)                       (abstrato — CSV ou JSON Lines)
        ├─► [vazio?] on_empty_input()? ──► EmptyInputAbortedError (hook)
        ├─► clean(records)                   (abstrato — regras de limpeza)
        └─► persist(records)                 (concreto — MySQL/sqlite)
```

## Como rodar

```bash
cp .env.example .env
docker-compose run --rm app python -m data_processing_pipeline.main process-csv my-bucket data.csv
docker-compose run --rm app python -m data_processing_pipeline.main process-json my-bucket data.jsonl
```

### Comandos

| Comando         | Descrição                                          |
|------------------|---------------------------------------------------|
| `process-csv`    | Processa um objeto CSV do S3 e persiste em MySQL    |
| `process-json`   | Processa um objeto JSON Lines do S3 e persiste em MySQL |

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os pipelines são testados com fakes em memória (`FakeS3Client`,
`FakeRepository`) nos testes unitários, e com `moto[s3]` + SQLite
(stand-in de MySQL) na CLI de integração.

## SOLID

- **SRP:** cada pipeline concreto só sabe ler/parsear/limpar seu próprio formato; `ProcessedRecordRepository` só persiste registros já limpos.
- **OCP:** um novo formato (ex.: Parquet) é uma nova classe `DataProcessingPipeline` — sem tocar no algoritmo de `process()` nem nos pipelines existentes.
- **LSP:** qualquer `DataProcessingPipeline` concreto pode ser executado via `process()` sem quebrar o contrato — todos retornam `ProcessingResult`.
- **ISP:** `DataProcessingPipeline` expõe só os três métodos abstratos que cada pipeline realmente precisa sobrescrever; `ProcessedRecordRepositoryLike`/`S3ClientLike` são Protocols mínimos.
- **DIP:** os pipelines dependem de `S3ClientLike`/`ProcessedRecordRepositoryLike` (abstrações), nunca do boto3/pymysql concretos diretamente — injeção via construtor em `main.py`.
