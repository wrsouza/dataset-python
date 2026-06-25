# UI Component Factory Multiplataforma

> **Design Pattern:** Abstract Factory
> **Categoria:** Creational
> **Framework:** Flask
> **Serviços:** PostgreSQL

## Objetivo Pedagógico

Este projeto demonstra o padrão Abstract Factory em uma API Flask que renderiza
famílias de componentes UI (Button, Input, Modal) para diferentes plataformas
(Windows, Linux, macOS). O aluno aprende a criar famílias de objetos relacionados
sem acoplar o código cliente às classes concretas, e como adicionar novas plataformas
sem modificar nenhum código existente — princípio Open/Closed em ação.

## O Pattern em Ação

A AbstractFactory (`UIComponentFactory`) declara métodos para criar cada componente.
Cada ConcreteFactory (`WindowsUIFactory`, `LinuxUIFactory`, `MacUIFactory`) produz
componentes coesos com o estilo/comportamento de sua plataforma. O Client
(`RenderUIFamilyUseCase`) usa apenas a abstração — nunca conhece a fábrica concreta.

| Papel do Pattern     | Classe                    | Arquivo                                        |
|----------------------|---------------------------|------------------------------------------------|
| AbstractFactory      | `UIComponentFactory`      | `src/ui_factory/domain/interfaces.py`          |
| ConcreteFactory      | `WindowsUIFactory`        | `src/ui_factory/infrastructure/factories.py`   |
| ConcreteFactory      | `LinuxUIFactory`          | `src/ui_factory/infrastructure/factories.py`   |
| ConcreteFactory      | `MacUIFactory`            | `src/ui_factory/infrastructure/factories.py`   |
| AbstractProduct      | `Button`, `Input`, `Modal`| `src/ui_factory/domain/interfaces.py`          |
| ConcreteProduct      | `WindowsButton`, etc.     | `src/ui_factory/infrastructure/factories.py`   |
| Client               | `RenderUIFamilyUseCase`   | `src/ui_factory/application/use_cases.py`      |

## Diagrama UML

```
<<abstract>>
UIComponentFactory
+ create_button() -> Button
+ create_input()  -> Input
+ create_modal()  -> Modal
        |
        ├── WindowsUIFactory
        │     + create_button() -> WindowsButton  (Fluent Design)
        │     + create_input()  -> WindowsInput
        │     + create_modal()  -> WindowsModal
        │
        ├── LinuxUIFactory
        │     + create_button() -> LinuxButton    (GTK/Adwaita)
        │     + create_input()  -> LinuxInput
        │     + create_modal()  -> LinuxModal
        │
        └── MacUIFactory
              + create_button() -> MacButton      (Aqua)
              + create_input()  -> MacInput
              + create_modal()  -> MacModal

<<Protocol>>           <<Protocol>>           <<Protocol>>
Button                 Input                  Modal
+ render()             + render()             + render()
+ get_style()          + get_validation_mode()+ get_animation()
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Adicionar suporte a Android/iOS exige apenas criar
  `AndroidUIFactory` + `AndroidButton/Input/Modal` em `infrastructure/factories.py`.
  Nenhum código existente — rotas Flask, use cases, interfaces — precisa mudar.

- **D — Dependency Inversion:** `RenderUIFamilyUseCase` (alto nível) depende de
  `UIComponentFactory` (abstração), nunca de `WindowsUIFactory` (implementação).
  As rotas Flask injetam a factory concreta no use case — a lógica jamais instancia
  diretamente uma classe concreta.

## Estrutura do Projeto

```
p1/
├── src/
│   └── ui_factory/
│       ├── app.py               ← Flask app + rotas (composition root)
│       ├── domain/
│       │   ├── interfaces.py    ← UIComponentFactory, Button, Input, Modal (ABCs/Protocols)
│       │   └── entities.py      ← ComponentFamilyResponse, ComponentUsageLog
│       ├── application/
│       │   └── use_cases.py     ← RenderUIFamilyUseCase, ListUsageLogsUseCase (Client)
│       └── infrastructure/
│           └── factories.py     ← Concrete factories/products + PostgreSQL repository
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_use_cases.py
│   └── integration/
│       └── test_integration.py
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
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir todos os serviços
docker-compose up --build

# 3. Testar a API
curl http://localhost:5000/components/windows
curl http://localhost:5000/components/linux
curl http://localhost:5000/components/mac
curl http://localhost:5000/logs
```

## Rodar os Testes

```bash
# Testes unitários (sem PostgreSQL)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (com PostgreSQL)
docker-compose run --rm app pytest tests/integration/ -v

# Todos com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável            | Descrição                          | Valor padrão                              |
|---------------------|------------------------------------|-------------------------------------------|
| `DATABASE_URL`      | URL de conexão PostgreSQL          | `postgresql://app:secret@db:5432/appdb`   |
| `POSTGRES_USER`     | Usuário do banco                   | `app`                                     |
| `POSTGRES_PASSWORD` | Senha do banco                     | `secret`                                  |
| `POSTGRES_DB`       | Nome do banco                      | `appdb`                                   |
| `FLASK_ENV`         | Ambiente Flask                     | `development`                             |

## Endpoints da API

| Método | Rota                    | Descrição                                      |
|--------|-------------------------|------------------------------------------------|
| GET    | `/components/{platform}`| Renderiza família de componentes da plataforma |
| GET    | `/logs`                 | Lista todos os logs de uso                     |
| GET    | `/health`               | Health check                                   |

Plataformas suportadas: `windows`, `linux`, `mac`
