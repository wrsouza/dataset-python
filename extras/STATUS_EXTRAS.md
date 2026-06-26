# Status — Extras (Scripts Generalistas)
> Cada sessão (uma por categoria) atualiza apenas seu próprio bloco.
> `[ ]` planejado · `[x]` script criado e executado sem erro

## Resumo

| Categoria | Briefing | Scripts | Status |
|---|---|---|---|
| Data Processing | `extras/briefings/data_processing.md` | 50 | `[x]` 50/50 |
| Utilities & Helpers | `extras/briefings/utilities.md` | 50 | `[x]` 50/50 |
| Algoritmos | `extras/briefings/algorithms.md` | 40 | `[x]` 40/40 |
| Exception Handling | `extras/briefings/exception_handling.md` | 30 | `[x]` 30/30 |
| Practical Code | `extras/briefings/practical.md` | 30 | `[x]` 30/30 |
| **TOTAL** | | **200** | `[x]` 200/200 |

---

## Data Processing (50/50)
- [x] pandas (20/20)
- [x] numpy (15/15)
- [x] files_csv_json_excel (15/15)

## Utilities & Helpers (50/50)
- [x] strings_regex (15/15)
- [x] file_io (10/10)
- [x] datetime (10/10)
- [x] validation (10/10)
- [x] encoding_decoding (5/5)

## Algoritmos (40/40)
- [x] sorting (8/8)
- [x] searching (8/8)
- [x] graphs (10/10)
- [x] dynamic_programming (8/8)
- [x] trees (6/6)

## Exception Handling (30/30)
- [x] custom_exceptions (8/8)
- [x] try_except_patterns (8/8)
- [x] logging_patterns (8/8)
- [x] error_recovery (6/6)

## Practical Code (30/30)
- [x] real_world_snippets (10/10)
- [x] problem_solving (8/8)
- [x] edge_cases (6/6)
- [x] performance (6/6)

---

## Log de Alterações
- 2026-06-25 — Criado `STATUS_EXTRAS.md` e os 5 briefings em `extras/briefings/`. Nenhum script criado ainda.
- 2026-06-25 — Categoria Data Processing concluída: 50/50 scripts criados em `extras/data_processing/{pandas,numpy,files_csv_json_excel}`, todos executados sem erro (3 subagentes em paralelo, 1 por subpasta).
- 2026-06-25 — Categoria Utilities & Helpers concluída: 50/50 scripts criados em `extras/utilities/{strings_regex,file_io,datetime,validation,encoding_decoding}`, todos executados sem erro (5 subagentes em paralelo, 1 por subpasta).
- 2026-06-25 — Categoria Algoritmos concluída: 40/40 scripts criados em `extras/algorithms/{sorting,searching,graphs,dynamic_programming,trees}`, todos executados sem erro (5 subagentes em paralelo, 1 por subpasta).
- 2026-06-26 — Categoria Exception Handling concluída: 30/30 scripts criados em `extras/exception_handling/{custom_exceptions,try_except_patterns,logging_patterns,error_recovery}` (4 subagentes em paralelo, 1 por subpasta). Faltava `logging_patterns/08_logging_supressao_ruido_terceiros.py`, criado manualmente. Corrigido bug de off-by-one em `error_recovery/02_circuit_breaker_simples.py` (estouro de exceção não tratada após o teste half-open). Todos os 30 scripts executados e validados sem erro.
- 2026-06-26 — Categoria Practical Code concluída: 30/30 scripts criados em `extras/practical/{real_world_snippets,problem_solving,edge_cases,performance}` (4 subagentes em paralelo, 1 por subpasta). Todos os 30 scripts executados e validados sem erro. **Dataset de extras (200/200 scripts) concluído.**
