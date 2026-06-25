# File Storage Factory

> **Design Pattern:** Factory Method
> **Categoria:** Creational
> **Framework:** Flask
> **Serviços:** LocalStack (S3), GCS fake (in-memory), Local filesystem

## Objetivo Pedagógico

Demonstra o Factory Method aplicado ao armazenamento de arquivos com múltiplos backends. O aluno aprende que o use case de upload/download nunca sabe qual storage backend está sendo usado — a decisão fica no ConcreteCreator injetado, tornando trivial adicionar novos providers (Azure Blob, MinIO, etc.).

## O Pattern em Ação

| Papel do Pattern   | Classe                  | Arquivo                                    |
|--------------------|-------------------------|--------------------------------------------|
| Creator (abstrato) | `StorageFactory`        | `src/storage/domain/interfaces.py`         |
| Product (Protocol) | `StorageClient`         | `src/storage/domain/interfaces.py`         |
| ConcreteCreator    | `S3StorageFactory`      | `src/storage/infrastructure/creators.py`   |
| ConcreteCreator    | `GCSStorageFactory`     | `src/storage/infrastructure/creators.py`   |
| ConcreteCreator    | `LocalStorageFactory`   | `src/storage/infrastructure/creators.py`   |
| ConcreteProduct    | `S3StorageClient`       | `src/storage/infrastructure/creators.py`   |
| ConcreteProduct    | `GCSStorageClient`      | `src/storage/infrastructure/creators.py`   |
| ConcreteProduct    | `LocalStorageClient`    | `src/storage/infrastructure/creators.py`   |

## Diagrama UML

```
<<abstract>>
StorageFactory
+ create_client() -> StorageClient    (factory method)
+ get_provider_name() -> str
        |
        |-- S3StorageFactory      -> S3StorageClient    (LocalStack)
        |-- GCSStorageFactory     -> GCSStorageClient   (fake in-memory)
        +-- LocalStorageFactory   -> LocalStorageClient (filesystem)

<<Protocol>>
StorageClient
+ upload(key, data) -> str
+ download(key) -> bytes
+ delete(key) -> None
+ list_keys(prefix) -> list[str]
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Adicionar Azure Blob = criar `AzureStorageClient` + `AzureStorageFactory` + registrar em `PROVIDER_REGISTRY`. Nenhum outro arquivo é alterado.
- **D — Dependency Inversion:** `UploadFileUseCase` recebe `StorageFactory` (abstração) — nunca uma classe concreta.
- **I — Interface Segregation:** `StorageClient` tem apenas 4 métodos focados — clientes que só leem dependem apenas de `download` e `list_keys`.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build

# Upload via S3 (LocalStack)
curl -X POST http://localhost:5000/files/s3 \
  -F "file=@myfile.txt" -F "key=uploads/myfile.txt"

# Upload via GCS (fake)
curl -X POST http://localhost:5000/files/gcs \
  -F "file=@myfile.txt" -F "key=uploads/myfile.txt"

# Download
curl http://localhost:5000/files/gcs/uploads/myfile.txt -o downloaded.txt

# Listar providers
curl http://localhost:5000/providers
```

## Variáveis de Ambiente

| Variável              | Descrição                      | Padrão                      |
|-----------------------|--------------------------------|-----------------------------|
| `AWS_ENDPOINT_URL`    | LocalStack endpoint            | `http://localstack:4566`    |
| `S3_BUCKET`           | Nome do bucket S3              | `app-files`                 |
| `GCS_BUCKET`          | Nome do bucket GCS (fake)      | `app-files-gcs`             |
| `LOCAL_STORAGE_DIR`   | Diretório local de arquivos    | `/tmp/app-files`            |
