# Order State Machine

> **Design Pattern:** State
> **Categoria:** Behavioral
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão **State** modelando o ciclo de vida de um pedido
(`Order`) como uma máquina de estados explícita. Cada estado (Pending, Paid,
Shipped, Delivered, Cancelled, RefundRequested, Refunded) é uma classe própria
que decide quais transições são válidas, eliminando condicionais `if state ==
"paid": ...` espalhados pelo código e tornando trivial adicionar novos estados.

## O Pattern em Ação

`Order` é o **Context**: não conhece regras de transição, apenas delega todo
comportamento ao objeto `_state` atual. `OrderState` é o **State** abstrato,
e cada estado concreto (`PendingState`, `PaidState`, etc.) implementa somente
as transições que permite — as demais usam o comportamento padrão da base, que
lança `InvalidTransitionError`.

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Context | `Order` | `src/orders/domain/entities.py` |
| State (abstrato) | `OrderState` | `src/orders/domain/interfaces.py` |
| ConcreteState | `PendingState` | `src/orders/infrastructure/states/pending.py` |
| ConcreteState | `PaidState` | `src/orders/infrastructure/states/paid.py` |
| ConcreteState | `ShippedState` | `src/orders/infrastructure/states/shipped.py` |
| ConcreteState | `DeliveredState` | `src/orders/infrastructure/states/delivered.py` |
| ConcreteState | `CancelledState` (terminal) | `src/orders/infrastructure/states/cancelled.py` |
| ConcreteState | `RefundRequestedState` | `src/orders/infrastructure/states/refund_requested.py` |
| ConcreteState | `RefundedState` (terminal) | `src/orders/infrastructure/states/refunded.py` |

## Diagrama UML (ASCII)

```
<<abstract>>
OrderState
+ pay(ctx: Order): void
+ ship(ctx: Order): void
+ deliver(ctx: Order): void
+ cancel(ctx: Order): void
+ request_refund(ctx: Order): void
+ process_refund(ctx: Order): void
+ get_name(): str
+ get_allowed_transitions(): list[str]
        |
        ├── PendingState        ── pay()──────────► PaidState
        │                       └─ cancel()───────► CancelledState
        │
        ├── PaidState           ── ship()─────────► ShippedState
        │                       └─ cancel()───────► CancelledState
        │
        ├── ShippedState        ── deliver()──────► DeliveredState
        │
        ├── DeliveredState      ── request_refund()► RefundRequestedState
        │
        ├── RefundRequestedState── process_refund()► RefundedState
        │
        ├── CancelledState      (terminal — nenhuma transição permitida)
        │
        └── RefundedState       (terminal — nenhuma transição permitida)
```

### Fluxo de transições

```
Pending ──pay──► Paid ──ship──► Shipped ──deliver──► Delivered ──request_refund──► RefundRequested ──process_refund──► Refunded
   │                │
   └──cancel──► Cancelled ◄──cancel──┘
```

`Order` (Context) delega chamadas como `order.pay()` para `self._state.pay(self)`.
O estado concreto decide se a transição é válida; se for, chama
`ctx.transition_to(NovoEstado(), "acao")`, que registra um
`StateTransitionRecord` no histórico e substitui `self._state`.

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Adicionar um novo estado (ex.: `OnHoldState`) exige
  apenas criar uma nova classe em `src/orders/infrastructure/states/` que
  estende `OrderState` e registrá-la em `STATE_MAP`
  (`src/orders/infrastructure/states/__init__.py`). Nenhum estado existente,
  nem `Order`, nem os use cases precisam ser modificados.
- **D — Dependency Inversion:** `CreateOrderUseCase` e `TransitionOrderUseCase`
  (`src/orders/application/use_cases.py`) dependem apenas de `OrderRepository`
  como abstração; a implementação concreta com SQLAlchemy/PostgreSQL é
  injetada via construtor a partir de `src/main.py` (composição root).
- **S — Single Responsibility:** `OrderRepository` cuida apenas de persistência
  e rehidratação; `Order` cuida apenas de delegar comportamento ao estado
  atual; cada `ConcreteState` cuida apenas das regras de transição daquele
  estado específico.
- **L — Liskov Substitution:** Qualquer `ConcreteState` pode substituir
  `OrderState` sem surpresas — todos lançam o mesmo `InvalidTransitionError`
  para transições não suportadas, e nenhum cliente faz `isinstance` para
  tratar um estado de forma especial.

## Estrutura do Projeto

```
state/p1/
├── src/
│   ├── main.py                          ← FastAPI app (composição root)
│   └── orders/
│       ├── domain/
│       │   ├── entities.py              ← Order (Context), OrderItem
│       │   └── interfaces.py            ← OrderState (abstrato), exceções
│       ├── application/
│       │   └── use_cases.py             ← CreateOrderUseCase, TransitionOrderUseCase
│       └── infrastructure/
│           ├── database.py              ← engine, sessão, modelos SQLAlchemy
│           ├── repository.py            ← OrderRepository (persistência)
│           └── states/                  ← ConcreteStates do pattern State
│               ├── pending.py
│               ├── paid.py
│               ├── shipped.py
│               ├── delivered.py
│               ├── cancelled.py
│               ├── refund_requested.py
│               └── refunded.py
├── tests/
│   ├── unit/test_order_states.py        ← transições válidas/inválidas, histórico
│   └── integration/test_api.py          ← fluxo via API com SQLite em memória
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
# FastAPI docs: http://localhost:8000/docs
```

## Rodar os Testes

```bash
# Testes unitários (sem serviços externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (SQLite em memória, não requer PostgreSQL)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Verificar Qualidade do Código

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `POSTGRES_USER` | Usuário do PostgreSQL | `app` |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | `secret` |
| `POSTGRES_DB` | Nome do banco de dados | `ordersdb` |
| `DATABASE_URL` | URL de conexão completa usada pela aplicação | `postgresql://app:secret@db:5432/ordersdb` |

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/orders` | Cria um novo pedido (estado inicial `Pending`) |
| `POST` | `/orders/{id}/pay` | Transição `pay` |
| `POST` | `/orders/{id}/ship` | Transição `ship` |
| `POST` | `/orders/{id}/deliver` | Transição `deliver` |
| `POST` | `/orders/{id}/cancel` | Transição `cancel` |
| `GET` | `/orders/{id}/state` | Estado atual e transições permitidas |
| `GET` | `/orders/{id}/history` | Histórico de transições do pedido |
