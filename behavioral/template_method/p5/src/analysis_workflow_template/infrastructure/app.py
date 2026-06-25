"""Streamlit application: Analysis Workflow Template.

Composition root: lets the user paste a dataset and pick a workflow,
then runs it through the registry. Every workflow is a pure Python
implementation of AnalysisWorkflow — no external analytics service.
"""

from __future__ import annotations

import streamlit as st

from analysis_workflow_template.application.workflows.registry import (
    get_workflow,
    list_workflow_names,
)


def main() -> None:
    st.set_page_config(page_title="Analysis Workflow Template", layout="centered")
    st.title("Analysis Workflow Template — Template Method Pattern")
    st.caption(
        "Cada workflow compartilha o mesmo esqueleto (preprocess → "
        "estatísticas → outliers → interpretação); só os passos "
        "abstratos mudam de um workflow para outro."
    )

    workflow_name = st.selectbox("Workflow", options=list_workflow_names())
    raw_input = st.text_area(
        "Dataset (números separados por vírgula)", value="1, 2, 3, 4, 100"
    )

    if st.button("Rodar análise"):
        try:
            values = [float(v.strip()) for v in raw_input.split(",") if v.strip()]
        except ValueError:
            st.error("Dataset inválido — use números separados por vírgula.")
            return

        report = get_workflow(workflow_name).run(values)

        st.subheader("Estatísticas")
        st.json(report.statistics)
        st.subheader("Interpretação")
        st.write(report.interpretation)
        if report.outliers:
            st.subheader("Outliers")
            st.write(report.outliers)


if __name__ == "__main__":
    main()
