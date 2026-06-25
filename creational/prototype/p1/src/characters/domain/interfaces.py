"""Domain interfaces for the Character Prototype pattern.

Defines the Prototype ABC and PrototypeRegistry interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Character(ABC):
    """Prototype interface for game characters.

    All character templates must implement clone() to support
    creating copies without depending on concrete classes.
    """

    @abstractmethod
    def clone(self) -> Character:
        """Create a deep copy of this character.

        Returns a new Character instance with all attributes copied.
        Post-clone customization is done via overrides on the returned object.
        """
        ...

    @abstractmethod
    def apply_overrides(self, overrides: dict[str, Any]) -> None:
        """Apply override values to this character's attributes."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Character name."""
        ...

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Name of the template this character is based on."""
        ...

    @property
    @abstractmethod
    def stats(self) -> dict[str, int]:
        """Character stats dictionary (strength, dexterity, etc.)."""
        ...

    @property
    @abstractmethod
    def skills(self) -> list[str]:
        """List of skills the character possesses."""
        ...

    @property
    @abstractmethod
    def equipment(self) -> list[str]:
        """List of equipment items the character carries."""
        ...

    @property
    @abstractmethod
    def level(self) -> int:
        """Character level."""
        ...


class CharacterRegistry(ABC):
    """Registry interface for managing character prototypes.

    Follows OCP: new templates are registered without modifying this interface.
    """

    @abstractmethod
    def register(self, name: str, template: Character) -> None:
        """Register a character template under the given name."""
        ...

    @abstractmethod
    def get(self, name: str) -> Character:
        """Retrieve a registered template by name."""
        ...

    @abstractmethod
    def clone(self, name: str, overrides: dict[str, Any]) -> Character:
        """Clone a registered template and apply overrides."""
        ...

    @abstractmethod
    def list_templates(self) -> list[str]:
        """Return all registered template names."""
        ...
