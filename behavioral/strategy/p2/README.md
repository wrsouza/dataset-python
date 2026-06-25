# Discount Strategy API (Strategy) — P2

API Flask que aplica diferentes regras de desconto sobre um pedido,
escolhidas em tempo de execução, e persiste o histórico de aplicações
em MySQL.

> **Nota de ambiente:** os testes usam SQLite como stand-in de MySQL
> (`DiscountHistoryRepository` funciona sobre qualquer conexão DB-API
> 2.0 — sqlite3 ou pymysql — só o placeholder de parâmetro muda entre
> dialetos). Em produção, `DB_DIALECT=mysql` aponta para o MySQL real.

## Objetivo pedagógico

Demonstrar o pattern **Strategy**: `DiscountCalculator` (Context) não
sabe nada sobre regras de desconto específicas — delega para o
`DiscountStrategy` configurado, que pode ser trocado em tempo de
execução via `set_strategy()`. Adicionar uma nova regra (ex.: "frete
grátis") é só uma nova classe, sem tocar no Context nem nas demais
estratégias.

Elementos do pattern:
- **Context:** `DiscountCalculator` (`application/context.py`)
- **Strategy (abstrato):** `DiscountStrategy` (`domain/interfaces.py`)
- **Concrete Strategies:** `PercentageDiscountStrategy`, `FixedAmountDiscountStrategy`, `BulkQuantityDiscountStrategy`, `NoDiscountStrategy` (`infrastructure/strategies/`)

## Diagrama (ASCII)

```
POST /discounts/apply {"strategy": "bulk_quantity", ...}
        │
        ▼
get_strategy("bulk_quantity", params) ──► BulkQuantityDiscountStrategy
        │
        ▼
DiscountCalculator.calculate() ──► strategy.apply() ──► DiscountResult
        │
        ▼
DiscountHistoryRepository.append() (MySQL / SQLite)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota                       | Descrição                                     |
|--------|-----------------------------|--------------------------------------------------|
| POST   | `/discounts/apply`          | Aplica uma estratégia de desconto                 |
| GET    | `/discounts/history`        | Lista todos os descontos aplicados                |
| GET    | `/discounts/strategies`     | Lista os nomes das estratégias disponíveis         |
| GET    | `/health`                   | Healthcheck                                        |

```bash
curl -X POST http://localhost:5000/discounts/apply \
  -H "Content-Type: application/json" \
  -d '{"strategy": "percentage", "original_total": 100, "params": {"percentage": 10}}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada estratégia concreta só sabe calcular seu próprio tipo de desconto; `DiscountHistoryRepository` só persiste/recupera o histórico.
- **OCP:** uma nova regra de desconto é uma nova classe `DiscountStrategy` mais uma entrada em `_STRATEGY_FACTORIES` — sem tocar nas estratégias existentes.
- **LSP:** qualquer `DiscountStrategy` concreta pode substituir outra em `DiscountCalculator` sem quebrar o contrato — todas retornam `DiscountResult`.
- **ISP:** `DiscountStrategy` expõe só os três métodos que o Context realmente precisa (`apply`, `get_name`, `get_description`).
- **DIP:** `DiscountCalculator` e os use cases dependem de `DiscountStrategy`/`DiscountHistoryRepository` (abstrações), nunca das classes concretas diretamente — injeção via construtor em `create_app`.
