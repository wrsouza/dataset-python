# Document Template Cloner

> **Design Pattern:** Prototype
> **Categoria:** Creational
> **Framework:** Flask
> **Serviços:** MongoDB

## Objetivo Pedagógico

Este projeto demonstra o padrão Prototype aplicado a documentos ricos com placeholders.
O aluno aprenderá como um clone pode aplicar substituições de texto em cópias independentes,
garantindo que o template original jamais seja modificado — usando `copy.deepcopy` internamente.

## O Pattern em Ação

Templates de documentos (contrato, relatório, formulário) são protótipos. Ao clonar via
`POST /documents/clone/{template_id}`, o sistema carrega o template do MongoDB, instancia
o ConcretePrototype correto, aplica `clone(substitutions)` e persiste o resultado.

| Papel do Pattern    | Classe                  | Arquivo                                       |
|---------------------|-------------------------|-----------------------------------------------|
| Prototype (ABC)     | `Document`              | `src/documents/domain/interfaces.py`          |
| ConcretePrototype   | `ContractDocument`      | `src/documents/infrastructure/prototypes.py`  |
| ConcretePrototype   | `ReportDocument`        | `src/documents/infrastructure/prototypes.py`  |
| ConcretePrototype   | `FormDocument`          | `src/documents/infrastructure/prototypes.py`  |
| Entity              | `TemplateRecord`        | `src/documents/domain/entities.py`            |
| Repository          | `MongoTemplateRepository` | `src/documents/infrastructure/mongodb.py`   |

## Diagrama UML

```
<<abstract>>
Document (ABC)
+ clone(substitutions: dict[str, str]) -> Document
+ doc_type: str   [property]
+ title: str      [property]
+ content: str    [property]
+ metadata: dict  [property]
         |
         ├── ContractDocument
         │     + clone(substitutions) -> ContractDocument
         │       [deepcopy → _apply_substitutions]
         │
         ├── ReportDocument
         │     + clone(substitutions) -> ReportDocument
         │
         └── FormDocument
               + clone(substitutions) -> FormDocument

MongoDB collections:
  templates  ←  TemplateRecord
  documents  ←  DocumentRecord (cloned)
```

## Fluxo de Clone

```
POST /documents/clone/{template_id}
  body: {"substitutions": {"client_name": "Acme", "contract_date": "2024-01-01"}}

  1. MongoTemplateRepository.find_by_id(template_id)
  2. get_template_by_type(doc_type)  → ContractDocument()
  3. Populate prototype with stored content
  4. prototype.clone(substitutions)
     → copy.deepcopy(self)          # cópia independente
     → _apply_substitutions(subs)   # {{client_name}} → "Acme"
  5. MongoDocumentRepository.save(cloned)
```

## Princípios SOLID Demonstrados

- **O — OCP:** Para adicionar `InvoiceDocument`, cria-se a classe e adiciona-se
  ao mapeamento em `get_template_by_type()`. Nenhuma rota ou use case precisa mudar.
- **S — SRP:** `MongoTemplateRepository` persiste templates. `MongoDocumentRepository`
  persiste documentos. `CloneDocumentUseCase` orquestra o fluxo. Papéis bem separados.

## Estrutura do Projeto

```
p2/
├── src/
│   ├── main.py                           ← Flask app
│   └── documents/
│       ├── domain/
│       │   ├── interfaces.py             ← Document ABC
│       │   └── entities.py              ← TemplateRecord, DocumentRecord
│       ├── application/
│       │   └── use_cases.py             ← CloneDocumentUseCase, etc.
│       └── infrastructure/
│           ├── prototypes.py            ← ConcretePrototypes
│           └── mongodb.py               ← MongoDB repositories
├── tests/
│   ├── unit/
│   │   ├── test_prototypes.py
│   │   └── test_use_cases.py
│   └── integration/
│       └── test_flask_routes.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API: http://localhost:5000
```

## Variáveis de Ambiente

| Variável        | Descrição              | Valor padrão                         |
|-----------------|------------------------|--------------------------------------|
| `MONGO_URI`     | URI de conexão MongoDB | `mongodb://app:secret@mongodb:27017/` |
| `MONGO_DB`      | Nome do banco          | `documents_db`                       |
| `MONGO_USER`    | Usuário MongoDB        | `app`                                |
| `MONGO_PASSWORD`| Senha MongoDB          | `secret`                             |
