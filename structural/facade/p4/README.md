# Data Migration Facade

> **Design Pattern:** Facade | **Categoria:** Structural
> **Framework:** CLI (Typer) | **Serviços:** MySQL → PostgreSQL

## Objetivo Pedagógico

Demonstrar o padrão Facade escondendo a complexidade de uma migração de dados
entre bancos diferentes: análise de schema, extração em batches, transformação,
carga, geração de relatório e rollback em caso de falha. O cliente (CLI) chama
apenas três métodos — `migrate()`, `dry_run()`, `rollback()` — sem nunca tocar
nos 6 subsistemas internos.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Facade | `MigrationFacade` | `src/migration/application/facade.py` |
| Subsystem: análise de schema | `GenericSchemaAnalyzer` | `infrastructure/schema_analyzer.py` |
| Subsystem: extração em batch | `BatchDataExtractor` | `infrastructure/extractor.py` |
| Subsystem: transformação | `TrimmingTypeTransformer` | `infrastructure/transformer.py` |
| Subsystem: carga | `GenericDataLoader` | `infrastructure/loader.py` |
| Subsystem: relatório | `SimpleMigrationReporter` | `infrastructure/reporter.py` |
| Subsystem: rollback | `RollbackManager` | `infrastructure/rollback_manager.py` |
| Client | CLI Typer | `src/migration/cli.py` |

## Diagrama UML (ASCII)

```
Client (cli.py)
      │
      ▼
MigrationFacade
      │  migrate() / dry_run() / rollback()
      ├──► SchemaAnalyzer        (inspeciona colunas + row count via cursor.description)
      ├──► DataExtractor         (SELECT * em batches via fetchmany)
      ├──► DataTransformer       (limpeza de valores antes da carga)
      ├──► DataLoader            (INSERT ... executemany no destino)
      ├──► MigrationReporter     (monta o MigrationReport final)
      └──► RollbackManager       (DELETE nas tabelas tocadas se a migração falhar)
```

## Por que um único `SchemaAnalyzer`/`Extractor`/`Loader` serve para MySQL, PostgreSQL e SQLite

Todos os drivers Python (`sqlite3`, `pymysql`, `psycopg2`) implementam o mesmo
contrato PEP 249 (DB-API 2.0): `cursor()`, `execute()`, `fetchmany()`,
`cursor.description`. O `GenericSchemaAnalyzer` e o `BatchDataExtractor`
dependem apenas desse contrato — não de um banco específico — então o mesmo
código migra de/para qualquer um dos três sem duplicação.

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** cada subsistema faz uma única coisa
  (`SchemaAnalyzer` só analisa, `DataLoader` só carrega, etc.).
- **D — Dependency Inversion:** `MigrationFacade` depende das interfaces em
  `domain/interfaces.py` (ABCs), nunca de `pymysql`/`psycopg2`/`sqlite3`
  diretamente — só `DriverConnectionFactory` conhece os drivers concretos.

## Segurança

Todo nome de tabela passa por `validate_table_name()`
(`infrastructure/identifiers.py`) antes de ser interpolado em SQL, prevenindo
injeção mesmo em uma ferramenta de linha de comando administrada por humanos
confiáveis — defesa em profundidade.

## Limitação de Design (documentada de propósito)

`RollbackManager.rollback()` simplifica o rollback para "DELETE de tudo que
essa migração inseriu nas tabelas tocadas" — correto para o caso comum de
migrar para tabelas de destino recém-provisionadas e vazias, mas não é um
rollback transacional completo (não desfaz updates em tabelas pré-existentes).

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

Isso sobe MySQL (fonte) + PostgreSQL (destino) e executa uma migração de
exemplo das tabelas `orders,products`.

## Uso Manual do CLI

```bash
python -m migration.cli migrate \
  --from mysql://app:secret@localhost/sourcedb \
  --to postgresql://app:secret@localhost/destdb \
  --tables orders,products

python -m migration.cli dry-run \
  --from mysql://app:secret@localhost/sourcedb \
  --tables orders,products
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente:

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes usam **SQLite real** como substituto de MySQL/PostgreSQL nos testes
de integração (mesmo contrato DB-API, sem precisar de servidores rodando) e
mocks das 5 interfaces nos testes unitários da Facade.
