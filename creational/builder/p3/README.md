# Email Template Builder

> **Design Pattern:** Builder
> **Categoria:** Creational
> **Framework:** Django
> **Serviços:** PostgreSQL, AWS SES (via LocalStack)

## Objetivo Pedagógico

Este projeto demonstra o padrão Builder construindo emails transacionais passo a passo
(remetente, destinatários, assunto, corpo HTML/texto, anexos) sem expor um construtor
gigante com dezenas de parâmetros opcionais. Um Director (`CampaignDirector`) encapsula
sequências de construção reutilizáveis — presets como "welcome email" ou "password reset"
— para que o código cliente nunca precise conhecer os detalhes de montagem de cada
template. O envio final é feito via um adapter de infraestrutura (`SESEmailSender`) que
fala com AWS SES (ou LocalStack em desenvolvimento), mantendo a lógica de negócio
desacoplada do SDK da AWS.

## O Pattern em Ação

| Papel do Pattern    | Classe                              | Arquivo                                              |
|----------------------|--------------------------------------|-------------------------------------------------------|
| Builder (interface)  | `EmailBuilder`                       | `src/email_builder/domain/interfaces.py`              |
| ConcreteBuilder       | `WelcomeEmailBuilder`                | `src/email_builder/infrastructure/builders.py`        |
| ConcreteBuilder       | `PasswordResetEmailBuilder`          | `src/email_builder/infrastructure/builders.py`        |
| ConcreteBuilder       | `OrderConfirmationEmailBuilder`      | `src/email_builder/infrastructure/builders.py`        |
| Director              | `CampaignDirector`                   | `src/email_builder/application/use_cases.py`          |
| Product               | `Email`                              | `src/email_builder/domain/entities.py`                |
| Port (DIP)            | `EmailSender` (Protocol)             | `src/email_builder/domain/interfaces.py`              |
| Adapter               | `SESEmailSender`                     | `src/email_builder/infrastructure/ses_sender.py`      |

## Diagrama UML (ASCII)

```
<<abstract>>
EmailBuilder
+ set_subject(subject) -> Self
+ set_from(address) -> Self
+ set_to(*addresses) -> Self
+ set_html_body(html) -> Self
+ set_text_body(text) -> Self
+ add_attachment(attachment) -> Self
+ build() -> Email
        |
        ├── BaseEmailBuilder (estado compartilhado)
        |        |
        |        ├── WelcomeEmailBuilder
        |        |     + with_user_name(name) -> Self
        |        |
        |        ├── PasswordResetEmailBuilder
        |        |     + with_reset_link(url) -> Self
        |        |
        |        └── OrderConfirmationEmailBuilder
        |              + with_order_details(id, items, total) -> Self

CampaignDirector
+ build_welcome(recipient, user_name) -> Email
+ build_password_reset(recipient, reset_url) -> Email
+ build_order_confirmation(recipient, order_id, items, total) -> Email

Email (Product)
- subject, from_address, to_addresses
- html_body, text_body, attachments
- template_type: TemplateType

EmailSender (Protocol)         SESEmailSender (Adapter)
+ send(email) -> SendResult  ◄── implementa via boto3 / SES (ou LocalStack)
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** cada `ConcreteBuilder` cuida apenas da montagem de
  um tipo de email (`WelcomeEmailBuilder`, `PasswordResetEmailBuilder`,
  `OrderConfirmationEmailBuilder`); `SESEmailSender` cuida apenas do envio via SES;
  `EmailLog` (Django model) cuida apenas da persistência do histórico de envios.
- **O — Open/Closed:** para adicionar um novo tipo de email (ex: `PromoEmailBuilder`),
  basta criar uma nova subclasse de `BaseEmailBuilder` — nenhuma classe existente é
  modificada, e o `CampaignDirector` pode ganhar um novo método `build_promo(...)`
  sem alterar os métodos já existentes.
- **D — Dependency Inversion:** `SendEmailUseCase` e `SendCampaignEmailUseCase`
  dependem da abstração `EmailSender` (Protocol), não de `SESEmailSender`
  diretamente. Isso permite injetar um `FakeEmailSender` nos testes unitários sem
  tocar em boto3 ou em rede real.

## Estrutura do Projeto

```
p3/
├── src/
│   ├── config/                      ← settings, urls (composição root do Django)
│   ├── email_builder/
│   │   ├── domain/
│   │   │   ├── entities.py          ← Email, Attachment, SendResult, TemplateType
│   │   │   └── interfaces.py        ← EmailBuilder (ABC), EmailSender (Protocol)
│   │   ├── application/
│   │   │   └── use_cases.py         ← CampaignDirector, SendCampaignEmailUseCase
│   │   ├── infrastructure/
│   │   │   ├── builders.py          ← ConcreteBuilders
│   │   │   └── ses_sender.py        ← SESEmailSender (boto3/SES adapter)
│   │   ├── models.py                ← EmailLog (histórico de envios)
│   │   ├── views.py                 ← API REST (SendEmailView, EmailLogListView)
│   │   └── urls.py
│   └── manage.py
├── tests/
│   ├── unit/                        ← builders, director, use cases, SES (mocked com moto)
│   └── integration/                 ← views Django end-to-end (SES mocked com moto)
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API: http://localhost:8000
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```

Localmente (fora do Docker):

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## Variáveis de Ambiente

| Variável                | Descrição                                   | Padrão                                          |
|--------------------------|----------------------------------------------|--------------------------------------------------|
| `DJANGO_SECRET_KEY`      | Chave secreta do Django                       | `dev-secret-key-change-in-production`            |
| `DEBUG`                  | Modo debug                                    | `True`                                           |
| `ALLOWED_HOSTS`          | Hosts permitidos                              | `*`                                              |
| `DATABASE_URL`           | URL de conexão PostgreSQL                     | `postgresql://app:secret@db:5432/email_builder_db` |
| `AWS_DEFAULT_REGION`     | Região AWS para o SES                         | `us-east-1`                                      |
| `AWS_ENDPOINT_URL`       | Endpoint do SES (LocalStack em dev)           | `http://localstack:4566`                         |
| `AWS_ACCESS_KEY_ID`      | Credencial AWS (fake em dev/LocalStack)       | `test`                                           |
| `AWS_SECRET_ACCESS_KEY`  | Credencial AWS (fake em dev/LocalStack)       | `test`                                           |

## Exemplos de Uso

```bash
# Enviar email de boas-vindas (preset do Director)
curl -X POST http://localhost:8000/emails/welcome \
  -H "Content-Type: application/json" \
  -d '{"recipient": "alice@example.com", "user_name": "Alice"}'

# Enviar email de reset de senha
curl -X POST http://localhost:8000/emails/password_reset \
  -H "Content-Type: application/json" \
  -d '{"recipient": "bob@example.com", "reset_url": "https://app.test/reset/token123"}'

# Listar histórico de envios
curl http://localhost:8000/emails/logs
```
