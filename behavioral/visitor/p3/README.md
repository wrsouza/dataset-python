# Content Export Visitor (Visitor) — P3

API Django que exporta conteúdo (artigos, imagens, vídeos) em
diferentes formatos (JSON, Markdown) e envia o resultado para o S3,
sem nenhum `isinstance` — cada nó decide para qual `visit_X` se
despachar.

> **Nota de ambiente:** o log de jobs de exportação usa SQLite — o
> PLAN.md só especifica AWS S3 para este projeto, sem banco relacional
> (mesmo precedente de outros projetos do dataset sem BD especificado).

## Objetivo pedagógico

Demonstrar o pattern **Visitor**: `ContentNode` (Element) expõe só
`accept(visitor)` — `ArticleContent`/`ImageContent`/`VideoContent`
nunca sabem qual formato de exportação está sendo gerado. Adicionar um
novo formato (ex.: HTML) é só uma nova classe `ContentVisitor`, sem
tocar nos nós existentes.

Elementos do pattern:
- **Visitor (abstrato):** `ContentVisitor` (`domain/interfaces.py`)
- **Element (abstrato):** `ContentNode`
- **Concrete Elements:** `ArticleContent`, `ImageContent`, `VideoContent`
- **Concrete Visitors:** `JSONExportVisitor`, `MarkdownExportVisitor` (`infrastructure/visitors/`)

## Diagrama (ASCII)

```
traverse(nodes, visitor)
        │
        └─► for node in nodes: node.accept(visitor)
                    │
                    ▼
        ArticleContent.accept() ──► visitor.visit_article(self)
        ImageContent.accept()   ──► visitor.visit_image(self)
        VideoContent.accept()   ──► visitor.visit_video(self)
                    │
                    ▼
              visitor.result ──► S3.put_object() ──► ExportJobModel (log)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

API disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota                              | Descrição                                  |
|--------|-------------------------------------|---------------------------------------------|
| POST   | `/exports/<json\|markdown>/`        | Exporta os nós para S3 no formato escolhido   |
| GET    | `/exports/jobs/<job_id>/`           | Consulta um job de exportação já executado    |

```bash
curl -X POST http://localhost:8000/exports/json/ \
  -H "Content-Type: application/json" \
  -d '{"nodes": [{"type": "article", "title": "Hello", "body": "World"}]}'
```

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`ExportContentUseCase` é testado com um `FakeS3Client` em memória nos
testes unitários, e com `moto[s3]` (bucket real simulado) nos testes
de integração das views.

## SOLID

- **SRP:** cada visitor concreto só sabe renderizar seu próprio formato; `DjangoExportJobRepository` só persiste/recupera o log de jobs.
- **OCP:** um novo formato é uma nova classe `ContentVisitor` mais uma entrada em `_VISITOR_FACTORIES` — sem tocar nos nós existentes.
- **LSP:** qualquer `ContentVisitor` concreto pode ser usado em `traverse()` sem quebrar o contrato — todos implementam os três `visit_X`.
- **ISP:** `ContentVisitor` expõe só os métodos que os elementos realmente chamam; `ContentNode` expõe só `accept()`.
- **DIP:** `ExportContentUseCase` depende de `S3ClientLike` (Protocol) e `DjangoExportJobRepository`, nunca do cliente boto3 concreto diretamente.
