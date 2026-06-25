# P1 — Notification Bridge

> **Design Pattern:** Bridge
> **Categoria:** Structural
> **Framework:** FastAPI + LocalStack (SES)
> **Servicos:** LocalStack SES, SNS

## Objetivo Pedagogico

Este projeto demonstra o padrao Bridge separando DUAS hierarquias independentes:
o TIPO de notificacao (Alert, Report, Welcome) e o CANAL de entrega (Email, SMS, Push).
Qualquer tipo pode ser entregue por qualquer canal sem modificar o codigo existente,
aplicando os principios Open/Closed e Single Responsibility.

## O Pattern em Acao

O Bridge e implementado pela composicao: cada `Notification` (Abstraction) recebe
um `NotificationSender` (Implementation) via construtor. O tipo sabe O QUE enviar;
o sender sabe COMO entregar.

| Papel do Pattern        | Classe                   | Arquivo                                         |
|-------------------------|--------------------------|-------------------------------------------------|
| Abstraction (ABC)       | `Notification`           | `src/notifications/domain/interfaces.py`        |
| RefinedAbstraction      | `AlertNotification`      | `src/notifications/domain/notifications.py`     |
| RefinedAbstraction      | `ReportNotification`     | `src/notifications/domain/notifications.py`     |
| RefinedAbstraction      | `WelcomeNotification`    | `src/notifications/domain/notifications.py`     |
| Implementation (ABC)    | `NotificationSender`     | `src/notifications/domain/interfaces.py`        |
| ConcreteImplementation  | `EmailSender`            | `src/notifications/infrastructure/implementations.py` |
| ConcreteImplementation  | `SMSSender`              | `src/notifications/infrastructure/implementations.py` |
| ConcreteImplementation  | `PushSender`             | `src/notifications/infrastructure/implementations.py` |

## Diagrama UML — Bridge (2 Hierarquias Independentes)

```
ABSTRACTION HIERARCHY          IMPLEMENTATION HIERARCHY
========================       ========================

<<abstract>>                   <<abstract>>
Notification                   NotificationSender
+ send(recipient, data)  <>--> + deliver(to, subject, body)
        |                               |
        |-- AlertNotification           |-- EmailSender   (LocalStack SES)
        |-- ReportNotification          |-- SMSSender     (log/fake)
        |-- WelcomeNotification         |-- PushSender    (log/fake)

COMBINACOES POSSIVEIS (3 x 3 = 9):
  AlertNotification   + EmailSender
  AlertNotification   + SMSSender
  AlertNotification   + PushSender
  ReportNotification  + EmailSender
  ReportNotification  + SMSSender
  ReportNotification  + PushSender
  WelcomeNotification + EmailSender
  WelcomeNotification + SMSSender
  WelcomeNotification + PushSender
```

## Principios SOLID Demonstrados

- **O — Open/Closed:** Adicionar `SlackNotification` ou `WhatsAppSender` = nova classe,
  zero alteracoes no codigo existente.
- **S — SRP:** `AlertNotification` formata conteudo; `EmailSender` gerencia entrega SES.
  Cada classe tem um unico motivo para mudar.
- **D — DIP:** `SendNotificationUseCase` depende de `NotificationSender` (ABC),
  nunca de `EmailSender` diretamente.

## Estrutura do Projeto

```
p1/
├── src/
│   ├── main.py                           <- FastAPI app + composition root
│   └── notifications/
│       ├── domain/
│       │   ├── interfaces.py             <- Notification ABC + NotificationSender ABC
│       │   ├── entities.py               <- DeliveryResult, NotificationPayload, enums
│       │   └── notifications.py          <- Alert/Report/WelcomeNotification
│       ├── application/
│       │   ├── use_cases.py              <- SendNotificationUseCase
│       │   └── schemas.py                <- Pydantic v2 request/response models
│       └── infrastructure/
│           └── implementations.py        <- EmailSender, SMSSender, PushSender
├── tests/
│   ├── unit/
│   │   ├── test_notifications.py         <- Bridge combination tests
│   │   ├── test_senders.py               <- Sender unit tests
│   │   └── test_api.py                   <- FastAPI route tests
│   └── integration/
│       └── test_email_sender.py          <- LocalStack SES integration test
├── scripts/
│   └── localstack-init.sh
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
# Swagger UI: http://localhost:8001/docs
# Health:     http://localhost:8001/health
```

## Exemplos de Requisicao

```bash
# Alert via SMS
curl -X POST http://localhost:8001/notifications/alert \
  -H "Content-Type: application/json" \
  -d '{"recipient": "+5511999990000", "channel": "sms", "severity": "CRITICAL", "message": "DB down", "source": "monitor"}'

# Report via Email
curl -X POST http://localhost:8001/notifications/report \
  -H "Content-Type: application/json" \
  -d '{"recipient": "mgr@example.com", "channel": "email", "report_name": "Sales Q1", "period": "2024-Q1", "summary": "Revenue up 12%", "download_url": "https://example.com/report.pdf"}'

# Welcome via Push
curl -X POST http://localhost:8001/notifications/welcome \
  -H "Content-Type: application/json" \
  -d '{"recipient": "device-token-abc", "channel": "push", "user_name": "Alice", "activation_link": "https://app.example.com/activate/abc"}'
```

## Rodar os Testes

```bash
# Testes unitarios (sem servicos externos)
docker-compose run --rm app pytest tests/unit/ -v

# Testes de integracao (requer LocalStack)
docker-compose run --rm app pytest tests/integration/ -v

# Todos com cobertura
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

## Variaveis de Ambiente

| Variavel              | Descricao                        | Valor padrao                  |
|-----------------------|----------------------------------|-------------------------------|
| `LOCALSTACK_ENDPOINT` | URL do LocalStack                | `http://localstack:4566`      |
| `SES_SENDER`          | Email remetente verificado no SES | `noreply@example.com`        |
| `AWS_ACCESS_KEY_ID`   | Credencial AWS (qualquer valor)  | `test`                        |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS (qualquer valor)| `test`                        |
| `AWS_DEFAULT_REGION`  | Regiao AWS                       | `us-east-1`                   |
