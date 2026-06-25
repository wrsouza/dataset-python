"""Streamlit application: Multi-step Form Wizard.

Composition root: builds (or reuses) the WizardSession in
`st.session_state` so it survives Streamlit reruns. Each step renders
its own form; "Next"/"Back"/"Submit" delegate to the FSM through the
application use cases.
"""

from __future__ import annotations

import streamlit as st

from form_wizard_fsm.application.use_cases import (
    AdvanceWizardUseCase,
    GoBackUseCase,
    SubmitWizardUseCase,
)
from form_wizard_fsm.domain.entities import WizardSession


def get_session() -> WizardSession:
    if "wizard" not in st.session_state:
        st.session_state["wizard"] = WizardSession(session_id="streamlit-session")
    session: WizardSession = st.session_state["wizard"]
    return session


def render_personal_info_step(session: WizardSession) -> None:
    st.subheader("1. Dados pessoais")
    name = st.text_input("Nome", value=session.data.get("name", ""))
    email = st.text_input("E-mail", value=session.data.get("email", ""))
    if st.button("Avançar"):
        AdvanceWizardUseCase().execute(session, {"name": name, "email": email})


def render_address_step(session: WizardSession) -> None:
    st.subheader("2. Endereço")
    street = st.text_input("Rua", value=session.data.get("street", ""))
    city = st.text_input("Cidade", value=session.data.get("city", ""))
    col1, col2 = st.columns(2)
    if col1.button("Voltar"):
        GoBackUseCase().execute(session)
    if col2.button("Avançar"):
        AdvanceWizardUseCase().execute(session, {"street": street, "city": city})


def render_review_step(session: WizardSession) -> None:
    st.subheader("3. Revisão")
    st.json(session.data)
    col1, col2 = st.columns(2)
    if col1.button("Voltar"):
        GoBackUseCase().execute(session)
    if col2.button("Confirmar envio"):
        SubmitWizardUseCase().execute(session)


def render_submitted_step(session: WizardSession) -> None:
    st.success("Formulário enviado com sucesso!")
    st.json(session.data)


_STEP_RENDERERS = {
    "PersonalInfo": render_personal_info_step,
    "Address": render_address_step,
    "Review": render_review_step,
    "Submitted": render_submitted_step,
}


def main() -> None:
    st.set_page_config(page_title="Multi-step Form Wizard", layout="centered")
    st.title("Multi-step Form Wizard — State Pattern")
    st.caption(
        "Cada etapa do formulário é um objeto de estado independente; "
        "WizardSession nunca decide sozinho para onde ir."
    )

    session = get_session()
    renderer = _STEP_RENDERERS[session.get_current_step_name()]
    renderer(session)


if __name__ == "__main__":
    main()
