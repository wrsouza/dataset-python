"""Streamlit application: ML Model Registry (Singleton pattern).

Composition root: builds the MockModelLoader (concrete infrastructure) and
injects it into the ModelRegistry singleton, which is then handed to use
cases (application layer). The UI never imports the loader directly when
running inference — it goes through `GetActiveModelUseCase`.

Visual proof of Singleton: `id(registry)` and `registry.instance_id()` are
displayed on every rerun. Because Streamlit reruns this whole script on
every interaction, a NEW `ModelRegistry(loader=...)` call happens each
time — yet `SingletonMeta` always returns the exact same object, so the id
never changes and the loaded-model cache is preserved across reruns.
"""

from __future__ import annotations

import streamlit as st

from model_registry.application.use_cases import (
    GetActiveModelUseCase,
    ListModelVersionsUseCase,
    PromoteModelVersionUseCase,
    RegisterModelVersionUseCase,
)
from model_registry.domain.entities import (
    DuplicateVersionError,
    ModelNotFoundError,
    ModelVersion,
)
from model_registry.infrastructure.loaders import MockModelLoader
from model_registry.infrastructure.registry import ModelRegistry

DEFAULT_FRAMEWORKS = ["scikit-learn", "pytorch", "tensorflow", "xgboost"]


def get_loader() -> MockModelLoader:
    """Build (or reuse) the mock loader for this Streamlit session."""
    if "loader" not in st.session_state:
        st.session_state["loader"] = MockModelLoader()
    loader: MockModelLoader = st.session_state["loader"]
    return loader


def render_registration_form(use_case: RegisterModelVersionUseCase) -> None:
    """Render the form for registering a new model version."""
    st.subheader("Registrar novo modelo")
    with st.form("register_form", clear_on_submit=True):
        model_name = st.text_input("Nome do modelo", value="fraud-detector")
        version = st.text_input("Versão", value="v1.0.0")
        framework = st.selectbox("Framework", options=DEFAULT_FRAMEWORKS)
        accuracy = st.slider("Accuracy", 0.0, 1.0, 0.9)
        f1_score = st.slider("F1 score", 0.0, 1.0, 0.88)
        latency_ms = st.number_input("Latência (ms)", min_value=0.0, value=42.0)
        tags_raw = st.text_input("Tags (separadas por vírgula)", value="")
        submitted = st.form_submit_button("Registrar")

        if submitted:
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            try:
                use_case.execute(
                    model_name=model_name,
                    version=version,
                    framework=framework,
                    accuracy=accuracy,
                    f1_score=f1_score,
                    latency_ms=latency_ms,
                    tags=tags,
                )
                st.success(f"Modelo '{model_name}:{version}' registrado.")
            except DuplicateVersionError as exc:
                st.error(str(exc))


def render_promotion_panel(
    versions: list[ModelVersion], promote_use_case: PromoteModelVersionUseCase
) -> None:
    """Render the panel that allows promoting a version to PRODUCTION."""
    st.subheader("Promover para produção")
    if not versions:
        st.info("Nenhum modelo registrado ainda.")
        return

    options = [f"{v.model_name}:{v.version}" for v in versions]
    selected = st.selectbox("Versão", options=options, key="promote_select")
    if st.button("Promover"):
        model_name, version = selected.split(":", maxsplit=1)
        promote_use_case.execute(model_name, version)
        st.success(f"'{selected}' promovido para PRODUCTION.")


def render_inference_panel(get_active_use_case: GetActiveModelUseCase) -> None:
    """Render the panel that runs a mock prediction using the active model."""
    st.subheader("Executar inferência (modelo ativo)")
    model_name = st.text_input("Nome do modelo para inferência", value="fraud-detector")
    feature_value = st.number_input("Valor da feature 'amount'", value=120.0)

    if st.button("Prever"):
        try:
            model = get_active_use_case.execute(model_name)
            score = model.predict({"amount": feature_value})
            st.metric("Score previsto", f"{score:.2f}")
        except ModelNotFoundError as exc:
            st.error(str(exc))


def render_registry_state(
    registry: ModelRegistry, versions: list[ModelVersion]
) -> None:
    """Render the proof-of-singleton panel: id, loaded count, all versions."""
    st.subheader("Estado único do Registry (prova do Singleton)")
    col1, col2, col3 = st.columns(3)
    col1.metric("id(registry)", str(registry.instance_id()))
    col2.metric("Versões registradas", len(versions))
    col3.metric("Modelos carregados em cache", registry.loaded_model_count())

    st.caption(
        "Recarregue a página ou interaja com qualquer widget: o Streamlit "
        "reexecuta este script inteiro, mas o id(registry) acima permanece "
        "idêntico porque SingletonMeta sempre devolve a mesma instância."
    )

    if versions:
        st.table([v.to_dict() for v in versions])


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="ML Model Registry", layout="wide")
    st.title("ML Model Registry — Singleton Pattern")
    st.caption(
        "Um único ModelRegistry compartilhado evita recarregar modelos "
        "pesados repetidamente e mantém metadados consistentes entre todas "
        "as seções da aplicação."
    )

    loader = get_loader()
    registry = ModelRegistry(loader=loader)

    register_use_case = RegisterModelVersionUseCase(registry)
    promote_use_case = PromoteModelVersionUseCase(registry)
    list_use_case = ListModelVersionsUseCase(registry)
    get_active_use_case = GetActiveModelUseCase(registry)

    versions = list_use_case.execute()

    render_registry_state(registry, versions)
    st.divider()

    left, right = st.columns(2)
    with left:
        render_registration_form(register_use_case)
    with right:
        render_promotion_panel(versions, promote_use_case)

    st.divider()
    render_inference_panel(get_active_use_case)


if __name__ == "__main__":
    main()
