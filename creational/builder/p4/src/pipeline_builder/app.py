"""Streamlit UI — Interactive Pipeline Builder.

The user constructs a data pipeline step by step through the sidebar.
Each step is appended to the session-state step list.
Clicking 'Run Pipeline' builds the Pipeline product and executes it,
showing a per-step result preview in the main area.
"""
from __future__ import annotations

import json
from typing import Any

import streamlit as st

from pipeline_builder.application.use_cases import BuildPipelineUseCase, ETLDirector
from pipeline_builder.domain.entities import ExecutionResult, SourceFormat
from pipeline_builder.infrastructure.builders import (
    APIPipelineBuilder,
    CSVPipelineBuilder,
    JSONPipelineBuilder,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Pipeline Builder",
    page_icon="🔧",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session-state bootstrap
# ---------------------------------------------------------------------------

if "steps" not in st.session_state:
    st.session_state["steps"]: list[dict[str, Any]] = []

if "results" not in st.session_state:
    st.session_state["results"]: list[ExecutionResult] = []

if "pipeline_ran" not in st.session_state:
    st.session_state["pipeline_ran"] = False


# ---------------------------------------------------------------------------
# Sidebar — step builder
# ---------------------------------------------------------------------------

def _builder_for_format(fmt: str) -> CSVPipelineBuilder | JSONPipelineBuilder | APIPipelineBuilder:
    builders = {
        SourceFormat.CSV.value: CSVPipelineBuilder,
        SourceFormat.JSON.value: JSONPipelineBuilder,
        SourceFormat.API.value: APIPipelineBuilder,
    }
    return builders[fmt]()


def _render_sidebar() -> None:
    st.sidebar.title("Pipeline Steps")
    st.sidebar.markdown("---")

    step_type = st.sidebar.radio(
        "Step type",
        ["source", "transform", "filter", "sink"],
        horizontal=True,
    )

    config: dict[str, Any] = {}

    if step_type == "source":
        config = _render_source_form()
    elif step_type == "transform":
        config = _render_transform_form()
    elif step_type == "filter":
        config = _render_filter_form()
    elif step_type == "sink":
        config = _render_sink_form()

    st.sidebar.markdown("---")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("Add Step", use_container_width=True):
            st.session_state["steps"].append({"type": step_type, "config": config})
            st.session_state["pipeline_ran"] = False
            st.rerun()

    with col2:
        if st.button("Clear All", use_container_width=True):
            st.session_state["steps"] = []
            st.session_state["results"] = []
            st.session_state["pipeline_ran"] = False
            st.rerun()

    # Director presets
    st.sidebar.markdown("---")
    st.sidebar.subheader("Director Presets")

    format_choice = st.sidebar.selectbox("Source format", ["csv", "json", "api"])

    preset = st.sidebar.selectbox(
        "Preset pipeline",
        ["standard_etl", "validation", "aggregation"],
    )

    if st.sidebar.button("Load Preset", use_container_width=True):
        _load_director_preset(preset, format_choice)
        st.rerun()


def _render_source_form() -> dict[str, Any]:
    fmt = st.sidebar.selectbox("Format", ["csv", "json", "api"])
    config: dict[str, Any] = {"format": fmt}

    if fmt == "csv":
        default_csv = "id,name,category,amount\n1,Alice,A,100\n2,Bob,B,200\n3,Alice,A,150\n4,Carol,C,300\n2,Bob,B,200"
        content = st.sidebar.text_area("CSV content", value=default_csv, height=120)
        config["content"] = content

    elif fmt == "json":
        default_json = '[{"id":1,"name":"Alice","amount":100},{"id":2,"name":"Bob","amount":200},{"id":3,"name":"Carol","amount":300}]'
        content = st.sidebar.text_area("JSON content", value=default_json, height=80)
        config["content"] = content

    else:
        endpoint = st.sidebar.text_input("API endpoint", value="/api/data")
        config["endpoint"] = endpoint

    return config


def _render_transform_form() -> dict[str, Any]:
    t_type = st.sidebar.selectbox(
        "Transform type",
        ["deduplicate", "sort", "rename", "cast", "aggregate"],
    )
    config: dict[str, Any] = {"transform_type": t_type}

    if t_type == "sort":
        config["column"] = st.sidebar.text_input("Sort column", value="id")
        config["descending"] = st.sidebar.checkbox("Descending")

    elif t_type == "rename":
        old_name = st.sidebar.text_input("Old column name", value="name")
        new_name = st.sidebar.text_input("New column name", value="full_name")
        config["mapping"] = {old_name: new_name}

    elif t_type == "cast":
        config["column"] = st.sidebar.text_input("Column to cast", value="amount")
        config["target_type"] = st.sidebar.selectbox("Target type", ["int", "float", "str"])

    elif t_type == "aggregate":
        config["group_by"] = st.sidebar.text_input("Group by column", value="category")
        config["agg_column"] = st.sidebar.text_input("Aggregate column", value="amount")

    return config


def _render_filter_form() -> dict[str, Any]:
    st.sidebar.markdown("**Condition examples:** `amount > 100`, `name == Alice`, `category contains A`")
    condition = st.sidebar.text_input("Condition", value="amount > 100")
    return {"condition": condition}


def _render_sink_form() -> dict[str, Any]:
    destination = st.sidebar.selectbox("Destination", ["console", "report", "dashboard"])
    fmt = st.sidebar.selectbox("Output format", ["table", "json", "chart"])
    return {"destination": destination, "format": fmt}


def _load_director_preset(preset: str, fmt: str) -> None:
    """Build a preset via the ETLDirector and convert to session-state steps."""
    builder = _builder_for_format(fmt)
    director = ETLDirector(builder)

    source_config: dict[str, Any] = _default_source_config(fmt)

    if preset == "standard_etl":
        pipeline = director.build_standard_etl(source_config)
    elif preset == "validation":
        pipeline = director.build_validation_pipeline(source_config, "amount > 100")
    else:
        pipeline = director.build_aggregation_pipeline(source_config, "category", "amount")

    st.session_state["steps"] = [
        {"type": step.step_type.value, "config": step.config}
        for step in pipeline.steps
    ]
    st.session_state["results"] = []
    st.session_state["pipeline_ran"] = False


def _default_source_config(fmt: str) -> dict[str, Any]:
    defaults: dict[str, dict[str, Any]] = {
        "csv": {
            "content": "id,name,category,amount\n1,Alice,A,100\n2,Bob,B,200\n3,Alice,A,150\n4,Carol,C,300\n2,Bob,B,200"
        },
        "json": {
            "content": '[{"id":1,"name":"Alice","category":"A","amount":100},{"id":2,"name":"Bob","category":"B","amount":200}]'
        },
        "api": {"endpoint": "/api/products"},
    }
    return defaults.get(fmt, {})


# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

def _render_main() -> None:
    st.title("Pipeline Builder")
    st.markdown(
        "Build a **data processing pipeline** step by step. "
        "Add steps from the sidebar, then click **Run Pipeline**."
    )

    _render_step_list()

    st.markdown("---")

    if st.button("Run Pipeline", type="primary", use_container_width=True):
        _execute_pipeline()

    if st.session_state["pipeline_ran"]:
        _render_results()


def _render_step_list() -> None:
    steps: list[dict[str, Any]] = st.session_state["steps"]

    if not steps:
        st.info("No steps yet. Add a Source step from the sidebar to get started.")
        return

    st.subheader(f"Pipeline Steps ({len(steps)})")

    for i, step in enumerate(steps):
        with st.expander(f"Step {i + 1}: [{step['type'].upper()}]", expanded=True):
            cfg = step["config"]
            # Avoid printing large embedded sample_data in the UI
            display_cfg = {k: v for k, v in cfg.items() if k != "sample_data"}
            st.json(display_cfg)

            if st.button(f"Remove step {i + 1}", key=f"rm_{i}"):
                st.session_state["steps"].pop(i)
                st.session_state["pipeline_ran"] = False
                st.rerun()


def _execute_pipeline() -> None:
    steps: list[dict[str, Any]] = st.session_state["steps"]

    if not steps:
        st.error("Add at least one step before running.")
        return

    # Determine source format from first step
    first = steps[0]
    fmt = first.get("config", {}).get("format", "csv")
    builder = _builder_for_format(fmt)

    # Load the initial dataset from the source config
    source_data = _load_source_data(first.get("config", {}), fmt)

    try:
        use_case = BuildPipelineUseCase(builder)
        pipeline = use_case.execute(steps)
        results = pipeline.execute(source_data)
        st.session_state["results"] = results
        st.session_state["pipeline_ran"] = True
    except Exception as exc:
        st.error(f"Pipeline build failed: {exc}")


def _load_source_data(config: dict[str, Any], fmt: str) -> list[dict[str, Any]]:
    """Extract dataset from the source step config (already parsed at build time)."""
    if "sample_data" in config:
        return list(config["sample_data"])

    # Fallback: parse inline content
    if fmt == "csv" and "content" in config:
        import csv as _csv
        import io as _io
        reader = _csv.DictReader(_io.StringIO(config["content"]))
        return [dict(row) for row in reader]

    if fmt == "json" and "content" in config:
        parsed = json.loads(config["content"])
        return parsed if isinstance(parsed, list) else [parsed]

    if fmt == "api":
        endpoint = config.get("endpoint", "/api/data")
        return [
            {"id": i, "endpoint": endpoint, "value": i * 10, "category": f"cat_{i % 3}"}
            for i in range(1, 21)
        ]

    return []


def _render_results() -> None:
    results: list[ExecutionResult] = st.session_state["results"]

    st.subheader("Execution Results")

    all_ok = all(r.success for r in results)
    if all_ok:
        st.success(f"Pipeline completed successfully — {len(results)} step(s) executed.")
    else:
        st.warning("Pipeline stopped due to a step failure.")

    for result in results:
        icon = "OK" if result.success else "FAIL"
        with st.expander(f"[{icon}] {result.summary}", expanded=result.success):
            col_a, col_b = st.columns(2)
            col_a.metric("Rows in", result.rows_in)
            col_b.metric("Rows out", result.rows_out)

            if result.error:
                st.error(result.error)
            elif result.preview:
                st.markdown("**Preview (up to 10 rows):**")
                st.dataframe(result.preview, use_container_width=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    _render_sidebar()
    _render_main()


if __name__ == "__main__":
    main()
