# S3 Bucket Iterator (Iterator) — P2

API Flask que percorre um bucket S3 de duas formas: paginação convencional
(`GET /objects`) e agregação de toda a coleção via um Iterator GoF genuíno
que busca páginas sob demanda (`GET /objects/summary`).

## Objetivo pedagógico

Demonstrar o pattern **Iterator** sobre uma fonte de dados externa (S3): o
cliente percorre o bucket inteiro chamando apenas `has_next()`/`next()`,
sem nunca saber que, por baixo, o `S3KeyIterator` está paginando com
`ContinuationToken` do S3.

Elementos do pattern:
- **Iterator (abstrato):** `S3ObjectIterator` (`domain/interfaces.py`)
- **Concrete Iterator:** `S3KeyIterator` — mantém um buffer interno e busca a próxima página só quando o buffer esvazia
- **Aggregate:** `S3ObjectSource` / `BotoS3ObjectSource` — fornece os objetos crus, sem saber nada sobre iteração
- **Client:** `SummarizeBucketUseCase`, que consome o iterator com um laço `while has_next(): next()` para somar contagem e tamanho total

## Diagrama (ASCII)

```
GET /objects/summary
      │
      ▼
SummarizeBucketUseCase ──cria──► S3KeyIterator(source, page_size=1000)
      │                                  │
      │  while iterator.has_next():      │
      │      obj = iterator.next()       │
      │      count += 1; size += obj.size│
      │                                  ▼
      │                    buffer vazio? ──sim──► source.fetch_page(token, 1000) ──► S3 list_objects_v2
      ▼
{"object_count": N, "total_size_bytes": M}
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:5000`.

### Endpoints

| Método | Rota               | Descrição                                                    |
|--------|--------------------|-----------------------------------------------------------------|
| GET    | `/objects`         | Uma página de objetos (`?continuation_token=&limit=`)            |
| GET    | `/objects/summary` | Contagem e tamanho total do bucket inteiro, via Iterator         |
| GET    | `/health`          | Healthcheck                                                     |

```bash
curl "http://localhost:5000/objects?limit=100"
curl "http://localhost:5000/objects/summary"
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes de `BotoS3ObjectSource` usam [`moto`](https://github.com/getmoto/moto)
para simular o S3; os de `S3KeyIterator` e da API usam um
`FakeS3ObjectSource` em memória — nenhuma chamada de rede real é feita.

## SOLID

- **SRP:** `S3KeyIterator` só sabe iterar; `BotoS3ObjectSource` só sabe listar páginas; nenhum dos dois conhece o outro além do contrato `S3ObjectSource`.
- **OCP:** trocar a fonte de dados (ex.: GCS) = criar uma nova `S3ObjectSource`, sem tocar no `S3KeyIterator` nem nos use cases.
- **LSP:** qualquer `S3ObjectIterator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `has_next`/`next`.
- **ISP:** `S3ObjectIterator` e `S3ObjectSource` são interfaces pequenas e focadas.
- **DIP:** `SummarizeBucketUseCase` e `ListObjectsPageUseCase` dependem de `S3ObjectSource` (abstração); o Flask `create_app()` injeta a implementação concreta, trocada por um fake nos testes.
