# P3 — Queue Bridge

> **Design Pattern:** Bridge
> **Categoria:** Structural
> **Framework:** Django
> **Servicos:** Celery/Redis, RabbitMQ, AWS SQS

## Objetivo Pedagogico

Este projeto demonstra o padrao Bridge desacoplando a ABSTRACAO de filas/mensageria
(semantica de enfileiramento: tarefa simples ou com prioridade) da IMPLEMENTACAO de
transporte (o broker concreto: Celery/Redis, RabbitMQ ou SQS). Qualquer semantica de
cliente pode rodar sobre qualquer broker sem alterar o codigo existente, aplicando os
principios Open/Closed e Dependency Inversion.

## O Pattern em Acao

O Bridge e implementado por composicao: cada `QueueClient` (Abstraction) recebe um
`MessageBroker` (Implementation) via construtor. O cliente sabe O QUE fazer com uma
mensagem (semantica de fila); o broker sabe COMO entrega-la (transporte).

| Papel do Pattern        | Classe                 | Arquivo                                              |
|--------------------------|------------------------|-------------------------------------------------------|
| Abstraction (ABC)         | `QueueClient`           | `src/task_queue/domain/interfaces.py`                |
| RefinedAbstraction        | `TaskQueueClient`       | `src/task_queue/domain/queue_clients.py`             |
| RefinedAbstraction        | `PriorityQueueClient`   | `src/task_queue/domain/queue_clients.py`             |
| Implementor (ABC)         | `MessageBroker`         | `src/task_queue/domain/interfaces.py`                |
| ConcreteImplementor       | `CeleryRedisBroker`     | `src/task_queue/infrastructure/brokers.py`           |
| ConcreteImplementor       | `RabbitMQBroker`        | `src/task_queue/infrastructure/brokers.py`           |
| ConcreteImplementor       | `SQSBroker`             | `src/task_queue/infrastructure/brokers.py`           |
| ConcreteImplementor       | `InMemoryBroker`        | `src/task_queue/infrastructure/brokers.py` (extra, demo) |

## Diagrama UML — Bridge (2 Hierarquias Independentes)

```
ABSTRACTION HIERARCHY              IMPLEMENTOR HIERARCHY
========================          ========================

<<abstract>>                       <<abstract>>
QueueClient                        MessageBroker
+ enqueue(payload, queue)   <>---> + publish(message)
+ dequeue(queue, max)               + consume(queue, max)
+ check_health()                    + acknowledge(message_id)
        |                            + health_check()
        |-- TaskQueueClient          + get_broker_name()
        |-- PriorityQueueClient              |
                                              |-- CeleryRedisBroker (Redis)
                                              |-- RabbitMQBroker    (pika)
                                              |-- SQSBroker         (boto3)
                                              |-- InMemoryBroker    (demo)

COMBINACOES POSSIVEIS (2 x 3 = 6, + InMemory para demo local):
  TaskQueueClient     + CeleryRedisBroker
  TaskQueueClient     + RabbitMQBroker
  TaskQueueClient     + SQSBroker
  PriorityQueueClient + CeleryRedisBroker
  PriorityQueueClient + RabbitMQBroker
  PriorityQueueClient + SQSBroker
```

## Principios SOLID Demonstrados

- **O — Open/Closed:** adicionar `KafkaBroker` ou `BulkQueueClient` = nova classe,
  zero alteracoes no codigo existente (`BROKER_REGISTRY` / `CLIENT_REGISTRY`).
- **S — SRP:** `TaskQueueClient` decide semantica de mensagem; `RabbitMQBroker`
  gerencia conexao/transporte. Cada classe tem um unico motivo para mudar.
- **D — DIP:** `EnqueueMessageUseCase` e os views Django dependem de `QueueClient`
  (abstracao), nunca de `CeleryRedisBroker` ou `SQSBroker` diretamente.
- **I — ISP:** `MessageBroker` expoe apenas publish/consume/acknowledge/health —
  nenhum metodo especifico de broker (ex.: `basic_get` do pika) escapa para a interface.

## Estrutura do Projeto

```
p3/
├── src/
│   ├── manage.py                          <- Django management entrypoint
│   └── task_queue/
│       ├── settings.py                    <- Django settings (sqlite in-memory)
│       ├── urls.py                        <- URL routing
│       ├── wsgi.py                        <- WSGI entrypoint
│       ├── domain/
│       │   ├── interfaces.py              <- QueueClient ABC + MessageBroker ABC
│       │   ├── entities.py                <- QueueMessage, BrokerHealth, results, erros
│       │   └── queue_clients.py           <- TaskQueueClient, PriorityQueueClient
│       ├── application/
│       │   └── use_cases.py               <- Enqueue/Dequeue/CheckHealth use cases
│       ├── infrastructure/
│       │   ├── brokers.py                 <- CeleryRedis/RabbitMQ/SQS/InMemory brokers
│       │   └── client_factory.py          <- Composition root (registries)
│       └── views/
│           └── queue_views.py             <- Django HTTP views
├── tests/
│   ├── unit/
│   │   ├── test_queue_clients.py          <- Bridge combination tests
│   │   ├── test_brokers.py                <- Broker unit tests (mocked redis/pika/boto3)
│   │   ├── test_use_cases.py              <- Application layer tests
│   │   └── test_client_factory.py         <- Composition root tests
│   └── integration/
│       └── test_django_views.py           <- Django test client, full HTTP stack
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Pre-requisitos

- Docker >= 24.0
- Docker Compose >= 2.24

## Como Rodar

```bash
# 1. Copiar variaveis de ambiente
cp .env.example .env

# 2. Subir todos os servicos
docker-compose up --build

# 3. Acessar a API
# App: http://localhost:8000
```

## Exemplos de Requisicao

```bash
# Health check do broker Redis/Celery
curl http://localhost:8000/queue/health/celery_redis/

# Enfileirar tarefa simples via RabbitMQ
curl -X POST http://localhost:8000/queue/enqueue/rabbitmq/task/ \
  -H "Content-Type: application/json" \
  -d '{"queue_name": "emails", "payload": {"to": "a@b.com", "subject": "Hi"}}'

# Enfileirar com prioridade via SQS
curl -X POST http://localhost:8000/queue/enqueue/sqs/priority/ \
  -H "Content-Type: application/json" \
  -d '{"queue_name": "alerts", "payload": {"priority": "critical", "message": "DB down"}}'

# Consumir mensagens pendentes
curl "http://localhost:8000/queue/dequeue/rabbitmq/emails/?max=5"
```

## Rodar os Testes

```bash
# Testes unitarios (sem servicos externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integracao (Django test client, sem brokers reais)
docker-compose run --rm app pytest tests/integration/ -v

# Todos com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variaveis de Ambiente

| Variavel              | Descricao                          | Valor padrao              |
|-----------------------|-------------------------------------|----------------------------|
| `REDIS_URL`           | URL de conexao Redis (CeleryRedis)  | `redis://redis:6379/0`     |
| `RABBITMQ_HOST`       | Host do RabbitMQ                    | `rabbitmq`                 |
| `RABBITMQ_PORT`       | Porta do RabbitMQ                   | `5672`                     |
| `AWS_ENDPOINT_URL`    | Endpoint SQS (LocalStack por padrao)| `http://localstack:4566`   |
| `AWS_DEFAULT_REGION`  | Regiao AWS                           | `us-east-1`                |
