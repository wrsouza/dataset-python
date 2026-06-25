# Data Validation Pipeline (Chain of Responsibility) — P5

Aplicação Streamlit onde cada registro digitado pelo usuário passa por uma
cadeia de validadores — campos obrigatórios → tipo → faixa de valor →
aprovação final — até receber um veredito (`VALID`/`INVALID`).

## Objetivo pedagógico

Demonstrar o pattern **Chain of Responsibility** de forma visual e
interativa: cada handler decide, isoladamente, se rejeita o registro ou o
passa adiante, e a UI exibe o histórico completo da cadeia (qual handler
decidiu, e por quê).

Elementos do pattern:
- **Handler (abstrato):** `ValidationHandler` (`domain/interfaces.py`)
- **Concrete Handlers:** `RequiredFieldsHandler`, `TypeCheckHandler`, `RangeCheckHandler`, `ApprovalHandler`
- **Client:** `ValidateRecordUseCase`, que dispara `chain.handle(record)` sem conhecer a topologia da cadeia

## Diagrama (ASCII)

```
Streamlit form
      │
      ▼
ValidateRecordUseCase
      │
      ▼
RequiredFieldsHandler ──(campos presentes)──► TypeCheckHandler ──(tipos OK)──► RangeCheckHandler ──(dentro da faixa)──► ApprovalHandler
     │ rejeita                                     │ rejeita                          │ rejeita                              │ aprova (sempre)
     ▼                                              ▼                                  ▼                                      ▼
  DataRecord (com 1 ValidationStep no histórico, exibido na UI)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

Acesse `http://localhost:8501`. Preencha o formulário e clique em "Validar"
para ver o resultado e o histórico da cadeia.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

O arquivo `infrastructure/app.py` (camada de UI do Streamlit) é excluído da
medição de cobertura, seguindo o mesmo padrão dos demais projetos Streamlit
do dataset — a lógica do pattern em si (domain/application/infrastructure
exceto `app.py`) é testada diretamente.

## SOLID

- **SRP:** cada handler verifica um único critério (presença, tipo, faixa); a UI não implementa nenhuma regra de validação.
- **OCP:** adicionar uma nova verificação (ex.: validação de formato de e-mail) = criar uma nova subclasse de `ValidationHandler` e religar a cadeia, sem tocar nas existentes.
- **LSP:** qualquer `ValidationHandler` pode substituir outro no encadeamento — todos respeitam o mesmo contrato `handle(record) -> record`.
- **ISP:** `ValidationHandler` é uma interface pequena e focada (um único método abstrato).
- **DIP:** `ValidateRecordUseCase` depende de `ValidationHandler` (abstração); a UI depende apenas do use case, nunca dos handlers concretos diretamente.
