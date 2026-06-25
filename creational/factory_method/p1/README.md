# Payment Gateway Factory

> **Design Pattern:** Factory Method
> **Categoria:** Creational
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Demonstra o Factory Method em um contexto real de gateway de pagamentos. O aluno verá como adicionar um novo provedor (ex: Boleto) criando apenas um novo par Creator/Product, sem tocar no código existente — aplicando OCP e DIP de forma prática.

## O Pattern em Ação

| Papel do Pattern   | Classe                    | Arquivo                                  |
|--------------------|---------------------------|------------------------------------------|
| Creator (abstrato) | `PaymentGatewayCreator`   | `src/payment/domain/interfaces.py`       |
| Product (Protocol) | `PaymentProcessor`        | `src/payment/domain/interfaces.py`       |
| ConcreteCreator    | `StripeGatewayCreator`    | `src/payment/infrastructure/creators.py` |
| ConcreteCreator    | `PayPalGatewayCreator`    | `src/payment/infrastructure/creators.py` |
| ConcreteCreator    | `PIXGatewayCreator`       | `src/payment/infrastructure/creators.py` |
| ConcreteProduct    | `StripePaymentProcessor`  | `src/payment/infrastructure/creators.py` |
| ConcreteProduct    | `PayPalPaymentProcessor`  | `src/payment/infrastructure/creators.py` |
| ConcreteProduct    | `PIXPaymentProcessor`     | `src/payment/infrastructure/creators.py` |

## Diagrama UML

```
<<abstract>>
PaymentGatewayCreator
+ create_payment_processor() -> PaymentProcessor  (factory method)
+ get_gateway_name() -> str
        |
        |-- StripeGatewayCreator
        |     + create_payment_processor() -> StripePaymentProcessor
        |
        |-- PayPalGatewayCreator
        |     + create_payment_processor() -> PayPalPaymentProcessor
        |
        +-- PIXGatewayCreator
              + create_payment_processor() -> PIXPaymentProcessor

<<Protocol>>
PaymentProcessor
+ process(request: PaymentRequest) -> PaymentResult
+ refund(transaction_id: str, amount: float) -> PaymentResult
        |
        |-- StripePaymentProcessor
        |-- PayPalPaymentProcessor
        +-- PIXPaymentProcessor
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Adicionar o gateway Boleto = criar `BoletoPaymentProcessor` + `BoletoGatewayCreator` + registrar em `GATEWAY_REGISTRY`. Zero modificações em `PaymentGatewayCreator`, use cases ou rotas.
- **D — Dependency Inversion:** `ProcessPaymentUseCase` recebe `PaymentGatewayCreator` (abstração) via construtor. A composição acontece em `main.py`, nunca dentro do use case.
- **S — Single Responsibility:** Creator cria processadores. Use case orquestra o fluxo. Repository persiste dados. Cada classe tem um único motivo para mudar.

## Estrutura do Projeto

```
p1/
├── src/payment/
│   ├── domain/
│   │   ├── interfaces.py    <- Creator ABC + Product Protocol
│   │   ├── entities.py      <- PaymentRequest, PaymentResult, Transaction
│   │   └── repositories.py  <- TransactionRepository Protocol
│   ├── application/
│   │   └── use_cases.py     <- ProcessPayment, GetTransaction, ListGateways
│   └── infrastructure/
│       ├── creators.py      <- ConcreteCreators + ConcreteProducts
│       ├── database.py      <- SQLAlchemy 2.0 engine + ORM
│       └── repositories.py  <- PostgresTransactionRepository
├── tests/
│   ├── conftest.py
│   ├── unit/test_factory.py
│   └── integration/test_integration.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir todos os serviços
docker-compose up --build

# 3. Acessar a documentação interativa
# http://localhost:8000/docs
```

## Rotas Disponíveis

| Método | Rota                           | Descrição                        |
|--------|-------------------------------|----------------------------------|
| POST   | `/payments/{gateway}`          | Processar pagamento via gateway  |
| GET    | `/payments/{transaction_id}`   | Buscar transação por ID          |
| GET    | `/payments/gateways`           | Listar gateways disponíveis      |

## Exemplo de Uso

```bash
# Processar pagamento via Stripe
curl -X POST http://localhost:8000/payments/stripe \
  -H "Content-Type: application/json" \
  -d '{"amount": 99.99, "currency": "USD", "metadata": {"order_id": "ORD-001"}}'

# Processar via PIX
curl -X POST http://localhost:8000/payments/pix \
  -H "Content-Type: application/json" \
  -d '{"amount": 150.00, "currency": "BRL"}'

# Listar gateways
curl http://localhost:8000/payments/gateways
```

## Rodar os Testes

```bash
# Testes unitários
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração
docker-compose run --rm app pytest tests/integration/ -v

# Todos com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável        | Descrição                     | Valor padrão                                    |
|-----------------|-------------------------------|-------------------------------------------------|
| `DATABASE_URL`  | URL de conexão PostgreSQL     | `postgresql://app:secret@db:5432/paymentdb`     |
| `POSTGRES_USER` | Usuário do banco              | `app`                                           |
| `POSTGRES_PASSWORD` | Senha do banco            | `secret`                                        |
| `POSTGRES_DB`   | Nome do banco                 | `paymentdb`                                     |
