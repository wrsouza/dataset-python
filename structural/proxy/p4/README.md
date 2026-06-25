# Remote File Proxy

> **Design Pattern:** Proxy (Virtual + Caching Proxy)
> **Categoria:** Structural
> **Framework:** CLI (Typer)
> **Serviços:** AWS S3 (testado com `moto`, executável manualmente contra LocalStack)

## Objetivo Pedagógico

Demonstrar como um **Proxy** pode substituir transparentemente o objeto real
em todo o código cliente, adiando uma operação custosa (download de um
arquivo do S3) até o primeiro acesso (**Virtual Proxy** / lazy loading) e
evitando downloads repetidos através de um **cache local** (**Caching
Proxy**). O cliente (a CLI) nunca importa boto3 nem decide quando o download
acontece -- ele apenas chama `.read()` em algo que satisfaz `FileResource`.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|---|---|---|
| Subject (interface) | `FileResource` (Protocol) | `src/remote_files/domain/interfaces.py` |
| RealSubject | `RealS3File` | `src/remote_files/infrastructure/real_s3_file.py` |
| Proxy | `RemoteFileProxy` | `src/remote_files/infrastructure/remote_file_proxy.py` |
| Client | comandos Typer | `src/cli/main.py` |

## Diagrama UML (ASCII)

```
                 «Protocol»
                FileResource
              +------------------+
              | read() -> bytes  |
              | exists() -> bool |
              | size: int        |
              | key: str         |
              +------------------+
                 ^            ^
                 |            |
   +-------------+--+      +--+----------------+
   | RealS3File      |      | RemoteFileProxy   |
   |-----------------|      |-------------------|
   | read()  -> S3   |<-----| _real_subject     |
   | exists() -> S3  |      | _cached_content    |
   | size -> S3 HEAD |      | read() (lazy+cache)|
   +-----------------+      | invalidate()       |
                            | cache_stats()      |
                            +--------------------+
                                      ^
                                      |
                              +---------------+
                              |  CLI (Typer)  |
                              |  use cases    |
                              +---------------+
```

## Por que o Cliente Nunca Sabe se Fala com o Proxy ou com o RealSubject

`ReadFileUseCase`, `CheckFileExistsUseCase` e a CLI dependem apenas do
Protocol `FileResource`. Em produção, a CLI sempre injeta um
`RemoteFileProxy` envolvendo um `RealS3File` -- mas qualquer código que
recebesse diretamente um `RealS3File` continuaria funcionando sem alteração
(Liskov Substitution). Isso é o que permite, por exemplo, testar os use
cases com um `FakeFileResource` em memória (ver `tests/conftest.py`), sem
nenhum mock de rede.

## Princípios SOLID Demonstrados

- **SRP**: `RealS3File` só sabe falar com S3; `RemoteFileProxy` só sabe fazer
  lazy loading + cache; a CLI só sabe traduzir argumentos em chamadas de use
  case. Nenhuma dessas classes mistura responsabilidades.
- **OCP**: novos tipos de proxy (ex.: um `PermissionCheckingProxy` que valida
  ACLs antes de delegar) podem ser adicionados implementando o mesmo
  `FileResource`, sem tocar em `RealS3File` nem no código cliente existente.
- **LSP**: `tests/integration/test_proxy_with_s3.py` prova que o proxy pode
  substituir o RealSubject em qualquer lugar -- o comportamento observável
  (`read()`, `exists()`, `size`, `key`) é idêntico, só a performance muda.
- **DIP**: `src/remote_files/application/use_cases.py` e `src/cli/main.py`
  importam apenas `FileResource`/use cases -- nunca `boto3` diretamente. A
  prova está em `tests/unit/test_use_cases.py`, onde os use cases rodam
  100% contra um `FakeFileResource`, sem nenhuma dependência de S3.

## Como Rodar

```bash
cp .env.example .env
docker-compose build
docker-compose up -d localstack
docker-compose run --rm app python -m src.cli read notes/todo.txt --bucket my-bucket
docker-compose run --rm app python -m src.cli check notes/todo.txt --bucket my-bucket
docker-compose run --rm app python -m src.cli stats notes/todo.txt --bucket my-bucket
docker-compose down
```

> Os testes automatizados usam `moto` (mock de S3 em memória) e **não**
> dependem do serviço `localstack` do compose. O LocalStack é útil apenas
> para rodar a CLI manualmente contra um S3 local, sem credenciais reais da
> AWS.

## Comandos da CLI

| Comando | Descrição |
|---|---|
| `read KEY [--bucket BUCKET]` | Lê o conteúdo do arquivo via proxy (lazy) e imprime o tamanho. |
| `check KEY [--bucket BUCKET]` | Verifica existência/tamanho sem baixar o conteúdo. |
| `stats KEY [--bucket BUCKET]` | Lê o mesmo arquivo duas vezes e imprime hits/misses/bytes economizados do cache. |

O bucket pode ser informado via `--bucket/-b` ou pela variável de ambiente
`S3_BUCKET`.

## Rodar os Testes

```bash
pip install -e ".[dev]"
black --check src/ tests/
ruff check src/ tests/
mypy src/
pytest --cov=src --cov-report=term-missing
```
