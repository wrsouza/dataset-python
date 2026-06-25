"""Streamlit application: Data Validation Pipeline (Chain of Responsibility).

Composition root: builds the validator chain from the default schema and
hands it to ValidateRecordUseCase (application layer). The UI never
implements validation logic itself — it only renders the record's
history of ValidationSteps produced by the chain.
"""

from __future__ import annotations

import uuid

import streamlit as st

from data_validation.application.use_cases import ValidateRecordUseCase
from data_validation.domain.entities import DataRecord, ValidationStatus
from data_validation.infrastructure.handlers import build_validation_chain
from data_validation.infrastructure.schema import DEFAULT_SCHEMA


def render_input_form() -> dict[str, object] | None:
    """Render the form for entering a record and return its raw field values."""
    st.subheader("Enviar registro para validação")
    with st.form("validate_form"):
        customer_id = st.text_input("customer_id", value="cust-001")
        age = st.number_input("age", min_value=-10, max_value=200, value=30, step=1)
        order_total = st.number_input("order_total", value=99.90)
        submitted = st.form_submit_button("Validar")

    if not submitted:
        return None
    return {
        "customer_id": customer_id,
        "age": int(age),
        "order_total": float(order_total),
    }


def render_result(record: DataRecord) -> None:
    """Render the validation outcome and the full chain trace."""
    st.subheader("Resultado")
    if record.status == ValidationStatus.VALID:
        st.success(f"Registro {record.record_id} é VÁLIDO.")
    else:
        st.error(f"Registro {record.record_id} é INVÁLIDO.")

    st.caption("Histórico da cadeia de validação:")
    st.table(
        [
            {
                "handler": step.handler_name,
                "status": step.status.value,
                "reason": step.reason,
            }
            for step in record.history
        ]
    )


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Data Validation Pipeline", layout="wide")
    st.title("Data Validation Pipeline — Chain of Responsibility")
    st.caption(
        "Cada registro passa por uma cadeia de validadores independentes "
        "(campos obrigatórios → tipo → faixa de valor → aprovação) até "
        "receber um veredito final."
    )

    fields = render_input_form()
    if fields is None:
        return

    chain = build_validation_chain(DEFAULT_SCHEMA)
    use_case = ValidateRecordUseCase(chain)

    record = DataRecord(record_id=str(uuid.uuid4())[:8], fields=fields)
    result = use_case.execute(record)

    render_result(result)


if __name__ == "__main__":
    main()
