"""Domain interfaces for the UI Component Decorator app.

Defines the Component ABC and the Decorator ABC following the GoF
Decorator pattern. Both concrete widgets and decorators implement the
same `UIComponent` contract, so they can be nested/stacked freely.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class UIComponent(ABC):
    """Component — the contract shared by every renderable widget.

    Every concrete widget and every decorator must implement `render`
    and `describe`. This is the core role in the GoF Decorator pattern:
    decorators and concrete components are interchangeable for the caller.
    """

    @abstractmethod
    def render(self) -> str:
        """Return the HTML/markdown fragment used by Streamlit to display."""
        ...

    @abstractmethod
    def describe(self) -> str:
        """Return a short human-readable label naming the decoration chain."""
        ...


class UIComponentDecorator(UIComponent):
    """Decorator — wraps a UIComponent and delegates to it by default.

    Subclasses add visual/behavioural concerns before/after calling
    `self._wrapped.render()`. Following OCP: a new visual concern is a
    new subclass, no existing widget or decorator needs to change.
    """

    def __init__(self, wrapped: UIComponent) -> None:
        self._wrapped = wrapped

    def render(self) -> str:
        """Default delegation — subclasses override to inject markup."""
        return self._wrapped.render()

    def describe(self) -> str:
        """Default delegation — subclasses override to extend the label."""
        return self._wrapped.describe()
