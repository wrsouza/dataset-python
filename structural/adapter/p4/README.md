# DataFrame Format Adapter

> **Design Pattern:** Adapter | **Categoria:** Structural
> **Framework:** Streamlit | **Serviços:** Nenhum (sem banco de dados ou API externa)

## Objetivo Pedagógico

Demonstrar o pattern **Adapter** unificando o acesso a três formatos de
arquivos tabulares — CSV, JSON e Parquet — sob uma única interface,
`TabularDataSource`. O usuário envia qualquer um dos três formatos via
upload no Streamlit; o restante da aplicação (use case, UI de preview,
exportação) nunca sabe (e não precisa saber) qual parser concreto foi
usado para ler o arquivo.

## O Pattern Aplicado

| Papel | Classe/Conceito | Arquivo |
|-------|------------------|---------|
| Target (interface desejada) | `TabularDataSource` (Protocol) | `domain/interfaces.py` |
| Produto do Target | `ParsedDataset` | `domain/entities.py` |
| Adaptee (parser CSV) | `pandas.read_csv` | `infrastructure/adapters.py` |
| Adaptee (parser JSON) | `pandas.read_json` | `infrastructure/adapters.py` |
| Adaptee (parser Parquet) | `pandas.read_parquet` (via pyarrow) | `infrastructure/adapters.py` |
| Adapter CSV | `CsvAdapter` | `infrastructure/adapters.py` |
| Adapter JSON | `JsonAdapter` | `infrastructure/adapters.py` |
| Adapter Parquet | `ParquetAdapter` | `infrastructure/adapters.py` |
| Seleção do Adapter | `AdapterFactory` | `application/use_cases.py` |
| Client | `NormalizeToCsvUseCase` + UI Streamlit | `application/use_cases.py`, `infrastructure/app.py` |

Cada Adapter concreto (`CsvAdapter`, `JsonAdapter`, `ParquetAdapter`)
traduz o resultado de um leitor pandas (`DataFrame`) para `ParsedDataset`
— a representação de dados tabulares independente de formato usada em
toda a aplicação. O `AdapterFactory` detecta o formato pela extensão do
nome do arquivo e devolve o `Adapter` correspondente; o `client`
(`NormalizeToCsvUseCase` e a UI) depende apenas de `TabularDataSource`,
nunca de um parser concreto.

### Por que pandas para os três formatos?

O dataset poderia usar os módulos `csv`/`json` da stdlib para CSV/JSON e
pandas/pyarrow apenas para Parquet. Optamos por **pandas como Adaptee
único** pelos seguintes motivos:

- **Consistência**: um único motor de inferência de tipos, encoding e
  tratamento de valores ausentes (`NaN`) evita que o aluno precise
  reconciliar duas semânticas de parsing diferentes (stdlib vs pandas).
- **Parquet não tem leitor na stdlib** — pandas/pyarrow é obrigatório
  para esse formato. Reaproveitar o mesmo motor para CSV/JSON deixa o
  papel de "tradução" de cada Adapter simétrico e fácil de comparar lado
  a lado (todos chamam `pd.read_*` e convertem o `DataFrame` resultante).
- Cada Adapter continua com responsabilidade única (SRP): apenas
  traduzir a saída de **um** leitor pandas para `ParsedDataset`.

`ParsedDataset` armazena todas as células como `str`: a fidelidade de
tipo (int vs float vs str) é intencionalmente descartada, pois o caso de
uso final (`NormalizeToCsvUseCase`) é exportar um CSV unificado em texto.

## Diagrama UML (ASCII)

```
                  <<Protocol>>
                  TabularDataSource
              ----------------------------
              + load(raw_bytes: bytes) -> ParsedDataset
                        ▲               ▲               ▲
                        |               |               |
                  CsvAdapter      JsonAdapter      ParquetAdapter
                  (Adapter)       (Adapter)        (Adapter)
                        |               |               |
                        v               v               v
                pandas.read_csv  pandas.read_json  pandas.read_parquet
                  (Adaptee CSV)   (Adaptee JSON)    (Adaptee Parquet, pyarrow)

AdapterFactory.create_for_filename(filename) -> TabularDataSource
        (detecta formato pela extensão; OCP: novo formato = nova entrada + Adapter)

Client:
  NormalizeToCsvUseCase(factory) -> depende só de TabularDataSource (DIP)
  app.py (Streamlit) -> file_uploader -> use_case.parse() -> preview + download
```

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** cada Adapter (`CsvAdapter`, `JsonAdapter`,
  `ParquetAdapter`) cuida exclusivamente da tradução de um formato; o
  `AdapterFactory` só decide qual Adapter usar; `NormalizeToCsvUseCase`
  só orquestra parse → normalização.
- **O (Open/Closed):** adicionar suporte a um novo formato (ex: Excel)
  significa criar uma nova classe Adapter e uma entrada no dicionário
  `_EXTENSION_TO_ADAPTER` (`application/use_cases.py`) — nenhum Adapter
  existente, nem `NormalizeToCsvUseCase`, nem a UI precisam ser alterados.
- **D (Dependency Inversion):** `NormalizeToCsvUseCase` e o `app.py`
  dependem apenas do Protocol `TabularDataSource` (`domain/interfaces.py`),
  nunca de `pandas`, `pyarrow` ou de uma classe `Adapter` concreta
  diretamente — a implementação é resolvida pelo `AdapterFactory`.

## Tratamento de Erros

Duas exceções de domínio cobrem os casos de falha:

- `UnsupportedFormatError`: lançada pelo `AdapterFactory` quando a
  extensão do arquivo não tem um Adapter registrado (ex: `.xml`).
- `InvalidDataError`: lançada por qualquer Adapter quando os bytes
  recebidos não podem ser parseados como o formato esperado (arquivo
  corrompido, JSON malformado, Parquet inválido, encoding incorreto).

A UI (`infrastructure/app.py`) captura ambas e exibe uma mensagem de erro
amigável via `st.error`, sem expor stack traces ao usuário final.

## Estrutura do Projeto

```
p4/
├── src/
│   └── dataframe_adapter/
│       ├── domain/
│       │   ├── interfaces.py      <- Target: TabularDataSource Protocol
│       │   └── entities.py        <- ParsedDataset, UnsupportedFormatError, InvalidDataError
│       ├── application/
│       │   └── use_cases.py       <- AdapterFactory, NormalizeToCsvUseCase
│       └── infrastructure/
│           ├── adapters.py        <- CsvAdapter, JsonAdapter, ParquetAdapter
│           └── app.py             <- Streamlit UI (Client; excluído da cobertura)
├── tests/
│   ├── unit/
│   │   ├── test_entities.py
│   │   ├── test_csv_adapter.py
│   │   ├── test_json_adapter.py
│   │   ├── test_parquet_adapter.py
│   │   ├── test_adapter_factory.py
│   │   └── test_normalize_use_case.py
│   └── integration/
│       └── test_normalize_flow.py  <- fluxo completo para os 3 formatos
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

### Localmente com Streamlit

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
streamlit run src/dataframe_adapter/infrastructure/app.py
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
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Ou via Docker:

```bash
docker-compose run --rm app pytest
```

## Qualidade de Código

```bash
black --check .
ruff check .
mypy --strict src
```

`app.py` é excluído da medição de cobertura (`[tool.coverage.run] omit`
em `pyproject.toml`), seguindo a convenção do dataset para módulos de UI
do Streamlit que não têm lógica de negócio testável isoladamente — a
mesma lógica (parse + normalize) já é coberta pelos testes de
`application/use_cases.py`.
