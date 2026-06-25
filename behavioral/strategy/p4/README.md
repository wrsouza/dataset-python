# Compression Strategy CLI (Strategy) — P4

CLI Typer que comprime/descomprime arquivos com um codec
intercambiável, escolhido na linha de comando — sem nenhum serviço
externo, só a stdlib (`gzip`, `zlib`, `bz2`).

## Objetivo pedagógico

Demonstrar o pattern **Strategy**: `FileCompressor` (Context) não sabe
nada sobre o formato de compressão — delega para a
`CompressionStrategy` configurada, intercambiável em tempo de execução
via `set_strategy()`. Adicionar um novo codec (ex.: `lzma`) é só uma
nova classe, sem tocar no Context nem nas demais estratégias.

Elementos do pattern:
- **Context:** `FileCompressor` (`application/context.py`)
- **Strategy (abstrato):** `CompressionStrategy` (`domain/interfaces.py`)
- **Concrete Strategies:** `GzipCompressionStrategy`, `ZlibCompressionStrategy`, `Bz2CompressionStrategy`, `NoneCompressionStrategy` (`infrastructure/strategies/`)

## Diagrama (ASCII)

```
compress file.txt --strategy gzip
        │
        ▼
get_strategy("gzip") ──► GzipCompressionStrategy
        │
        ▼
FileCompressor.compress() ──► strategy.compress() ──► CompressionResult
        │
        ▼
file.txt.gz (escrito em disco)
```

## Como rodar

```bash
docker-compose run --rm app python -m compression_strategy_cli.main compress file.txt --strategy gzip
docker-compose run --rm app python -m compression_strategy_cli.main decompress file.txt.gz --strategy gzip
docker-compose run --rm app python -m compression_strategy_cli.main list-strategies
```

### Comandos

| Comando           | Descrição                                              |
|--------------------|-----------------------------------------------------------|
| `compress`         | Comprime um arquivo com a estratégia escolhida (`-s`)      |
| `decompress`       | Descomprime um arquivo com a estratégia escolhida (`-s`)   |
| `list-strategies`  | Lista os nomes das estratégias disponíveis                 |

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Todas as estratégias são testadas com um round-trip
`compress`/`decompress` parametrizado, garantindo que cada uma honra o
mesmo contrato.

## SOLID

- **SRP:** cada estratégia concreta só sabe codificar/decodificar seu próprio formato; os use cases só leem/escrevem arquivos.
- **OCP:** um novo codec é uma nova classe `CompressionStrategy` mais uma entrada em `_STRATEGY_MAP` — sem tocar nas estratégias existentes.
- **LSP:** qualquer `CompressionStrategy` concreta pode substituir outra em `FileCompressor` sem quebrar o contrato — todas fazem o round-trip `compress`/`decompress`.
- **ISP:** `CompressionStrategy` expõe só os quatro métodos que o Context realmente precisa.
- **DIP:** `FileCompressor` e os use cases dependem de `CompressionStrategy` (abstração), nunca das classes concretas diretamente.
