# Authentication Strategy (Strategy) — P3

API Django que autentica usuários através de mecanismos
intercambiáveis (senha, token de API, OAuth) escolhidos pela rota
chamada, sem nenhum serviço externo (PLAN.md não especifica BD para
este projeto — usa SQLite).

## Objetivo pedagógico

Demonstrar o pattern **Strategy**: `Authenticator` (Context) não sabe
nada sobre como validar credenciais — delega para a
`AuthenticationStrategy` configurada. Adicionar um novo mecanismo (ex.:
"magic link") é só uma nova classe, sem tocar no Context nem nas
demais estratégias.

Elementos do pattern:
- **Context:** `Authenticator` (`application/context.py`)
- **Strategy (abstrato):** `AuthenticationStrategy` (`domain/interfaces.py`)
- **Concrete Strategies:** `PasswordAuthStrategy`, `TokenAuthStrategy`, `OAuthStrategy` (`infrastructure/strategies/`)

## Diagrama (ASCII)

```
POST /auth/password/ {"username": "...", "password": "..."}
        │
        ▼
get_strategy("password") ──► PasswordAuthStrategy
        │
        ▼
Authenticator.authenticate() ──► strategy.authenticate() ──► AuthResult
        │
        ▼
DjangoAuthAttemptLogRepository.append() (log de toda tentativa, sucesso ou não)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                       | Descrição                                          |
|--------|-----------------------------|------------------------------------------------------|
| POST   | `/auth/password/`           | Autentica com usuário/senha                           |
| POST   | `/auth/token/`               | Autentica com um token de API estático                |
| POST   | `/auth/oauth/`                | Resolve uma identidade OAuth já verificada pelo provedor |
| GET    | `/auth/attempts/`            | Lista todas as tentativas de autenticação registradas |

```bash
curl -X POST http://localhost:8000/auth/password/ \
  -H "Content-Type: application/json" \
  -d '{"username": "ana", "password": "s3cret"}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada estratégia concreta só sabe validar seu próprio tipo de credencial; `DjangoAuthAttemptLogRepository` só persiste/recupera o log.
- **OCP:** um novo mecanismo de autenticação é uma nova classe `AuthenticationStrategy` mais uma entrada em `_STRATEGY_MAP` — sem tocar nas estratégias existentes.
- **LSP:** qualquer `AuthenticationStrategy` concreta pode substituir outra em `Authenticator` sem quebrar o contrato — todas retornam `AuthResult`.
- **ISP:** `AuthenticationStrategy` expõe só os dois métodos que o Context realmente precisa (`authenticate`, `get_name`).
- **DIP:** `Authenticator` e os use cases dependem de `AuthenticationStrategy`/`DjangoAuthAttemptLogRepository` (abstrações), nunca das classes concretas diretamente.
