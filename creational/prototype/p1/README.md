# Game Character Template System

> **Design Pattern:** Prototype
> **Categoria:** Creational
> **Framework:** FastAPI
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Prototype em um sistema de personagens de jogos.
O aluno aprenderá como `copy.deepcopy` cria cópias completamente independentes de objetos
complexos (com dicts e listas aninhados), e como um `PrototypeRegistry` centraliza o
gerenciamento de templates para evitar duplicação de código de criação.

## O Pattern em Ação

O Prototype permite criar personagens a partir de templates sem conhecer suas classes
concretas. A API recebe `POST /characters/clone/warrior` e o registry localiza o template,
chama `clone()` (que usa deepcopy internamente), aplica overrides e persiste no PostgreSQL.

| Papel do Pattern    | Classe                    | Arquivo                                      |
|---------------------|---------------------------|----------------------------------------------|
| Prototype (ABC)     | `Character`               | `src/characters/domain/interfaces.py`        |
| ConcretePrototype   | `WarriorTemplate`         | `src/characters/infrastructure/prototypes.py`|
| ConcretePrototype   | `MageTemplate`            | `src/characters/infrastructure/prototypes.py`|
| ConcretePrototype   | `RogueTemplate`           | `src/characters/infrastructure/prototypes.py`|
| PrototypeRegistry   | `CharacterTemplateRegistry` | `src/characters/infrastructure/prototypes.py`|
| Entity              | `CharacterRecord`         | `src/characters/domain/entities.py`          |

## Diagrama UML

```
<<abstract>>
Character (ABC)
+ clone() -> Character
+ apply_overrides(overrides: dict) -> None
+ name: str  [property]
+ template_name: str  [property]
+ stats: dict  [property]
+ skills: list  [property]
+ equipment: list  [property]
+ level: int  [property]
         |
         |  (extends BaseCharacter)
         |
         ├── WarriorTemplate
         │     + clone() -> WarriorTemplate   [uses copy.deepcopy]
         │
         ├── MageTemplate
         │     + clone() -> MageTemplate      [uses copy.deepcopy]
         │
         └── RogueTemplate
               + clone() -> RogueTemplate     [uses copy.deepcopy]

CharacterTemplateRegistry
- _templates: dict[str, Character]
+ register(name: str, template: Character) -> None
+ get(name: str) -> Character
+ clone(name: str, overrides: dict) -> Character   [get → clone → apply_overrides]
+ list_templates() -> list[str]
```

## deepcopy vs clone customizado

```python
import copy

warrior = WarriorTemplate()

# copy.deepcopy: clona recursivamente todos os objetos aninhados
deep = copy.deepcopy(warrior)
deep._stats["strength"] = 1
assert warrior.stats["strength"] == 18  # original inalterado ✓

# copy.copy (shallow): _stats seria compartilhado entre original e cópia!
# É por isso que clone() usa deepcopy internamente.
```

## Princípios SOLID Demonstrados

- **S — SRP:** `CharacterTemplateRegistry` gerencia templates. `CharacterRepository`
  persiste dados. `CloneCharacterUseCase` orquestra o fluxo. Cada classe tem um único motivo para mudar.
- **O — OCP:** Para adicionar `PaladinTemplate`, basta criar a classe e chamr
  `registry.register("paladin", PaladinTemplate())`. Nenhuma classe existente precisa ser modificada.

## Estrutura do Projeto

```
p1/
├── src/
│   ├── main.py                          ← FastAPI app + composição root
│   └── characters/
│       ├── domain/
│       │   ├── interfaces.py            ← Character ABC, CharacterRegistry ABC
│       │   └── entities.py             ← CharacterRecord, CloneRequest, erros
│       ├── application/
│       │   └── use_cases.py            ← CloneCharacterUseCase, etc.
│       └── infrastructure/
│           ├── prototypes.py           ← ConcretePrototypes + Registry
│           └── database.py             ← SQLAlchemy 2.0 async repository
├── tests/
│   ├── unit/
│   │   ├── test_prototypes.py          ← testa deepcopy vs clone
│   │   └── test_use_cases.py          ← testa use cases com mocks
│   └── integration/
│       └── test_api.py                 ← testa endpoints FastAPI
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
# API disponível em: http://localhost:8000/docs
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/unit/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável          | Descrição                       | Valor padrão                                    |
|-------------------|---------------------------------|-------------------------------------------------|
| `DATABASE_URL`    | URL de conexão PostgreSQL async | `postgresql+asyncpg://app:secret@db:5432/appdb` |
| `POSTGRES_USER`   | Usuário do banco                | `app`                                           |
| `POSTGRES_PASSWORD` | Senha do banco               | `secret`                                        |
| `POSTGRES_DB`     | Nome do banco                   | `appdb`                                         |
