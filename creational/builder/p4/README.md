# Pipeline Builder Visual

> **Design Pattern:** Builder
> **Categoria:** Creational
> **Framework:** Streamlit
> **Domínio:** pipeline_builder

## Objetivo Pedagógico

Este projeto demonstra o padrão Builder construindo pipelines de processamento de dados
passo a passo através de uma interface visual Streamlit. O aluno aprende como separar a
construção de um objeto complexo (Pipeline) de sua representação final, usando um Director
(ETLDirector) para orquestrar receitas de pipelines reutilizáveis.

## O Pattern em Ação

| Papel do Pattern   | Classe                   | Arquivo                                              |
|--------------------|--------------------------|------------------------------------------------------|
| Builder (ABC)      | `PipelineBuilder`        | `src/pipeline_builder/domain/interfaces.py`          |
| ConcreteBuilder    | `CSVPipelineBuilder`     | `src/pipeline_builder/infrastructure/builders.py`    |
| ConcreteBuilder    | `JSONPipelineBuilder`    | `src/pipeline_builder/infrastructure/builders.py`    |
| ConcreteBuilder    | `APIPipelineBuilder`     | `src/pipeline_builder/infrastructure/builders.py`    |
| Director           | `ETLDirector`            | `src/pipeline_builder/application/use_cases.py`      |
| Product            | `Pipeline`               | `src/pipeline_builder/domain/entities.py`            |

## Diagrama UML

```
<<abstract>>
PipelineBuilder
+ add_source(config) -> Self
+ add_transform(type, params) -> Self
+ add_filter(condition) -> Self
+ add_sink(config) -> Self
+ build() -> Pipeline
+ reset() -> None
+ source_format: SourceFormat  [property]
        |
        ├── CSVPipelineBuilder   (SourceFormat.CSV)
        ├── JSONPipelineBuilder  (SourceFormat.JSON)
        └── APIPipelineBuilder   (SourceFormat.API)

ETLDirector
- _builder: PipelineBuilder
+ build_standard_etl(source_config) -> Pipeline
+ build_validation_pipeline(source_config, condition) -> Pipeline
+ build_aggregation_pipeline(source_config, group_by, agg_col) -> Pipeline

Pipeline (Product)
- name: str
- source_format: SourceFormat
- steps: list[PipelineStep]
+ execute(data) -> list[ExecutionResult]
+ describe() -> list[str]

PipelineStep
- step_type: StepType  (SOURCE | TRANSFORM | FILTER | SINK)
- name: str
- config: dict[str, Any]

ExecutionResult
- step_name: str
- success: bool
- rows_in: int
- rows_out: int
- preview: list[dict]
- error: str | None
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** Cada step handler (`_handle_source`, `_handle_filter`,
  `_handle_transform`, `_handle_sink`) tem uma responsabilidade. O `ETLDirector` apenas
  orquestra; os builders apenas constroem; `Pipeline.execute()` apenas executa.
- **O — Open/Closed:** Para adicionar um novo formato de source (ex: Parquet), cria-se
  `ParquetPipelineBuilder` sem modificar `_BasePipelineBuilder` ou o Director.
- **D — Dependency Inversion:** `ETLDirector` recebe `PipelineBuilder` (ABC) no
  construtor — nunca uma implementação concreta. A UI pode injetar qualquer builder.

## Estrutura do Projeto

```
p4/
├── src/
│   └── pipeline_builder/
│       ├── domain/
│       │   ├── interfaces.py    <- PipelineBuilder (ABC)
│       │   └── entities.py      <- Pipeline, PipelineStep, ExecutionResult
│       ├── application/
│       │   └── use_cases.py     <- ETLDirector, BuildPipelineUseCase
│       ├── infrastructure/
│       │   └── builders.py      <- CSVPipelineBuilder, JSONPipelineBuilder, APIPipelineBuilder
│       └── app.py               <- Streamlit UI
├── tests/
│   ├── unit/test_builders.py
│   └── integration/test_integration.py
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Como Rodar

```bash
cp .env.example .env

# Rodar app Streamlit
docker-compose up app
# Acesse: http://localhost:8501

# Rodar testes
docker-compose run --rm test
```

## Rodar sem Docker

```bash
pip install -e ".[dev]"
streamlit run src/pipeline_builder/app.py
```

## Variáveis de Ambiente

| Variável                    | Descrição                       | Padrão  |
|-----------------------------|---------------------------------|---------|
| `STREAMLIT_SERVER_PORT`     | Porta do servidor Streamlit     | `8501`  |
| `STREAMLIT_SERVER_HEADLESS` | Modo headless (para Docker)     | `true`  |
| `STREAMLIT_THEME_BASE`      | Tema da UI                      | `light` |

## Usando a UI

1. **Sidebar → Step type:** escolha `source`, `transform`, `filter` ou `sink`
2. Configure os parâmetros do step (formato, coluna, condição…)
3. Clique **Add Step** para adicionar ao pipeline
4. Repita para adicionar mais steps
5. Clique **Run Pipeline** para executar — veja os resultados por step
6. Use **Director Presets** para carregar pipelines pré-configurados:
   - `standard_etl`: source → deduplicate → sort → sink
   - `validation`: source → filter → sink
   - `aggregation`: source → aggregate → sort → sink

## Transforms Disponíveis

| Transform     | Parâmetros                                    |
|---------------|-----------------------------------------------|
| `sort`        | `column`, `descending`                        |
| `deduplicate` | (nenhum)                                      |
| `rename`      | `mapping` (old_name → new_name)               |
| `cast`        | `column`, `target_type` (int/float/str)       |
| `aggregate`   | `group_by`, `agg_column` (soma por grupo)     |

## Filtros Disponíveis

Sintaxe: `coluna operador valor`

| Operador   | Exemplo              |
|------------|----------------------|
| `==`       | `name == Alice`      |
| `!=`       | `status != inactive` |
| `>`        | `amount > 100`       |
| `<`        | `price < 50`         |
| `>=`       | `score >= 7`         |
| `<=`       | `age <= 30`          |
| `contains` | `category contains A`|
