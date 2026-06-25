# Messaging Protocol Adapter

> **Design Pattern:** Adapter
> **Categoria:** Structural
> **Framework:** CLI Typer
> **Serviços:** RabbitMQ, Kafka
> **Domínio:** messaging_adapter

## Objetivo Pedagógico

Demonstra como o padrão Adapter permite que código cliente (comandos CLI,
casos de uso) publique e consuma mensagens em RabbitMQ e Kafka através de
uma única interface `MessageBroker`, sem nunca importar `pika` ou
`kafka-python` diretamente. O aluno verá como adicionar um terceiro broker
(ex: AWS SQS) exige apenas um novo Adapter — zero alterações no código
existente.

## O Pattern em Ação

| Papel do Pattern              | Classe                     | Arquivo                                              |
|--------------------------------|----------------------------|-------------------------------------------------------|
| Target (interface desejada)    | `MessageBroker` (Protocol) | `src/messaging_adapter/domain/interfaces.py`          |
| Adaptee RabbitMQ               | `pika` (lib externa)       | usado em `infrastructure/rabbitmq_adapter.py`          |
| Adaptee Kafka                  | `kafka-python` (lib externa) | usado em `infrastructure/kafka_adapter.py`           |
| Adapter RabbitMQ               | `RabbitMQAdapter`          | `src/messaging_adapter/infrastructure/rabbitmq_adapter.py` |
| Adapter Kafka                  | `KafkaAdapter`             | `src/messaging_adapter/infrastructure/kafka_adapter.py`    |
| Entidade compartilhada         | `Message`                  | `src/messaging_adapter/domain/entities.py`             |
| Client                         | CLI Typer + Use Cases      | `main.py`, `application/use_cases.py`                  |

## Diagrama UML (ASCII)

```
<<Protocol>>                         (Target)
MessageBroker
+ connect() -> None
+ publish(topic: str, message: Message) -> None
+ consume(config: ConsumeConfig) -> Iterator[Message]
+ close() -> None
        ^                                   ^
        |                                   |
  RabbitMQAdapter                     KafkaAdapter
  (Adapter)                           (Adapter)
        |                                   |
        v                                   v
  pika.BlockingConnection             kafka.KafkaProducer
  channel.basic_publish               kafka.KafkaConsumer
  channel.basic_get                   producer.send / consumer.poll
  (Adaptee: RabbitMQ)                 (Adaptee: Kafka)

Client (Typer CLI / Use Cases) -----> MessageBroker (Protocol only)

<<dataclass, frozen>>
Message                              <- shared across every Adapter
+ topic: str
+ value: bytes
+ key: str | None
+ headers: dict[str, str]
+ timestamp: datetime | None
```

Cada Adapter traduz a API nativa e incompatível do seu broker (pika é
channel/exchange/queue/basic_publish; kafka-python é producer.send /
consumer.poll) para o contrato único `MessageBroker`. O código cliente
nunca sabe qual biblioteca nativa está por trás do Adapter selecionado.

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** `RabbitMQAdapter` só traduz a API do
  pika; `KafkaAdapter` só traduz a API do kafka-python. Nenhum dos dois
  conhece o outro.
- **O — Open/Closed:** adicionar um broker novo (ex: AWS SQS) = criar
  `SQSAdapter` implementando `MessageBroker` e registrar em
  `BROKER_REGISTRY` (`infrastructure/registry.py`). Zero alterações em
  `RabbitMQAdapter`, `KafkaAdapter` ou no Protocol `MessageBroker`.
- **D — Dependency Inversion:** `main.py` (CLI) e
  `application/use_cases.py` dependem exclusivamente do Protocol
  `MessageBroker`. Nenhuma dessas camadas importa `pika` ou
  `kafka-python`.
- **I — Interface Segregation:** `MessageBroker` tem apenas 4 métodos —
  `connect`, `publish`, `consume`, `close` — o mínimo viável para um
  cliente de mensageria.
- **L — Liskov Substitution:** `RabbitMQAdapter` e `KafkaAdapter` são
  intercambiáveis; `tests/unit/test_adapters.py::TestLiskovSubstitution`
  valida isso parametricamente.

## Modo de Simulação (sem Docker)

Cada Adapter tenta abrir uma conexão real (`pika.BlockingConnection` /
`kafka.KafkaProducer`) dentro de `connect()`. Se a biblioteca nativa não
estiver instalada OU o broker estiver inalcançável, qualquer exceção é
capturada e o Adapter cai em **modo de simulação**: mensagens publicadas
são guardadas em um buffer em memória por tópico, e `consume()` as
devolve na ordem em que foram publicadas. Se o buffer estiver vazio (ex:
testar consumo isolado), um pequeno conjunto de mensagens determinísticas
é gerado para manter os testes previsíveis. Isso permite que toda a
suíte `tests/unit/` rode sem nenhum serviço externo, enquanto
`docker-compose.yml` sobe RabbitMQ e Kafka reais para os testes de
integração.

## Estrutura do Projeto

```
p5/
├── src/messaging_adapter/
│   ├── domain/
│   │   ├── interfaces.py        <- Target: MessageBroker Protocol
│   │   └── entities.py          <- Message, BrokerType, PublishConfig, ConsumeConfig, exceptions
│   ├── application/
│   │   └── use_cases.py         <- PublishMessage, ConsumeMessages, ListBrokers
│   ├── infrastructure/
│   │   ├── rabbitmq_adapter.py  <- RabbitMQAdapter (wraps pika, simulates if unavailable)
│   │   ├── kafka_adapter.py     <- KafkaAdapter (wraps kafka-python, simulates if unavailable)
│   │   └── registry.py          <- OCP-friendly broker selection
│   └── main.py                  <- Typer CLI: publish, consume, brokers
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_adapters.py     <- Target/LSP/OCP/DIP tests, no real broker needed
│   └── integration/
│       └── test_integration.py  <- real-broker tests, skipped unless RUN_INTEGRATION=true
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir RabbitMQ + Kafka + app
docker-compose up --build

# 3. Em outro terminal — publicar uma mensagem no RabbitMQ
docker-compose run --rm app python -m messaging_adapter.main publish \
  --broker rabbitmq --topic payments --message '{"amount": 99.9}'

# 4. Consumir do Kafka
docker-compose run --rm app python -m messaging_adapter.main consume \
  --broker kafka --topic orders --limit 5

# 5. Listar brokers disponíveis
docker-compose run --rm app python -m messaging_adapter.main brokers
```

## Comandos CLI

### `publish`

```
Usage: publish [OPTIONS]

Options:
  -b, --broker TEXT    Broker type: rabbitmq | kafka  [default: rabbitmq]
  -t, --topic TEXT     Topic / queue name  [default: default-topic]
  -m, --message TEXT   Message payload (text)  [default: {}]
  -k, --key TEXT        Optional message key
```

### `consume`

```
Usage: consume [OPTIONS]

Options:
  -b, --broker TEXT    Broker type: rabbitmq | kafka  [default: rabbitmq]
  -t, --topic TEXT     Topic / queue name  [default: default-topic]
  -g, --group TEXT     Consumer group ID (Kafka)  [default: default-group]
  -l, --limit INTEGER  Max messages to consume (0 = unlimited)  [default: 10]
  --timeout FLOAT      Poll timeout in seconds  [default: 5.0]
```

### `brokers`

```
Usage: brokers

List all available broker Adapters.
```

## Rodar os Testes

```bash
# Testes unitários (sem brokers reais)
pip install -e ".[dev]"
pytest tests/unit/ -v

# Testes de integração (requer brokers via docker-compose)
RUN_INTEGRATION=true pytest tests/integration/ -v

# Todos com cobertura
pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável                   | Descrição                          | Valor padrão    |
|-----------------------------|-------------------------------------|------------------|
| `RABBITMQ_USER`            | Usuário RabbitMQ                   | `app`            |
| `RABBITMQ_PASSWORD`        | Senha RabbitMQ                     | `secret`         |
| `RABBITMQ_HOST`            | Host do RabbitMQ                   | `rabbitmq`       |
| `RABBITMQ_PORT`            | Porta do RabbitMQ                  | `5672`           |
| `KAFKA_BOOTSTRAP_SERVERS`  | Endereço do cluster Kafka          | `kafka:9092`     |
| `RUN_INTEGRATION`          | Habilita testes de integração      | `false`          |
