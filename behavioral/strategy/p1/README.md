# Tax Calculation Engine

> **Design Pattern:** Strategy
> **Categoria:** Behavioral
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Strategy aplicado ao cálculo de impostos para
múltiplas jurisdições fiscais (Brasil, EUA, União Europeia, isenção). O aluno
aprenderá como trocar o algoritmo de cálculo de imposto em tempo de execução
sem alterar o código que o consome, e como isso viabiliza o princípio
Open/Closed: adicionar um novo país não exige tocar no `Context` nem nas
demais estratégias.

## O Pattern em Ação

`TaxStrategy` é a interface abstrata que declara o contrato de cálculo de
impostos. Cada jurisdição fiscal implementa sua própria regra como uma
subclasse concreta. `TaxCalculator` é o Context: ele recebe uma `TaxStrategy`
por injeção de dependência (construtor ou `set_strategy()`) e delega o
cálculo, sem nunca conhecer as regras fiscais de nenhum país específico.

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Strategy (abstrata) | `TaxStrategy` | `src/tax/domain/interfaces.py` |
| Context | `TaxCalculator` | `src/tax/application/context.py` |
| ConcreteStrategy | `BrazilianTaxStrategy` | `src/tax/infrastructure/strategies/brazilian.py` |
| ConcreteStrategy | `USFederalTaxStrategy` | `src/tax/infrastructure/strategies/us_federal.py` |
| ConcreteStrategy | `EUVATStrategy` | `src/tax/infrastructure/strategies/eu_vat.py` |
| ConcreteStrategy | `ExemptTaxStrategy` | `src/tax/infrastructure/strategies/exempt.py` |
| Strategy Registry | `get_strategy()` / `get_all_strategies()` | `src/tax/infrastructure/strategies/registry.py` |

## Diagrama UML (ASCII)

```
<<abstract>>
TaxStrategy
+ calculate(order: Order, customer: Customer): TaxBreakdown
+ get_name(): str
+ get_description(): str
        |
        ├── BrazilianTaxStrategy
        │     + calculate(...)   → ICMS 18% + PIS 0.65% + COFINS 3%
        │
        ├── USFederalTaxStrategy
        │     + calculate(...)   → Federal 10% + State (CA/NY/TX/FL/WA)
        │
        ├── EUVATStrategy
        │     + calculate(...)   → VAT por país (DE 19%, FR 20%, PT 23%...)
        │
        └── ExemptTaxStrategy
              + calculate(...)   → zero tax (B2B com certificado)

TaxCalculator (Context)
- _strategy: TaxStrategy
+ set_strategy(strategy: TaxStrategy) -> None
+ calculate(order: Order, customer: Customer) -> TaxBreakdown
        |
        └── delega para self._strategy.calculate(...)
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** uma nova jurisdição fiscal (ex.: Canadá) é adicionada
  criando `CanadianTaxStrategy(TaxStrategy)` em
  `src/tax/infrastructure/strategies/` e registrando-a em `registry.py`.
  Nenhuma linha de `TaxCalculator` (`src/tax/application/context.py`) ou da
  API (`src/main.py`) precisa ser alterada.
- **D — Dependency Inversion:** `TaxCalculator` depende apenas da abstração
  `TaxStrategy` (`src/tax/domain/interfaces.py`), nunca de uma implementação
  concreta. A estratégia concreta é injetada no construtor ou via
  `set_strategy()`, e a rota `calculate_tax` em `src/main.py` resolve a
  implementação através do registry, mantendo a composição fora do domínio.
- **L — Liskov Substitution:** todas as subclasses de `TaxStrategy` honram o
  mesmo contrato — recebem `Order` e `Customer`, devolvem `TaxBreakdown`, e
  nenhuma lança exceções fora do que a base permite (`ExemptTaxStrategy`
  apenas retorna uma lista de taxas vazia, sem comportamento especial).
- **S — Single Responsibility:** cada estratégia conhece somente as regras
  fiscais de sua jurisdição; persistência fica em `infrastructure/database/`;
  orquestração HTTP fica em `main.py`.
- **I — Interface Segregation:** `TaxStrategy` expõe apenas três métodos
  coesos (`calculate`, `get_name`, `get_description`), sem forçar
  implementações vazias.

## Estrutura do Projeto

```
strategy/p1/
├── src/
│   ├── main.py                          ← FastAPI app + rotas
│   └── tax/
│       ├── domain/
│       │   ├── entities.py              ← Order, Customer, TaxBreakdown...
│       │   ├── interfaces.py            ← TaxStrategy (ABC)
│       │   └── exceptions.py            ← exceções de domínio
│       ├── application/
│       │   └── context.py               ← TaxCalculator (Context)
│       └── infrastructure/
│           ├── database/                ← models, repository, connection
│           └── strategies/               ← Concrete Strategies + registry
├── tests/
│   ├── conftest.py
│   ├── unit/                            ← cada strategy isolada + context/registry
│   └── integration/                     ← API completa via TestClient
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
# FastAPI: http://localhost:8000/docs
```

## Rodar os Testes

```bash
# Testes unitários (sem serviços externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (API completa via TestClient)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

> **Decisão de arquitetura:** os testes de integração usam SQLite em memória
> via override do dependency `get_db` do FastAPI, em vez de exigir um
> PostgreSQL real durante a execução do `pytest`. Isso mantém a suíte
> determinística e rápida em qualquer ambiente (CI, máquina local sem
> Docker). O fluxo `docker-compose up` + `app` continua usando PostgreSQL
> real em produção/desenvolvimento, conforme `DATABASE_URL` em `.env`.

## Verificar Qualidade do Código

```bash
# Dentro do container ou com venv ativo
black src/ tests/
ruff check src/ tests/
mypy src/
```

Resultado nesta revisão: `black` sem alterações pendentes, `ruff check`
sem erros, `mypy --strict` sem erros, `pytest --cov` com **97.66%** de
cobertura (mínimo exigido: 80%).

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `DATABASE_URL` | URL de conexão PostgreSQL | `postgresql://app:secret@db:5432/taxdb` |
| `POSTGRES_USER` | Usuário do container PostgreSQL | `app` |
| `POSTGRES_PASSWORD` | Senha do container PostgreSQL | `secret` |
| `POSTGRES_DB` | Nome do banco de dados | `taxdb` |

## Endpoints Principais

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/tax/strategies` | Lista todas as estratégias fiscais registradas |
| `POST` | `/orders` | Cria um novo pedido |
| `POST` | `/orders/{order_id}/calculate-tax?strategy=<brazil\|us\|eu\|exempt>` | Calcula impostos de um pedido com a estratégia escolhida |
