# P2 — Image Thumbnail Cache (Flyweight)

**Framework:** Flask + LocalStack (S3)  
**Domain:** `thumbnails`  
**Pattern:** Flyweight — `ThumbnailSpec` (frozen dataclass) shared across `ImageThumbnail` contexts.

## Flyweight Roles

| Role | Class | Responsabilidade |
|------|-------|-----------------|
| Flyweight | `ThumbnailSpec` | Estado intrínseco: width, height, quality, format, filters |
| FlyweightFactory | `ThumbnailSpecFactory` | Pool com `get_or_create()` — retorna MESMA instância para params iguais |
| Context | `ImageThumbnail` | Estado extrínseco: image_key + thumbnail_key; referência ao Flyweight |

## Economia de Memória

| Cenário | Objetos | Bytes estimados |
|---------|---------|-----------------|
| 10.000 thumbnails **sem** Flyweight | 10.000 specs | ~2.000.000 bytes |
| 10.000 thumbnails **com** Flyweight | 6 specs compartilhadas | ~12.480 bytes |
| **Economia** | — | **~99,4%** |

> Cada `ThumbnailSpec` ocupa ~200 bytes. Sem Flyweight, cada thumbnail duplicaria esses dados.  
> Com Flyweight, 10.000 thumbnails compartilham apenas 6 objetos de spec.

## SOLID

| Princípio | Onde |
|-----------|------|
| **SRP** | `GenerateThumbnailUseCase`, `GetThumbnailUseCase`, `GetFactoryStatsUseCase` — cada um tem uma única responsabilidade |
| **DIP** | Use cases dependem de `ImageStorageProtocol`, `ThumbnailRepositoryProtocol`, `ThumbnailSpecFactoryProtocol` — não de classes concretas |

## Rotas

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/thumbnails/generate` | Gera thumbnail; body: `{"image_key": "...", "spec_name": "thumb_sm"}` |
| `GET` | `/thumbnails/<image_key>/<spec_name>` | Retorna metadados + URL do thumbnail |
| `GET` | `/specs` | Lista todos os ThumbnailSpec Flyweights |
| `GET` | `/factory/stats` | Estatísticas: specs únicos vs total thumbnails, economia de memória |

## Specs pré-definidas

| Nome | Dimensões | Qualidade | Formato |
|------|-----------|-----------|---------|
| `thumb_sm` | 120×120 | 75 | JPEG |
| `thumb_md` | 300×300 | 80 | JPEG |
| `thumb_lg` | 600×600 | 85 | JPEG |
| `banner` | 1200×400 | 90 | JPEG |
| `avatar` | 64×64 | 85 | PNG |
| `webp_sm` | 200×200 | 80 | WEBP |

## Como rodar

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir serviços
docker-compose up --build

# 3. Testes
docker-compose run --rm app pytest

# Sem Docker
pip install -e ".[dev]"
cp .env.example .env
flask --app src.main run --port 5000
```

## Exemplo de uso

```bash
# Upload de imagem de teste para o LocalStack
aws --endpoint-url=http://localhost:4566 s3 cp photo.jpg s3://thumbnails/photo.jpg

# Gerar thumbnail
curl -X POST http://localhost:5000/thumbnails/generate \
  -H "Content-Type: application/json" \
  -d '{"image_key": "photo.jpg", "spec_name": "thumb_md"}'

# Ver stats do Flyweight pool
curl http://localhost:5000/factory/stats
```
