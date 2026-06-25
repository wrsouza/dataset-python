"""Domain interfaces (Protocols) for feature flags.

OCP: new flag sources (SSM, LaunchDarkly, DB) implement FlagLoader
without changing any existing code.
DIP: the application layer depends on these abstractions, never on
concrete loaders.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from feature_flags.domain.entities import FlagConfig


@runtime_checkable
class FlagLoader(Protocol):
    """Loads flag configurations from an external source.

    Implementors: JsonFlagLoader, SsmFlagLoader, LaunchDarklyLoader.
    """

    def load(self) -> dict[str, FlagConfig]:
        """Return all flags keyed by flag name.

        Raises:
            FlagLoadError: when the source is unreachable or malformed.
        """
        ...


class FlagLoadError(Exception):
    """Raised when flag configuration cannot be loaded from the source."""
