"""Domain exceptions for the Content Export Visitor system."""

from __future__ import annotations


class InvalidFormatError(Exception):
    """Raised when an export format name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown export format '{name}'")
        self.name = name


class InvalidNodeTypeError(Exception):
    """Raised when a content node's `type` field is not recognised."""

    def __init__(self, node_type: str) -> None:
        super().__init__(f"Unknown content node type '{node_type}'")
        self.node_type = node_type


class ExportJobNotFoundError(Exception):
    """Raised when a previously run export job cannot be found."""

    def __init__(self, job_id: str) -> None:
        super().__init__(f"Export job '{job_id}' not found")
        self.job_id = job_id
