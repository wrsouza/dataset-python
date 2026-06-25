"""Domain exceptions for the Data Processing Pipeline."""

from __future__ import annotations


class EmptyInputAbortedError(Exception):
    """Raised when a pipeline gets no input records and chooses to abort
    instead of persisting zero records (via `on_empty_input()`)."""

    def __init__(self, pipeline_name: str) -> None:
        super().__init__(f"Pipeline '{pipeline_name}' aborted: no input records")
        self.pipeline_name = pipeline_name
