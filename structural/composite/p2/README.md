# Virtual File System

> **Design Pattern:** Composite
> **Categoria:** Structural
> **Framework:** Flask
> **Serviços:** AWS S3 (LocalStack para dev local, moto para testes)

## Objetivo Pedagógico

Este projeto demonstra o padrão Composite construindo um sistema de arquivos
virtual sobre o AWS S3. O aluno aprende a tratar arquivos individuais
(`File`) e pastas com filhos (`Directory`) de forma uniforme através de uma
única interface (`FSNode`), eliminando a necessidade de `isinstance()` no
código cliente — seja para calcular tamanho total, listar conteúdo ou
apagar recursivamente.

## O Pattern em Ação

S3 não tem "pastas" reais — apenas chaves de objeto com prefixos. A camada
de infraestrutura (`S3StorageClient`) traduz essa estrutura plana em uma
árvore de objetos `FSNode`, e o restante da aplicação nunca lida com
strings de chave S3 diretamente.

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Component (abstrato) | `FSNode` | `src/filesystem/domain/interfaces.py` |
| Leaf | `File` | `src/filesystem/domain/entities.py` |
| Composite | `Directory` | `src/filesystem/domain/entities.py` |
| Client (usa Component) | `GetTreeUseCase`, `CalculateTotalSizeUseCase`, etc. | `src/filesystem/application/use_cases.py` |

## Diagrama UML

```
                    <<abstract>>
                       FSNode
        + get_size(): int
        + get_path(): str
        + list_contents(): list[dict]
        + delete(): None
        + to_dict(): dict
                /              \
               /                \
          [Leaf]              [Composite]
           File               Directory
        + get_size()        + get_size()          (soma recursiva dos filhos)
        + delete()          + delete()            (remove filhos, depois si mesmo)
        + to_dict()         + add_child(FSNode)
                             + remove_child(FSNode)
                             + get_children(): list[FSNode]
                             + to_dict()           (inclui children[] recursivamente)

  Directory --> contém 0..N --> FSNode (File ou Directory)
```

Um `Directory` mantém uma lista de `FSNode` filhos (que podem ser `File`
leaves ou outros `Directory` composites), carregada de forma lazy a partir
do S3 na primeira chamada de `get_children()` / `_ensure_loaded()`.

## Princípios SOLID Demonstrados

- **L — Liskov Substitution:** `File` e `Directory` implementam exatamente
  o mesmo contrato `FSNode`. Qualquer código que recebe um `FSNode` (ex.:
  `DeleteNodeUseCase.execute`) funciona idêntico para um arquivo único ou
  uma árvore de pastas inteira, sem checagem de tipo.
- **O — Open/Closed:** novos tipos de nó (ex.: um futuro `SymlinkNode`)
  podem ser adicionados implementando `FSNode`, sem alterar `Directory`,
  os use cases ou as rotas Flask.
- **D — Dependency Inversion:** todos os use cases em
  `application/use_cases.py` recebem `S3StorageClient` via construtor —
  nunca instanciam `boto3.client` diretamente. Em `app.py`, `create_app()`
  aceita um `storage` opcional, permitindo injetar um cliente moto-mockado
  nos testes sem alterar o código de produção.
- **S — Single Responsibility:** `S3StorageClient` só sabe traduzir
  S3 ↔ `FSNode`; cada use case (`GetTreeUseCase`, `UploadFileUseCase`, ...)
  tem uma única razão para mudar.

## Estrutura do Projeto

```
composite/p2/
├── src/
│   └── filesystem/
│       ├── app.py                   ← Flask app + composition root
│       ├── domain/
│       │   ├── interfaces.py        ← FSNode (Component)
│       │   ├── entities.py          ← File (Leaf), Directory (Composite)
│       │   └── exceptions.py        ← FSNodeNotFoundError, FSStorageError, ...
│       ├── application/
│       │   └── use_cases.py         ← GetTree, CalculateTotalSize, Upload, ...
│       └── infrastructure/
│           └── s3_client.py         ← boto3 adapter (S3 ↔ FSNode)
├── tests/
│   ├── conftest.py                  ← fixtures moto_s3 / storage
│   ├── unit/                        ← entities, use cases, s3_client, app module
│   └── integration/                 ← Flask test client end-to-end
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## API Endpoints (Flask)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Health check |
| `GET` | `/tree/<path>` | Retorna a árvore `FSNode` (arquivo ou pasta) serializada |
| `GET` | `/size/<path>` | Tamanho total em bytes (soma recursiva para pastas) |
| `GET` | `/contents/<path>` | Lista plana de todos os arquivos sob o path |
| `POST` | `/files/<key>` | Faz upload do corpo da requisição como um arquivo |
| `POST` | `/directories/<path>` | Cria um marcador de pasta vazia |
| `DELETE` | `/nodes/<path>` | Apaga um arquivo, ou uma pasta e todo seu conteúdo |

Respostas de erro: `404` para `FSNodeNotFoundError`, `502` para
`FSStorageError` (falha inesperada do S3).

## Pré-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Como Rodar

### Local (sem Docker)

```bash
cp .env.example .env
pip install -e ".[dev]"
flask --app filesystem.app:app run --host 0.0.0.0 --port 8000
```

> Sem um LocalStack rodando em `AWS_ENDPOINT_URL`, as rotas que tocam o S3
> falharão — ajuste `.env` para apontar a um S3/LocalStack real, ou use os
> testes (que usam moto e não precisam de rede).

### Docker

```bash
cp .env.example .env
docker-compose up --build
```

Isso sobe a aplicação Flask e um container LocalStack com S3 emulado.

## Rodar os Testes

```bash
# Testes unitários (mocks via moto, sem rede)
pytest tests/unit/ -v

# Testes de integração (Flask test client + moto)
pytest tests/integration/ -v

# Todos os testes com cobertura
pytest --cov=src --cov-report=term-missing
```

Via Docker:

```bash
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
|----------|-----------|--------------|
| `FLASK_APP` | Módulo:objeto WSGI do Flask | `filesystem.app:app` |
| `FLASK_RUN_HOST` | Host de bind | `0.0.0.0` |
| `FLASK_RUN_PORT` | Porta de bind | `8000` |
| `FLASK_DEBUG` | Modo debug do Flask | `1` |
| `S3_BUCKET` | Nome do bucket S3 usado pelo sistema de arquivos virtual | `vfs-bucket` |
| `AWS_DEFAULT_REGION` | Região AWS | `us-east-1` |
| `AWS_ENDPOINT_URL` | Endpoint do S3 (LocalStack em dev) | `http://localstack:4566` |
| `AWS_ACCESS_KEY_ID` | Chave de acesso (fake em dev/test) | `test` |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta (fake em dev/test) | `test` |
