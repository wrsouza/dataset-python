# Nested Dashboard UI

> **Design Pattern:** Composite | **Categoria:** Structural
> **Framework:** Streamlit | **Serviços:** Nenhum (sem banco de dados ou API externa)

## Objetivo Pedagógico

Demonstrar o pattern **Composite** em um dashboard com layout aninhado:
widgets atômicos (`metric_card`, `text_block`, `chart`) e containers de
layout (`row`, `column`, `tab_group`) compartilham a mesma interface
`DashboardComponent`. O aluno deve aprender a **transparência** do pattern:
o código cliente (a aplicação Streamlit, os use cases) nunca precisa saber
se está lidando com um widget isolado ou com um container que esconde uma
árvore inteira de outros containers e widgets.

## O Pattern Aplicado

`DashboardComponent` (`src/dashboard/domain/interfaces.py`) é o Component:
uma ABC com `render()`, `count_widgets()` e `depth()`. `MetricCard`,
`TextBlock` e `ChartWidget` (`src/dashboard/infrastructure/widgets.py`) são
os Leafs — widgets atômicos sem filhos. `Row`, `Column` e `TabGroup`
(`src/dashboard/infrastructure/containers.py`) são os Composites: cada um
guarda uma lista ordenada de `DashboardComponent`s, que podem ser outros
Leafs **ou** outros Composites, permitindo aninhamento arbitrário (uma
`TabGroup` com `Row`s que contêm `Column`s que contêm `chart`s).

A árvore é construída a partir de uma definição JSON
(`src/dashboard/infrastructure/definition_parser.py`), que recursivamente
decide se cada nó é um container (`row`/`column`/`tab_group`, com
`children`) ou um leaf (com `props`), delegando a construção de leafs ao
registry de widgets (`src/dashboard/infrastructure/registry.py`). O
`app.py` (`src/main.py`) nunca percorre a árvore de domínio diretamente:
ele chama `component.render()`, recebe uma estrutura de dicts/listas
totalmente serializável, e a converte em chamadas `st.*`.

## Diagrama UML (ASCII)

```
                <<interface>>
                DashboardComponent
            ----------------------------
            + name: str
            + component_type: str
            + render(): dict
            + count_widgets(): int
            + depth(): int
                      ▲
                      | implements
        ┌─────────────┼──────────────────────────┐
        │                                         │
  MetricCard / TextBlock / ChartWidget      _BaseContainer
       (Leaf — sem filhos)                  (Composite — children: tuple)
                                                   ▲
                                                   | extends
                                     ┌─────────────┼─────────────┐
                                     │             │             │
                                    Row          Column       TabGroup
                              (lado a lado)   (empilhado)   (abas, + tab_labels)

  Cliente (use cases / app.py)
       |
       └──> component.render() / .count_widgets() / .depth()
            (não sabe, nem precisa saber, se `component` é leaf ou container)
```

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** a árvore de domínio (`domain/`) só define
  o contrato; a montagem a partir de JSON (`infrastructure/definition_parser.py`)
  e o registry de tipos (`infrastructure/registry.py`) ficam isolados da
  renderização real, que vive inteiramente em `src/main.py`.
- **O (Open/Closed):** um novo tipo de widget (ex: `image_widget`) é
  adicionado escrevendo uma nova classe Leaf e chamando
  `register_widget_builder(...)` em `registry.py` — nenhum código existente
  em `Row`, `Column`, `TabGroup` ou no parser precisa ser modificado.
- **L (Liskov Substitution):** `Row`, `Column`, `TabGroup` e qualquer Leaf
  são intercambiáveis onde `DashboardComponent` é esperado — os testes em
  `tests/unit/test_containers.py::test_mixed_container_types_are_interchangeable`
  comprovam isso misturando leafs e containers como filhos do mesmo nó.

## Como Rodar

### Localmente com Streamlit

```bash
pip install -e ".[dev]"
streamlit run src/main.py
```

Acesse `http://localhost:8501`.

### Via Docker Compose

```bash
cp .env.example .env
docker-compose up --build
```

Acesse `http://localhost:8501`.

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Ou localmente:

```bash
pytest --cov=src --cov-report=term-missing
```

## Estrutura do Projeto

```
structural/composite/p5/
├── src/
│   ├── main.py                          ← app.py Streamlit (composition root)
│   └── dashboard/
│       ├── domain/
│       │   ├── interfaces.py            ← DashboardComponent (ABC, Component)
│       │   ├── entities.py              ← MetricCardData, TextBlockData, ChartData, TreeMetrics
│       │   └── exceptions.py            ← exceções específicas do domínio
│       ├── application/
│       │   └── use_cases.py             ← construir árvore, renderizar, calcular métricas
│       └── infrastructure/
│           ├── widgets.py               ← Leafs: MetricCard, TextBlock, ChartWidget
│           ├── containers.py            ← Composites: Row, Column, TabGroup
│           ├── registry.py              ← registro OCP de builders de widget
│           └── definition_parser.py     ← parsing JSON/dict -> árvore
├── examples/sales_dashboard.json        ← definição de exemplo (3 níveis de profundidade)
├── tests/
│   ├── unit/                            ← leaf isolado, composite aninhado, registry, parser, use cases
│   └── integration/                     ← fluxo completo JSON -> árvore -> dados renderizáveis
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```
