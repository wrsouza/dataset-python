"""Streamlit application: DataFrame Format Adapter (Adapter pattern).

Composition root: builds the AdapterFactory (infrastructure) and injects it
into NormalizeToCsvUseCase (application layer), which depends only on the
TabularDataSource abstraction (DIP). Excluded from coverage — see
pyproject.toml `[tool.coverage.run] omit`.
"""  # pragma: no cover

from __future__ import annotations

import streamlit as st

from dataframe_adapter.application.use_cases import (
    AdapterFactory,
    NormalizeToCsvUseCase,
)
from dataframe_adapter.domain.entities import (
    InvalidDataError,
    ParsedDataset,
    UnsupportedFormatError,
)

SUPPORTED_EXTENSIONS = ("csv", "json", "parquet")


@st.cache_resource
def get_use_case() -> NormalizeToCsvUseCase:
    """Build the use case once per Streamlit session."""
    return NormalizeToCsvUseCase(AdapterFactory())


def render_preview(dataset: ParsedDataset) -> None:
    """Render the parsed dataset as a table plus metadata."""
    st.subheader(f"Preview — formato detectado: {dataset.source_format}")
    st.write(f"{dataset.row_count} linha(s), {len(dataset.columns)} coluna(s)")
    st.dataframe([dict(zip(dataset.columns, row, strict=True)) for row in dataset.rows])


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="DataFrame Format Adapter", layout="wide")
    st.title("DataFrame Format Adapter — Adapter Pattern")
    st.caption(
        "Envie um arquivo CSV, JSON ou Parquet. A aplicação usa o pattern "
        "Adapter para tratar qualquer um dos três formatos por meio da "
        "mesma interface TabularDataSource, e oferece exportação para um "
        "CSV normalizado, independente do formato de origem."
    )

    use_case = get_use_case()
    uploaded_file = st.file_uploader(
        "Selecione um arquivo", type=list(SUPPORTED_EXTENSIONS)
    )

    if uploaded_file is None:
        st.info("Aguardando upload de um arquivo .csv, .json ou .parquet.")
        return

    raw_bytes = uploaded_file.getvalue()
    try:
        dataset = use_case.parse(raw_bytes, uploaded_file.name)
    except UnsupportedFormatError as exc:
        st.error(str(exc))
        return
    except InvalidDataError as exc:
        st.error(str(exc))
        return

    render_preview(dataset)

    st.divider()
    st.subheader("Exportar CSV normalizado")
    csv_text = dataset.to_csv_text()
    st.download_button(
        label="Baixar CSV normalizado",
        data=csv_text,
        file_name="normalized.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
