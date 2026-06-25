# ML Model Strategy (Strategy) — P5

App Streamlit que estima o preço de um imóvel usando um "modelo" de
previsão escolhido pelo usuário — sem nenhuma dependência real de ML;
cada modelo é uma função Python determinística que substitui o que
seria um modelo treinado offline e carregado em produção.

## Objetivo pedagógico

Demonstrar o pattern **Strategy**: `ModelPredictor` (Context) não sabe
nada sobre como cada modelo calcula sua previsão — delega para a
`MLModelStrategy` configurada, intercambiável em tempo de execução via
`set_strategy()`. Trocar de `linear_regression` para `random_forest` no
selectbox da UI é só re-injetar uma estratégia diferente, sem tocar no
Context.

Elementos do pattern:
- **Context:** `ModelPredictor` (`application/context.py`)
- **Strategy (abstrato):** `MLModelStrategy` (`domain/interfaces.py`)
- **Concrete Strategies:** `LinearRegressionStrategy`, `DecisionTreeStrategy`, `RandomForestStrategy` (`infrastructure/strategies/`)

## Diagrama (ASCII)

```
Streamlit "Prever preço" (modelo = "random_forest")
        │
        ▼
get_strategy("random_forest") ──► RandomForestStrategy
        │
        ▼
ModelPredictor.predict() ──► strategy.predict(features) ──► PredictionResult
```

## Como rodar

```bash
docker-compose up --build
```

App disponível em `http://localhost:8501`.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`app.py` é excluído do cálculo de cobertura (mesmo padrão dos demais
projetos Streamlit do dataset); todos os modelos são testados de forma
parametrizada para garantir que honram o mesmo contrato
(`predict`/`get_name`/`get_feature_count`).

## SOLID

- **SRP:** cada modelo concreto só sabe calcular sua própria previsão; `ModelPredictor` só orquestra a chamada à estratégia configurada.
- **OCP:** um novo modelo é uma nova classe `MLModelStrategy` mais uma entrada em `_STRATEGY_MAP` — sem tocar nos modelos existentes.
- **LSP:** qualquer `MLModelStrategy` concreta pode substituir outra em `ModelPredictor` sem quebrar o contrato — todas retornam `PredictionResult` para o mesmo formato de `features`.
- **ISP:** `MLModelStrategy` expõe só os três métodos que o Context realmente precisa.
- **DIP:** `ModelPredictor` e `PredictUseCase` dependem de `MLModelStrategy` (abstração), nunca das classes concretas diretamente.
