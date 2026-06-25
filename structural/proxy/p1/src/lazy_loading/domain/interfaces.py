"""Domain interfaces (Subject) for the Lazy DB Proxy pattern.

The Protocol here is the Subject role in the Proxy pattern.
Both RealSubject (PostgresUserProfileService) and Proxy (LazyUserProfileProxy)
implement this interface, ensuring DIP and LSP.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from lazy_loading.domain.entities import (
    UserAnalytics,
    UserAvatar,
    UserDocument,
    UserProfile,
)


@runtime_checkable
class UserProfileService(Protocol):
    """Subject: defines the interface for user profile operations.

    Clients depend only on this Protocol, not on any concrete implementation.
    This enforces DIP: high-level modules (use cases, routes) are decoupled
    from low-level modules (Postgres, Proxy).
    """

    async def get_profile(self, user_id: int) -> UserProfile:
        """Return base profile data for the given user."""
        ...

    async def get_avatar(self, user_id: int) -> UserAvatar:
        """Return avatar binary data for the given user."""
        ...

    async def get_documents(self, user_id: int) -> list[UserDocument]:
        """Return all documents belonging to the given user."""
        ...

    async def get_analytics(self, user_id: int) -> UserAnalytics:
        """Return analytics summary for the given user."""
        ...
