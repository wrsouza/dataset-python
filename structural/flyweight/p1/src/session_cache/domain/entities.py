"""Domain entities for Session Token Cache — Flyweight pattern.

SessionMetadata is the Flyweight: frozen dataclass guaranteeing immutability.
UserSession is the Context: combines user-specific state with a Flyweight reference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SessionMetadata:
    """Flyweight — intrinsic state shared by all sessions of the same role.

    frozen=True enforces immutability at runtime, making this safe to share
    across thousands of UserSession instances without risk of mutation.
    """

    role: str
    permissions: frozenset[str]
    app_version: str
    max_session_duration: int  # seconds
    allowed_ip_ranges: frozenset[str] = field(default_factory=frozenset)
    requires_mfa: bool = False

    def has_permission(self, permission: str) -> bool:
        """Check if this role includes the given permission."""
        return permission in self.permissions

    def __repr__(self) -> str:
        return (
            f"SessionMetadata(role={self.role!r}, "
            f"permissions={len(self.permissions)} perms, "
            f"app_version={self.app_version!r})"
        )


@dataclass
class UserSession:
    """Context — combines user-specific (extrinsic) state with a Flyweight reference.

    The Flyweight (metadata) is NOT stored per-session; it is a shared reference.
    Only user_id, token, and timestamps are unique per session.
    """

    user_id: str
    token: str
    metadata: (
        SessionMetadata  # shared Flyweight — same object for all sessions of same role
    )
    created_at: datetime
    expires_at: datetime
    last_activity: datetime

    @property
    def role(self) -> str:
        """Delegate role access to the shared Flyweight."""
        return self.metadata.role

    @property
    def permissions(self) -> frozenset[str]:
        """Delegate permissions to the shared Flyweight."""
        return self.metadata.permissions

    def is_expired(self, now: datetime | None = None) -> bool:
        """Check session expiry using extrinsic expires_at state."""
        check_time = now or datetime.utcnow()
        return check_time > self.expires_at

    def has_permission(self, permission: str) -> bool:
        """Delegate permission check to the shared Flyweight."""
        return self.metadata.has_permission(permission)

    def to_dict(self) -> dict[str, object]:
        """Serialize session for Redis storage — only extrinsic state + role key."""
        return {
            "user_id": self.user_id,
            "token": self.token,
            "role": self.metadata.role,  # key to reconstruct Flyweight
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }


@dataclass(frozen=True)
class CacheStats:
    """Statistics showing memory economy from the Flyweight pattern."""

    total_sessions: int
    unique_flyweights: int
    roles_cached: list[str]
    estimated_bytes_without_flyweight: int
    estimated_bytes_with_flyweight: int

    @property
    def memory_saved_bytes(self) -> int:
        return (
            self.estimated_bytes_without_flyweight - self.estimated_bytes_with_flyweight
        )

    @property
    def savings_percentage(self) -> float:
        if self.estimated_bytes_without_flyweight == 0:
            return 0.0
        return (self.memory_saved_bytes / self.estimated_bytes_without_flyweight) * 100
