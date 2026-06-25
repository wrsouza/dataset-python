# Processo de Desenvolvimento — Design Patterns Dataset
> **Versão:** 1.0 | **Data:** 2026-06-20
> Guia de processo para todos os agentes e contribuidores deste dataset.

---

## 1. Filosofia do Projeto

Este dataset é **educacional**. Cada projeto deve ser:

1. **Legível antes de otimizado** — um aluno lendo pela primeira vez deve entender o pattern em 5 minutos.
2. **Realista** — não apenas "Animal.speak()", mas aplicações que poderiam existir em produção.
3. **Independente** — cada projeto em `pN/` roda sozinho com `docker-compose up`.
4. **Rastreável** — todo projeto reflete seu status em STATUS.md.

---

## 2. Workflow de Execução

### 2.1 Ciclo de vida de um projeto

```
PLAN.md define projeto
      ↓
STATUS.md atualizado para [~]
      ↓
Agente cria estrutura de pastas
      ↓
Agente implementa código (domain → application → infra)
      ↓
Agente escreve testes
      ↓
Agente adiciona Docker + configs
      ↓
Validação: pytest + ruff + mypy
      ↓
README.md escrito
      ↓
STATUS.md atualizado para [x]
```

### 2.2 Briefing padrão para cada agente especializado

Cada agente que construir um projeto recebe este template de briefing:

```
PATTERN:     <nome do pattern>
CATEGORIA:   <Creational | Structural | Behavioral>
PROJETO:     P<N> — <nome do projeto>
FRAMEWORK:   <FastAPI | Flask | Django | Streamlit | CLI Typer | gRPC>
SERVIÇOS:    <PostgreSQL | Redis | Kafka | etc.>
DIRETÓRIO:   <category>/<pattern>/p<N>/

OBJETIVO PEDAGÓGICO:
  Demonstrar <nome do pattern> em contexto de <domínio real>.
  O aluno deve conseguir identificar: <lista dos elementos do pattern: Creator, Product, etc.>

PRINCÍPIOS SOLID OBRIGATÓRIOS:
  - <Princípio 1>: como se aplica
  - <Princípio 2>: como se aplica

ENTREGÁVEIS OBRIGATÓRIOS:
  [ ] src/<domínio>/domain/         → entidades e interfaces (sem dependências externas)
  [ ] src/<domínio>/application/    → casos de uso e lógica do pattern
  [ ] src/<domínio>/infrastructure/ → integrações (DB, cloud, mensageria)
  [ ] tests/unit/                   → testes unitários (mocks para dependências externas)
  [ ] tests/integration/            → testes de integração (via docker-compose)
  [ ] Dockerfile                    → multi-stage: base, dev, prod
  [ ] docker-compose.yml            → app + todos os serviços necessários
  [ ] pyproject.toml                → Black, Ruff, mypy, pytest configurados
  [ ] .env.example                  → todas as variáveis documentadas
  [ ] README.md                     → objetivo, UML ASCII, como rodar, SOLID mapeado
```

---

## 3. Estrutura de Pastas de cada Projeto

```
<category>/<pattern>/p<N>/
├── src/
│   └── <domain_name>/
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── interfaces.py      ← ABCs e Protocols
│       │   └── entities.py        ← dataclasses, value objects
│       ├── application/
│       │   ├── __init__.py
│       │   └── use_cases.py       ← lógica de negócio usando o pattern
│       └── infrastructure/
│           ├── __init__.py
│           └── <adapter>.py       ← implementações concretas (DB, API, cloud)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                ← fixtures compartilhadas
│   ├── unit/
│   │   └── test_<module>.py
│   └── integration/
│       └── test_<module>.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 4. Padrões de Código

### 4.1 Clean Code — Regras Obrigatórias

| Regra | Detalhamento |
|-------|-------------|
| **Nomes revelam intenção** | `calculate_tax_for_order()` não `calc()` ou `process()` |
| **Funções fazem UMA coisa** | Máximo ~20 linhas; se ficou grande, extraia |
| **Sem magic numbers** | `MAX_RETRIES = 3` não `if retries > 3` |
| **Sem comentários óbvios** | O código fala; comentários para WHY não-óbvio |
| **Type hints obrigatórios** | Em toda assinatura de função e variável de módulo |
| **Docstrings em interfaces** | ABCs e funções públicas têm docstring de uma linha |
| **Exceções específicas** | `raise PaymentDeclinedError(...)` não `raise Exception(...)` |
| **Evitar flags booleanos** | Prefira polimorfismo a `if is_premium:` dentro de funções |

### 4.2 SOLID — Aplicação Prática

#### S — Single Responsibility
- Cada classe tem **um motivo para mudar**
- Separar: regras de negócio / persistência / apresentação / notificação
- Sinal de violação: classe com `and` na descrição ("salva e notifica")

#### O — Open/Closed
- Aberto para extensão (novas subclasses/strategies), fechado para modificação
- Usar herança de ABC ou Protocol ao invés de `if isinstance(...)`
- Sinal de violação: adicionar novo tipo exige modificar código existente

#### L — Liskov Substitution
- Subclasses devem ser substituíveis pela superclasse sem surpresas
- Não restringir pré-condições nem lançar exceções que a base não lança
- Sinal de violação: `if isinstance(obj, SubClass): do_special_thing`

#### I — Interface Segregation
- ABCs pequenas e focadas; não forçar implementação de métodos não usados
- Preferir múltiplas interfaces pequenas a uma grande
- Sinal de violação: `def method(self): raise NotImplementedError` em muitos métodos

#### D — Dependency Inversion
- Módulos de alto nível dependem de abstrações, não de implementações
- Injetar dependências no construtor (Dependency Injection)
- Sinal de violação: `self.db = PostgreSQLConnection()` dentro do use case

---

## 5. Configuração de Ferramentas

### 5.1 pyproject.toml base

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "W", "I", "N", "UP", "ANN", "S", "B", "A", "C4", "PT"]
ignore = ["ANN101", "ANN102"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
omit = ["tests/*", "*/__init__.py"]
```

### 5.2 Dockerfile base (multi-stage)

```dockerfile
# ── base ──────────────────────────────────────────────
FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── dev ───────────────────────────────────────────────
FROM base AS dev
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"
COPY . .

# ── prod ──────────────────────────────────────────────
FROM base AS prod
COPY pyproject.toml .
RUN pip install --no-cache-dir -e "."
COPY src/ src/
```

### 5.3 docker-compose.yml base

```yaml
version: "3.9"

services:
  app:
    build:
      context: .
      target: dev
    volumes:
      - .:/app
    env_file: .env
    depends_on:
      - <service>   # substituir pelo serviço real
    ports:
      - "8000:8000"

  # Adicionar serviços necessários ao projeto:
  # postgres, mysql, redis, rabbitmq, kafka, etc.
```

---

## 6. README.md Padrão por Projeto

```markdown
# <Nome do Projeto>

> **Design Pattern:** <Pattern Name> | **Categoria:** <Creational|Structural|Behavioral>
> **Framework:** <...> | **Serviços:** <...>

## Objetivo Pedagógico

<Explicação em 2-3 linhas do que o aluno aprenderá neste projeto.>

## O Pattern Aplicado

<Descrever brevemente como o pattern aparece no contexto real deste projeto.>

## Diagrama UML (ASCII)

\`\`\`
<Creator>
    + factory_method(): Product
         |
    [ConcreteCreator]
         |
    <Product>
    [ConcreteProduct]
\`\`\`

## Princípios SOLID Demonstrados

- **O (Open/Closed):** <onde e como>
- **D (Dependency Inversion):** <onde e como>

## Como Rodar

\`\`\`bash
cp .env.example .env
docker-compose up --build
\`\`\`

## Rodar os Testes

\`\`\`bash
docker-compose run --rm app pytest
\`\`\`
```

---

## 7. Convenções de Nomenclatura

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Arquivos Python | snake_case | `payment_gateway.py` |
| Classes | PascalCase | `StripePaymentGateway` |
| Funções/Métodos | snake_case | `process_payment()` |
| Constantes de módulo | UPPER_SNAKE | `MAX_RETRY_COUNT = 3` |
| ABCs/Interfaces | Prefixo `Abstract` ou sufixo `Protocol` | `AbstractNotifier`, `StorageProtocol` |
| Pastas de projeto | snake_case | `abstract_factory/p1/` |
| Variáveis de ambiente | UPPER_SNAKE | `DATABASE_URL`, `AWS_REGION` |

---

## 8. Controle de Qualidade — Checklist Final

Antes de marcar um projeto como `[x]` no STATUS.md:

```bash
# 1. Formatar
black src/ tests/

# 2. Linter
ruff check src/ tests/

# 3. Tipos
mypy src/

# 4. Testes com cobertura
pytest --cov=src --cov-report=term-missing

# 5. Docker
docker-compose build
docker-compose up -d
docker-compose run --rm app pytest
docker-compose down
```

Todos devem passar sem erros antes de atualizar o STATUS.md.

---

## 9. Registro de Decisões de Arquitetura

Mudanças de escopo, tecnologia ou convenção devem ser registradas em:
`docs/decisions/ADR-<NNN>-<titulo>.md`

Formato ADR:
```markdown
# ADR-<NNN>: <Título>
**Data:** YYYY-MM-DD | **Status:** Accepted | **Decisores:** <nomes>

## Contexto
## Decisão
## Consequências
```

---

## 10. Comunicação de Problemas

Quando um agente identificar bloqueio (`[!]` no STATUS.md):

1. Atualizar STATUS.md com `[!]` e descrição do problema na coluna Observações
2. Registrar no Log de Alterações
3. Não avançar para o próximo projeto do mesmo pattern até resolução

---

*Documento criado em 2026-06-20. Versionar alterações neste arquivo via log em STATUS.md.*
