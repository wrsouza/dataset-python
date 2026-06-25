# Shopping Cart Visitors (Visitor) — P2

API Flask que aplica diferentes operações (preço, frete, fatura) sobre
um carrinho com itens de tipos distintos (físico, digital, assinatura),
sem nenhum `isinstance` — cada item sabe se apresentar ao visitor
certo via double-dispatch.

> **Nota de ambiente:** os testes usam SQLite como stand-in de MySQL
> (`CartReportRepository` funciona sobre qualquer conexão DB-API 2.0 —
> sqlite3 ou pymysql — mesmo truque dialect-aware de `strategy/p2`).

## Objetivo pedagógico

Demonstrar o pattern **Visitor**: `CartItem` (Element) expõe só
`accept(visitor)`, que chama o `visit_X` certo no visitor — o item
nunca sabe qual operação está sendo executada. Adicionar uma nova
operação (ex.: "calcular pontos de fidelidade") é só uma nova classe
`CartVisitor`, sem tocar em `PhysicalItem`/`DigitalItem`/`SubscriptionItem`.

Elementos do pattern:
- **Visitor (abstrato):** `CartVisitor` (`domain/interfaces.py`)
- **Element (abstrato):** `CartItem`
- **Concrete Elements:** `PhysicalItem`, `DigitalItem`, `SubscriptionItem`
- **Concrete Visitors:** `PriceCalculatorVisitor`, `ShippingCalculatorVisitor`, `InvoiceFormatterVisitor` (`infrastructure/visitors/`)

## Diagrama (ASCII)

```
traverse(items, visitor)
        │
        └─► for item in items: item.accept(visitor)
                    │
                    ▼
        PhysicalItem.accept() ──► visitor.visit_physical(self)
        DigitalItem.accept()  ──► visitor.visit_digital(self)
        SubscriptionItem.accept() ──► visitor.visit_subscription(self)
                    │
                    ▼
              visitor.result  (CartReport persistido em MySQL/SQLite)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota                                         | Descrição                                |
|--------|-----------------------------------------------|--------------------------------------------|
| POST   | `/carts/operations/<price\|shipping\|invoice>` | Roda uma operação sobre os itens do carrinho |
| GET    | `/carts/operations/<operation>/history`        | Lista os relatórios já gerados para a operação |
| GET    | `/health`                                       | Healthcheck                                 |

```bash
curl -X POST http://localhost:5000/carts/operations/price \
  -H "Content-Type: application/json" \
  -d '{"items": [{"type": "physical", "name": "Book", "unit_price": 10, "quantity": 1, "weight_kg": 0.5}]}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada visitor concreto só sabe calcular sua própria operação; `CartReportRepository` só persiste/recupera relatórios.
- **OCP:** uma nova operação é uma nova classe `CartVisitor` mais uma entrada em `_VISITOR_FACTORIES` — sem tocar nos itens existentes.
- **LSP:** qualquer `CartVisitor` concreto pode ser usado em `traverse()` sem quebrar o contrato — todos implementam os três `visit_X`.
- **ISP:** `CartVisitor` expõe só os três métodos que os elementos realmente chamam; `CartItem` expõe só `accept()`.
- **DIP:** os use cases dependem de `CartVisitor`/`CartReportRepository` (abstrações), nunca das classes concretas diretamente — injeção via construtor em `create_app`.
