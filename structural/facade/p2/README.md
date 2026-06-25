# Payment Processing Facade

> **Design Pattern:** Facade
> **Categoria:** Structural
> **Framework:** Flask
> **Serviços:** Stripe (mockado), MySQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Facade simplificando o fluxo complexo de
processamento de um pagamento com cartão de crédito. Cobrar um cliente
envolve coordenar quatro etapas independentes — validação do cartão, chamada
à API do Stripe, persistência da transação em MySQL e envio de um recibo —
cada uma com suas próprias regras e exceções. A `PaymentFacade` esconde toda
essa orquestração atrás de poucos métodos (`process_payment`,
`get_transaction`, `refund_payment`), de forma que a camada HTTP (Flask) nunca
precisa conhecer Stripe ou SQL diretamente.

## O Pattern em Ação

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Facade | `PaymentFacade` | `src/payment/application/facade.py` |
| Subsystem — Validação de cartão | `LuhnCardValidator` (via `CardValidatorProtocol`) | `src/payment/infrastructure/card_validator.py` |
| Subsystem — Gateway de pagamento | `MockStripeGateway` / `StripePaymentGateway` (via `PaymentGatewayProtocol`) | `src/payment/infrastructure/stripe_gateway.py` |
| Subsystem — Persistência | `MySQLTransactionRepository` (via `TransactionRepositoryProtocol`) | `src/payment/infrastructure/transaction_repository.py` |
| Subsystem — Recibo | `EmailReceiptService` (via `ReceiptServiceProtocol`) | `src/payment/infrastructure/receipt_service.py` |
| Client | rotas Flask (`/payments`, `/payments/<id>`, `/payments/<id>/refund`) | `src/payment/main.py` |

A `PaymentFacade` não conhece o SDK do Stripe, PyMySQL ou qualquer detalhe de
infraestrutura — ela depende apenas das abstrações (`Protocol`) declaradas em
`src/payment/domain/interfaces.py`. Quem decide quais implementações
concretas usar é a composição root (`build_facade()` em
`src/payment/main.py`), seguindo Dependency Inversion. Em produção,
`USE_MOCK_STRIPE=false` troca `MockStripeGateway` por `StripePaymentGateway`
(real, via `stripe` SDK) sem qualquer mudança na Facade.

## Diagrama UML (ASCII)

```
                    Cliente (rotas Flask em src/payment/main.py)
                                       |
                                       | usa apenas
                                       v
                         +---------------------------+
                         |       PaymentFacade        |
                         |-----------------------------|
                         | + process_payment(customer, |
                         |     card, amount, currency)  |
                         | + get_transaction(id)        |
                         | + refund_payment(id)         |
                         +---------------------------+
                  orquestra (composição via injeção no construtor)
        ________________________|________________________________
       |                  |                   |                   |
       v                  v                   v                   v
+----------------+ +----------------+ +--------------------+ +----------------+
| CardValidator  | | PaymentGateway | | TransactionRepository| | ReceiptService |
| (Protocol)     | | (Protocol)     | | (Protocol)            | | (Protocol)     |
+----------------+ +----------------+ +--------------------+ +----------------+
       ^                  ^                    ^                    ^
       |                  |                    |                    |
+----------------+ +----------------+ +--------------------+ +----------------+
| LuhnCard       | | MockStripe /   | | MySQLTransaction      | | EmailReceipt   |
| Validator      | | StripePayment  | | Repository             | | Service        |
|                | | Gateway        | | (MySQL)                | |                |
+----------------+ +----------------+ +--------------------+ +----------------+

Fluxo de process_payment():
  1. validate()                  -> CardValidator   (sem rede; rejeita cedo)
  2. Transaction.create() + save()-> TransactionRepository (status PENDING)
  3. charge()                    -> PaymentGateway   (Stripe)
  4. approve()/decline() + update()-> TransactionRepository
  5. send_receipt()              -> ReceiptService   (apenas se aprovado)
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** cada subsistema tem exatamente uma
  responsabilidade (`LuhnCardValidator` só valida dados de cartão,
  `MySQLTransactionRepository` só persiste, `EmailReceiptService` só envia
  recibos). A `PaymentFacade` também tem uma única responsabilidade —
  **orquestrar** a sequência validação → cobrança → persistência → recibo —
  sem conter lógica de checksum de cartão, SQL ou chamadas HTTP ao Stripe.
- **O — Open/Closed:** trocar `MockStripeGateway` por `StripePaymentGateway`
  (ou futuramente um gateway PayPal) exige apenas uma nova classe que
  satisfaça `PaymentGatewayProtocol` e seja injetada em `build_facade()` — a
  `PaymentFacade` e as rotas Flask não são modificadas.
- **L — Liskov Substitution:** `MockStripeGateway` e `StripePaymentGateway`
  são intercambiáveis: ambas lançam `CardDeclinedError`/
  `PaymentProcessingError` (exceções de domínio) e nunca deixam escapar
  exceções específicas do SDK do Stripe ou de PyMySQL.
- **I — Interface Segregation:** os `Protocol`s em
  `src/payment/domain/interfaces.py` são pequenos (1–2 métodos cada), um por
  subsistema. A `PaymentFacade` depende de quatro interfaces enxutas em vez
  de uma única interface "Deus" misturando validação, cobrança, persistência
  e notificação.
- **D — Dependency Inversion:** a `PaymentFacade` recebe todos os
  subsistemas via construtor, tipados pelos `Protocol`s — nunca instancia
  `StripePaymentGateway` ou `MySQLTransactionRepository` diretamente. A única
  classe que conhece as implementações concretas é a composição root
  (`build_facade()` em `src/payment/main.py`), o que torna a `PaymentFacade`
  100% testável com mocks (ver `tests/unit/test_payment_facade.py`).

## Estrutura do Projeto

```
facade/p2/
├── src/
│   └── payment/
│       ├── main.py                          ← Flask app, rotas, composição root
│       ├── domain/
│       │   ├── entities.py                  ← CreditCard, Transaction, Receipt, etc.
│       │   ├── exceptions.py                ← InvalidCardError, CardDeclinedError, etc.
│       │   └── interfaces.py                ← Protocols dos 4 subsistemas
│       ├── application/
│       │   └── facade.py                    ← PaymentFacade (o pattern em si)
│       └── infrastructure/
│           ├── database.py                  ← engine/session SQLAlchemy + criação de tabela
│           ├── card_validator.py             ← LuhnCardValidator
│           ├── stripe_gateway.py             ← StripePaymentGateway + MockStripeGateway
│           ├── transaction_repository.py     ← MySQLTransactionRepository
│           └── receipt_service.py            ← EmailReceiptService
├── tests/
│   ├── conftest.py                          ← fixtures (FlaskClient + SQLite)
│   ├── unit/
│   │   ├── test_card_validator.py
│   │   ├── test_stripe_gateway.py
│   │   ├── test_receipt_service.py
│   │   ├── test_transaction_repository.py
│   │   └── test_payment_facade.py           ← PaymentFacade com todos os subsistemas mockados
│   └── integration/
│       └── test_api.py                      ← fluxo HTTP completo via FlaskClient
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
# Processar um pagamento
curl -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
    "customer_name": "Jane Doe",
    "customer_email": "jane@example.com",
    "card_number": "4242424242424242",
    "card_exp_month": 12,
    "card_exp_year": 2099,
    "card_cvc": "123",
    "amount_cents": 2500,
    "currency": "usd"
  }'

# Consultar uma transação
curl http://localhost:8000/payments/<transaction_id>

# Reembolsar uma transação aprovada
curl -X POST http://localhost:8000/payments/<transaction_id>/refund

# Health check
curl http://localhost:8000/health
```

> **Dica de teste manual:** use `card_number: "4000000000000002"` para
> simular um pagamento recusado (cartões terminados em `0002` são recusados
> por convenção do Stripe test mode e replicados em `MockStripeGateway`).

## Rodar os Testes

```bash
# Testes unitários (subsistemas isolados + PaymentFacade com mocks, sem I/O real)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (via FlaskClient + SQLite)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

> **Decisão de teste:** os testes usam SQLite (arquivo temporário, não MySQL
> real) e `MockStripeGateway` (`USE_MOCK_STRIPE=true`) em vez de depender do
> `docker-compose up`. Isso é possível porque `infrastructure/database.py`
> evita SQL específico do MySQL (sem `AUTO_INCREMENT`, sem
> `ON DUPLICATE KEY UPDATE`) e usa apenas recursos portáveis do SQLAlchemy
> Core. Essa escolha está documentada em `tests/conftest.py`, seguindo o
> mesmo padrão já usado em `facade/p1`.

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
| `MYSQL_USER` | Usuário do banco MySQL | `app` |
| `MYSQL_PASSWORD` | Senha do banco MySQL | `secret` |
| `MYSQL_DATABASE` | Nome do banco MySQL | `appdb` |
| `MYSQL_ROOT_PASSWORD` | Senha root do MySQL | `rootsecret` |
| `DATABASE_URL` | URL de conexão SQLAlchemy | `mysql+pymysql://app:secret@db:3306/appdb` |
| `USE_MOCK_STRIPE` | Usa `MockStripeGateway` em vez do SDK real do Stripe | `true` |
| `STRIPE_API_KEY` | Chave secreta de teste do Stripe (`sk_test_...`) | `sk_test_placeholder` |
| `FLASK_DEBUG` | Ativa modo debug do Flask | `false` |
