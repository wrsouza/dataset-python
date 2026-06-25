"""Abstract interfaces for the UI Component Factory pattern.

This module defines the AbstractFactory and AbstractProduct roles.
All concrete factories and products must implement these contracts.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class Button(Protocol):
    """AbstractProduct: Button component interface."""

    def render(self) -> dict[str, str]:
        """Render the button and return its properties as a dictionary."""
        ...

    def get_style(self) -> str:
        """Return the CSS/style descriptor for this platform's button."""
        ...


class Input(Protocol):
    """AbstractProduct: Input field component interface."""

    def render(self) -> dict[str, str]:
        """Render the input and return its properties as a dictionary."""
        ...

    def get_validation_mode(self) -> str:
        """Return the validation mode used by this platform's input."""
        ...


class Modal(Protocol):
    """AbstractProduct: Modal dialog component interface."""

    def render(self) -> dict[str, str]:
        """Render the modal and return its properties as a dictionary."""
        ...

    def get_animation(self) -> str:
        """Return the animation type used by this platform's modal."""
        ...


class UIComponentFactory(ABC):
    """AbstractFactory: defines the interface for creating UI component families.

    Each ConcreteFactory produces components that are visually and
    behaviorally consistent with a specific platform (Windows, Linux, Mac).
    OCP: add a new platform by creating a new subclass — no existing code changes.
    DIP: Flask routes depend on this abstraction, not on concrete factories.
    """

    @abstractmethod
    def create_button(self) -> Button:
        """Create a platform-specific Button component."""
        ...

    @abstractmethod
    def create_input(self) -> Input:
        """Create a platform-specific Input component."""
        ...

    @abstractmethod
    def create_modal(self) -> Modal:
        """Create a platform-specific Modal component."""
        ...

    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the human-readable platform name."""
        ...
