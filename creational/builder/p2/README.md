# Report Builder (PDF / Excel / CSV)

> **Design Pattern:** Builder
> **Categoria:** Creational
> **Framework:** Flask
> **Serviços:** (nenhum externo — tudo in-process)

## Objetivo Pedagógico

Demonstra como o padrão Builder desacopla a lógica de montagem de um relatório (Director)
do formato de saída (ConcreteBuilder). O mesmo conteúdo — título, tabelas, rodapé — é
produzido em CSV, Excel ou PDF sem alterar uma linha dos Directors. O aluno aprende que
novos formatos são adicionados criando novos builders, nunca modificando os existentes.

## O Pattern em Ação

| Papel do Pattern   | Classe                    | Arquivo                                        |
|--------------------|---------------------------|------------------------------------------------|
| Builder (interface)| `ReportBuilder`           | `src/report_builder/domain/interfaces.py`      |
| ConcreteBuilder    | `CSVReportBuilder`        | `src/report_builder/infrastructure/builders.py`|
| ConcreteBuilder    | `ExcelReportBuilder`      | `src/report_builder/infrastructure/builders.py`|
| ConcreteBuilder    | `PDFReportBuilder`        | `src/report_builder/infrastructure/builders.py`|
| Director           | `SalesReportDirector`     | `src/report_builder/application/use_cases.py`  |
| Director           | `InventoryReportDirector` | `src/report_builder/application/use_cases.py`  |
| Product            | `Report`                  | `src/report_builder/domain/entities.py`        |

## Diagrama UML

```
<<abstract>>
ReportBuilder
+ set_title(title) -> Self
+ add_header(text) -> Self
+ add_data_table(table) -> Self
+ add_chart(chart) -> Self
+ add_footer(text) -> Self
+ build() -> Report
        |
        ├── CSVReportBuilder    (csv stdlib)
        ├── ExcelReportBuilder  (openpyxl)
        └── PDFReportBuilder    (reportlab)

SalesReportDirector      InventoryReportDirector
- _builder: ReportBuilder
+ build(data) -> Report
```

## Princípios SOLID Demonstrados

- **O — Open/Closed:** Para adicionar um formato PPTX, cria-se `PPTXReportBuilder`
  implementando `ReportBuilder` — sem alterar nenhum Director ou `ReportBuilder`.
- **D — Dependency Inversion:** `SalesReportDirector` depende de `ReportBuilder`
  (abstração). O builder concreto é injetado na rota Flask.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
# API: http://localhost:5000
```

## Endpoints

```bash
# Gerar CSV de vendas
curl -X POST http://localhost:5000/reports/csv \
  -H "Content-Type: application/json" \
  -d '{"type":"sales","data":{"period":"Q1 2024","rows":[["2024-01-01","Alice","Widget",2,100.0]],"total":100.0}}'

# Gerar Excel de inventário
curl -X POST http://localhost:5000/reports/excel \
  -H "Content-Type: application/json" \
  -d '{"type":"inventory","data":{"warehouse":"Main","rows":[["SKU1","Widget","Electronics",50,10]]}}'

# Gerar PDF de vendas
curl -X POST http://localhost:5000/reports/pdf \
  -H "Content-Type: application/json" \
  -d '{"type":"sales","data":{"period":"Q1 2024","rows":[["2024-01-01","Bob","Gadget",1,75.0]],"total":75.0}}'

# Listar templates disponíveis
curl http://localhost:5000/reports/templates
```

## Rodar os Testes

```bash
docker-compose run --rm app pytest --cov=src --cov-report=term-missing
```
