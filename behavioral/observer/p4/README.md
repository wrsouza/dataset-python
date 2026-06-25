# Cloud Event Notifier (Observer) — P4

CLI Typer que publica eventos simultaneamente para observadores locais
(stdout) e para um tópico AWS SNS — dois canais de fan-out
independentes acionados pelo mesmo `publish`.

## Objetivo pedagógico

Demonstrar o pattern **Observer** num cenário híbrido: `SnsCloudEventPublisher`
(Subject) notifica observadores locais (`CloudEventObserver`) de forma
síncrona e incondicional, e em seguida publica o mesmo evento no SNS —
o canal remoto, que por sua vez pode ter qualquer número de assinantes
externos (e-mail, SQS, Lambda) sem que este código precise saber quais.

Elementos do pattern:
- **Subject (abstrato):** `CloudEventPublisher` (`domain/interfaces.py`)
- **ConcreteSubject:** `SnsCloudEventPublisher` (`infrastructure/sns_publisher.py`)
- **Observer (abstrato):** `CloudEventObserver` (`domain/interfaces.py`)
- **ConcreteObservers:** `ConsoleObserver`, `EventLogObserver` (`infrastructure/observers.py`)

## Diagrama (ASCII)

```
PublishEventUseCase.execute()
        │
        ▼
SnsCloudEventPublisher.publish()
        │
        ├──► observadores locais (ConsoleObserver, EventLogObserver, ...)
        │
        └──► AWS SNS topic (assinantes externos: e-mail, SQS, Lambda)
```

## Como rodar

```bash
cp .env.example .env
docker-compose run --rm app python -m cloud_event_notifier.main order.created '{"order_id": "o1"}'
```

### Comandos

| Comando   | Descrição                                                |
|-----------|------------------------------------------------------------|
| `publish` | Publica um evento (tipo + payload JSON) localmente e no SNS |

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`SnsCloudEventPublisher` é testado com `moto` (sem rede real); a CLI é
testada via `typer.testing.CliRunner` com um tópico SNS fake criado
para cada teste.

## SOLID

- **SRP:** `ConsoleObserver`/`EventLogObserver` cada um só reage ao evento de uma forma; `SnsCloudEventPublisher` só orquestra o fan-out local + a publicação remota.
- **OCP:** um novo observador local (ex.: métricas) é uma nova classe `CloudEventObserver`, inscrita via `subscribe` — sem alterar `SnsCloudEventPublisher`.
- **LSP:** qualquer implementação de `CloudEventPublisher`/`CloudEventObserver` pode substituir as concretas nos use cases sem quebrar o contrato (ver `FakeCloudEventPublisher` nos testes).
- **ISP:** `CloudEventObserver` expõe só `on_cloud_event`; `CloudEventPublisher` só os três métodos que o domínio realmente precisa.
- **DIP:** `PublishEventUseCase` depende de `CloudEventPublisher` (abstração), nunca de `SnsCloudEventPublisher` diretamente — injeção via construtor em `main.py`.
