# Docker-Compose Generator CLI

> **Design Pattern:** Builder
> **Categoria:** Creational
> **Framework:** CLI Typer
> **Serviços:** Nenhum (gera especificações docker-compose.yml para terceiros; não há serviços externos reais)

## Objetivo Pedagógico

Este projeto demonstra o padrão Builder construindo passo a passo a especificação de um
arquivo `docker-compose.yml` (serviços, volumes, redes) através de uma interface fluente
de method chaining, sem acoplar a CLI à lógica de montagem de cada stack. O aluno aprende
a separar a construção de um objeto complexo (`ComposeFile`) de sua representação final
(YAML), e a usar um Director para encapsular sequências de construção reutilizáveis
("presets") como `web-postgres-redis`, `fastapi-postgres`, `django-redis` e `kafka-stack`.

**Importante:** o `docker-compose.yml` gerado pela ferramenta (a saída do Builder) é um
artefato diferente do `docker-compose.yml` que existe na raiz deste projeto — este último
apenas executa a CLI dentro de um container, ele não é o produto do pattern.

## O Pattern em Ação

| Papel do Pattern    | Classe                                                          | Arquivo                                                  |
|---------------------|------------------------------------------------------------------|-----------------------------------------------------------|
| Builder (interface) | `DockerComposeBuilder`                                          | `src/compose_builder/domain/interfaces.py`                |
| ConcreteBuilder     | `WebAppComposeBuilder`, `DataPipelineComposeBuilder`, `MicroservicesComposeBuilder` | `src/compose_builder/infrastructure/builders.py` |
| Director            | `WebPostgresRedisDirector`, `FastAPIWithPostgresDirector`, `DjangoWithRedisDirector`, `KafkaStackDirector` | `src/compose_builder/application/directors.py` |
| Product             | `ComposeFile` (+ `ServiceDefinition`, `VolumeDefinition`, `NetworkDefinition`) | `src/compose_builder/domain/entities.py` |
| Serializer (infra)  | `YamlComposeSerializer`                                          | `src/compose_builder/infrastructure/yaml_writer.py`        |
| Use Case            | `GenerateComposeUseCase`, `DataPipelinePresetUseCase`            | `src/compose_builder/application/use_cases.py`             |
| CLI                 | Typer `app` (`list-presets`, `generate`, `print`)                | `src/compose_builder/main.py`                              |

## Diagrama UML (ASCII)

```
                  <<abstract>>
                DockerComposeBuilder
        + set_version(version) -> Self
        + add_service(name, image, ...) -> Self
        + add_volume(name, driver) -> Self
        + add_network(name, driver) -> Self
        + build() -> ComposeFile
        + reset() -> None
                     ▲
                     │ implementa
     ┌───────────────┼───────────────────────┐
     │               │                       │
WebAppComposeBuilder DataPipelineComposeBuilder MicroservicesComposeBuilder
(rede "web" padrão)  (rede "data", restart     (rede "microservices",
                      on-failure)               healthcheck padrão)

     ┌──────────────────────────────────────────────────┐
     │                      usa / constrói via           │
     ▼                                                    │
WebPostgresRedisDirector ───┐                              │
FastAPIWithPostgresDirector ─┤── recebe DockerComposeBuilder no construtor
DjangoWithRedisDirector ─────┤   e chama os passos do builder em sequência
KafkaStackDirector ─────────┘   para montar um preset conhecido
     │
     │ retorna
     ▼
ComposeFile (Product)
  - version: str
  - services: dict[str, ServiceDefinition]
  - volumes: dict[str, VolumeDefinition]
  - networks: dict[str, NetworkDefinition]
  + to_dict() -> dict

     │ serializado por
     ▼
YamlComposeSerializer
  + to_yaml(compose) -> str
  + write(compose, path) -> Path
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** `WebAppComposeBuilder` (e demais ConcreteBuilders) só
  sabem acumular `ServiceDefinition`/`VolumeDefinition`/`NetworkDefinition` e montar o
  `ComposeFile`. Os Directors (`WebPostgresRedisDirector`, `KafkaStackDirector`, etc.) só
  sabem a sequência de passos de cada preset — eles não sabem serializar YAML nem
  persistir em disco, isso é responsabilidade exclusiva de `YamlComposeSerializer`.
- **O — Open/Closed:** Para adicionar um novo preset (ex.: um stack "observability"), basta
  criar um novo Director que recebe um `DockerComposeBuilder` e chama seus métodos —
  nenhuma classe existente (`DockerComposeBuilder`, builders concretos, outros Directors)
  precisa ser modificada. O mesmo vale para novos tipos de stack: cria-se um novo
  ConcreteBuilder com seus próprios defaults sem alterar `_BaseComposeBuilder`.
- **D — Dependency Inversion:** Os Directors dependem da abstração `DockerComposeBuilder`,
  nunca de uma classe concreta — o builder concreto é injetado no construtor
  (`WebPostgresRedisDirector(WebAppComposeBuilder())`). `GenerateComposeUseCase` depende
  da interface `DockerComposeBuilder` e do serializer, escolhendo a implementação concreta
  apenas em um ponto único de composição (`_builder_for`).

## Estrutura do Projeto

```
p5/
├── src/
│   └── compose_builder/
│       ├── domain/
│       │   ├── interfaces.py    ← DockerComposeBuilder (ABC)
│       │   └── entities.py      ← ServiceDefinition, VolumeDefinition, NetworkDefinition, ComposeFile
│       ├── application/
│       │   ├── directors.py     ← Directors (presets)
│       │   └── use_cases.py     ← GenerateComposeUseCase, DataPipelinePresetUseCase
│       ├── infrastructure/
│       │   ├── builders.py      ← ConcreteBuilders
│       │   └── yaml_writer.py   ← YamlComposeSerializer (PyYAML)
│       ├── main.py              ← Typer CLI
│       └── __main__.py          ← python -m compose_builder
├── tests/
│   ├── unit/                    ← builders, directors, entities, YAML, use cases, CLI (sem tocar disco)
│   └── integration/             ← gera YAML real em tmp_path e faz parse de volta
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável    | Descrição                              | Padrão |
|-------------|------------------------------------------|--------|
| `LOG_LEVEL` | Nível de log da CLI (não usa serviços externos) | `INFO` |

## Exemplos de Uso

```bash
# Listar presets disponíveis
python -m compose_builder list-presets

# Gerar um docker-compose.yml a partir de um preset e salvar em arquivo
python -m compose_builder generate --preset web-postgres-redis --output docker-compose.generated.yml

# Gerar o preset FastAPI + Postgres (+ Redis)
python -m compose_builder generate --preset fastapi-postgres --output fastapi-stack.yml

# Imprimir o YAML gerado direto no stdout, sem escrever em disco
python -m compose_builder print --preset kafka-stack
```
