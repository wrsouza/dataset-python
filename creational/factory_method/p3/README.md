# Auth Provider Factory — Factory Method Pattern

> **Design Pattern:** Factory Method | **Categoria:** Creational
> **Framework:** Django | **Serviços:** Nenhum externo real (SQLite/sem DB; OAuth simulado em memória)

## Objetivo Pedagógico

Demonstra o padrão Factory Method aplicado à criação de provedores de
autenticação. O aluno aprende como um `Creator` abstrato delega a decisão de
"qual produto criar" para subclasses (`ConcreteCreator`), permitindo adicionar
novos esquemas de login (email/senha, OAuth Google, OAuth GitHub, API Key)
sem alterar o código que já consome a fábrica.

## O Pattern Aplicado

Cada esquema de autenticação tem um par `ConcreteCreator` + `ConcreteProduct`:

| ConcreteCreator             | ConcreteProduct (AuthProvider) | Esquema        |
|------------------------------|----------------------------------|----------------|
| `EmailPasswordAuthFactory`   | `EmailPasswordAuthProvider`      | `email_password` |
| `OAuthGoogleAuthFactory`     | `OAuthGoogleAuthProvider`        | `oauth_google`   |
| `OAuthGithubAuthFactory`     | `OAuthGithubAuthProvider`        | `oauth_github`   |
| `APIKeyAuthFactory`          | `APIKeyAuthProvider`             | `api_key`        |

Os providers OAuth **não fazem chamadas reais** ao Google/GitHub — eles
simulam o intercâmbio do `auth_code` por uma identidade, usando dicionários
em memória (`GOOGLE_ACCOUNTS`, `GITHUB_ACCOUNTS`) como "diretório de
identidade" mockado. O foco pedagógico é o pattern, não o protocolo OAuth2.

As Use Cases (`LoginUseCase`, `ValidateTokenUseCase`, `LogoutUseCase`) nunca
instanciam um provider concreto: elas recebem um `AuthProviderFactory`
(abstração) no construtor e chamam `factory.create_provider()` — esse é o
**factory method**.

## Diagrama UML (ASCII)

```
                  <<Protocol>>
                  AuthProvider
        + authenticate(credentials) -> user_id
        + issue_token(user_id) -> token
        + validate_token(token) -> user_id
        + revoke(token) -> None
                       ^
                       | implements
   ┌──────────────────┬──────────────────┬──────────────────┐
   |                  |                  |                  |
EmailPassword   OAuthGoogleAuth   OAuthGithubAuth      APIKeyAuth
AuthProvider      Provider           Provider          Provider


            AuthProviderFactory (Creator, ABC)
        + create_provider(): AuthProvider   <-- factory method (abstract)
        + get_scheme_name(): str            <-- template method (concreto)
                       ^
                       | extends
   ┌──────────────────┬──────────────────┬──────────────────┐
   |                  |                  |                  |
EmailPasswordAuth  OAuthGoogleAuth   OAuthGithubAuth    APIKeyAuth
   Factory            Factory           Factory           Factory
+create_provider()  +create_provider() +create_provider() +create_provider()
  -> EmailPassword     -> OAuthGoogle     -> OAuthGithub    -> APIKeyAuth
     AuthProvider()       AuthProvider()     AuthProvider()    Provider()


Client (LoginUseCase / ValidateTokenUseCase / LogoutUseCase)
   depende apenas de AuthProviderFactory (abstração) — DIP
```

## Como o Cliente Usa a Fábrica

```python
factory = SCHEME_REGISTRY["oauth_google"]   # AuthProviderFactory concreto
use_case = LoginUseCase(factory)
result = use_case.execute({"auth_code": "google-oauth-code-alice"})
# result.scheme == "OAuthGoogle"
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Para adicionar um novo esquema (ex.: `OAuthMicrosoftAuthFactory`),
  basta criar uma nova subclasse de `AuthProviderFactory` e registrá-la em
  `SCHEME_REGISTRY` — nenhuma classe existente (`LoginUseCase`, views, outras
  factories) precisa ser modificada. Ver `src/auth/infrastructure/creators.py`.
- **D — Dependency Inversion:** `LoginUseCase`, `ValidateTokenUseCase` e
  `LogoutUseCase` (em `src/auth/application/use_cases.py`) dependem apenas da
  abstração `AuthProviderFactory` (definida em `domain/interfaces.py`), nunca
  de uma implementação concreta. A escolha do provider concreto é feita na
  borda do sistema (views, via `get_factory(scheme)`), não dentro da lógica
  de negócio.
- **L — Liskov Substitution:** Todos os `ConcreteProduct` (`EmailPasswordAuthProvider`,
  `OAuthGoogleAuthProvider`, `OAuthGithubAuthProvider`, `APIKeyAuthProvider`)
  respeitam o mesmo contrato do `AuthProvider` Protocol — sempre retornam
  `str` e lançam apenas `AuthenticationError`/`InvalidTokenError` (exceções de
  domínio), nunca exceções específicas de uma integração.

## Estrutura do Projeto

```
p3/
├── src/
│   ├── manage.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── auth/
│       ├── domain/
│       │   ├── entities.py       <- AuthToken, AuthResult, exceções de domínio
│       │   └── interfaces.py     <- AuthProvider (Protocol) + AuthProviderFactory (Creator ABC)
│       ├── application/
│       │   └── use_cases.py      <- LoginUseCase, ValidateTokenUseCase, LogoutUseCase
│       ├── infrastructure/
│       │   └── creators.py       <- 4 ConcreteCreators + 4 ConcreteProducts + SCHEME_REGISTRY
│       └── views/
│           └── api.py            <- login, validate, logout (Django views)
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_factory.py       <- Factory Method: Creator -> Product, mocks de OAuth
│   │   └── test_use_cases.py     <- Use cases injetando cada ConcreteCreator
│   └── integration/
│       └── test_api.py          <- endpoints Django via test client
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Endpoints da API

| Método | URL                          | Descrição                                  |
|--------|------------------------------|---------------------------------------------|
| POST   | `/auth/<scheme>/login`       | Autentica e emite token                     |
| POST   | `/auth/<scheme>/validate`    | Valida um token e retorna o `user_id`       |
| POST   | `/auth/<scheme>/logout`      | Revoga um token                             |

`<scheme>` é um de: `email_password`, `oauth_google`, `oauth_github`, `api_key`.

### Exemplo

```bash
curl -X POST http://localhost:8000/auth/email_password/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

## Banco de Dados — Decisão

Este projeto **não usa banco de dados** (`DATABASES = {}` em `settings.py`).
Todos os "stores" (usuários, contas OAuth simuladas, API keys) são
dicionários em memória dentro de `infrastructure/creators.py`, suficientes
para o objetivo pedagógico de demonstrar o Factory Method. Por isso o
`docker-compose.yml` define apenas o serviço `app`, sem PostgreSQL.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API disponível em http://localhost:8000/auth/<scheme>/login
```

### Localmente (sem Docker)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
$env:DJANGO_SETTINGS_MODULE = "settings"
$env:PYTHONPATH = "src"
python src/manage.py runserver 0.0.0.0:8000
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/ -v
```

Ou localmente:

```bash
pytest --cov=src --cov-report=term-missing
```

## Pré-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Variáveis de Ambiente

| Variável                     | Descrição                                  | Padrão                       |
|-------------------------------|---------------------------------------------|-------------------------------|
| `DJANGO_SECRET_KEY`           | Chave secreta Django                        | dev-only (mude!)             |
| `DJANGO_DEBUG`                 | Modo debug                                  | `true`                        |
| `ALLOWED_HOSTS`                | Hosts permitidos                            | `localhost,127.0.0.1`         |
| `JWT_SECRET`                   | Segredo reservado para uso futuro com JWT   | dev-only (mude!)              |
| `OAUTH_GOOGLE_CLIENT_ID`       | Mockado — não usado em chamadas reais       | `mock-google-client-id`       |
| `OAUTH_GOOGLE_CLIENT_SECRET`   | Mockado — não usado em chamadas reais       | `mock-google-client-secret`   |
| `OAUTH_GITHUB_CLIENT_ID`       | Mockado — não usado em chamadas reais       | `mock-github-client-id`       |
| `OAUTH_GITHUB_CLIENT_SECRET`   | Mockado — não usado em chamadas reais       | `mock-github-client-secret`   |
