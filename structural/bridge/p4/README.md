# Export Format Bridge

> **Design Pattern:** Bridge | **Categoria:** Structural
> **Framework:** CLI Typer | **Serviços:** nenhum

## Objetivo Pedagógico

Este projeto demonstra o pattern **Bridge** aplicado à exportação de relatórios: uma
CLI que exporta o mesmo `Report` para CSV, JSON, XML ou Excel sem que a lógica de
exportação conheça os detalhes de codificação de cada formato. O aluno deve conseguir
identificar:

- **Abstraction:** `ReportExporter` (`src/exporter/application/use_cases.py`)
- **Implementor:** `FormatExporter` (`src/exporter/domain/interfaces.py`)
- **ConcreteImplementor:** `CsvFormatExporter`, `JsonFormatExporter`, `XmlFormatExporter`,
  `ExcelFormatExporter` (`src/exporter/infrastructure/`)
- **Client:** `ExportReportUseCase` e a CLI (`cli.py`), que dependem apenas de
  `ReportExporter`/`FormatExporter`

## O Pattern Aplicado

`ReportExporter` é a Abstraction: expõe uma API estável (`export`) para o código
cliente, mas não sabe como bytes são produzidos — ela delega essa responsabilidade a
um `FormatExporter` injetado no construtor (o Implementor). Cada formato concreto
(CSV, JSON, XML, Excel) implementa `serialize()`, `file_extension()` e `format_name()`
de forma independente. Isso significa que a Abstraction e a Implementação variam em
eixos diferentes: é possível adicionar um novo formato (ex.: YAML) sem tocar em
`ReportExporter`, e é possível estender `ReportExporter` (ex.: `CompressedReportExporter`
que zipa o resultado) sem tocar nos formatos.

## Diagrama UML (ASCII)

```
                <<Abstraction>>                      <<Implementor>>
                ReportExporter                        FormatExporter
                ─────────────────────                 ──────────────────
                - format_exporter: FormatExporter      + serialize(report): bytes
                + export(report): bytes                + file_extension(): str
                + format_name(): str                   + format_name(): str
                + file_extension(): str                       ▲
                         │ delegates to                        │
                         └───────────────────────►   ┌─────────┼─────────┬──────────┐
                                                      │         │         │          │
                                              CsvFormat  JsonFormat  XmlFormat  ExcelFormat
                                              Exporter   Exporter    Exporter   Exporter
                                            (ConcreteImplementors — uma por formato)
```

A Abstraction (`ReportExporter`) e a hierarquia de Implementors (`FormatExporter`)
evoluem de forma independente: trocar o formato é apenas trocar qual
`FormatExporter` concreto é injetado — nenhuma classe de Abstraction muda.

## Princípios SOLID Demonstrados

- **O (Open/Closed):** novos formatos de exportação são adicionados criando uma nova
  classe em `infrastructure/` que implementa `FormatExporter` e registrando-a em
  `build_format_exporter()` (`infrastructure/factory.py`). `ReportExporter`,
  `ExportReportUseCase` e a CLI permanecem inalterados.
- **D (Dependency Inversion):** `ReportExporter` e `ExportReportUseCase`
  (`application/use_cases.py`) recebem suas dependências via construtor e dependem
  apenas da abstração `FormatExporter` — nunca importam `csv`, `json`, `xml` ou
  `openpyxl` diretamente. A única peça que conhece as implementações concretas é
  `cli.py`, a composition root.
- **I (Interface Segregation):** `FormatExporter` tem apenas três métodos coesos
  (`serialize`, `file_extension`, `format_name`), todos relevantes para qualquer
  implementação de formato — nenhum método é deixado vazio ou lança
  `NotImplementedError`.
- **L (Liskov Substitution):** todas as `ConcreteImplementor`s são substituíveis por
  `FormatExporter` sem alterar o comportamento esperado: mesma assinatura, mesmo
  contrato de retorno (`bytes`), nenhuma lança exceções fora do esperado.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

A CLI fica disponível dentro do container `app`. Exemplos de uso:

```bash
docker-compose run --rm app python -m exporter.cli list-formats
docker-compose run --rm app python -m exporter.cli export "Sales Report" data/sales.json --format csv
docker-compose run --rm app python -m exporter.cli export "Sales Report" data/sales.json --format excel -o ./exports
```

O arquivo `data_file` é um JSON simples:

```json
{
  "columns": ["product", "units", "revenue"],
  "rows": [
    {"product": "Widget", "units": 10, "revenue": 199.9},
    {"product": "Gadget", "units": 5, "revenue": 249.5}
  ]
}
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente (fora do Docker), com um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

Os testes unitários (`tests/unit/`) cobrem cada `FormatExporter` isoladamente e a
`ReportExporter`/`ExportReportUseCase` com um `FormatExporter` falso, sem tocar disco
fora de diretórios temporários. Os testes de integração (`tests/integration/`)
exercitam o fluxo completo via `ExportReportUseCase` escrevendo arquivos reais em um
diretório temporário para cada formato suportado.
