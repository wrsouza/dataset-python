# Plano — Extras (Scripts Generalistas)
> **Versão:** 1.0 | **Data:** 2026-06-25
> **Objetivo:** ~200 scripts Python independentes (não-pattern), cobrindo data processing, utilitários, algoritmos, exception handling e código prático. Cada script é um arquivo único, comentado, sem Docker/pytest/estrutura de projeto — ao contrário de `creational/structural/behavioral`.

---

## Diferenças em relação ao dataset de patterns

| Dimensão | Patterns (atual) | Extras (novo) |
|---|---|---|
| Unidade | Projeto completo (`pN/`) | 1 arquivo `.py` |
| Artefatos | README, Docker, tests, SOLID | Apenas o script + docstring/comentários inline |
| Tempo por unidade | ~1-2h (agente) | ~5-10min (agente) |
| Critério de qualidade | pytest/ruff/mypy/cobertura | Roda sem erro, comentado, didático, sem dependências exóticas |

---

## Estrutura de Diretórios

```
extras/
├── PLAN_EXTRAS.md          ← este arquivo
├── STATUS_EXTRAS.md        ← rastreamento (1 linha por script)
├── data_processing/
│   ├── pandas/              (~20)
│   ├── numpy/                (~15)
│   └── files_csv_json_excel/ (~15)
├── utilities/
│   ├── strings_regex/        (~15)
│   ├── file_io/               (~10)
│   ├── datetime/               (~10)
│   ├── validation/             (~10)
│   └── encoding_decoding/      (~5)
├── algorithms/
│   ├── sorting/               (~8)
│   ├── searching/             (~8)
│   ├── graphs/                (~10)
│   ├── dynamic_programming/   (~8)
│   └── trees/                 (~6)
├── exception_handling/
│   ├── custom_exceptions/     (~8)
│   ├── try_except_patterns/   (~8)
│   ├── logging_patterns/      (~8)
│   └── error_recovery/        (~6)
└── practical/
    ├── real_world_snippets/   (~10)
    ├── problem_solving/        (~8)
    ├── edge_cases/              (~6)
    └── performance/             (~6)
```

Convenção de nomes: `extras/<categoria>/<subtema>/NN_nome_descritivo.py`, numerado sequencialmente dentro da subpasta (`01_..`, `02_..`).

---

## Padrão de Script

Cada arquivo segue o template:

```python
"""
<Título curto>

O que este script demonstra: <1-2 frases>
Quando usar: <1 frase>
"""

# ... código comentado em pontos não-óbvios ...

if __name__ == "__main__":
    # exemplo de uso executável
    ...
```

Regras:
- Sem dependências fora de: `pandas`, `numpy`, `openpyxl`/`xlsxwriter` (para Excel), stdlib. Nada de framework/DB/cloud.
- Executável standalone via `python arquivo.py` (dados de exemplo embutidos ou gerados em runtime).
- Comentários explicam o *porquê*, não o *o quê* (mesma regra do projeto principal).
- Sem testes formais — opcionalmente um `assert` rápido ao final do `__main__` como sanity check.

---

## Estimativa de Esforço

| Categoria | Qtd | Esforço/script (agente) | Subtotal |
|---|---|---|---|
| Data Processing | 50 | ~8 min | ~6,5h |
| Utilities & Helpers | 50 | ~6 min | ~5h |
| Algoritmos | 40 | ~10 min | ~6,5h |
| Exception Handling | 30 | ~6 min | ~3h |
| Practical Code | 30 | ~10 min | ~5h |
| **Total** | **200** | — | **~26h de trabalho-agente** |

Isso é tempo de **execução de agente**, não tempo de relógio — ver paralelização abaixo. Inclui geração de código + revisão leve, não inclui validação humana final.

---

## Estratégia de Execução: 1 Sessão por Categoria

Em vez de paralelizar com subagentes dentro desta mesma conversa, cada **categoria** (data_processing, utilities, algorithms, exception_handling, practical) é executada em uma **sessão nova e independente do Claude Code**, focada apenas naquela categoria.

Motivos:
- Mantém o contexto de cada sessão pequeno e focado (sem acumular histórico de outras categorias).
- Permite rodar as 5 sessões em paralelo manualmente (5 janelas/worktrees), se desejado.
- Cada sessão pode usar subagentes internamente por subpasta, sem competir por contexto com as outras categorias.
- Rastreamento fica isolado: cada sessão só lê/escreve as linhas do seu bloco em `STATUS_EXTRAS.md`.

Cada categoria tem um **briefing autocontido** em `extras/briefings/<categoria>.md` — a nova sessão não precisa desta conversa, só precisa abrir esse arquivo. Os 5 briefings foram criados:

| Categoria | Briefing | Subpastas | Scripts |
|---|---|---|---|
| Data Processing | `extras/briefings/data_processing.md` | 3 | 50 |
| Utilities & Helpers | `extras/briefings/utilities.md` | 5 | 50 |
| Algoritmos | `extras/briefings/algorithms.md` | 5 | 40 |
| Exception Handling | `extras/briefings/exception_handling.md` | 4 | 30 |
| Practical Code | `extras/briefings/practical.md` | 4 | 30 |

### Como abrir cada sessão

Em uma sessão nova do Claude Code, dentro de `C:\Projects\dataset-python`, peça:
> "Leia `extras/briefings/<categoria>.md` e execute o briefing."

A sessão pode (a critério dela) usar subagentes em paralelo por subpasta dentro da própria categoria — isso é opcional, não obrigatório.

### Ordem recomendada

Não há dependência entre categorias — podem ser abertas nas 5 sessões **simultaneamente**. Se preferir sequencial (para revisar antes de seguir), sugestão de ordem por simplicidade crescente de revisão:
1. Exception Handling (30, mais previsível)
2. Utilities (50)
3. Data Processing (50, exige pandas/numpy instalados)
4. Practical (30)
5. Algoritmos (40, mais peso conceitual — bom revisar com calma)

### Esforço por sessão

| Categoria | Esforço-agente | Tempo de relógio (sessão única, sem subagentes internos) |
|---|---|---|
| Data Processing | ~6,5h | ~45-60min |
| Utilities | ~5h | ~35-45min |
| Algoritmos | ~6,5h | ~50-65min |
| Exception Handling | ~3h | ~25-30min |
| Practical | ~5h | ~35-45min |

Se cada sessão usar subagentes internos por subpasta, o tempo de relógio cai para ~10-15min por categoria.

---

## Próximos Passos

1. Revisar os briefings em `extras/briefings/` (títulos dos 200 scripts já estão listados lá).
2. Criar `extras/STATUS_EXTRAS.md` com os blocos por categoria (placeholders `[ ]`).
3. Abrir as sessões — uma por categoria, na ordem ou em paralelo, à sua escolha.
