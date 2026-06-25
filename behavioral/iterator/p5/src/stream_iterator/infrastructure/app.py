"""Streamlit application: Stream Data Iterator (Iterator pattern over Kafka).

Composition root: builds a real KafkaMessageSource and hands it to
SummarizeAvailableMessagesUseCase (application layer) every time the user
clicks "Poll messages". Accumulated totals live in `st.session_state` so
the running summary persists across Streamlit reruns.
"""

from __future__ import annotations

import streamlit as st

from stream_iterator.application.use_cases import SummarizeAvailableMessagesUseCase
from stream_iterator.infrastructure.factory import build_source


def _init_session_state() -> None:
    if "total_messages" not in st.session_state:
        st.session_state["total_messages"] = 0
    if "total_amount" not in st.session_state:
        st.session_state["total_amount"] = 0.0


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Stream Data Iterator", layout="wide")
    st.title("Stream Data Iterator — Iterator Pattern over Kafka")
    st.caption(
        "Cada clique em 'Poll messages' drena as mensagens disponíveis no "
        "tópico Kafka através de um KafkaStreamIterator — o use case nunca "
        "vê o polling por baixo, apenas has_next()/next()."
    )

    _init_session_state()

    if st.button("Poll messages"):
        source = build_source()
        use_case = SummarizeAvailableMessagesUseCase(source)
        summary, messages = use_case.execute()

        st.session_state["total_messages"] += summary.message_count
        st.session_state["total_amount"] += summary.total_amount

        st.subheader(f"Drained {summary.message_count} message(s) this poll")
        if messages:
            st.table(
                [
                    {
                        "partition": m.partition,
                        "offset": m.offset,
                        "key": m.key,
                        "value": m.value,
                    }
                    for m in messages
                ]
            )
        else:
            st.info("No messages currently available on the topic.")

    st.divider()
    st.subheader("Running totals (accumulated across polls)")
    col1, col2 = st.columns(2)
    col1.metric("Total messages drained", st.session_state["total_messages"])
    col2.metric("Total amount", f"{st.session_state['total_amount']:.2f}")


if __name__ == "__main__":
    main()
