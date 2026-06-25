# ETL Pipeline Template (Template Method) — P3

API Django onde dois pipelines de ETL (clientes e pedidos) compartilham
o mesmo esqueleto extract→transform→load→notificação, com Celery
disparando a notificação de conclusão para um tópico Kafka.

> **Nota de ambiente:** o PLAN.md especifica PostgreSQL; este projeto
> usa SQLite como stand-in (mesmo precedente de outros projetos do
> dataset). Troque o `ENGINE` em `config/settings.py` por
> `django.db.backends.postgresql` para apontar para uma instância real.

## Objetivo pedagógico

Demonstrar o pattern **Template Method**: `ETLPipeline` (AbstractClass)
define o algoritmo fixo em `run()` — extrair, transformar, carregar,
notificar — e cada pipeline concreto só sobrescreve os três passos que
variam (`extract`, `transform`, `load`), cada um lendo/escrevendo em
suas próprias tabelas de staging/destino. `emit_completion_event()` é
compartilhado por todos os pipelines: dispara uma task Celery que
publica no Kafka, sem que o algoritmo principal saiba nada sobre
fila de mensagens.

Elementos do pattern:
- **AbstractClass:** `ETLPipeline` (`domain/interfaces.py`)
- **Template Method:** `ETLPipeline.run()`
- **ConcreteClasses:** `CustomerETLPipeline`, `OrderETLPipeline` (`application/pipelines/`)
- **Hook:** `should_emit_event()`

## Diagrama (ASCII)

```
ETLPipeline.run()
        │
        ├─► extract()                  (abstrato — staging table própria)
        ├─► transform(records)          (abstrato — mapeamento próprio)
        ├─► load(records)               (abstrato — tabela destino própria)
        └─► should_emit_event()? ──► emit_completion_event(result)
                                              │
                                              ▼
                                   publish_etl_completion_task.delay()
                                   (Celery → Kafka, tópico etl-events)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                              | Descrição                          |
|--------|-------------------------------------|---------------------------------------|
| POST   | `/pipelines/customers/run/`         | Roda o pipeline ETL de clientes        |
| POST   | `/pipelines/orders/run/`            | Roda o pipeline ETL de pedidos         |

```bash
curl -X POST http://localhost:8000/pipelines/customers/run/
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`CELERY_TASK_ALWAYS_EAGER` (definido em `config/settings_test.py`) faz
a task de publicação rodar de forma síncrona nos testes; `build_kafka_producer`
é substituído por um `FakeKafkaProducer` (fixture `autouse` em
`tests/conftest.py`) para que nenhum teste precise de um broker Kafka real.

## SOLID

- **SRP:** cada pipeline concreto só sabe extrair/transformar/carregar seus próprios dados; `KafkaEtlEventPublisher` só publica o evento de conclusão.
- **OCP:** um novo pipeline (ex.: produtos) é uma nova classe `ETLPipeline` — sem tocar no algoritmo de `run()` nem nos pipelines existentes.
- **LSP:** qualquer `ETLPipeline` concreto pode ser executado via `run()` sem quebrar o contrato — todos retornam `ETLResult`.
- **ISP:** `ETLPipeline` expõe só os três métodos abstratos que cada pipeline realmente precisa sobrescrever.
- **DIP:** os pipelines concretos dependem de repositórios injetados via construtor (`DjangoCustomerStagingRepository`, etc.), não de SQL bruto espalhado pelo código.
