# Lazy DB Proxy — Virtual Proxy Pattern

> **Design Pattern:** Proxy (Virtual Proxy) | **Categoria:** Structural
> **Framework:** FastAPI | **Serviços:** PostgreSQL

## Objetivo Pedagógico

Demonstrar o padrão Proxy controlando o acesso a recursos caros: cada grupo de
dados de usuário (perfil, avatar, documentos, analytics) só é carregado do
PostgreSQL na primeira vez que é efetivamente acessado, e fica em cache para
acessos subsequentes — sem o cliente saber se está falando com o Proxy ou com
o serviço real.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Subject (interface) | `UserProfileService` (Protocol) | `domain/interfaces.py` |
| RealSubject | `PostgresUserProfileService` | `infrastructure/real_subject.py` |
| Proxy | `LazyUserProfileProxy` | `infrastructure/proxy.py` |
| Client | use cases + rotas FastAPI | `application/use_cases.py`, `main.py` |

## Diagrama UML (ASCII)

```
<<Protocol>>
UserProfileService (Subject)
  + get_profile(user_id) -> UserProfile
  + get_avatar(user_id) -> UserAvatar
  + get_documents(user_id) -> list[UserDocument]
  + get_analytics(user_id) -> UserAnalytics
        ▲                              ▲
        │ implements                  │ implements
        │                              │
PostgresUserProfileService      LazyUserProfileProxy
  (RealSubject — queries reais)   (Proxy — cache por user_id, delega ao RealSubject)
```

## Por que o Client nunca sabe se fala com o Proxy ou o RealSubject

`GetUserProfileUseCase` e as rotas FastAPI recebem `UserProfileService`
(o Protocol) via injeção de dependência — nunca importam
`PostgresUserProfileService` nem `LazyUserProfileProxy` diretamente. Trocar
o Proxy por uma chamada direta ao RealSubject (ou vice-versa) não exige
nenhuma alteração no código cliente — exatamente o contrato que LSP exige.

## Princípios SOLID Demonstrados

- **D — Dependency Inversion:** `LazyUserProfileProxy.__init__` recebe
  `UserProfileService` (a abstração), não `PostgresUserProfileService` (a
  implementação concreta) — pode envolver qualquer implementação do Subject.
- **L — Liskov Substitution:** `LazyUserProfileProxy` e
  `PostgresUserProfileService` são substituíveis em qualquer lugar que espera
  `UserProfileService`, sem surpresas de comportamento.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000/docs`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/users/{id}/profile` | Perfil básico (lazy-loaded) |
| GET | `/users/{id}/avatar` | Avatar binário (lazy-loaded) |
| GET | `/users/{id}/documents` | Documentos do usuário (lazy-loaded) |
| GET | `/users/{id}/analytics` | Analytics agregado, query pesada (lazy-loaded) |
| GET | `/profile/load-stats` | Estatísticas de cache hits vs. loads reais |

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente:

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes unitários usam um `FakeUserProfileService` em memória implementando
o mesmo Protocol — sem qualquer dependência de PostgreSQL real. Os testes de
integração usam o `TestClient` do FastAPI com `asyncpg.create_pool`
mockado no startup e `dependency_overrides` para substituir o Proxy real por
um Proxy de teste, exercitando o fluxo HTTP → use case → Proxy de ponta a
ponta sem precisar de banco de dados.
