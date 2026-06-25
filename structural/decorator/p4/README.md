# Observability Decorator

> **Design Pattern:** Decorator | **Categoria:** Structural
> **Framework:** CLI (Typer) | **Serviços:** AWS CloudWatch (Metrics + Logs)

## Objetivo Pedagógico

Demonstrar o pattern **Decorator** instrumentando uma operação de negócio simples
(processamento de pedidos) com camadas de observabilidade empilháveis — métricas,
tracing e captura de erros — sem alterar o código da regra de negócio original.

## O Pattern Aplicado

- **Component (`OrderProcessor`)** — interface comum implementada tanto pelo
  componente concreto quanto pelos decoradores (`src/observability/domain/interfaces.py`).
- **ConcreteComponent (`ProcessOrderUseCase`)** — lógica de negócio pura: valida e
  calcula o total do pedido, sem qualquer conhecimento de observabilidade
  (`src/observability/application/use_cases.py`).
- **Decorator base (`ObservabilityDecorator`)** — guarda referência ao componente
  envolvido e delega por padrão (`src/observability/infrastructure/observability_decorator.py`).
- **ConcreteDecorators:**
  - `MetricsDecorator` — publica duração e contagem de chamadas no CloudWatch Metrics.
  - `TracingDecorator` — exporta um span (duração + atributos) para CloudWatch Logs.
  - `ErrorCaptureDecorator` — reporta exceções como métrica de erro e relança.

As camadas são compostas em `src/observability/infrastructure/factory.py`,
podendo ser empilhadas em qualquer ordem/combinação sem modificar o componente
de negócio nem os outros decoradores (Open/Closed).

## Diagrama UML (ASCII)

```
                  <<interface>>
                  OrderProcessor
                  + process(req): OrderResult
                        ^
                        |
        ----------------------------------------
        |                                       |
ProcessOrderUseCase                  ObservabilityDecorator
(ConcreteComponent)                  - _wrapped: OrderProcessor
                                      + process(req): OrderResult
                                              ^
                        ------------------------------------------
                        |                |                       |
              MetricsDecorator  TracingDecorator      ErrorCaptureDecorator
              - _publisher      - _exporter            - _reporter
              (CloudWatchMetricsPublisher) (CloudWatchTraceExporter) (CloudWatchErrorReporter)

Composição (factory.py):
  ErrorCaptureDecorator(
    TracingDecorator(
      MetricsDecorator(
        ProcessOrderUseCase()
      )
    )
  )
```

## Princípios SOLID Demonstrados

- **O (Open/Closed):** novos comportamentos de observabilidade (ex.: um futuro
  `AuditDecorator`) são adicionados criando uma nova subclasse de
  `ObservabilityDecorator`, sem modificar `ProcessOrderUseCase` nem os
  decoradores existentes.
- **L (Liskov Substitution):** qualquer `ObservabilityDecorator` pode substituir
  um `OrderProcessor` em qualquer ponto da cadeia — todos respeitam o mesmo
  contrato (`process(request) -> OrderResult`), incluindo as mesmas exceções
  de domínio propagadas, nunca abafadas.
- **D (Dependency Inversion):** os decoradores dependem de `Protocol`s
  (`MetricsPublisher`, `TraceExporter`, `ErrorReporter`) definidos em
  `domain/interfaces.py`, não diretamente de `boto3` ou do CloudWatch — os
  adapters concretos ficam isolados em `infrastructure/`.
- **S (Single Responsibility):** cada decorador trata de exatamente um
  aspecto de observabilidade (métricas, tracing ou erros).

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

O serviço `app` processa um pedido de exemplo via CLI contra um LocalStack
simulando CloudWatch. Para rodar comandos arbitrários:

```bash
docker-compose run --rm app python -m observability.cli process-order \
  --customer-id cust-42 --item-sku SKU-9 --quantity 3 --unit-price 12.50
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente (sem Docker):

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```
