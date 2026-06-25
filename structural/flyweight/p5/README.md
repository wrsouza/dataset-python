# Glyph Font Renderer

> **Design Pattern:** Flyweight | **Categoria:** Structural
> **Framework:** Streamlit | **Serviços:** Nenhum (sem banco de dados ou API externa)

## Objetivo Pedagógico

Demonstrar o pattern **Flyweight** em um renderizador de texto. Renderizar
texto longo caractere por caractere é caro em memória se cada ocorrência de
"A" em "Arial 12 bold" criar seu próprio objeto com bitmap e métricas. O
Flyweight resolve isso: existe **um único `Glyph`** por combinação
(caractere, fonte, tamanho, peso), compartilhado por todas as ocorrências
daquele caractere no texto. O aluno aprenderá a distinguir **estado
intrínseco** (compartilhável) de **estado extrínseco** (único por ocorrência)
e a medir, na prática, a economia de objetos que isso gera.

## O Pattern Aplicado

| Papel Flyweight | Classe | Responsabilidade |
|------------------|--------|-------------------|
| **Flyweight** (ConcreteFlyweight) | `Glyph` | Estado intrínseco imutável: `char`, `font_family`, `size`, `weight`, `bitmap` simulado, `width`/`height` |
| **FlyweightFactory** | `GlyphFactoryImpl` | Cache (`dict`) que garante a MESMA instância de `Glyph` para a mesma chave `(char, font_family, size, weight)` |
| **Context** | `PositionedGlyph` | Estado extrínseco: `x`, `y` — referencia o `Glyph` compartilhado, nunca duplica seus dados |
| **Strategy auxiliar** | `FontMetricsSimulator` (`FontMetricsProvider`) | Calcula bitmap/métricas de forma determinística, extensível por catálogo (OCP) |

### Estado Intrínseco vs Extrínseco

```
INTRÍNSECO (compartilhado — vive no Glyph)        EXTRÍNSECO (único — vive no PositionedGlyph)
────────────────────────────────────────          ──────────────────────────────────────────────
char           "A"                                 x, y     posição absoluta no layout
font_family    "Arial"
size           12
weight         "bold"
bitmap         "<bitmap:Arial:bold:12:'A':3f>"
width, height  derivados da métrica
```

Um texto de 10.000 caracteres usando poucas variações de fonte pode precisar
de apenas algumas dezenas de objetos `Glyph` — cada ocorrência adicional do
mesmo caractere reutiliza a mesma instância (comparável com `is`), pagando
apenas o custo de um `PositionedGlyph` (dois inteiros + uma referência).

## Diagrama UML / Fluxo (ASCII)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         src/fontrender/                             │
│                                                                       │
│  domain/                                                             │
│  ├── entities.py                                                     │
│  │     Glyph (Flyweight, frozen)         PositionedGlyph (Context)  │
│  │     FontStyle (value object)          CacheStatistics            │
│  └── interfaces.py                                                   │
│        GlyphFactory (Protocol)  FontMetricsProvider (Protocol)      │
│                       ▲                         ▲                   │
│                       │ implements               │ implements        │
│  application/         │                         │                   │
│  └── use_cases.py     │                         │                   │
│        RenderTextUseCase ──────────depends on────┘                  │
│        GetCacheStatisticsUseCase                                     │
│                       │                                              │
│  infrastructure/      │ injected at composition root                │
│  ├── glyph_factory.py │                                              │
│  │     GlyphFactoryImpl (cache dict) ◄── FontMetricsSimulator       │
│  ├── font_metrics.py                                                 │
│  │     FONT_METRIC_PROFILES (catálogo extensível — OCP)             │
│  └── (UI)  src/main.py — Streamlit                                  │
└─────────────────────────────────────────────────────────────────────┘

Fluxo do Flyweight:

   "AAAB"  ──► RenderTextUseCase.execute()
                     │
                     ▼  para cada caractere
              GlyphFactoryImpl.get_or_create(char, font, size, weight)
                     │
            ┌────────┴─────────┐
            │  chave já em      │  chave nova
            │  cache?           │
            ▼ sim (hit)         ▼ não (miss)
      retorna Glyph        cria novo Glyph
      EXISTENTE            e guarda no cache
            │                   │
            └─────────┬─────────┘
                       ▼
        Glyph COMPARTILHADO (mesma instância)
                       │
     ┌─────────────────┼─────────────────┬─────────────────┐
     ▼                 ▼                 ▼                 ▼
PositionedGlyph   PositionedGlyph   PositionedGlyph   PositionedGlyph
 (x=0,y=0,'A')     (x=8,y=0,'A')     (x=16,y=0,'A')    (x=24,y=0,'B')
        \________________\________________/                  |
                  todas referenciam o MESMO Glyph('A')   Glyph('B') próprio
```

## Princípios SOLID Demonstrados

- **S (Single Responsibility):** `Glyph`/`PositionedGlyph` (estado), `GlyphFactoryImpl`
  (cache), `RenderTextUseCase`/`GetCacheStatisticsUseCase` (lógica de aplicação) e
  `src/main.py` (apresentação Streamlit) vivem em módulos distintos, cada um
  com um único motivo para mudar.
- **O (Open/Closed):** novas famílias de fonte são adicionadas registrando uma
  entrada em `FONT_METRIC_PROFILES` (`src/fontrender/infrastructure/font_metrics.py`)
  — nenhum código em `GlyphFactoryImpl`, nos use cases ou no domínio precisa
  ser alterado. Não há `if/elif` por família de fonte.
- **D (Dependency Inversion):** `RenderTextUseCase` e `GetCacheStatisticsUseCase`
  dependem apenas do protocolo `GlyphFactory` (`domain/interfaces.py`), nunca de
  `GlyphFactoryImpl` diretamente. `GlyphFactoryImpl`, por sua vez, depende do
  protocolo `FontMetricsProvider`, não de `FontMetricsSimulator` fixa — a
  implementação concreta é injetada na composição root (`src/main.py`).

## Como Rodar

### Localmente com Streamlit

```bash
pip install -e ".[dev]"
streamlit run src/main.py
```

Acesse `http://localhost:8501`.

### Via Docker Compose

```bash
cp .env.example .env
docker-compose up --build
```

Acesse `http://localhost:8501`.

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Ou localmente:

```bash
pytest --cov=src --cov-report=term-missing
```

`src/main.py` (UI Streamlit) é excluído da cobertura via
`[tool.coverage.run] omit` em `pyproject.toml` — os testes cobrem apenas
`domain/`, `application/` e a parte não-UI de `infrastructure/`.
