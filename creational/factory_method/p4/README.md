# Message Consumer Factory

> **Design Pattern:** Factory Method
> **Categoria:** Creational
> **Framework:** CLI Typer
> **Serviços:** Kafka (bitnami), RabbitMQ, LocalStack (SQS)
> **Domínio:** messaging

## Objetivo Pedagógico

Demonstra o Factory Method em um contexto real de mensageria. O aluno verá como
adicionar suporte a um novo broker (ex: Apache Pulsar) criando apenas um novo par
Creator/Product, sem alterar nenhuma linha de código existente — aplicando OCP e
DIP em um cenário de CLI com múltiplos brokers de mensagens.

## O Pattern em Ação

| Papel do Pattern   | Classe                      | Arquivo                                     |
|--------------------|-----------------------------|---------------------------------------------|
| Creator (ABC)      | `ConsumerFactory`           | `src/messaging/domain/interfaces.py`        |
| Product (Protocol) | `MessageConsumer`           | `src/messaging/domain/interfaces.py`        |
| ConcreteCreator    | `KafkaConsumerFactory`      | `src/messaging/infrastructure/consumers.py` |
| ConcreteCreator    | `RabbitMQConsumerFactory`   | `src/messaging/infrastructure/consumers.py` |
| ConcreteCreator    | `SQSConsumerFactory`        | `src/messaging/infrastructure/consumers.py` |
| ConcreteProduct    | `KafkaConsumer`             | `src/messaging/infrastructure/consumers.py` |
| ConcreteProduct    | `RabbitMQConsumer`          | `src/messaging/infrastructure/consumers.py` |
| ConcreteProduct    | `SQSConsumer`               | `src/messaging/infrastructure/consumers.py` |

## Diagrama UML (ASCII)

```
<<abstract>>
ConsumerFactory
+ create_consumer(config: ConsumeConfig) -> MessageConsumer   (factory method)
+ get_broker_name() -> str
+ consume_all(config: ConsumeConfig) -> list[Message]         (template method)
        |
        |-- KafkaConsumerFactory
        |     + create_consumer() -> KafkaConsumer
        |
        |-- RabbitMQConsumerFactory
        |     + create_consumer() -> RabbitMQConsumer
        |
        +-- SQSConsumerFactory
              + create_consumer() -> SQSConsumer

<<Protocol>>
MessageConsumer
+ connect() -> None
+ subscribe(topic_or_queue: str) -> None
+ consume() -> Iterator[Message]
+ ack(message: Message) -> None
+ close() -> None
        |
        |-- KafkaConsumer
        |-- RabbitMQConsumer
        +-- SQSConsumer

<<dataclass>>
Message
+ topic: str
+ key: str | None
+ value: bytes
+ timestamp: datetime
+ headers: dict[str, str]
+ partition: int | None
+ offset: int | None
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Adicionar Apache Pulsar = criar `PulsarConsumer` +
  `PulsarConsumerFactory` + registrar em `CONSUMER_FACTORY_REGISTRY`. Zero
  modificações em `ConsumerFactory`, use cases ou CLI.
- **D — Dependency Inversion:** `ConsumeMessagesUseCase` recebe
  `ConsumerFactory` (abstração) via construtor. Nunca importa Kafka, pika ou
  boto3 diretamente.
- **I — Interface Segregation:** `MessageConsumer` tem apenas 5 métodos — o
  mínimo viável. Clientes que só leem nunca precisam implementar partes que não
  usam.
- **S — Single Responsibility:** `ConsumerFactory` cria consumers.
  `ConsumeMessagesUseCase` orquestra a sessão. `StreamMessagesUseCase` oferece
  modo lazy. Cada classe tem um único motivo para mudar.

## Estrutura do Projeto

```
p4/
├── src/messaging/
│   ├── domain/
│   │   ├── interfaces.py        <- ConsumerFactory ABC + MessageConsumer Protocol
│   │   └── entities.py          <- Message, ConsumeConfig, BrokerType, Exceptions
│   ├── application/
│   │   └── use_cases.py         <- ConsumeMessages, StreamMessages, ListBrokers
│   └── infrastructure/
│       └── consumers.py         <- ConcreteCreators + ConcreteProducts + Registry
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_factory.py
│   └── integration/
│       └── test_integration.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Como Rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir todos os serviços (Kafka + RabbitMQ + LocalStack)
docker-compose up --build

# 3. Em outro terminal — consumir mensagens do Kafka
docker-compose run --rm app python -m messaging.main consume \
  --broker kafka --topic orders --group my-group --limit 10

# 4. Consumir do RabbitMQ
docker-compose run --rm app python -m messaging.main consume \
  --broker rabbitmq --queue payments --limit 100

# 5. Consumir do SQS (LocalStack)
docker-compose run --rm app python -m messaging.main consume \
  --broker sqs --queue notifications --limit 50

# 6. Listar brokers disponíveis
docker-compose run --rm app python -m messaging.main brokers
```

## Comandos CLI

### `consume`

```
Usage: consume [OPTIONS]

Options:
  -b, --broker TEXT    Broker type: kafka | rabbitmq | sqs  [default: kafka]
  -t, --topic TEXT     Kafka topic name
  -q, --queue TEXT     RabbitMQ / SQS queue name
  -g, --group TEXT     Consumer group ID (Kafka)  [default: default-group]
  -l, --limit INTEGER  Max messages to consume (0 = unlimited)  [default: 10]
  --timeout FLOAT      Poll timeout in seconds  [default: 5.0]
  --stream             Stream messages one by one (lazy mode)
```

### `brokers`

```
Usage: brokers

List all available broker factories.
```

## Rodar os Testes

```bash
# Testes unitários (sem brokers reais)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integração (requer brokers)
docker-compose run --rm app pytest tests/integration/ -v -e RUN_INTEGRATION=true

# Todos com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável                   | Descrição                          | Valor padrão          |
|----------------------------|------------------------------------|-----------------------|
| `KAFKA_BOOTSTRAP_SERVERS`  | Endereço do cluster Kafka          | `kafka:9092`          |
| `RABBITMQ_USER`            | Usuário RabbitMQ                   | `app`                 |
| `RABBITMQ_PASSWORD`        | Senha RabbitMQ                     | `secret`              |
| `LOCALSTACK_ENDPOINT`      | URL do LocalStack                  | `http://localstack:4566` |
| `AWS_DEFAULT_REGION`       | Região AWS para LocalStack         | `us-east-1`           |
| `RUN_INTEGRATION`          | Habilita testes de integração      | `false`               |
