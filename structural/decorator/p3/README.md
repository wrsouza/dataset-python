# Permission Decorator Layers

> **Design Pattern:** Decorator | **Categoria:** Structural
> **Framework:** Django | **Serviços:** PostgreSQL

## Objetivo Pedagógico

Demonstrar o Decorator pattern aplicado a regras de autorização: cada camada de
permissão (autenticação, role, ownership, auditoria) é uma classe independente
que envolve um `ResourceAccessService` e pode ser empilhada em qualquer ordem,
sem alterar nenhuma das camadas existentes nem o serviço base.

O aluno deve conseguir identificar:
- **Component**: `ResourceAccessService` (ABC) — contrato compartilhado pelo
  serviço base e por todos os decorators.
- **ConcreteComponent**: `DocumentAccessService` — localiza o recurso, sem
  aplicar nenhuma regra de autorização.
- **Decorator (base)**: `ResourceAccessDecorator` — guarda a referência ao
  componente envolvido e delega por padrão.
- **ConcreteDecorators**: `RequireAuthDecorator`, `RequireRoleDecorator`,
  `RequireOwnershipDecorator`, `AuditLogDecorator`.

## O Pattern Aplicado

Em vez de um único método `check_permissions()` com vários `if`s, cada regra de
autorização é isolada em sua própria classe. Um *use case* (`EvaluateDocumentAccessUseCase`)
escolhe, em tempo de execução, quais camadas envolver — por exemplo, leituras
não exigem ownership, mas escritas/exclusões exigem:

```python
service = AuditLogDecorator(
    RequireOwnershipDecorator(
        RequireRoleDecorator(
            RequireAuthDecorator(DocumentAccessService(repository)),
            required_role="editor",
        )
    )
)
result = service.access(context)
```

Cada decorator delega para `self._wrapped.access(context)` e só nega o acesso
quando a regra que ele representa falha — preservando o resultado (e a lista de
camadas aplicadas) das camadas mais internas. `AuditLogDecorator` é colocado por
fora de todas as demais, registrando o resultado final sem influenciar a decisão.

## Diagrama UML (ASCII)

```
                    <<abstract>>
                ResourceAccessService
                ----------------------
                + access(context): ResourceAccessResult
                         ▲
           ┌─────────────┼───────────────────────┐
           │                                      │
  DocumentAccessService              ResourceAccessDecorator
  ----------------------             ------------------------
  + access(context)                 - _wrapped: ResourceAccessService
  (ConcreteComponent)               + access(context)  [delegates]
                                              ▲
                  ┌───────────────┬───────────┼───────────────┐
                  │               │           │               │
      RequireAuthDecorator  RequireRoleDecorator  RequireOwnershipDecorator  AuditLogDecorator
      ----------------------  ---------------------  ----------------------------  ------------------
      + access(context)       + access(context)       + access(context)            + access(context)
      (denies if anonymous)   (denies if role missing) (denies if not owner)       (logs, never denies)
```

Composição em runtime (de fora para dentro):

```
AuditLogDecorator
  └─ RequireOwnershipDecorator
       └─ RequireRoleDecorator(required_role="editor")
            └─ RequireAuthDecorator
                 └─ DocumentAccessService  (consulta PostgreSQL via DjangoResourceRepository)
```

## Domínio

O domínio simulado é um serviço de documentos corporativos (`DocumentModel`)
onde cada acesso (`read`/`write`/`delete`) precisa passar por camadas de
autorização configuráveis por endpoint. Toda tentativa de acesso — concedida ou
negada — é registrada em `AccessLogModel` para auditoria.

- `src/permission_layers/domain/` — `User`, `Resource`, `RequestContext`,
  `ResourceAccessResult` (dataclasses puras, sem Django).
- `src/permission_layers/application/use_cases.py` — monta a pilha de
  decorators de acordo com a ação solicitada.
- `src/permission_layers/infrastructure/` — decorators concretos, serviço
  base, `models.py` (Django ORM/PostgreSQL), `repository.py` (adapta ORM →
  entidades de domínio).
- `src/permission_layers/views/api.py` — view Django fina que traduz
  HTTP ↔ use case.

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** cada decorator concentra exatamente uma
  regra (`RequireAuthDecorator` só verifica autenticação; `AuditLogDecorator`
  só loga). A persistência do log de auditoria fica na view, não no decorator.
- **O (Open/Closed):** uma nova regra de autorização (ex.: `RequireMfaDecorator`)
  é adicionada criando uma nova classe — nenhum decorator existente é
  modificado.
- **L (Liskov Substitution):** qualquer composição de decorators pode
  substituir `DocumentAccessService` sem que o `use_case` ou a view percebam
  diferença — todos implementam `ResourceAccessService.access()`.
- **I (Interface Segregation):** `ResourceAccessService` tem um único método
  abstrato; `ResourceRepository` também expõe apenas `find_by_id`.
- **D (Dependency Inversion):** `EvaluateDocumentAccessUseCase` e os
  decorators dependem de `ResourceAccessService`/`ResourceRepository`
  (abstrações), nunca de `DocumentModel` ou do Django ORM diretamente — a
  ponte concreta (`DjangoResourceRepository`) é injetada apenas na view
  (composition root).

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

A API expõe `POST /access/evaluate`:

```bash
curl -X POST http://localhost:8000/access/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "owner-1", "username": "alice", "roles": [],
    "is_authenticated": true,
    "resource_id": "doc-1", "owner_id": "owner-1", "title": "Q3 Report",
    "action": "write", "required_role": null
  }'
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente (sem PostgreSQL), os testes usam `settings_test.py` (SQLite em
memória), configurado via `DJANGO_SETTINGS_MODULE = "settings_test"` em
`pyproject.toml`.
