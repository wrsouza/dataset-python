# Product Variant System

> **Design Pattern:** Prototype
> **Categoria:** Creational
> **Framework:** Django
> **Servicos:** MySQL 8.0

## Objetivo Pedagogico

Demonstra o padrao Prototype em um sistema de variantes de produtos e-commerce.
Um produto-base (template) e clonado para gerar variantes (tamanho GG, cor azul,
plano anual) sem que o codigo cliente conhca a classe concreta do produto.
`copy.deepcopy` garante que atributos aninhados (dicts de dimensoes, listas de
features) sao objetos completamente independentes no clone.

## O Pattern em Acao

O cliente faz `POST /products/clone/{product_id}/` enviando overrides no body.
O `ProductTemplateRegistry` localiza o template, delega a `clone(variant_attrs)`,
que internamente usa `copy.deepcopy` e aplica os overrides so no clone.

| Papel do Pattern    | Classe                    | Arquivo                                           |
|---------------------|---------------------------|---------------------------------------------------|
| Prototype (ABC)     | `Product`                 | `src/products/domain/interfaces.py`               |
| ConcretePrototype   | `PhysicalProduct`         | `src/products/infrastructure/prototypes.py`       |
| ConcretePrototype   | `DigitalProduct`          | `src/products/infrastructure/prototypes.py`       |
| ConcretePrototype   | `SubscriptionProduct`     | `src/products/infrastructure/prototypes.py`       |
| PrototypeRegistry   | `ProductTemplateRegistry` | `src/products/infrastructure/prototypes.py`       |
| ORM Model           | `ProductModel`            | `src/products/infrastructure/models.py`           |
| ORM Model           | `ProductVariantModel`     | `src/products/infrastructure/models.py`           |

## Diagrama UML ASCII

```
<<abstract>>
Product (ABC)
+ clone(variant_attrs: dict) -> Product
+ get_sku() -> str
+ name: str            [property]
+ base_price: float    [property]
+ description: str     [property]
+ attributes: dict     [property]
+ to_dict() -> dict
         |
    (extends BaseProduct)
         |
         +-- PhysicalProduct
         |     - weight_kg: float
         |     - dimensions_cm: dict[str, float]
         |
         +-- DigitalProduct
         |     - download_url: str
         |     - file_size_mb: float
         |
         +-- SubscriptionProduct
               - billing_cycle: str
               - trial_days: int

ProductTemplateRegistry
- _templates: dict[str, Product]
+ register(key, product) -> None
+ get(key) -> Product
+ clone(key, overrides) -> Product   [get -> clone -> deepcopy+overrides]
+ list_templates() -> list[str]
```

## Principios SOLID Demonstrados

- **O — OCP:** Para adicionar `BundleProduct`, basta criar a classe herdando
  `BaseProduct` e registrar no registry. Nenhuma classe existente e modificada.
- **L — LSP:** `PhysicalProduct`, `DigitalProduct` e `SubscriptionProduct` sao
  substituiveis por `Product` em qualquer ponto do codigo cliente. As views e
  use cases trabalham apenas com a interface `Product`.

## Estrutura do Projeto

```
p3/
+-- src/
|   +-- manage.py                          <- Django management
|   +-- config/
|   |   +-- settings.py                   <- Settings (MySQL / SQLite para tests)
|   |   +-- urls.py                       <- Root URL conf
|   +-- products/
|       +-- domain/
|       |   +-- interfaces.py             <- Product ABC, ProductRegistry ABC
|       |   +-- entities.py              <- CloneRequest, VariantRecord, erros
|       +-- application/
|       |   +-- use_cases.py             <- ListTemplates, CloneProduct, ListVariants
|       +-- infrastructure/
|       |   +-- prototypes.py            <- ConcretePrototypes + Registry
|       |   +-- models.py               <- Django ORM (ProductModel, ProductVariantModel)
|       +-- views/
|       |   +-- product_views.py        <- Django views (CBV)
|       +-- urls.py                     <- URL patterns
|       +-- apps.py
+-- tests/
|   +-- conftest.py                     <- pytest-django + SQLite override
|   +-- unit/
|   |   +-- test_prototypes.py          <- testa deepcopy independence
|   |   +-- test_use_cases.py          <- testa use cases com mocks
|   +-- integration/
|       +-- test_views.py              <- testa endpoints com Django test client
+-- Dockerfile
+-- docker-compose.yml
+-- pyproject.toml
+-- .env.example
```

## Pre-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API disponivel em: http://localhost:8000
```

## Endpoints

| Metodo | URL                              | Descricao                          |
|--------|----------------------------------|------------------------------------|
| GET    | /products/templates/             | Lista templates registrados        |
| POST   | /products/clone/{product_id}/    | Clona produto com overrides no body|
| GET    | /products/{product_id}/variants/ | Lista variantes de um produto      |

### Exemplo de Clone

```bash
# Criar um produto template via shell Django (ou fixtures)
# POST clone com overrides
curl -X POST http://localhost:8000/products/clone/1/ \
  -H "Content-Type: application/json" \
  -d '{"overrides": {"name": "Camiseta GG", "base_price": 59.90, "weight_kg": 0.25}}'
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variaveis de Ambiente

| Variavel             | Descricao                  | Padrao         |
|----------------------|----------------------------|----------------|
| `DJANGO_SECRET_KEY`  | Chave secreta Django       | dev-insecure   |
| `DJANGO_DEBUG`       | Modo debug                 | true           |
| `MYSQL_DATABASE`     | Nome do banco              | products_db    |
| `MYSQL_USER`         | Usuario MySQL              | app            |
| `MYSQL_PASSWORD`     | Senha MySQL                | secret         |
| `MYSQL_HOST`         | Host MySQL                 | db             |
| `MYSQL_PORT`         | Porta MySQL                | 3306           |
