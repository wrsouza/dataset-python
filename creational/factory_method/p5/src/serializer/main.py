"""Streamlit app — Serializer Factory UI.

Composition root: the only place where concrete factories are selected.
All use cases receive SerializerFactory abstractions (DIP).

Features:
  - Upload a file or paste JSON data
  - Select output format (JSON, XML, CSV, Parquet)
  - Serialize and preview result
  - Download serialized file
  - Deserialize: upload a file and visualize records as a table
"""

from __future__ import annotations

import json
import traceback
from typing import Any

import streamlit as st

from serializer.application.use_cases import (
    DeserializeDataUseCase,
    ListFormatsUseCase,
    SerializeDataUseCase,
)
from serializer.domain.entities import (
    DeserializationError,
    SerializationError,
    UnsupportedFormatError,
)
from serializer.infrastructure.serializers import SERIALIZER_FACTORY_REGISTRY

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Serializer Factory",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Sidebar — pattern explanation ─────────────────────────────────────────────

with st.sidebar:
    st.title("🏭 Factory Method")
    st.markdown("""
**Pattern:** Factory Method
**Domain:** Serializer

Each format (JSON, XML, CSV, YAML) is a **ConcreteCreator** that overrides
`create_serializer()`. The `SerializerFactory` ABC never knows which
concrete `DataSerializer` will be returned.

**SOLID:**
- **OCP** — Add YAML? Create `YAMLSerializerFactory`. Zero existing code changes.
- **DIP** — Use cases depend on `SerializerFactory` Protocol, never on concrete classes.
""")

    st.divider()
    list_use_case = ListFormatsUseCase(SERIALIZER_FACTORY_REGISTRY)
    formats_info = list_use_case.execute()
    st.subheader("Available Formats")
    for fmt in formats_info:
        st.markdown(f"**{fmt['name']}** — `.{fmt['extension']}` — `{fmt['mime_type']}`")


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_serialize, tab_deserialize = st.tabs(["📤 Serialize", "📥 Deserialize"])


# ── Serialize Tab ─────────────────────────────────────────────────────────────

with tab_serialize:
    st.header("Serialize Data")
    st.markdown(
        "Provide data as a JSON array, then choose the output format "
        "and click **Serialize**."
    )

    col_input, col_output = st.columns(2)

    with col_input:
        st.subheader("Input")

        input_method = st.radio(
            "Input method",
            options=["Paste JSON", "Upload JSON file"],
            horizontal=True,
        )

        raw_input: str | None = None

        if input_method == "Paste JSON":
            default_json = json.dumps(
                [
                    {"id": 1, "name": "Alice", "role": "engineer", "salary": 95000},
                    {"id": 2, "name": "Bob", "role": "designer", "salary": 87000},
                    {"id": 3, "name": "Carol", "role": "manager", "salary": 105000},
                ],
                indent=2,
            )
            raw_input = st.text_area(
                "JSON data (array of objects)",
                value=default_json,
                height=250,
            )
        else:
            uploaded = st.file_uploader("Upload JSON file", type=["json"])
            if uploaded is not None:
                raw_input = uploaded.read().decode("utf-8")
                st.text_area(
                    "Uploaded content", value=raw_input, height=200, disabled=True
                )

        format_options = {fmt["name"]: fmt["slug"] for fmt in formats_info}
        selected_format_name = st.selectbox(
            "Output format",
            options=list(format_options.keys()),
        )
        selected_slug = format_options.get(selected_format_name or "JSON", "json")

        serialize_btn = st.button("🔄 Serialize", type="primary")

    with col_output:
        st.subheader("Output")

        if serialize_btn and raw_input:
            try:
                data: list[dict[str, Any]] = json.loads(raw_input)
                if not isinstance(data, list):
                    st.error("Input must be a JSON array (list of objects).")
                else:
                    factory = SERIALIZER_FACTORY_REGISTRY.get(selected_slug)
                    if factory is None:
                        raise UnsupportedFormatError(selected_slug)

                    serialize_use_case = SerializeDataUseCase(factory)
                    result = serialize_use_case.execute(data)

                    st.success(
                        f"Serialized {result.record_count} record(s) → "
                        f"{result.size_kb} KB as `.{result.extension}`"
                    )

                    # Preview
                    preview_text = result.raw.decode("utf-8", errors="replace")
                    preview_language = (
                        result.extension if result.extension != "csv" else "text"
                    )
                    st.code(
                        preview_text[:2000]
                        + (" …[truncated]" if len(preview_text) > 2000 else ""),
                        language=preview_language,
                    )

                    # Download button
                    st.download_button(
                        label=f"⬇️ Download .{result.extension}",
                        data=result.raw,
                        file_name=f"data.{result.extension}",
                        mime=result.mime_type,
                    )

            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON input: {exc}")
            except SerializationError as exc:
                st.error(f"Serialization error: {exc}")
            except UnsupportedFormatError as exc:
                st.error(str(exc))
            except Exception:
                st.error("Unexpected error:")
                st.code(traceback.format_exc())
        elif serialize_btn:
            st.warning("Please provide input data before serializing.")
        else:
            st.info("Configure the input and click **Serialize** to see the result.")


# ── Deserialize Tab ───────────────────────────────────────────────────────────

with tab_deserialize:
    st.header("Deserialize Data")
    st.markdown(
        "Upload a serialized file. The format is auto-detected from the extension."
    )

    uploaded_file = st.file_uploader(
        "Upload file to deserialize",
        type=["json", "xml", "csv", "yaml", "yml"],
        key="deserialize_upload",
    )

    if uploaded_file is not None:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        ext = "yaml" if ext == "yml" else ext
        factory = SERIALIZER_FACTORY_REGISTRY.get(ext)

        if factory is None:
            st.error(
                f"Format '.{ext}' is not supported. "
                f"Supported: {', '.join(SERIALIZER_FACTORY_REGISTRY.keys())}"
            )
        else:
            st.info(f"Detected format: **{factory.get_format_name()}** (.{ext})")
            deserialize_btn = st.button("📥 Deserialize", type="primary")

            if deserialize_btn:
                try:
                    raw_bytes = uploaded_file.read()
                    deserialize_use_case = DeserializeDataUseCase(factory)
                    deser_result = deserialize_use_case.execute(raw_bytes)

                    st.success(f"Deserialized {deser_result.record_count} record(s).")
                    st.dataframe(deser_result.records, use_container_width=True)

                    # Also offer re-download as JSON for easy inspection
                    as_json = json.dumps(
                        deser_result.records, indent=2, ensure_ascii=False
                    )
                    st.download_button(
                        label="⬇️ Download as JSON",
                        data=as_json.encode("utf-8"),
                        file_name="deserialized.json",
                        mime="application/json",
                    )
                except DeserializationError as exc:
                    st.error(f"Deserialization error: {exc}")
                except Exception:
                    st.error("Unexpected error:")
                    st.code(traceback.format_exc())
    else:
        st.info("Upload a .json, .xml, .csv, or .yaml file to deserialize it.")
