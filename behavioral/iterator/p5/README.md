# Stream Data Iterator (Iterator) — P5

Aplicação Streamlit que drena as mensagens atualmente disponíveis em um
tópico Kafka através de um Iterator GoF, exibindo cada mensagem e
mantendo um total acumulado entre os polls.

## Objetivo pedagógico

Demonstrar o pattern **Iterator** sobre uma fonte verdadeiramente
ilimitada (um stream Kafka): o cliente drena "o que está disponível agora"
chamando apenas `has_next()`/`next()`, sem nunca saber que, por baixo, o
`KafkaStreamIterator` está chamando `consumer.poll()` e que um poll vazio
sinaliza o fim daquela rodada de drenagem.

Elementos do pattern:
- **Iterator (abstrato):** `MessageIterator` (`domain/interfaces.py`)
- **Concrete Iterator:** `KafkaStreamIterator` — mantém um buffer interno e poll vazio termina a iteração
- **Aggregate:** `MessageSource` / `KafkaMessageSource` — faz o polling cru do Kafka, sem saber nada sobre iteração
- **Client:** `SummarizeAvailableMessagesUseCase`, que consome o iterator com um laço `while has_next(): next()` para agregar contagem e soma

## Diagrama (ASCII)

```
Streamlit: botão "Poll messages"
      │
      ▼
SummarizeAvailableMessagesUseCase ──cria──► KafkaStreamIterator(source)
      │                                            │
      │  while iterator.has_next():                │
      │      msg = iterator.next()                 │
      │      count += 1; total += msg.value.amount │
      │                                            ▼
      │                    buffer vazio? ──sim──► source.poll(1000) ──► Kafka consumer.poll()
      │                                            │
      │                    poll retornou vazio? ──sim──► iteração termina (exhausted)
      ▼
st.session_state acumula totais entre polls
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

Acesse `http://localhost:8501`. Publique mensagens JSON (ex.:
`{"amount": 42}`) no tópico `data-stream` e clique em "Poll messages"
para drená-las e ver o total acumulado.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

O arquivo `infrastructure/app.py` (camada de UI do Streamlit) é excluído
da medição de cobertura, seguindo o mesmo padrão dos demais projetos
Streamlit do dataset. Os testes de `KafkaMessageSource` usam um
`FakeConsumer`; os de `KafkaStreamIterator` e dos use cases usam um
`FakeMessageSource` em memória — nenhuma chamada de rede real é feita.

## SOLID

- **SRP:** `KafkaStreamIterator` só sabe drenar; `KafkaMessageSource` só sabe fazer polling; nenhum dos dois conhece o outro além do contrato `MessageSource`.
- **OCP:** trocar a fonte (ex.: RabbitMQ, SQS) = criar uma nova `MessageSource`, sem tocar no `KafkaStreamIterator` nem nos use cases.
- **LSP:** qualquer `MessageIterator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `has_next`/`next`.
- **ISP:** `MessageIterator` e `MessageSource` são interfaces pequenas e focadas.
- **DIP:** `SummarizeAvailableMessagesUseCase` e `DrainAvailableMessagesUseCase` dependem de `MessageSource` (abstração); a UI Streamlit é o único lugar que conhece `KafkaMessageSource`.
