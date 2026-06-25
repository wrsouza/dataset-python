# UI Component Decorator

> **Design Pattern:** Decorator (GoF Structural)
> **Categoria:** Structural
> **Framework:** Streamlit
> **Serviços:** (nenhum externo)

## Objetivo Pedagógico

Demonstra o padrão Decorator GoF aplicado a componentes de UI. O aluno aprenderá
como empilhar camadas visuais independentes (borda, sombra, tooltip, badge,
seção colapsável) sobre um widget base, escolhendo a ordem em runtime, sem
alterar o widget original nem os decoradores já existentes (OCP).

## O Pattern em Ação

| Papel do Pattern    | Classe                     | Arquivo                                          |
|---------------------|-----------------------------|---------------------------------------------------|
| Component (ABC)     | `UIComponent`               | `src/ui_components/domain/interfaces.py`          |
| Decorator ABC       | `UIComponentDecorator`      | `src/ui_components/domain/interfaces.py`          |
| ConcreteComponent   | `TextWidget`                | `src/ui_components/infrastructure/widgets.py`     |
| ConcreteDecorator   | `BorderDecorator`           | `src/ui_components/infrastructure/decorators.py`  |
| ConcreteDecorator   | `ShadowDecorator`           | `src/ui_components/infrastructure/decorators.py`  |
| ConcreteDecorator   | `TooltipDecorator`          | `src/ui_components/infrastructure/decorators.py`  |
| ConcreteDecorator   | `BadgeDecorator`            | `src/ui_components/infrastructure/decorators.py`  |
| ConcreteDecorator   | `CollapsibleDecorator`      | `src/ui_components/infrastructure/decorators.py`  |

## Diagrama UML — Cadeia de Decoradores

```
<<abstract>>
UIComponent
+ render() -> str
+ describe() -> str
        |
        ├── TextWidget                  (ConcreteComponent)
        │     + render(), describe()
        │
        └── UIComponentDecorator       (Decorator ABC)
              - _wrapped: UIComponent
              + render()/describe() -> delegates to _wrapped
                    |
                    ├── BorderDecorator
                    │     adiciona borda colorida
                    │
                    ├── ShadowDecorator
                    │     adiciona box-shadow
                    │
                    ├── TooltipDecorator
                    │     adiciona atributo title (hover)
                    │
                    ├── BadgeDecorator
                    │     fixa selo (ex: "NEW", "HOT")
                    │
                    └── CollapsibleDecorator
                          envolve em <details>/<summary>

Composição em runtime (outer -> inner), escolhida pelo usuário na sidebar:
  BadgeDecorator(
    ShadowDecorator(
      BorderDecorator(
        TextWidget()
      )
    )
  )
```

## Composição em Código

```python
# src/ui_components/application/use_cases.py
widget = TextWidget(spec)
widget = BorderDecorator(widget)
widget = ShadowDecorator(widget)
widget = BadgeDecorator(widget, "NEW")

# A app Streamlit permite escolher decoradores e ordem interativamente
# (src/ui_components/app.py -> _build_widget_from_selection)
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Um novo efeito visual (ex: `PulseDecorator`) é uma nova
  classe em `infrastructure/decorators.py` — nenhuma classe existente
  (`UIComponent`, `TextWidget`, demais decoradores) precisa ser alterada.
- **S — Single Responsibility:** Cada decorador adiciona exatamente uma
  preocupação visual (borda, sombra, tooltip, badge ou colapsabilidade).
- **D — Dependency Inversion:** `UIComponentDecorator` depende da abstração
  `UIComponent`, não de `TextWidget` nem de nenhum decorador concreto — por
  isso decoradores podem envolver outros decoradores livremente.

## Estrutura do Projeto

```
p5/
├── src/
│   └── ui_components/
│       ├── app.py                          ← app Streamlit (composition root da UI)
│       ├── domain/
│       │   ├── interfaces.py               ← UIComponent ABC, UIComponentDecorator ABC
│       │   └── entities.py                 ← WidgetSpec, InvalidDecorationError
│       ├── application/
│       │   └── use_cases.py               ← build_*_widget() — composições prontas
│       └── infrastructure/
│           ├── widgets.py                 ← TextWidget (ConcreteComponent)
│           └── decorators.py              ← Border, Shadow, Tooltip, Badge, Collapsible
├── tests/
│   ├── conftest.py
│   ├── unit/test_widgets.py
│   ├── unit/test_decorators.py
│   ├── unit/test_use_cases.py
│   └── integration/test_app_composition.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# App: http://localhost:8501
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest tests/unit/ -v
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável                    | Descrição                          | Padrão    |
|------------------------------|-------------------------------------|-----------|
| `STREAMLIT_SERVER_PORT`     | Porta do servidor Streamlit         | `8501`    |
| `STREAMLIT_SERVER_ADDRESS`  | Endereço de bind do servidor        | `0.0.0.0` |
| `LOG_LEVEL`                 | Nível de log da aplicação           | `INFO`    |
