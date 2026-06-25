# Request Validation Chain

> **Design Pattern:** Chain of Responsibility
> **Categoria:** Behavioral
> **Framework:** FastAPI
> **Serviços:** Nenhum serviço externo obrigatório (validação em memória)

## Objetivo Pedagógico

Este projeto demonstra o padrão Chain of Responsibility numa pipeline de
validação de requisições HTTP. O aluno aprenderá como decompor validações
independentes (rate limit, autenticação, autorização, schema) em handlers
encadeados, onde cada um decide processar a requisição ou delegá-la ao
próximo, sem que o chamador precise conhecer a ordem ou a quantidade de
handlers existentes.

## O Pattern em Ação

A requisição `POST /orders` percorre uma corrente de handlers montada em
`src/main.py` (composition root). Cada handler tem uma única responsabilidade
e decide entre **interromper a corrente** (retornando um `APIResponse`) ou
**delegar ao próximo** (retornando `None` e chamando `self._pass_to_next`).

| Papel do Pattern        | Classe                      | Arquivo |
|--------------------------|------------------------------|---------|
| Handler (abstrato)       | `RequestHandler`             | `src/validation/domain/interfaces.py` |
| ConcreteHandler           | `RateLimitHandler`           | `src/validation/infrastructure/handlers/rate_limit.py` |
| ConcreteHandler           | `JWTAuthHandler`             | `src/validation/infrastructure/handlers/jwt_auth.py` |
| ConcreteHandler           | `RoleAuthorizationHandler`   | `src/validation/infrastructure/handlers/role_authorization.py` |
| ConcreteHandler           | `SchemaValidationHandler`    | `src/validation/infrastructure/handlers/schema_validation.py` |
| Request/Response (Product)| `APIRequest`, `APIResponse` | `src/validation/domain/entities.py` |
| Client (monta a corrente) | `build_default_chain`        | `src/validation/application/validate_request_use_case.py` |
| Invoker                   | `ValidateRequestUseCase`     | `src/validation/application/validate_request_use_case.py` |

## Diagrama UML (ASCII)

```
        <<abstract>>
        RequestHandler
        --------------------------------
        - _next_handler: RequestHandler | None
        --------------------------------
        + set_next(handler): RequestHandler
        + handle(request): APIResponse | None
        # _pass_to_next(request): APIResponse | None
                 |
                 |  (cada subclasse implementa handle())
                 |
   ┌─────────────┼──────────────┬───────────────────┐
   │             │              │                   │
RateLimitHandler  JWTAuthHandler RoleAuthorizationHandler SchemaValidationHandler
   │             │              │                   │
   └──── set_next encadeia a ordem em build_default_chain() ────┘

Fluxo de uma requisição POST /orders:

  APIRequest
      │
      ▼
 [RateLimitHandler] ──(excedeu limite)──> APIResponse 429
      │ (ok)
      ▼
 [JWTAuthHandler] ──(token inválido/ausente)──> APIResponse 401
      │ (ok, enriquece request.user_id / user_role)
      ▼
 [RoleAuthorizationHandler] ──(role insuficiente)──> APIResponse 403
      │ (ok)
      ▼
 [SchemaValidationHandler] ──(body inválido)──> APIResponse 422
      │ (ok)
      ▼
 APIResponse 200 (sucesso — fim da corrente)
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** `RequestHandler` é uma ABC fechada para modificação.
  Adicionar um novo handler (ex.: `IdempotencyKeyHandler`) significa apenas
  criar uma nova classe em `infrastructure/handlers/` e incluí-la na chamada
  de `build_default_chain(...)` em `src/main.py` — nenhum handler existente
  precisa ser alterado. O `RequestHandler.handle()` abstrato garante que o
  contrato é respeitado por toda extensão futura.
- **D — Dependency Inversion:** `ValidateRequestUseCase` depende apenas da
  abstração `RequestHandler` (recebida via construtor), nunca de uma classe
  concreta. `RateLimitHandler` também recebe seu `_SlidingWindowCounter` via
  injeção, permitindo substituí-lo por uma implementação Redis sem alterar o
  handler.
- **S — Single Responsibility:** cada handler cuida de exatamente uma
  preocupação (limite de taxa, autenticação, autorização, schema). Nenhum
  deles "valida e loga e notifica".
- **L — Liskov Substitution:** todas as subclasses de `RequestHandler`
  retornam `APIResponse | None` e nunca lançam exceções que a base não
  declare — qualquer handler pode substituir outro na corrente sem efeitos
  colaterais inesperados.
- **I — Interface Segregation:** `RequestHandler` expõe apenas dois métodos
  (`set_next`, `handle`), o mínimo necessário para participar da corrente.

## Estrutura do Projeto

```
chain_of_responsibility/p1/
├── src/
│   ├── main.py                          ← composition root (FastAPI)
│   └── validation/
│       ├── domain/
│       │   ├── interfaces.py            ← RequestHandler (ABC)
│       │   └── entities.py              ← APIRequest, APIResponse, UserRole
│       ├── application/
│       │   └── validate_request_use_case.py  ← monta e invoca a corrente
│       └── infrastructure/
│           └── handlers/
│               ├── rate_limit.py
│               ├── jwt_auth.py
│               ├── role_authorization.py
│               └── schema_validation.py
├── tests/
│   ├── conftest.py
│   ├── unit/        ← cada handler testado isoladamente (next mockado)
│   └── integration/ ← corrente completa via TestClient do FastAPI
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

# 2. Subir a aplicação
docker-compose up --build

# 3. Acessar a documentação interativa
# http://localhost:8000/docs
```

## Rodar os Testes

```bash
# Testes unitários (handlers isolados, sem nenhuma dependência externa)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (corrente completa via TestClient)
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
| `APP_HOST` | Host do servidor Uvicorn | `0.0.0.0` |
| `APP_PORT` | Porta do servidor Uvicorn | `8000` |
| `RATE_LIMIT_MAX_REQUESTS` | Limite de requisições por janela (referência; hardcoded no handler) | `10` |
| `RATE_LIMIT_WINDOW_SECONDS` | Duração da janela em segundos (referência; hardcoded no handler) | `60` |

## Exemplo de Requisição

```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer <header>.<payload-base64>.<assinatura>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod-1", "quantity": 2, "price": 19.9, "customer_id": "cust-1"}'
```

> **Nota:** o `JWTAuthHandler` usa um decodificador simplificado (base64,
> sem verificação de assinatura) apenas para fins didáticos. Em produção,
> use bibliotecas como `python-jose` ou `PyJWT` com verificação criptográfica
> real (RS256/HS256).
