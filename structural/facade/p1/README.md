# E-commerce Order Facade

> **Design Pattern:** Facade
> **Categoria:** Structural
> **Framework:** FastAPI
> **Serviços:** PostgreSQL, AWS SQS

## Objetivo Pedagógico

Este projeto demonstra o padrão Facade simplificando o fluxo complexo de
criação de um pedido em um e-commerce. Colocar um pedido envolve coordenar
cinco subsistemas independentes — estoque, frete, pagamento, persistência e
notificação — cada um com sua própria interface e suas próprias regras de
falha/rollback. A `OrderFacade` esconde toda essa orquestração atrás de um
único método (`place_order`), de forma que a camada HTTP (FastAPI) — e
qualquer outro cliente futuro (worker assíncrono, CLI administrativa, etc.) —
não precisa conhecer nem manipular os subsistemas individualmente.

## O Pattern em Ação

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Facade | `OrderFacade` | `src/order/application/facade.py` |
| Subsystem — Estoque | `PostgresInventoryService` (via `InventoryServiceProtocol`) | `src/order/infrastructure/inventory_service.py` |
| Subsystem — Pagamento | `MockPaymentService` (via `PaymentServiceProtocol`) | `src/order/infrastructure/payment_service.py` |
| Subsystem — Frete | `MockShippingService` (via `ShippingServiceProtocol`) | `src/order/infrastructure/shipping_service.py` |
| Subsystem — Notificação | `SQSNotificationService` (via `NotificationServiceProtocol`) | `src/order/infrastructure/notification_service.py` |
| Subsystem — Persistência | `PostgresOrderRepository` (via `OrderRepositoryProtocol`) | `src/order/infrastructure/order_repository.py` |
| Client | rotas FastAPI (`place_order`, `get_order`) | `src/main.py` |

A `OrderFacade` não conhece PostgreSQL, boto3/SQS ou qualquer detalhe de
infraestrutura — ela depende apenas das abstrações (`Protocol`) declaradas em
`src/order/domain/interfaces.py`. Quem decide quais implementações concretas
usar é a composição root (`build_facade()` em `src/main.py`), seguindo
Dependency Inversion.

## Diagrama UML (ASCII)

```
                         Cliente (rotas FastAPI em src/main.py)
                                       |
                                       | usa apenas
                                       v
                         +---------------------------+
                         |        OrderFacade         |
                         |-----------------------------|
                         | + place_order(cart,         |
                         |     customer, payment)      |
                         | + get_order(order_id)        |
                         |-----------------------------|
                         | - _ensure_stock_available()  |
                         | - _rollback_reservations()   |
                         +---------------------------+
                  orquestra (composição via injeção no construtor)
        ___________________|____________________________________________
       |              |               |                |                |
       v              v               v                v                v
+--------------+ +-----------+ +--------------+ +----------------+ +----------------+
| Inventory    | | Payment   | | Shipping     | | Notification   | | OrderRepository|
| Service      | | Service   | | Service      | | Service        | | (Protocol)     |
| (Protocol)   | | (Protocol)| | (Protocol)   | | (Protocol)     | |                |
+--------------+ +-----------+ +--------------+ +----------------+ +----------------+
       ^               ^              ^                  ^                 ^
       |               |              |                  |                 |
+--------------+ +-----------+ +--------------+ +----------------+ +----------------+
| Postgres     | | Mock      | | Mock         | | SQS            | | Postgres       |
| Inventory    | | Payment   | | Shipping     | | Notification   | | Order          |
| Service      | | Service   | | Service      | | Service        | | Repository     |
| (PostgreSQL) | |           | |              | | (AWS SQS)      | | (PostgreSQL)   |
+--------------+ +-----------+ +--------------+ +----------------+ +----------------+

Fluxo de place_order():
  1. check_availability()       -> InventoryService
  2. reserve_stock()            -> InventoryService
  3. calculate_shipping()       -> ShippingService
  4. Order.create() + save()    -> OrderRepository
  5. charge()                   -> PaymentService
  6. generate_label()           -> ShippingService
  7. confirm() + update()       -> OrderRepository
  8. send_order_confirmation()  -> NotificationService
     (rollback automático de estoque/pedido em caso de falha em
      qualquer etapa — ver OrderFacade.place_order)
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** cada subsistema tem exatamente uma
  responsabilidade (`PostgresInventoryService` só lida com estoque,
  `SQSNotificationService` só lida com notificação, etc.). A `OrderFacade`
  também tem uma única responsabilidade — **orquestrar** a sequência de
  chamadas aos subsistemas e o rollback em caso de falha — sem conter lógica
  de persistência, pagamento ou estoque. Isso é o próprio motivo de existir
  do Facade: reduzir o acoplamento entre o cliente (rota HTTP) e os múltiplos
  subsistemas, sem violar SRP ao empilhar responsabilidades não relacionadas
  em uma única classe.
- **O — Open/Closed:** novas implementações de subsistema (ex.: trocar
  `MockPaymentService` por `StripePaymentService`, ou `SQSNotificationService`
  por uma implementação via Kafka) só exigem uma nova classe que satisfaça o
  `Protocol` correspondente e ser injetada em `build_facade()` — a
  `OrderFacade` e as rotas FastAPI não precisam ser modificadas.
- **L — Liskov Substitution:** qualquer implementação de
  `InventoryServiceProtocol`, `PaymentServiceProtocol`, etc. pode substituir
  outra sem surpresas — todas seguem o mesmo contrato (mesmas assinaturas,
  mesmas exceções de domínio como `InsufficientStockError`/
  `PaymentDeclinedError`, nunca exceções de infraestrutura como erros do
  psycopg2 ou do boto3 vazando para o chamador).
- **I — Interface Segregation:** os `Protocol`s em
  `src/order/domain/interfaces.py` são pequenos e focados (2–4 métodos cada),
  um por subsistema. A `OrderFacade` depende de cinco interfaces enxutas em
  vez de uma única interface "Deus" que misturaria estoque, pagamento, frete,
  notificação e persistência.
- **D — Dependency Inversion:** a `OrderFacade` recebe todos os subsistemas
  via construtor, tipados pelos `Protocol`s — nunca instancia
  `PostgresInventoryService` ou `SQSNotificationService` diretamente. A única
  classe que conhece as implementações concretas é a composição root
  (`build_facade()` em `src/main.py`), o que torna a `OrderFacade` 100%
  testável com mocks (ver `tests/unit/test_order_facade.py`).

## Estrutura do Projeto

```
facade/p1/
├── src/
│   ├── main.py                          ← FastAPI app, rotas, composição root
│   └── order/
│       ├── domain/
│       │   ├── entities.py              ← Cart, Order, Customer, ShippingLabel, etc.
│       │   ├── exceptions.py            ← InsufficientStockError, PaymentDeclinedError, etc.
│       │   └── interfaces.py            ← Protocols dos 5 subsistemas
│       ├── application/
│       │   └── facade.py                ← OrderFacade (o pattern em si)
│       └── infrastructure/
│           ├── database.py              ← engine/session SQLAlchemy + criação de tabelas
│           ├── inventory_service.py      ← PostgresInventoryService
│           ├── payment_service.py        ← MockPaymentService
│           ├── shipping_service.py       ← MockShippingService
│           ├── notification_service.py   ← SQSNotificationService
│           └── order_repository.py       ← PostgresOrderRepository
├── tests/
│   ├── conftest.py                      ← fixtures (TestClient + SQLite + moto SQS)
│   ├── unit/
│   │   └── test_order_facade.py         ← OrderFacade com todos os subsistemas mockados
│   └── integration/
│       └── test_api.py                  ← fluxo HTTP completo via TestClient
├── scripts/
│   └── init-localstack.sh               ← cria a fila SQS "orders" no LocalStack
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

A API estará disponível em `http://localhost:8000`.

### Endpoints

```bash
# Criar um pedido
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
    "customer_name": "Jane Doe",
    "customer_email": "jane@example.com",
    "customer_address": "123 Main St",
    "items": [
      {"product_id": "PROD001", "quantity": 2, "unit_price": 29.99, "product_name": "Widget Pro"}
    ],
    "card_token": "tok_test_123",
    "card_last_four": "4242",
    "card_brand": "Visa"
  }'

# Consultar um pedido
curl http://localhost:8000/orders/<order_id>

# Health check
curl http://localhost:8000/health
```

> **Dica de teste manual:** use `card_last_four: "0000"` para simular um
> pagamento recusado (`MockPaymentService` declina cartões terminados em
> `0000`), ou peça uma `quantity` maior que o estoque disponível
> (`PROD001`: 100, `PROD002`: 50, `PROD003`: 25) para simular estoque
> insuficiente.

## Rodar os Testes

```bash
# Testes unitários (OrderFacade com subsistemas mockados, sem I/O)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (via TestClient + SQLite in-memory + moto SQS)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

> **Decisão de teste:** os testes de integração usam SQLite (arquivo
> temporário, não PostgreSQL real) e moto para mockar o AWS SQS em memória,
> em vez de depender do `docker-compose up`. Isso é possível porque
> `infrastructure/database.py` evita SQL específico do PostgreSQL (sem
> `JSONB`, sem `ON CONFLICT`) e usa apenas recursos portáveis do SQLAlchemy
> Core. Essa escolha está documentada em `tests/conftest.py`.

## Verificar Qualidade do Código

```bash
pip install -e ".[dev]"
black src/ tests/
ruff check src/ tests/
mypy src/ --strict
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `POSTGRES_USER` | Usuário do banco PostgreSQL | `app` |
| `POSTGRES_PASSWORD` | Senha do banco PostgreSQL | `secret` |
| `POSTGRES_DB` | Nome do banco PostgreSQL | `appdb` |
| `DATABASE_URL` | URL de conexão SQLAlchemy | `postgresql://app:secret@db:5432/appdb` |
| `SQS_QUEUE_URL` | URL completa da fila SQS de notificações | `http://localstack:4566/000000000000/orders` |
| `AWS_ENDPOINT_URL` | Endpoint do SQS (LocalStack em dev; vazio para AWS real) | `http://localstack:4566` |
| `AWS_DEFAULT_REGION` | Região AWS | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Credencial (fake, aceita pelo LocalStack) | `test` |
| `AWS_SECRET_ACCESS_KEY` | Credencial (fake, aceita pelo LocalStack) | `test` |
