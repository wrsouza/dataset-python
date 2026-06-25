# Chart Visualization Factory

> **Design Pattern:** Abstract Factory
> **Categoria:** Creational
> **Framework:** Streamlit
> **Dependências:** Plotly, Matplotlib, Altair, pandas

## Objetivo Pedagógico

Este projeto demonstra o padrão Abstract Factory em um app Streamlit que exibe
dados de vendas sintéticos usando famílias de charts de bibliotecas diferentes.
O aluno aprende como trocar toda uma família de gráficos (Plotly → Matplotlib →
Altair) sem modificar uma linha do código cliente — apenas injetando outra
ConcreteFactory. O princípio Open/Closed é observável ao vivo: adicionar Bokeh
significa criar uma nova classe, não editar as existentes.

## O Pattern em Ação

A `AbstractFactory` (`ChartFactory`) declara três métodos de criação.
Cada `ConcreteFactory` produz uma família coesa de charts renderizados pela
mesma biblioteca. O `Client` (`RenderChartFamilyUseCase`) usa apenas a
abstração — nunca sabe qual biblioteca está por baixo.

| Papel do Pattern  | Classe                                   | Arquivo                                             |
|-------------------|------------------------------------------|-----------------------------------------------------|
| AbstractFactory   | `ChartFactory`                           | `src/chart_factory/domain/interfaces.py`            |
| ConcreteFactory   | `PlotlyChartFactory`                     | `src/chart_factory/infrastructure/factories.py`     |
| ConcreteFactory   | `MatplotlibChartFactory`                 | `src/chart_factory/infrastructure/factories.py`     |
| ConcreteFactory   | `AltairChartFactory`                     | `src/chart_factory/infrastructure/factories.py`     |
| AbstractProduct   | `LineChart`, `BarChart`, `PieChart`      | `src/chart_factory/domain/interfaces.py`            |
| ConcreteProduct   | `PlotlyLineChart`, `MatplotlibBarChart`… | `src/chart_factory/infrastructure/factories.py`     |
| Client            | `RenderChartFamilyUseCase`               | `src/chart_factory/application/use_cases.py`        |

## Diagrama UML (ASCII)

```
<<abstract>>
ChartFactory
+ create_line_chart() -> LineChart
+ create_bar_chart()  -> BarChart
+ create_pie_chart()  -> PieChart
+ get_library_name()  -> str
        |
        ├── PlotlyChartFactory
        │     + create_line_chart() -> PlotlyLineChart
        │     + create_bar_chart()  -> PlotlyBarChart
        │     + create_pie_chart()  -> PlotlyPieChart
        │
        ├── MatplotlibChartFactory
        │     + create_line_chart() -> MatplotlibLineChart
        │     + create_bar_chart()  -> MatplotlibBarChart
        │     + create_pie_chart()  -> MatplotlibPieChart
        │
        └── AltairChartFactory
              + create_line_chart() -> AltairLineChart
              + create_bar_chart()  -> AltairBarChart
              + create_pie_chart()  -> AltairPieChart

<<abstract>>          <<abstract>>          <<abstract>>
LineChart             BarChart              PieChart
+ render(df)          + render(df)          + render(df)
+ get_library_name()  + get_library_name()  + get_library_name()
```

## Princípios SOLID Demonstrados

| Princípio | Onde aparece                                                                                   |
|-----------|-----------------------------------------------------------------------------------------------|
| **O — OCP** | Adicionar Bokeh = criar `BokehLineChart`, `BokehBarChart`, `BokehPieChart`, `BokehChartFactory` e registrar em `CHART_FACTORIES`. Zero linhas modificadas. |
| **D — DIP** | `RenderChartFamilyUseCase` recebe `ChartFactory` (ABC) via construtor. `app.py` é o único lugar que instancia a fábrica concreta. |
| **S — SRP** | Cada produto renderiza um único tipo de gráfico. O use case orquestra os três, mas não renderiza. |
| **I — ISP** | `LineChart`, `BarChart` e `PieChart` são ABCs separados — nenhum cliente depende de métodos que não usa. |

## Estrutura do Projeto

```
p4/
├── src/
│   └── chart_factory/
│       ├── app.py                  ← Streamlit UI + composition root
│       ├── domain/
│       │   ├── interfaces.py       ← ChartFactory, LineChart, BarChart, PieChart (ABCs)
│       │   └── entities.py         ← SalesDataset, ChartRenderResult
│       ├── application/
│       │   └── use_cases.py        ← RenderChartFamilyUseCase (Client)
│       └── infrastructure/
│           └── factories.py        ← Concrete factories and products
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_use_cases.py
│   └── integration/
│       └── test_integration.py
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

# 2. Subir o app
docker-compose up --build

# 3. Acessar no navegador
open http://localhost:8501
```

## Rodar os Testes

```bash
# Testes unitários
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (requer as bibliotecas de charts)
docker-compose run --rm app pytest tests/integration/ -v

# Todos com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável                                  | Descrição                    | Padrão  |
|-------------------------------------------|------------------------------|---------|
| `STREAMLIT_SERVER_PORT`                   | Porta do servidor Streamlit  | `8501`  |
| `STREAMLIT_SERVER_HEADLESS`               | Modo headless (containers)   | `true`  |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS`    | Telemetria Streamlit         | `false` |
