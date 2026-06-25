# P2 — Event-driven Price Alert (Observer Pattern)

> **Design Pattern:** Observer
> **Categoria:** Behavioral
> **Framework:** Flask
> **Serviços:** Kafka

## Objetivo Pedagógico

Este projeto demonstra o padrão Observer em um sistema de alertas de preço orientado a
eventos. Clientes se inscrevem (`subscribe`) para receber notificações de mudança de
preço por e-mail, SMS ou webhook, e o Subject distribui os eventos via Kafka, mostrando
como o padrão se conecta com mensageria assíncrona em produção.

## O Pattern em Ação

| Papel do Pattern | Classe | Arquivo |
|-----------------|--------|---------|
| Subject (abstrato) | `PriceMonitor` | `src/price_alerts/domain/interfaces.py` |
| ConcreteSubject | `KafkaPriceMonitor` | `src/price_alerts/infrastructure/kafka_subject.py` |
| Observer (abstrato) | `PriceObserver` | `src/price_alerts/domain/interfaces.py` |
| ConcreteObserver | `EmailAlertObserver` | `src/price_alerts/infrastructure/notification_observers.py` |
| ConcreteObserver | `SmsAlertObserver` | `src/price_alerts/infrastructure/notification_observers.py` |
| ConcreteObserver | `WebhookAlertObserver` | `src/price_alerts/infrastructure/notification_observers.py` |
| Evento (Value Object) | `PriceEvent` | `src/price_alerts/domain/entities.py` |

`KafkaPriceMonitor.notify_price_change` publica o evento no tópico Kafka
`price-changes`; uma thread consumidora (`start_consumer`/`_consume_loop`)
lê o tópico e chama `_fan_out`, que percorre as `Subscription`s ativas que
ultrapassaram o `threshold` configurado e invoca `observer.on_price_change(event)`
em cada uma. Quando o broker Kafka não está acessível (como neste ambiente de
testes), o método cai automaticamente para fan-out direto em processo — o
contrato Subject/Observer permanece o mesmo nos dois casos.

## Diagrama UML (ASCII)

```
        ┌──────────────────────────────┐
        │       «interface»            │
        │        PriceMonitor          │   ← Subject
        │───────────────────────────────│
        │ +subscribe(obs, pid, thr)     │
        │ +unsubscribe(sub_id)          │
        │ +notify_price_change(...)     │
        └─────────────┬─────────────────┘
                       │ implements
        ┌──────────────▼─────────────────┐
        │      KafkaPriceMonitor          │   ← ConcreteSubject
        │──────────────────────────────────│
        │ - _subscriptions: dict           │
        │ - _observers: dict                │
        │ - _product_index: dict            │
        │ + start_consumer() / stop_consumer│
        └──────────────┬────────────────────┘
                        │ on_price_change(event)
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
  ┌───────────────┐ ┌──────────────┐ ┌───────────────────┐
  │ «interface»   │ │              │ │                    │
  │ PriceObserver │ │              │ │                    │
  │───────────────│ │              │ │                    │
  │+on_price_change│ │              │ │                    │
  │+observer_id   │ │              │ │                    │
  └──────┬────────┘ └──────────────┘ └────────────────────┘
         │ implements
   ┌─────┼─────────────┬───────────────────┐
   ▼                   ▼                   ▼
┌────────────────┐ ┌───────────────┐ ┌──────────────────────┐
│EmailAlert       │ │SmsAlert       │ │WebhookAlert           │
│Observer         │ │Observer       │ │Observer                │
│(ConcreteObserver)│ │(ConcreteObserver)│ │(ConcreteObserver)   │
└─────────────────┘ └───────────────┘ └────────────────────────┘
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** adicionar um novo canal de notificação (ex.: push
  notification, Slack) significa apenas criar uma nova classe que implementa
  `PriceObserver` em `infrastructure/`. `KafkaPriceMonitor` e os use cases não
  precisam ser alterados — o `CHANNEL_FACTORIES` em `main.py` é o único ponto
  de composição que cresce, e mesmo isso é só registro de uma fábrica, não
  modificação de lógica existente.
- **D — Dependency Inversion:** os use cases em `application/use_cases.py`
  (`RegisterPriceAlertUseCase`, `ProcessPriceUpdateUseCase`, etc.) recebem um
  `PriceMonitor` (abstração) via construtor — nunca instanciam
  `KafkaPriceMonitor` diretamente. Isso permite testar com mocks sem broker.
- **S — Single Responsibility:** cada `ConcreteObserver` cuida de um único
  canal (e-mail, SMS ou webhook); `KafkaPriceMonitor` cuida apenas de
  orquestrar inscrições e publicar/consumir do Kafka; os use cases cuidam
  apenas de validação e delegação.
- **I — Interface Segregation:** `PriceObserver` tem só dois membros
  (`on_price_change`, `observer_id`); `PriceMonitor` tem três métodos focados
  em inscrição/notificação, sem métodos que implementações não usem.
- **L — Liskov Substitution:** qualquer `PriceObserver` concreto pode ser
  passado para `KafkaPriceMonitor.subscribe` sem alterar o comportamento do
  Subject; nenhum observer lança exceções fora do contrato da base.

## Estrutura do Projeto

```
observer/p2/
├── src/
│   └── price_alerts/
│       ├── domain/
│       │   ├── interfaces.py     ← PriceMonitor (Subject ABC), PriceObserver (Observer ABC)
│       │   └── entities.py       ← PriceEvent, Subscription, AlertRecord
│       ├── application/
│       │   └── use_cases.py      ← Register/Remove/List alerts, ProcessPriceUpdate
│       ├── infrastructure/
│       │   ├── kafka_subject.py            ← KafkaPriceMonitor (ConcreteSubject)
│       │   └── notification_observers.py   ← Email/SMS/Webhook (ConcreteObservers)
│       └── main.py               ← Flask app (composition root)
├── tests/
│   ├── unit/
│   └── integration/
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

# 2. Subir app + Kafka + Zookeeper
docker-compose up --build

# 3. Cadastrar um alerta (subscribe)
curl -X POST http://localhost:8000/alerts \
  -H "Content-Type: application/json" \
  -d '{"channel": "email", "target": "buyer@example.com", "product_id": "SKU-1", "threshold": 5.0}'

# 4. Listar alertas
curl http://localhost:8000/alerts

# 5. Remover um alerta (unsubscribe)
curl -X DELETE http://localhost:8000/alerts/<subscription_id>

# 6. Simular uma mudança de preço (publica no Kafka / fan-out direto)
curl -X POST http://localhost:8000/prices/SKU-1 \
  -H "Content-Type: application/json" \
  -d '{"old_price": 100.0, "new_price": 110.0}'
```

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| POST | `/alerts` | Cadastrar alerta (subscribe) — `channel`, `target`, `product_id`, `threshold` |
| GET | `/alerts` | Listar alertas cadastrados |
| DELETE | `/alerts/<subscription_id>` | Remover alerta (unsubscribe) |
| POST | `/prices/<product_id>` | Simular evento de preço — `old_price`, `new_price` |
| GET | `/health` | Health check |

## Rodar os Testes

```bash
# Testes unitários (sem serviços externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (via Flask test client, sem broker real)
docker-compose run --rm app pytest tests/integration/ -v

# Todos os testes com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

> **Nota sobre testes sem Kafka real:** este ambiente de desenvolvimento não
> possui um broker Kafka disponível para os testes automatizados. Os testes
> unitários e de integração usam o fallback documentado em
> `KafkaPriceMonitor._publish_to_kafka`: quando o broker está inacessível, o
> Subject cai automaticamente para fan-out direto em processo
> (`_fan_out`), preservando o mesmo contrato Subject/Observer. Isso permite
> validar toda a lógica de negócio sem exigir `docker-compose up` do Kafka.
> A integração real com Kafka é validada manualmente ao rodar
> `docker-compose up` (passo "Como Rodar" acima).

## Verificar Qualidade do Código

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `KAFKA_BOOTSTRAP_SERVERS` | Endereço do broker Kafka | `kafka:9092` |
| `LOG_LEVEL` | Nível de log da aplicação | `INFO` |
