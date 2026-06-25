# Multi-Cloud Storage Adapter

> **Design Pattern:** Adapter
> **Categoria:** Structural
> **Framework:** Django
> **Servicos:** LocalStack (S3), FakeGCS, FakeAzure

## Objetivo Pedagogico

Demonstra como o padrao Adapter permite que um sistema use tres provedores
de cloud storage (AWS S3, Google Cloud Storage, Azure Blob) por meio de
uma unica interface `CloudStorage`, sem que o codigo cliente (views Django)
precise conhecer nenhum SDK especifico.

## O Pattern em Acao

| Papel | Classe | Arquivo |
|-------|--------|---------|
| Target (interface desejada) | `CloudStorage` (Protocol) | `domain/interfaces.py` |
| Adaptee S3 | boto3 S3 client | `infrastructure/adapters.py` |
| Adaptee GCS | `FakeGCSClient` | `infrastructure/fake_clients.py` |
| Adaptee Azure | `FakeAzureClient` | `infrastructure/fake_clients.py` |
| Adapter S3 | `S3StorageAdapter` | `infrastructure/adapters.py` |
| Adapter GCS | `GCSStorageAdapter` | `infrastructure/adapters.py` |
| Adapter Azure | `AzureStorageAdapter` | `infrastructure/adapters.py` |
| Client | Django views + Use Cases | `web/views.py`, `application/use_cases.py` |

## Diagrama UML ASCII

```
<<Protocol>>
CloudStorage
+ upload(key, data) -> str
+ download(key) -> bytes
+ delete(key) -> None
+ list_keys(prefix) -> list[str]
+ get_url(key) -> str
        ^               ^               ^
        |               |               |
S3StorageAdapter  GCSStorageAdapter  AzureStorageAdapter
(Adapter)         (Adapter)          (Adapter)
        |               |               |
        v               v               v
  boto3 client    FakeGCSClient    FakeAzureClient
  (Adaptee S3)   (Adaptee GCS)   (Adaptee Azure)

Client (Django views) -> CloudStorage (Protocol only)
```

## Principios SOLID

- **I — Interface Segregation:** `CloudStorage` tem exatamente 5 metodos de storage.
  Nenhum cliente precisa depender de metodos que nao usa.
- **D — Dependency Inversion:** Views e use cases dependem de `CloudStorage` (abstrato),
  nunca de boto3, google-cloud-storage ou azure-storage-blob diretamente.
- **L — Liskov Substitution:** Todos os adapters podem ser trocados entre si.
  O teste `TestLSPCompliance` valida isso parametricamente.

## Estrutura do Projeto

```
p3/
├── src/
│   ├── manage.py
│   └── cloud_adapter/
│       ├── domain/
│       │   ├── interfaces.py      <- Target: CloudStorage Protocol
│       │   └── entities.py        <- UploadResult, StorageError, etc.
│       ├── application/
│       │   └── use_cases.py       <- Upload/Download/Delete/List use cases
│       ├── infrastructure/
│       │   ├── fake_clients.py    <- FakeGCSClient + FakeAzureClient (Adaptees)
│       │   ├── adapters.py        <- S3/GCS/Azure Adapters
│       │   └── factory.py         <- Composition root (make_storage)
│       ├── web/
│       │   ├── models.py          <- FileUpload Django model
│       │   ├── views.py           <- Django views (Client)
│       │   ├── urls.py
│       │   ├── apps.py
│       │   └── migrations/
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
├── tests/
│   ├── unit/
│   │   ├── test_adapters.py       <- Testa cada Adapter isolado
│   │   └── test_use_cases.py      <- Testa use cases com mock
│   └── integration/
│       └── test_django_views.py   <- Testa views com Django test client
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
# 1. Copiar variaveis de ambiente
cp .env.example .env

# 2. Subir LocalStack + aplicacao
docker-compose up --build

# API disponivel em: http://localhost:8000
```

## Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | `/files/upload?provider=s3\|gcs\|azure` | Upload de arquivo |
| GET | `/files/` | Listar todos os arquivos |
| GET | `/files/?provider=s3` | Listar por provedor |
| GET | `/files/{id}/download` | Download de arquivo |
| DELETE | `/files/{id}` | Deletar arquivo |

## Exemplos curl

```bash
# Upload para S3 (LocalStack)
curl -X POST "http://localhost:8000/files/upload?provider=s3" \
     -F "file=@report.pdf"

# Upload para GCS (fake)
curl -X POST "http://localhost:8000/files/upload?provider=gcs" \
     -F "file=@photo.jpg"

# Listar arquivos S3
curl "http://localhost:8000/files/?provider=s3"

# Download
curl -o output.pdf "http://localhost:8000/files/1/download"

# Delete
curl -X DELETE "http://localhost:8000/files/1"
```

## Rodar os Testes

```bash
# Testes unitarios (sem Docker, sem credenciais)
pip install -e ".[dev]"
pytest tests/unit/ -v

# Cobertura completa
pytest --cov=src --cov-report=term-missing

# Via Docker
docker-compose run --rm app pytest tests/ -v
```

## Variaveis de Ambiente

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `AWS_ENDPOINT_URL` | URL do LocalStack | `http://localstack:4566` |
| `S3_BUCKET` | Nome do bucket S3 | `cloud-adapter-bucket` |
| `GCS_BUCKET` | Nome do bucket GCS | `cloud-adapter-gcs` |
| `AZURE_CONTAINER` | Nome do container Azure | `cloud-adapter-azure` |
