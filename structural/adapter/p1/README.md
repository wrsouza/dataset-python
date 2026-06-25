# SOAP → REST Adapter

> **Design Pattern:** Adapter
> **Categoria:** Structural
> **Framework:** FastAPI
> **Servicos:** SOAP Server (Flask, simulated), httpx

## Objetivo Pedagogico

Este projeto demonstra o padrao Adapter em um cenario real de modernizacao de sistemas:
uma API REST moderna (FastAPI + JSON) que consome um servico legado SOAP (XML) sem
que o codigo cliente precise saber nada sobre XML ou SOAP. O aluno aprende como isolar
interfaces incompativeis e manter o codigo de negocio desacoplado da camada de comunicacao.

## O Pattern em Acao

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Target (interface desejada) | `RESTProductService` | `src/soap_adapter/domain/interfaces.py` |
| Adaptee (interface legada) | `LegacySoapClient` | `src/soap_adapter/infrastructure/soap_client.py` |
| Adapter | `SoapToRestAdapter` | `src/soap_adapter/infrastructure/adapters.py` |
| Client | FastAPI routes + Use Cases | `src/soap_adapter/main.py`, `application/use_cases.py` |

## Diagrama UML

```
<<Protocol>>                    <<Adaptee>>
RESTProductService              LegacySoapClient
+ get_product(id) -> Product    + get_product_xml(id) -> str
+ list_products() -> [Product]  + list_products_xml() -> str
+ create_product(data) -> Product  + create_product_xml(xml) -> str
        ^                               |
        |                               | (usa internamente)
        |                               v
        +--------- SoapToRestAdapter ---+
                   (Adapter)
                   + get_product(id) -> Product
                   + list_products() -> [Product]
                   + create_product(data) -> Product
```

## Principios SOLID Demonstrados

- **I — Interface Segregation:** `RESTProductService` tem exatamente 3 metodos, um por operacao de recurso.
- **D — Dependency Inversion:** As rotas FastAPI e os use cases dependem de `RESTProductService` (Protocol), nao de `LegacySoapClient` (concreto).

## Estrutura do Projeto

```
p1/
├── src/soap_adapter/
│   ├── domain/
│   │   ├── interfaces.py    <- Target Protocol
│   │   └── entities.py      <- Product, ProductCreate, erros de dominio
│   ├── application/
│   │   └── use_cases.py     <- GetProduct, ListProducts, CreateProduct
│   ├── infrastructure/
│   │   ├── soap_client.py   <- LegacySoapClient (Adaptee) + helpers XML
│   │   └── adapters.py      <- SoapToRestAdapter (Adapter)
│   └── main.py              <- FastAPI app (composicao root)
├── soap_server/
│   ├── app.py               <- Servidor SOAP simulado (Flask)
│   └── Dockerfile
├── tests/
│   ├── unit/test_adapter.py
│   ├── unit/test_use_cases.py
│   └── integration/test_api.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API REST: http://localhost:8000/docs
# SOAP Server: http://localhost:5000/soap
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/unit/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variaveis de Ambiente

| Variavel | Descricao | Valor padrao |
|----------|-----------|--------------|
| `SOAP_SERVICE_URL` | URL do servidor SOAP legado | `http://soap-server:5000` |

## Endpoints REST

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/products/{id}` | Buscar produto por ID |
| GET | `/products` | Listar todos os produtos |
| POST | `/products` | Criar novo produto |
| GET | `/health` | Health check |
