"""Streamlit application: ML Model Strategy.

Composition root: lets the user pick a model and input features, then
runs the chosen strategy through the use case. Every model is a pure
Python function standing in for a real trained model — the focus is
swapping algorithms via Strategy, not the predictions themselves.
"""

from __future__ import annotations

import streamlit as st

from ml_model_strategy.application.use_cases import PredictInput, PredictUseCase
from ml_model_strategy.infrastructure.strategies.registry import list_strategy_names


def main() -> None:
    st.set_page_config(page_title="ML Model Strategy", layout="centered")
    st.title("ML Model Strategy — Strategy Pattern")
    st.caption(
        "Cada modelo é uma estratégia intercambiável; o Context "
        "(ModelPredictor) nunca sabe como cada um calcula a previsão."
    )

    model_name = st.selectbox("Modelo", options=list_strategy_names())
    size = st.slider("Tamanho (m²)", min_value=20.0, max_value=300.0, value=90.0)
    age = st.slider("Idade do imóvel (anos)", min_value=0.0, max_value=80.0, value=10.0)
    location_score = st.slider(
        "Nota da localização (0-10)", min_value=0.0, max_value=10.0, value=6.0
    )

    if st.button("Prever preço"):
        result = PredictUseCase().execute(
            PredictInput(model_name=model_name, features=[size, age, location_score])
        )
        st.metric("Preço estimado", f"${result.prediction:,.2f}")
        st.caption(f"Confiança: {result.confidence:.0%}")


if __name__ == "__main__":
    main()
