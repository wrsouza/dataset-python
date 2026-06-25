# Template de README — Copiar para cada projeto

> Substituir todos os campos `<...>` antes de finalizar o projeto.

---

# <Nome do Projeto>

> **Design Pattern:** <Pattern Name>
> **Categoria:** <Creational | Structural | Behavioral>
> **Framework:** <FastAPI | Flask | Django | Streamlit | CLI Typer | gRPC>
> **Serviços:** <PostgreSQL | Redis | Kafka | AWS S3 | ...>

## Objetivo Pedagógico

<Explicação em 2-3 linhas do que o aluno aprenderá com este projeto.
Ex: "Este projeto demonstra o padrão Factory Method em um gateway de pagamentos real,
mostrando como adicionar novos provedores (Stripe, PIX, PayPal) sem modificar o código
existente, aplicando o princípio Open/Closed.">

## O Pattern em Ação

<Descrever onde e como o pattern aparece no projeto.
- Identificar: Creator, ConcreteCreator, Product, ConcreteProduct (ou equivalentes)
- Apontar os arquivos onde cada papel do pattern é implementado>

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Creator (abstrato) | `PaymentGateway` | `src/domain/interfaces.py` |
| ConcreteCreator | `StripeGateway` | `src/infrastructure/stripe.py` |
| Product | `PaymentResult` | `src/domain/entities.py` |

## Diagrama UML

```
<<abstract>>
PaymentGateway
+ create_charge(amount: float): PaymentResult
        |
        ├── StripeGateway
        │     + create_charge(amount: float): PaymentResult
        │
        ├── PayPalGateway
        │     + create_charge(amount: float): PaymentResult
        │
        └── PIXGateway
              + create_charge(amount: float): PaymentResult
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Novos provedores são adicionados criando novas subclasses em
  `src/infrastructure/`, sem alterar `PaymentGateway` ou os use cases.
- **D — Dependency Inversion:** `ProcessPaymentUseCase` depende de `PaymentGateway`
  (abstração), não de `StripeGateway` (implementação concreta).

## Estrutura do Projeto

```
<pattern>/p<N>/
├── src/
│   └── <domain>/
│       ├── domain/
│       │   ├── interfaces.py    ← ABCs e Protocols
│       │   └── entities.py      ← dataclasses
│       ├── application/
│       │   └── use_cases.py     ← lógica com o pattern
│       └── infrastructure/
│           └── <adapters>.py    ← implementações concretas
├── tests/
│   ├── unit/
│   └── integration/
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
# Streamlit: http://localhost:8501
# Django: http://localhost:8000/admin
```

## Rodar os Testes

```bash
# Testes unitários (sem serviços externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (com serviços externos)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Verificar Qualidade do Código

```bash
# Dentro do container ou com venv ativo
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `DATABASE_URL` | URL de conexão PostgreSQL | `postgresql://app:secret@db:5432/appdb` |
| `...` | ... | ... |
