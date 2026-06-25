# Data Source Bridge

> **Design Pattern:** Bridge | **Categoria:** Structural
> **Framework:** Streamlit | **Serviços:** SQL Server, MongoDB

## Objetivo Pedagógico

Demonstrar o Bridge pattern desacoplando a abstração de "consultar dados para
um relatório" (`DataView`) da tecnologia concreta de armazenamento
(`DataSource`). O aluno deve conseguir identificar: a Abstraction
(`DataView`), a Refined Abstraction (`SummarizedDataView`), o Implementor
(`DataSource`) e os dois Concrete Implementors (`SqlServerDataSource`,
`MongoDataSource`) — e perceber que ambas as hierarquias evoluem
independentemente.

## O Pattern Aplicado

A aplicação Streamlit permite escolher uma fonte de dados (SQL Server ou
MongoDB) e consultar uma tabela/coleção. Em vez de a camada de aplicação
saber sobre `pyodbc` ou `pymongo`, ela depende apenas da interface
`DataSource` (Implementor). A classe `DataView` (Abstraction) recebe um
`DataSource` por injeção de dependência e delega a ele toda a execução real
da consulta (`connect` → `fetch` → `disconnect`). A subclasse
`SummarizedDataView` (Refined Abstraction) adiciona um resumo textual sem
exigir nenhuma mudança nos Implementors. Trocar de SQL Server para MongoDB
(ou adicionar um terceiro backend, como PostgreSQL) nunca exige alterar
`DataView`, `LoadReportUseCase` ou a UI — apenas implementar uma nova
subclasse de `DataSource`.

## Diagrama UML (ASCII)

```
                  <<Abstraction>>
                     DataView
                  -----------------
                  - data_source: DataSource
                  -----------------
                  + load(collection, filters): QueryResult
                  + source_name(): str
                          |
                          | (composição / DIP)
                          |
              <<Refined Abstraction>>
              SummarizedDataView
              -----------------
              + load_with_summary(collection, filters)
                  : (QueryResult, str)


                  <<Implementor>>
                    DataSource (ABC)
                  -----------------
                  + connect(): None
                  + disconnect(): None
                  + fetch(collection, filters): QueryResult
                  + source_name(): str
                       /        \
                      /          \
   <<ConcreteImplementor>>   <<ConcreteImplementor>>
   SqlServerDataSource       MongoDataSource
   -----------------         -----------------
   usa pyodbc                usa pymongo
```

A seta vertical da Abstraction para o Implementor é a "ponte": `DataView`
mantém apenas uma **referência** à interface `DataSource`, nunca a uma
implementação concreta.

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** `DataView` cuida da orquestração da
  consulta; cada `DataSource` cuida exclusivamente de como conectar e
  consultar seu próprio banco (`SqlServerDataSource` só conhece pyodbc,
  `MongoDataSource` só conhece pymongo).
- **O (Open/Closed):** adicionar um novo banco de dados (ex.: PostgreSQL)
  significa apenas criar uma nova classe `DataSource` em
  `infrastructure/` — nenhuma linha de `DataView`, dos use cases ou da UI
  precisa mudar.
- **L (Liskov Substitution):** qualquer `DataSource` concreto pode
  substituir outro sem que `DataView` precise saber qual é qual; ambos
  lançam o mesmo `DataSourceError` e respeitam o mesmo contrato de
  `connect/fetch/disconnect`.
- **I (Interface Segregation):** `DataSource` expõe apenas quatro métodos
  estritamente necessários para qualquer fonte de dados — nada de métodos
  específicos de SQL ou de documentos vazando para a interface.
- **D (Dependency Inversion):** `DataView.__init__` recebe um `DataSource`
  abstrato por injeção (`infrastructure/factory.py` é o único lugar que
  conhece as classes concretas); a camada de aplicação e a UI dependem
  somente da abstração.

## Estrutura do Projeto

```
src/data_view/
├── domain/
│   ├── entities.py        ← Record, QueryResult, ConnectionConfig
│   └── interfaces.py      ← DataSource (Implementor) e DataSourceError
├── application/
│   └── use_cases.py        ← DataView, SummarizedDataView, use cases
├── infrastructure/
│   ├── sqlserver_source.py ← SqlServerDataSource (pyodbc)
│   ├── mongodb_source.py   ← MongoDataSource (pymongo)
│   └── factory.py          ← composição: monta DataView com cada DataSource
└── app.py                  ← Streamlit (composition root)
```

## Como Rodar

### Com Docker Compose (recomendado)

```bash
cp .env.example .env
docker-compose up --build
```

A aplicação fica disponível em `http://localhost:8501`, com SQL Server em
`localhost:1433` e MongoDB em `localhost:27017`.

### Localmente

```bash
cp .env.example .env
pip install -e ".[dev]"
streamlit run src/data_view/app.py
```

## Rodar os Testes

```bash
# Via Docker
docker-compose run --rm app pytest

# Localmente
pytest --cov=src --cov-report=term-missing
```

- `tests/unit/` — testa cada componente isoladamente, usando mocks para
  `pyodbc` (módulo falso via `unittest.mock`) e `mongomock` para `pymongo`.
- `tests/integration/` — testa o fluxo completo domain → application →
  infrastructure passando pela `factory.py`, para os dois Implementors,
  ainda sem tocar em bancos reais.
