"""Streamlit application: Data Transformation Visitor.

Composition root: lets the user describe a small dataset (one numeric,
one text, one date column) and pick a transformation, then runs it
through the use case. Every transformation is a pure Python
implementation of ColumnVisitor — no external data service.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from data_transformation_visitor.application.use_cases import (
    TransformDatasetInput,
    TransformDatasetUseCase,
)
from data_transformation_visitor.infrastructure.visitors.registry import (
    list_transformation_names,
)


def main() -> None:
    st.set_page_config(page_title="Data Transformation Visitor", layout="centered")
    st.title("Data Transformation Visitor — Visitor Pattern")
    st.caption(
        "Cada coluna (numérica, texto, data) nunca sabe qual transformação "
        "está sendo aplicada; o visitor escolhido decide isso via accept()."
    )

    transformation = st.selectbox("Transformação", options=list_transformation_names())

    numeric_input = st.text_input(
        "Coluna numérica (separada por vírgula)", "10, 20, 30"
    )
    text_input = st.text_input("Coluna de texto (separada por vírgula)", "Ana, Bob")
    date_input = st.text_input(
        "Coluna de data ISO (separada por vírgula)", "2026-01-15, 2026-03-20"
    )

    if st.button("Transformar"):
        columns: list[dict[str, Any]] = [
            {
                "type": "numeric",
                "name": "value",
                "values": [
                    float(v.strip()) for v in numeric_input.split(",") if v.strip()
                ],
            },
            {
                "type": "text",
                "name": "name",
                "values": [v.strip() for v in text_input.split(",") if v.strip()],
            },
            {
                "type": "date",
                "name": "date",
                "values": [v.strip() for v in date_input.split(",") if v.strip()],
            },
        ]

        result = TransformDatasetUseCase().execute(
            TransformDatasetInput(transformation_name=transformation, columns=columns)
        )

        st.subheader("Resultado")
        st.json(result.columns)


if __name__ == "__main__":
    main()
