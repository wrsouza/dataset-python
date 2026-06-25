"""Domain interfaces for the Document Prototype pattern."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Document(ABC):
    """Prototype interface for clonable document templates.

    OCP: new document types extend this ABC without modifying it.
    SRP: only defines the cloning contract — persistence is elsewhere.
    """

    @abstractmethod
    def clone(self, substitutions: dict[str, str]) -> Document:
        """Clone this document, replacing placeholder values.

        Args:
            substitutions: mapping of placeholder keys to replacement values.
                           e.g. {"{{client_name}}": "Acme Corp"}

        Returns:
            A new independent Document with substitutions applied.
        """
        ...

    @property
    @abstractmethod
    def doc_type(self) -> str:
        """Document type identifier (contract, report, form)."""
        ...

    @property
    @abstractmethod
    def title(self) -> str:
        """Document title."""
        ...

    @property
    @abstractmethod
    def content(self) -> str:
        """Document body content (may contain {{placeholders}})."""
        ...

    @property
    @abstractmethod
    def metadata(self) -> dict[str, str]:
        """Document metadata fields."""
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, object]:
        """Serialize document to a dictionary (for MongoDB storage)."""
        ...
