# Code Metrics Visitor (Visitor) — P4

CLI Typer que roda diferentes métricas (linhas, complexidade,
cobertura de docstring) sobre a estrutura de um módulo descrita em
JSON — sem nenhum serviço externo.

## Objetivo pedagógico

Demonstrar o pattern **Visitor** combinado com **Composite**:
`ModuleNode`/`ClassNode` despacham `accept()` para seus filhos antes
de se visitarem (pós-ordem), então `FunctionNode`/`ClassNode`/
`ModuleNode` nunca sabem qual métrica está sendo calculada. Adicionar
uma nova métrica (ex.: contagem de imports) é só uma nova classe
`CodeMetricVisitor`, sem tocar na estrutura de nós.

Elementos do pattern:
- **Visitor (abstrato):** `CodeMetricVisitor` (`domain/interfaces.py`)
- **Element (abstrato):** `CodeElement`
- **Concrete Elements:** `FunctionNode`, `ClassNode`, `ModuleNode` (Composite)
- **Concrete Visitors:** `LineCountVisitor`, `ComplexityVisitor`, `DocCoverageVisitor` (`infrastructure/visitors/`)

## Diagrama (ASCII)

```
ModuleNode.accept(visitor)
        │
        ├─► for cls in classes: cls.accept(visitor)
        │         └─► for method in methods: method.accept(visitor) ──► visit_function
        │             visitor.visit_class(cls)
        ├─► for fn in functions: fn.accept(visitor) ──► visit_function
        └─► visitor.visit_module(self)
                    │
                    ▼
              visitor.result
```

## Como rodar

```bash
docker-compose run --rm app python -m code_metrics_visitor.main analyze module.json --metric lines
docker-compose run --rm app python -m code_metrics_visitor.main list-metrics
```

### Formato do JSON de entrada

```json
{
  "name": "my_module",
  "functions": [{"name": "f", "line_count": 5, "branch_count": 1, "has_docstring": true}],
  "classes": [{"name": "C", "has_docstring": false, "methods": [...]}]
}
```

### Comandos

| Comando        | Descrição                                              |
|------------------|------------------------------------------------------|
| `analyze`        | Roda a métrica escolhida (`-m`) sobre o módulo JSON     |
| `list-metrics`    | Lista os nomes das métricas disponíveis                 |

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

## SOLID

- **SRP:** cada visitor concreto só sabe calcular sua própria métrica; `FunctionNode`/`ClassNode`/`ModuleNode` só conhecem sua própria estrutura.
- **OCP:** uma nova métrica é uma nova classe `CodeMetricVisitor` mais uma entrada em `_VISITOR_FACTORIES` — sem tocar nos nós existentes.
- **LSP:** qualquer `CodeMetricVisitor` concreto pode ser usado em `traverse()` sem quebrar o contrato — todos implementam os três `visit_X`.
- **ISP:** `CodeMetricVisitor` expõe só os três métodos que os elementos realmente chamam; `CodeElement` expõe só `accept()`.
- **DIP:** `AnalyzeModuleUseCase` depende de `CodeMetricVisitor` (abstração) via o registro, nunca de uma classe concreta diretamente.
