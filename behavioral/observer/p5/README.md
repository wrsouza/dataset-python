# Live Dashboard (Observer) — P5

App Streamlit que publica métricas simultaneamente para o estado do
próprio dashboard (observador local) e para um tópico GCP Pub/Sub
(observadores remotos) — dois canais de fan-out independentes
acionados pelo mesmo `publish`.

## Objetivo pedagógico

Demonstrar o pattern **Observer** num cenário híbrido, espelhando
`observer/p4` (SNS) com GCP Pub/Sub: `PubSubMetricsPublisher` (Subject)
notifica observadores locais de forma síncrona e incondicional, e em
seguida publica o mesmo evento no Pub/Sub — que pode ter qualquer
número de assinantes externos sem que este código precise saber quais.

Elementos do pattern:
- **Subject (abstrato):** `MetricsPublisher` (`domain/interfaces.py`)
- **ConcreteSubject:** `PubSubMetricsPublisher` (`infrastructure/pubsub_publisher.py`)
- **Observer (abstrato):** `MetricsObserver` (`domain/interfaces.py`)
- **ConcreteObservers:** `DashboardStateObserver`, `EventLogObserver` (`infrastructure/observers.py`)

## Diagrama (ASCII)

```
"Simular atualização" (Streamlit)
        │
        ▼
PublishMetricUseCase.execute()
        │
        ▼
PubSubMetricsPublisher.publish()
        │
        ├──► DashboardStateObserver (atualiza st.session_state)
        │
        └──► GCP Pub/Sub topic (assinantes externos)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

App disponível em `http://localhost:8501`.

Sem emulador local do Pub/Sub: o publisher real (`google-cloud-pubsub`)
só é efetivamente alcançável com credenciais/projeto GCP válidos — sem
eles, a chamada de publish remoto falha silenciosamente do ponto de
vista do dashboard, mas o observador local (`DashboardStateObserver`)
sempre atualiza, pois é notificado antes da tentativa de publicação remota.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`app.py` é excluído do cálculo de cobertura (mesmo padrão dos demais
projetos Streamlit do dataset). Como não existe um equivalente do
`moto` para GCP, `PubSubMetricsPublisher` é testado contra um
`FakePubSubClient` mínimo em memória — mesma abordagem usada para os
fakes de Redis/RabbitMQ em outros projetos deste dataset.

## SOLID

- **SRP:** `DashboardStateObserver`/`EventLogObserver` cada um só reage ao evento de uma forma; `PubSubMetricsPublisher` só orquestra o fan-out local + a publicação remota.
- **OCP:** um novo observador local (ex.: alertas) é uma nova classe `MetricsObserver`, inscrita via `subscribe` — sem alterar `PubSubMetricsPublisher`.
- **LSP:** qualquer implementação de `MetricsPublisher`/`MetricsObserver` pode substituir as concretas nos use cases sem quebrar o contrato (ver `FakeMetricsPublisher` nos testes).
- **ISP:** `MetricsObserver` expõe só `on_metric_event`; `MetricsPublisher` só os três métodos que o domínio realmente precisa.
- **DIP:** os use cases dependem de `MetricsPublisher` (abstração), nunca de `PubSubMetricsPublisher` diretamente — injeção via construtor em `app.py`.
