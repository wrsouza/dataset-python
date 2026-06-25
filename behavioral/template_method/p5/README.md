# Analysis Workflow Template (Template Method) — P5

App Streamlit onde dois workflows de análise (descritivo e de
tendência) compartilham o mesmo esqueleto preprocess→estatísticas→
outliers→interpretação — sem nenhum serviço externo.

## Objetivo pedagógico

Demonstrar o pattern **Template Method**: `AnalysisWorkflow`
(AbstractClass) define o algoritmo fixo em `run()` e cada workflow
concreto só sobrescreve `preprocess()`/`interpret()`. O hook
`should_flag_outliers()` deixa `TrendAnalysisWorkflow` pular a
detecção de outliers (uma série em tendência naturalmente se afasta da
própria média, o que dispararia falsos positivos) sem alterar o
algoritmo principal.

Elementos do pattern:
- **AbstractClass:** `AnalysisWorkflow` (`domain/interfaces.py`)
- **Template Method:** `AnalysisWorkflow.run()`
- **ConcreteClasses:** `DescriptiveAnalysisWorkflow`, `TrendAnalysisWorkflow` (`application/workflows/`)
- **Hook:** `should_flag_outliers()`

## Diagrama (ASCII)

```
AnalysisWorkflow.run(raw_values)
        │
        ├─► preprocess(raw_values)            (abstrato)
        ├─► compute_statistics(values)         (concreto, compartilhado)
        ├─► should_flag_outliers()? ──► detect_outliers(values, stats)  (hook + concreto)
        └─► interpret(stats)                   (abstrato)
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

- **SRP:** cada workflow concreto só sabe limpar e interpretar seus próprios dados; `compute_statistics`/`detect_outliers` ficam centralizados na AbstractClass.
- **OCP:** um novo workflow (ex.: sazonalidade) é uma nova classe `AnalysisWorkflow` — sem tocar no algoritmo de `run()` nem nos workflows existentes.
- **LSP:** qualquer `AnalysisWorkflow` concreto pode ser executado via `run()` sem quebrar o contrato — todos retornam `AnalysisReport`.
- **ISP:** `AnalysisWorkflow` expõe só os dois métodos abstratos que cada workflow realmente precisa sobrescrever.
- **DIP:** `app.py` depende só do registro (`get_workflow`/`list_workflow_names`), nunca de uma classe concreta diretamente.
