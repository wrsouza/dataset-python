"""Domain entities for the Access Control Proxy project."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Role(StrEnum):
    """Permission roles ordered by ascending privilege."""

    GUEST = "GUEST"
    VIEWER = "VIEWER"
    EDITOR = "EDITOR"
    OWNER = "OWNER"


@dataclass
class User:
    """Authenticated application user."""

    user_id: str
    username: str
    email: str
    role: Role
    is_active: bool = True


@dataclass
class Document:
    """A document managed by DocumentService."""

    doc_id: str
    title: str
    content: str
    owner_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_deleted: bool = False


@dataclass
class AuditLog:
    """Record of an access attempt (granted or denied)."""

    log_id: str
    user_id: str
    action: str  # "get", "create", "update", "delete", "list"
    resource_id: str  # doc_id or "*" for list
    granted: bool
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
