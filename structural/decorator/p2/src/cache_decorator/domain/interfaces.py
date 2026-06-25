"""Domain interfaces for the Cache Decorator API.

Defines the Component ABC and Decorator ABC for the data service layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

# `entities` has no dependency on `interfaces`, so importing it at module
# top-level (instead of at the bottom of the file) does not create a real
# import cycle. The previous bottom-of-file import with `noqa: E402` was a
# workaround left over from an earlier draft; moving it here keeps imports
# conventional (stdlib -> local) per docs/standards/clean_code.md.
from cache_decorator.domain.entities import DataQuery, DataResult

__all__ = ["DataService", "DataServiceDecorator"]


class DataService(ABC):
    """Component ABC — the interface that all services and decorators implement.

    Following the GoF Decorator pattern, both the concrete service and all
    decorators share this interface so they are fully interchangeable.
    """

    @abstractmethod
    def get_data(self, query: DataQuery) -> DataResult:
        """Fetch data for the given query."""
        ...


class DataServiceDecorator(DataService):
    """Decorator ABC — wraps a DataService and optionally adds behaviour.

    Subclasses inject caching, logging, retry, etc. without touching
    the concrete service (OCP). Each decorator has one responsibility (SRP).
    """

    def __init__(self, wrapped: DataService) -> None:
        self._wrapped = wrapped

    def get_data(self, query: DataQuery) -> DataResult:
        """Default delegation to the wrapped service."""
        return self._wrapped.get_data(query)
