# Renderer Bridge

> **Design Pattern:** Bridge
> **Categoria:** Structural
> **Framework:** Flask
> **Serviços:** Nenhum (em memória)

## Objetivo Pedagógico

Este projeto demonstra o padrão Bridge desacoplando **o que renderizar** (tipos de
página: Produto, Post de blog, Perfil de usuário) de **como renderizar** (formato de
saída: HTML, JSON, XML). Qualquer combinação de página × formato funciona sem que uma
hierarquia conheça a outra, evitando a explosão combinatória de subclasses que herança
múltipla causaria.

## O Pattern em Ação

- **Abstraction:** `Page` define o contrato de páginas e guarda uma referência ao
  renderer injetado (a "ponte").
- **RefinedAbstraction:** `ProductPage`, `BlogPostPage`, `UserProfilePage` sabem montar
  um `PageContent` a partir dos seus próprios dados, mas delegam a serialização.
- **Implementor:** `ContentRenderer` define o contrato de renderização (`render_page`,
  `content_type`).
- **ConcreteImplementor:** `HTMLRenderer`, `JSONRenderer`, `XMLRenderer` sabem
  transformar um `PageContent` genérico no formato de saída, sem saber se vieram de um
  produto, post ou perfil.

| Papel do Pattern | Classe | Arquivo |
|------------------|--------|---------|
| Abstraction | `Page` | `src/renderer/domain/interfaces.py` |
| RefinedAbstraction | `ProductPage`, `BlogPostPage`, `UserProfilePage` | `src/renderer/domain/pages.py` |
| Implementor | `ContentRenderer` | `src/renderer/domain/interfaces.py` |
| ConcreteImplementor | `HTMLRenderer`, `JSONRenderer`, `XMLRenderer` | `src/renderer/infrastructure/implementations.py` |

## Diagrama UML (ASCII)

```
<<abstract>>                         <<abstract>>
Page                                 ContentRenderer
- renderer: ContentRenderer  ------> + render_page(content): str
+ render(): str                      + content_type: str
     |                                     |
     |--- ProductPage                      |--- HTMLRenderer
     |--- BlogPostPage                     |--- JSONRenderer
     |--- UserProfilePage                  |--- XMLRenderer
```

A seta entre `Page` e `ContentRenderer` é a "ponte": composição, não herança. Cada
`Page` é construída com QUALQUER `ContentRenderer`, e novos tipos de página ou novos
formatos podem ser adicionados independentemente.

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Adicionar um novo formato (ex: `MarkdownRenderer`) ou um novo
  tipo de página (ex: `OrderPage`) não exige alterar nenhuma classe existente — apenas
  criar uma nova subclasse.
- **D — Dependency Inversion:** `Page` depende da abstração `ContentRenderer`, nunca de
  uma implementação concreta. `RenderPageUseCase` recebe o renderer já instanciado via
  injeção, e a rota Flask decide qual concreto usar a partir do parâmetro `format`.
- **S — Single Responsibility:** Páginas só sabem montar `PageContent`; renderers só
  sabem serializar `PageContent`. Nenhuma classe faz as duas coisas.

## Estrutura do Projeto

```
bridge/p2/
├── src/
│   └── renderer/
│       ├── app.py                       ← Flask app (composition root)
│       ├── domain/
│       │   ├── interfaces.py            ← Page, ContentRenderer (ABCs)
│       │   ├── entities.py              ← PageContent, ProductData, ...
│       │   └── pages.py                 ← RefinedAbstractions
│       ├── application/
│       │   └── use_cases.py             ← RenderPageUseCase
│       ├── infrastructure/
│       │   └── implementations.py       ← HTMLRenderer, JSONRenderer, XMLRenderer
│       └── templates/pages/              ← Templates Jinja2 para HTMLRenderer
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
cp .env.example .env
docker-compose up --build
```

A API fica disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota | Query params |
|--------|------|---------------|
| GET | `/health` | — |
| GET | `/products/<product_id>` | `?format=html\|json\|xml` |
| GET | `/blog/<slug>` | `?format=html\|json\|xml` |
| GET | `/users/<user_id>` | `?format=html\|json\|xml` |

Exemplo:

```bash
curl "http://localhost:8000/products/p-100?format=xml"
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/unit/ -v
docker-compose run --rm app pytest tests/integration/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Verificar Qualidade do Código

```bash
black src/ tests/
ruff check src/ tests/
mypy src/ --strict
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|---------------|
| `FLASK_APP` | Módulo:app do Flask | `renderer.app:app` |
| `FLASK_RUN_HOST` | Host de bind | `0.0.0.0` |
| `FLASK_RUN_PORT` | Porta de bind | `8000` |
| `FLASK_DEBUG` | Ativa modo debug | `1` |
