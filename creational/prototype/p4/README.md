# Dashboard Config Cloner

> **Design Pattern:** Prototype | **Categoria:** Creational
> **Framework:** Streamlit | **Serviços:** Nenhum (sem banco de dados ou API externa)

## Objetivo Pedagógico

Demonstrar o pattern **Prototype** clonando configurações de dashboard (vendas,
estoque, marketing) a partir de templates pré-configurados em um Registry. O
aluno deve aprender a diferença prática entre **cópia rasa (shallow copy)** e
**cópia profunda (deep copy)**: editar uma cópia clonada nunca deve afetar o
template original, mesmo quando o objeto contém listas e dicionários aninhados.

## O Pattern Aplicado

`DashboardConfig` é a interface Prototype, com o método `clone()`. As classes
concretas `SalesDashboardConfig`, `InventoryDashboardConfig` e
`MarketingDashboardConfig` (ConcretePrototypes) implementam `clone()` usando
`copy.deepcopy` para garantir que listas (`metrics`, `filters`) e o dicionário
`extra` sejam objetos novos e independentes em cada cópia.

O `JsonDashboardRegistry` é o Registry de prototypes: mantém templates
pré-configurados (`vendas-brasil`, `estoque-geral`, `marketing-q4`),
persistidos em `data/registry.json`, e oferece `clone(name, overrides)` para
gerar cópias editáveis sem nunca mutar o template original.

A camada `application/use_cases.py` orquestra o fluxo: listar templates,
obter o original, clonar, e editar a cópia — sempre depend do de
`DashboardRegistry` (abstração), nunca da implementação concreta.

## Diagrama UML (ASCII)

```
                  <<interface>>
                  DashboardConfig
              ----------------------------
              + clone(overrides): DashboardConfig
              + to_dict(): dict
              + from_dict(data): DashboardConfig
              + title: str
              + dashboard_type: str
                        ▲
                        | implements
            ┌───────────┴────────────────┐
            │                            │
    BaseDashboardConfig ◄────────────────┘
   (deepcopy em clone())
            ▲
            | extends
   ┌────────┼─────────────┬───────────────────────┐
   │                      │                       │
SalesDashboardConfig  InventoryDashboardConfig  MarketingDashboardConfig
(ConcretePrototype)   (ConcretePrototype)        (ConcretePrototype)


                  <<interface>>
                  DashboardRegistry
              ----------------------------
              + register(name, config): None
              + get(name): DashboardConfig
              + clone(name, overrides): DashboardConfig
              + list_templates(): list[str]
                        ▲
                        | implements
                  JsonDashboardRegistry
              (persiste templates em JSON;
               clone() delega a config.clone())
```

## Princípios SOLID Demonstrados

- **O (Open/Closed):** novos tipos de dashboard (ex: `FinanceDashboardConfig`)
  são adicionados criando uma nova subclasse de `BaseDashboardConfig` e uma
  entrada em `_DESERIALIZERS` (`src/dashboard/infrastructure/prototypes.py`) —
  nenhum código existente em `DashboardConfig`, `DashboardRegistry` ou nos
  use cases precisa ser alterado.
- **D (Dependency Inversion):** `application/use_cases.py` depende apenas da
  abstração `DashboardRegistry` (`domain/interfaces.py`), nunca de
  `JsonDashboardRegistry` diretamente. A implementação concreta é injetada na
  composição root (`src/main.py`), permitindo testar os use cases com
  qualquer registry (real ou fake) sem alterar o código de produção.
- **S (Single Responsibility):** `JsonDashboardRegistry` cuida apenas de
  registrar/persistir/clonar templates; a edição de campos da cópia é
  responsabilidade isolada de `EditClonedDashboardUseCase`; a renderização
  fica inteiramente em `src/main.py`.

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
