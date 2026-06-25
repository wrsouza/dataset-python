# Build Task Composite

> **Design Pattern:** Composite | **Categoria:** Structural
> **Framework:** CLI Typer | **Serviços:** Nenhum (sem dependências externas)

## Objetivo Pedagógico

Demonstrar o pattern Composite em um executor de build tasks, ao estilo de
um Makefile/Gradle simplificado. O aluno deve aprender a tratar uma tarefa
atômica (compilar, rodar testes) e um grupo de tarefas (que pode conter
outros grupos) através da mesma interface, sem nenhum `isinstance` no
código cliente.

## O Pattern Aplicado

- **Component:** `BuildTask` (`src/build_tasks/domain/interfaces.py`) — ABC
  com `name`, `execute() -> TaskResult` e `estimated_duration_seconds()`.
- **Leaf:** `ShellCommandTask`, `PythonFunctionTask`, `SimulatedTask`
  (`src/build_tasks/infrastructure/leaf_tasks.py`) — tarefas atômicas que
  fazem o trabalho real (ou simulado, para fins didáticos).
- **Composite:** `TaskGroup`
  (`src/build_tasks/infrastructure/task_group.py`) — guarda uma lista
  ordenada de `BuildTask` (que podem ser outros `TaskGroup`s) e executa cada
  filho sequencialmente, agregando os resultados em um único `TaskResult`.
- **Client:** a CLI Typer (`src/cli/main.py`) e o use case
  `ExecuteBuildTaskUseCase` chamam apenas `task.execute()` — nunca sabem (e
  não precisam saber) se `task` é uma tarefa simples ou uma árvore com
  dezenas de tarefas aninhadas.

Uma árvore de exemplo (`examples/build_all.yml`):

```
build_all (group)
├── compile (leaf)
├── test_all (group)
│   ├── unit_tests (leaf)
│   └── integration_tests (leaf)
└── package (leaf)
```

## Diagrama UML (ASCII)

```
        <<abstract>>
          BuildTask
   ---------------------------
   + name: str
   + execute(): TaskResult
   + estimated_duration_seconds(): float
            ^
            |
   -----------------------------------------------
   |                    |                        |
ShellCommandTask   SimulatedTask            TaskGroup
(Leaf)             (Leaf)                   (Composite)
                                       ---------------------------
                                       - children: list[BuildTask]
                                       ---------------------------
                                       + add(task: BuildTask)
                                       + execute(): TaskResult
                                             |
                                             | contém 0..N
                                             v
                                          BuildTask  (recursivo)
```

## Princípios SOLID Demonstrados

- **SRP (Single Responsibility):** a definição da árvore de tasks
  (`infrastructure/definition_parser.py`), a execução/agregação
  (`application/use_cases.py`) e a apresentação CLI (`cli/main.py`) vivem em
  módulos separados, cada um com um único motivo para mudar.
- **OCP (Open/Closed):** novos tipos de Leaf (ex: `ShellCommandTask`,
  `PythonFunctionTask`) são adicionados implementando `BuildTask`, sem
  modificar `TaskGroup` nem o use case de execução. O parser também aceita
  novos tipos de leaf adicionando uma entrada em `SUPPORTED_LEAF_TYPES`.
- **LSP (Liskov Substitution):** `TaskGroup` e qualquer Leaf são
  totalmente substituíveis onde `BuildTask` é esperado — `test_client_treats_leaf_and_composite_identically`
  em `tests/unit/test_task_group.py` exercita exatamente essa garantia.
- **DIP (Dependency Inversion):** `ExecuteBuildTaskUseCase` e
  `BuildTaskTreeFromFileUseCase` dependem apenas da abstração `BuildTask`,
  nunca de uma implementação concreta.

## Formato do Arquivo de Definição

Arquivos `.yml`/`.yaml` ou `.json` descrevem a árvore recursivamente:

```yaml
type: group            # "group" (Composite) ou um tipo de leaf
name: build_all
stop_on_failure: true  # opcional, default true; só se aplica a groups
tasks:
  - type: simulated     # leaf didático, não executa nada real
    name: compile
    duration_seconds: 0.2
    should_succeed: true
  - type: shell          # leaf real, roda via subprocess
    name: run_lint
    command: "echo linting..."
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

### Exemplos de uso da CLI

```bash
# Executar a árvore completa de um arquivo de definição
python -m src.cli run examples/build_all.yml

# Apenas descrever a árvore e sua duração estimada, sem executar
python -m src.cli describe examples/build_all.yml
```

Saída de exemplo (`run`):

```
[OK] build_all (0.602s)
  [OK] compile (0.200s)
  [OK] test_all (0.700s)
    [OK] unit_tests (0.300s)
    [OK] integration_tests (0.400s)
  [OK] package (0.100s)

SUCCESS — 4 succeeded, 0 failed, 0.602s total
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```
