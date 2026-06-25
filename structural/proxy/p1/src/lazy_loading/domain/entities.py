"""Domain entities for the Lazy DB Proxy project."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """Core user profile data — cheap to load."""

    user_id: int
    username: str
    email: str
    full_name: str
    created_at: datetime
    is_active: bool = True


class UserAvatar(BaseModel):
    """Avatar binary data — potentially large, loaded lazily."""

    user_id: int
    content_type: str = "image/png"
    data: bytes = Field(default=b"")
    size_bytes: int = 0
    updated_at: datetime | None = None


class UserDocument(BaseModel):
    """A document owned by a user — loaded as a list lazily."""

    document_id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    file_size_kb: float = 0.0


class UserAnalytics(BaseModel):
    """Analytics summary — computed on demand, heavy query."""

    user_id: int
    login_count: int = 0
    document_count: int = 0
    last_login: datetime | None = None
    total_storage_kb: float = 0.0
    activity_score: float = 0.0


class LoadStats(BaseModel):
    """Tracks how many times each proxy method was called vs cached."""

    profile_loads: int = 0
    profile_cache_hits: int = 0
    avatar_loads: int = 0
    avatar_cache_hits: int = 0
    documents_loads: int = 0
    documents_cache_hits: int = 0
    analytics_loads: int = 0
    analytics_cache_hits: int = 0

    @property
    def total_loads(self) -> int:
        return (
            self.profile_loads
            + self.avatar_loads
            + self.documents_loads
            + self.analytics_loads
        )

    @property
    def total_cache_hits(self) -> int:
        return (
            self.profile_cache_hits
            + self.avatar_cache_hits
            + self.documents_cache_hits
            + self.analytics_cache_hits
        )
