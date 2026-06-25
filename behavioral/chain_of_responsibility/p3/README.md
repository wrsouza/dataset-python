# Content Moderation Pipeline (Chain of Responsibility) — P3

Django app that routes user-generated content (text + optional image) through
a moderation chain — profanity filter → AWS Rekognition image safety check →
manual review fallback — until a verdict is reached.

## Objetivo pedagógico

Demonstrar o pattern **Chain of Responsibility** num pipeline de moderação
realista: cada elo da cadeia decide de forma independente se rejeita o
conteúdo ou se o passa adiante, sem que o cliente (`SubmitContentUseCase`)
precise conhecer a ordem ou a quantidade de verificações.

Elementos do pattern:
- **Handler (abstrato):** `ModerationHandler` (`domain/interfaces.py`)
- **Concrete Handlers:** `TextProfanityHandler`, `ImageSafetyHandler`, `ManualReviewHandler`
- **Client:** `SubmitContentUseCase`, que dispara `chain.handle(submission)` sem conhecer a topologia da cadeia

## Diagrama (ASCII)

```
Client
  │
  ▼
SubmitContentUseCase
  │
  ▼
TextProfanityHandler ──(sem termo banido)──► ImageSafetyHandler ──(sem imagem/sem flag)──► ManualReviewHandler
     │ rejeita                                    │ rejeita (Rekognition)                       │ aprova (sempre)
     ▼                                            ▼                                              ▼
  ContentSubmission (com 1 ModerationStep no histórico)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                       | Descrição                              |
|--------|----------------------------|------------------------------------------|
| POST   | `/submissions/`             | Envia conteúdo para moderação            |
| GET    | `/submissions/<id>/`        | Consulta o resultado de uma submissão    |

```bash
curl -X POST http://localhost:8000/submissions/ \
  -H "Content-Type: application/json" \
  -d '{"author": "alice", "text": "hello world"}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes de `ImageSafetyHandler`/`RekognitionImageModerationClient` usam
[`moto`](https://github.com/getmoto/moto) para simular o AWS Rekognition —
nenhuma chamada de rede real é feita.

## SOLID

- **SRP:** cada handler verifica um único critério (texto, imagem); persistência fica isolada em `DjangoSubmissionRepository`.
- **OCP:** adicionar uma nova verificação (ex.: análise de spam por ML) = criar uma nova subclasse de `ModerationHandler` e religar a cadeia, sem tocar nas existentes.
- **LSP:** qualquer `ModerationHandler` pode substituir outro no encadeamento — todos respeitam o mesmo contrato `handle(submission) -> submission`.
- **ISP:** `ModerationHandler` e `SubmissionRepository` são interfaces pequenas e focadas.
- **DIP:** `SubmitContentUseCase` depende de `ModerationHandler`/`SubmissionRepository` (abstrações); `ImageSafetyHandler` depende do `Protocol` `ImageModerationClient`, não da implementação concreta do Rekognition.
