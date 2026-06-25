# Access Control Proxy — Protection Proxy Pattern

> **Design Pattern:** Proxy (Protection Proxy) | **Categoria:** Structural
> **Framework:** Django | **Serviços:** PostgreSQL

## Objetivo Pedagógico

Demonstrar o padrão Proxy controlando acesso por permissão: toda operação
em `DocumentService` passa primeiro por `PermissionProxy`, que verifica o
papel (role) do usuário atual antes de delegar ao serviço real — e registra
a decisão (concedida ou negada) em um audit log.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Subject (interface) | `DocumentService` (Protocol) | `domain/interfaces.py` |
| RealSubject | `DjangoDocumentService` | `infrastructure/real_subject.py` |
| Proxy | `PermissionProxy` | `infrastructure/proxy.py` |
| Client | views + middleware | `views.py`, `middleware.py` |

## Diagrama UML (ASCII)

```
<<Protocol>>
DocumentService (Subject)
  + get/create/update/delete/list
        ▲                       ▲
        │ implements            │ implements
        │                       │
DjangoDocumentService     PermissionProxy
  (RealSubject — ORM)       (verifica role → delega ao real)
                                  │
                                  ▼
                           AuditLogger (cada decisão é registrada)
```

## Matriz de Permissões

| Role | read | write (create/update) | delete |
|--------|:----:|:----:|:----:|
| GUEST | ❌ | ❌ | ❌ |
| VIEWER | ✅ | ❌ | ❌ |
| EDITOR | ✅ | ✅ | ❌ |
| OWNER | ✅ | ✅ | ✅ |

## Onde o Proxy é Injetado

`PermissionProxyMiddleware` resolve o usuário atual (header `X-User-Id`) e
injeta `request.document_service = PermissionProxy(...)` em toda request —
as views (`DocumentListCreateView`, `DocumentDetailView`) usam apenas
`request.document_service`, sem nunca instanciar `DjangoDocumentService`
nem `PermissionProxy` diretamente.

## Princípios SOLID Demonstrados

- **D — Dependency Inversion:** `PermissionProxy` depende de `DocumentService`
  e `AuditLogger` (abstrações), nunca de modelos Django diretamente.
- **L — Liskov Substitution:** `PermissionProxy` e `DjangoDocumentService`
  são intercambiáveis em qualquer lugar que espera `DocumentService`.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

Isso roda as migrations, popula usuários demo (um por role) e documentos de
exemplo, e inicia o servidor em `http://localhost:8000`.

## Testando os Papéis

```bash
# VIEWER consegue ler
curl -H "X-User-Id: viewer-1" http://localhost:8000/documents/doc-1/

# GUEST não consegue
curl -H "X-User-Id: guest-1" http://localhost:8000/documents/doc-1/   # 403

# Apenas OWNER consegue deletar
curl -X DELETE -H "X-User-Id: owner-1" http://localhost:8000/documents/doc-1/
```

## Endpoints

| Método | Rota | Permissão necessária |
|--------|------|----------------------|
| GET | `/documents/` | read |
| POST | `/documents/` | write |
| GET | `/documents/{id}/` | read |
| PUT | `/documents/{id}/` | write |
| DELETE | `/documents/{id}/` | delete |

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente:

```bash
pip install -e ".[dev]"
DJANGO_SETTINGS_MODULE=config.settings_test python -m pytest --cov=src --cov-report=term-missing
```

Os testes usam SQLite em memória (`config.settings_test`) — nenhum servidor
PostgreSQL é necessário para rodar a suíte de testes.
