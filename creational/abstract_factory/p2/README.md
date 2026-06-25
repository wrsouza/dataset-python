# Cloud Storage Factory

> **Design Pattern:** Abstract Factory
> **Categoria:** Creational
> **Framework:** FastAPI
> **Serviços:** LocalStack (AWS S3 mock), GCS fake, Azure fake

## Objetivo Pedagógico

Este projeto demonstra o Abstract Factory em uma API FastAPI para upload/download
de arquivos em múltiplos provedores de cloud (AWS S3, GCS, Azure Blob Storage).
O aluno aprende a trocar provedores inteiramente sem alterar nenhuma lógica de
negócio, e como o ISP permite que cada cliente consuma apenas o produto que precisa
(StorageClient OU MetadataClient OU URLSigner).

## O Pattern em Ação

| Papel do Pattern  | Classe                   | Arquivo                                           |
|-------------------|--------------------------|---------------------------------------------------|
| AbstractFactory   | `CloudStorageFactory`    | `src/cloud_storage/domain/interfaces.py`          |
| ConcreteFactory   | `AWSStorageFactory`      | `src/cloud_storage/infrastructure/factories.py`   |
| ConcreteFactory   | `GCSStorageFactory`      | `src/cloud_storage/infrastructure/factories.py`   |
| ConcreteFactory   | `AzureStorageFactory`    | `src/cloud_storage/infrastructure/factories.py`   |
| AbstractProduct   | `StorageClient`          | `src/cloud_storage/domain/interfaces.py`          |
| AbstractProduct   | `MetadataClient`         | `src/cloud_storage/domain/interfaces.py`          |
| AbstractProduct   | `URLSigner`              | `src/cloud_storage/domain/interfaces.py`          |
| Client            | `UploadFileUseCase`      | `src/cloud_storage/application/use_cases.py`      |

## Diagrama UML

```
<<abstract>>
CloudStorageFactory
+ create_storage_client()  -> StorageClient
+ create_metadata_client() -> MetadataClient
+ create_url_signer()      -> URLSigner
        |
        ├── AWSStorageFactory   → AWSS3StorageClient / AWSS3MetadataClient / AWSS3URLSigner
        ├── GCSStorageFactory   → FakeGCSStorageClient / FakeGCSMetadataClient / FakeGCSURLSigner
        └── AzureStorageFactory → FakeAzureStorageClient / FakeAzureMetadataClient / FakeAzureURLSigner

<<Protocol>>          <<Protocol>>           <<Protocol>>
StorageClient         MetadataClient         URLSigner
+ upload()            + get_metadata()       + sign_url()
+ download()          + list_keys()          + get_provider_name()
+ delete()
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Adicionar Backblaze B2 exige apenas criar `BackblazeStorageFactory`
  + produtos concretos e registrá-la em `build_factory_for_provider`. Nenhuma rota
  ou use case muda.
- **I — Interface Segregation:** `GetSignedUrlUseCase` depende apenas de `URLSigner`
  (não de `StorageClient`). `GetMetadataUseCase` depende apenas de `MetadataClient`.
  Cada cliente usa exatamente a interface que precisa — sem métodos desnecessários.
- **D — Dependency Inversion:** use cases recebem `CloudStorageFactory` pelo construtor.
  A implementação concreta (AWS/GCS/Azure) é injetada na composição root (`app.py`).

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build

# Upload para AWS (LocalStack)
curl -F "file=@myfile.txt" "http://localhost:8000/upload?provider=aws&key=myfile.txt"

# Upload para GCS (fake)
curl -F "file=@myfile.txt" "http://localhost:8000/upload?provider=gcs&key=myfile.txt"

# URL assinada
curl "http://localhost:8000/signed-url/myfile.txt?provider=aws&expires_in=600"

# Documentação interativa
open http://localhost:8000/docs
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/unit/ -v
docker-compose run --rm app pytest tests/integration/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável              | Descrição                    | Valor padrão                    |
|-----------------------|------------------------------|---------------------------------|
| `LOCALSTACK_URL`      | URL do LocalStack            | `http://localstack:4566`        |
| `AWS_DEFAULT_REGION`  | Região AWS                   | `us-east-1`                     |
| `AWS_ACCESS_KEY_ID`   | Credencial LocalStack        | `test`                          |
| `AWS_SECRET_ACCESS_KEY` | Credencial LocalStack      | `test`                          |
| `S3_BUCKET_NAME`      | Nome do bucket S3            | `app-bucket`                    |
