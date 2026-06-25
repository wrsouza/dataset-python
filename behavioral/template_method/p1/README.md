# Data Import Pipeline

> **Design Pattern:** Template Method
> **Categoria:** Behavioral
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Template Method em um pipeline de importação de
dados multi-formato (CSV, JSON, XML). O algoritmo de importação — ler, parsear,
validar, transformar, persistir e gerar relatório — é fixo e definido uma única
vez na classe abstrata. Cada formato implementa apenas os passos que variam
(`read_raw`, `parse`, `validate`, `transform`), sem nunca tocar na ordem de
execução ou na lógica de persistência/relatório compartilhada.

## O Pattern em Ação

`DataImporter` (AbstractClass) define o método template `import_data()`, que
fixa a sequência: `read_raw -> parse -> validate -> transform -> persist ->
generate_report`. As subclasses `CSVImporter`, `JSONImporter` e `XMLImporter`
(ConcreteClasses) implementam os passos abstratos sem alterar essa sequência.
O hook `on_validation_error()` permite que cada formato decida se continua a
importação com os registros válidos (`CSVImporter`, `XMLImporter`) ou aborta
no primeiro erro de validação (`JSONImporter`, comportamento padrão herdado).

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| AbstractClass | `DataImporter` | `src/data_import/domain/interfaces.py` |
| Template Method | `DataImporter.import_data()` | `src/data_import/domain/interfaces.py` |
| Passos abstratos | `read_raw`, `parse`, `validate`, `transform` | `src/data_import/domain/interfaces.py` |
| Passos concretos (compartilhados) | `persist`, `generate_report` | `src/data_import/domain/interfaces.py` |
| Hook | `on_validation_error` | `src/data_import/domain/interfaces.py` |
| ConcreteClass | `CSVImporter` | `src/data_import/application/pipelines/csv_importer.py` |
| ConcreteClass | `JSONImporter` | `src/data_import/application/pipelines/json_importer.py` |
| ConcreteClass | `XMLImporter` | `src/data_import/application/pipelines/xml_importer.py` |

## Diagrama UML

```
<<abstract>>
DataImporter
+ import_data(source_path: str): ImportResult     [TEMPLATE METHOD — sequência fixa]
----------------------------------------------------------------------------------
# read_raw(path: str): bytes                       [abstract]
# parse(raw: bytes): list[dict]                     [abstract]
# validate(records: list[dict]): ValidationResult   [abstract]
# transform(records: list[dict]): list[dict]        [abstract]
----------------------------------------------------------------------------------
# persist(records: list[dict]): int                 [concrete — PostgreSQL, compartilhado]
# generate_report(...): ImportReport                 [concrete — compartilhado]
# on_validation_error(errors): bool                  [hook — default: False, aborta]
        |
        ├── CSVImporter
        │     # read_raw / parse / validate / transform   (csv.DictReader)
        │     # on_validation_error -> True (tolera falhas parciais)
        │
        ├── JSONImporter
        │     # read_raw / parse / validate / transform   (json.loads)
        │     # mantém hook padrão -> False (aborta em erro)
        │
        └── XMLImporter
              # read_raw / parse / validate / transform   (ElementTree)
              # on_validation_error -> True (tolera falhas parciais)
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** adicionar um novo formato (ex.: `ParquetImporter`) exige
  apenas criar uma nova subclasse de `DataImporter` em
  `src/data_import/application/pipelines/`, implementando os 4 passos
  abstratos. A classe `DataImporter` e o método `import_data()` (a sequência
  do algoritmo) **nunca são modificados** — fechados para modificação, abertos
  para extensão via herança.
- **D — Dependency Inversion:** `import_data()` depende apenas dos passos
  abstratos declarados na própria classe (`self.read_raw`, `self.parse`,
  etc.), não de implementações concretas. `_run_import()` em `src/main.py`
  recebe a instância de `DataImporter` já construída — a composição concreta
  (`CSVImporter()`, `JSONImporter()`, `XMLImporter()`) acontece apenas nas
  rotas, que funcionam como composição root.
- **L — Liskov Substitution:** qualquer subclasse de `DataImporter` pode
  substituir a base em `import_data()` sem alterar o contrato — todas
  retornam `ValidationResult`/`list[dict]` nos mesmos formatos esperados pelo
  template method.
- **S — Single Responsibility:** `JobStore` (rastreamento de status) e
  `PostgresImportRepository` (persistência) são classes separadas, cada uma
  com um único motivo para mudar.

## Estrutura do Projeto

```
template_method/p1/
├── src/
│   ├── main.py                        ← FastAPI app (composição root)
│   └── data_import/
│       ├── domain/
│       │   ├── interfaces.py          ← DataImporter (AbstractClass + template method)
│       │   └── entities.py            ← ImportResult, ImportReport, ValidationResult, erros
│       ├── application/
│       │   └── pipelines/
│       │       ├── csv_importer.py    ← ConcreteClass CSV
│       │       ├── json_importer.py   ← ConcreteClass JSON
│       │       └── xml_importer.py    ← ConcreteClass XML
│       └── infrastructure/
│           ├── job_store.py           ← status de jobs em memória
│           └── postgres_repository.py ← persistência PostgreSQL
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_template_method_order.py
│   └── integration/
│       └── test_import_endpoints.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Pré-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Como Rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir todos os serviços
docker-compose up --build

# 3. Acessar a aplicação
# Swagger UI: http://localhost:8000/docs
```

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/import/csv` | Importa um arquivo CSV |
| `POST` | `/import/json` | Importa um arquivo JSON |
| `POST` | `/import/xml` | Importa um arquivo XML |
| `GET`  | `/import/{job_id}/status` | Consulta o status de um job de importação |

## Rodar os Testes

```bash
# Testes unitários (sem serviços externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (banco mockado — ver decisão abaixo)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

> **Decisão de teste:** os testes de integração usam `fastapi.testclient.TestClient`
> e mockam `PostgresImportRepository.bulk_insert` (ver `tests/conftest.py`).
> Isso mantém os testes rápidos e determinísticos sem exigir um PostgreSQL
> real no ambiente de CI/dev, enquanto ainda exercitam o pipeline completo —
> upload HTTP, leitura, parse, validação, transformação e geração de
> relatório — através das rotas reais do FastAPI.

## Verificar Qualidade do Código

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `DATABASE_URL` | URL de conexão PostgreSQL usada por `PostgresImportRepository` | `postgresql://app:secret@db:5432/appdb` |
| `POSTGRES_USER` | Usuário do container PostgreSQL | `app` |
| `POSTGRES_PASSWORD` | Senha do container PostgreSQL | `secret` |
| `POSTGRES_DB` | Nome do banco de dados | `appdb` |
