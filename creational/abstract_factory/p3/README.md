# Message Broker Factory

> **Design Pattern:** Abstract Factory | **Categoria:** Creational
> **Framework:** CLI Typer | **Serviços:** RabbitMQ, Kafka, AWS SQS (via LocalStack)

## Objetivo Pedagógico

Este projeto demonstra o pattern **Abstract Factory** aplicado a um cenário real de
mensageria: uma CLI capaz de publicar, consumir e administrar filas/tópicos em três
brokers diferentes (RabbitMQ, Kafka, SQS) sem que o código cliente conheça qual
implementação concreta está em uso. O aluno deve conseguir identificar:

- **AbstractFactory:** `MessageBrokerFactory` (`src/broker_factory/domain/interfaces.py`)
- **ConcreteFactory:** `RabbitMQFactory`, `KafkaFactory`, `SQSFactory`, `InMemoryBrokerFactory`
  (`src/broker_factory/infrastructure/factories.py`)
- **AbstractProduct:** `Producer`, `Consumer`, `QueueAdmin` (Protocols em `domain/interfaces.py`)
- **ConcreteProduct:** `RabbitMQProducer`/`RabbitMQConsumer`/`RabbitMQQueueAdmin`,
  `KafkaProducer`/`KafkaConsumer`/`KafkaQueueAdmin`,
  `SQSProducer`/`SQSConsumer`/`SQSQueueAdmin`

## O Pattern Aplicado

Cada broker é uma **família de produtos relacionados** — um Producer, um Consumer e um
QueueAdmin que sabem conversar entre si usando o mesmo protocolo de conexão (AMQP,
Kafka wire protocol, ou a API SQS). A `MessageBrokerFactory` garante que, ao escolher
"kafka", o cliente sempre recebe os três produtos da família Kafka — nunca um Producer
RabbitMQ misturado com um Consumer Kafka. Os casos de uso em `application/use_cases.py`
dependem apenas da abstração `MessageBrokerFactory` e dos Protocols `Producer`/
`Consumer`/`QueueAdmin`, nunca de uma classe concreta. A composição (qual fábrica usar)
acontece em um único lugar: `build_broker_factory()`, chamada pela CLI (`cli.py`), que é
a *composition root* da aplicação.

## Diagrama UML (ASCII)

```
                    <<interface>>                    <<Protocol>>
              MessageBrokerFactory                      Producer
              ───────────────────────              ──────────────────
              + create_producer(): Producer         + publish(dest, msg)
              + create_consumer(): Consumer          + close()
              + create_admin(): QueueAdmin
              + get_broker_name(): str                  <<Protocol>>
                       ▲                                 Consumer
        ┌──────────────┼──────────────┐             ──────────────────
        │              │              │             + consume(src, n)
[RabbitMQFactory] [KafkaFactory]  [SQSFactory]       + acknowledge(id)
        │              │              │             + close()
        ▼              ▼              ▼
 RabbitMQProducer  KafkaProducer  SQSProducer  ──┐      <<Protocol>>
 RabbitMQConsumer  KafkaConsumer  SQSConsumer  ──┼──▶   QueueAdmin
 RabbitMQQueueAdmin KafkaQueueAdmin SQSQueueAdmin┘     ──────────────────
                                                        + create_queue(name)
   (ConcreteFactories)      (ConcreteProducts,           + delete_queue(name)
                              uma família por broker)     + list_queues()
```

Cada coluna abaixo de uma `ConcreteFactory` é uma família completa e coesa de produtos
para aquele broker. Trocar de família (RabbitMQ → Kafka) significa apenas trocar qual
`ConcreteFactory` é instanciada em `build_broker_factory()` — nenhum outro código muda.

## Princípios SOLID Demonstrados

- **O (Open/Closed):** novos brokers (ex.: Pulsar, NATS) são adicionados criando uma
  nova `ConcreteFactory` + seus `ConcreteProducts` e registrando uma entrada em
  `build_broker_factory()` (`infrastructure/factories.py`). Nenhuma classe existente
  (`MessageBrokerFactory`, use cases, CLI) precisa ser modificada.
- **D (Dependency Inversion):** `PublishMessageUseCase`, `ConsumeMessagesUseCase`,
  `CreateQueueUseCase` e `ListQueuesUseCase` (`application/use_cases.py`) recebem a
  `MessageBrokerFactory` via construtor e dependem apenas da abstração — nunca importam
  `pika`, `kafka` ou `boto3` diretamente. A única peça que conhece implementações
  concretas é `cli.py`, a composition root.
- **I (Interface Segregation):** `Producer`, `Consumer` e `QueueAdmin` são `Protocol`s
  pequenos e independentes (`domain/interfaces.py`). Um cliente que só publica mensagens
  (`PublishMessageUseCase`) depende apenas de `Producer`, sem ser forçado a implementar
  ou conhecer métodos de `Consumer`/`QueueAdmin`.
- **L (Liskov Substitution):** todas as `ConcreteFactory`s (incluindo
  `InMemoryBrokerFactory`, usada nos testes) são substituíveis por
  `MessageBrokerFactory` sem alterar o comportamento esperado pelo cliente — mesmo
  contrato de retorno, mesmas exceções de domínio.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

A CLI fica disponível dentro do container `app`. Exemplos de uso:

```bash
docker-compose run --rm app python -m broker_factory.cli publish orders "hello" --broker rabbitmq
docker-compose run --rm app python -m broker_factory.cli consume orders --broker rabbitmq
docker-compose run --rm app python -m broker_factory.cli create-queue payments --broker kafka
docker-compose run --rm app python -m broker_factory.cli list-queues --broker sqs
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente (fora do Docker), com um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes unitários (`tests/unit/`) usam `InMemoryBrokerFactory` e mocks das SDKs
(`pika`, `kafka`, `boto3`) — não exigem nenhum serviço em execução. Os testes de
integração (`tests/integration/`) exercitam os brokers reais e são automaticamente
**pulados** (`pytest.skip`) se RabbitMQ/Kafka/LocalStack não estiverem acessíveis;
para executá-los de fato:

```bash
docker-compose up -d rabbitmq kafka localstack
pytest tests/integration -m integration
```
