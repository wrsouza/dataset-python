# Dashboard Component Mediator (Mediator) — P5

Aplicação Streamlit com três widgets — filtro, tabela e resumo — que nunca
se referenciam diretamente. Todos leem e escrevem o estado compartilhado
através de um único `InMemoryDashboardMediator`.

## Objetivo pedagógico

Demonstrar o pattern **Mediator** numa UI declarativa: o widget de filtro
muda o estado através do mediador; os widgets de tabela e resumo leem o
mesmo estado, também através do mediador — nenhum deles sabe que os
outros existem. Trocar ou adicionar um widget nunca exige tocar nos
demais.

Elementos do pattern:
- **Mediator (abstrato):** `DashboardMediator` (`domain/interfaces.py`)
- **Concrete Mediator:** `InMemoryDashboardMediator` — guarda o filtro atual e o dataset, calcula o resultado filtrado
- **Colleagues:** `render_filter_panel`, `render_table_widget`, `render_summary_widget` — cada um só conhece o mediador
- **Client:** `UpdateFilterUseCase`/`GetDashboardDataUseCase`

## Diagrama (ASCII)

```
render_filter_panel ──UpdateFilterUseCase.execute(category, max_price)──► InMemoryDashboardMediator.set_filter()
                                                                                    │
                                                                                    ▼
render_table_widget ──GetDashboardDataUseCase.execute()──► mediator.get_filtered_products() ──► tabela
render_summary_widget ──GetDashboardDataUseCase.execute()──► mediator.get_filtered_products() ──► métricas

(nenhum widget chama o outro — todos passam pelo mesmo InMemoryDashboardMediator,
 mantido em st.session_state entre reruns do Streamlit)
```

## Como rodar

```bash
cp .env.example .env
docker-compose up --build
```

Acesse `http://localhost:8501`. Mude a categoria ou o preço máximo no
painel de filtro e veja a tabela e o resumo se atualizarem juntos.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

O arquivo `infrastructure/app.py` (camada de UI do Streamlit) é excluído
da medição de cobertura, seguindo o mesmo padrão dos demais projetos
Streamlit do dataset.

## SOLID

- **SRP:** `InMemoryDashboardMediator` só guarda estado e filtra; cada widget só sabe renderizar sua própria visão.
- **OCP:** adicionar um novo widget (ex.: gráfico de pizza) = ler do mesmo `DashboardMediator`, sem tocar nos widgets existentes.
- **LSP:** qualquer `DashboardMediator` pode substituir outro nos use cases — todos respeitam o mesmo contrato `set_filter`/`get_filter`/`get_filtered_products`/`get_categories`.
- **ISP:** `DashboardMediator` é uma interface pequena e focada.
- **DIP:** `UpdateFilterUseCase`/`GetDashboardDataUseCase` dependem de `DashboardMediator` (abstração); a UI é o único lugar que conhece `InMemoryDashboardMediator`.
