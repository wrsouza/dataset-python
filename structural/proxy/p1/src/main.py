"""FastAPI application — Lazy DB Proxy (Virtual Proxy pattern).

Composition root: wires PostgresUserProfileService (RealSubject) behind
LazyUserProfileProxy (Proxy). Routes depend only on UserProfileService
(the Subject Protocol) via dependency injection — they never know whether
they're talking to the Proxy or a bare RealSubject.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from fastapi import Depends, FastAPI, HTTPException, status

from lazy_loading.application.use_cases import (
    GetLoadStatsUseCase,
    GetUserAnalyticsUseCase,
    GetUserAvatarUseCase,
    GetUserDocumentsUseCase,
    GetUserProfileUseCase,
)
from lazy_loading.domain.entities import (
    LoadStats,
    UserAnalytics,
    UserAvatar,
    UserDocument,
    UserProfile,
)
from lazy_loading.domain.exceptions import AvatarNotFoundError, UserNotFoundError
from lazy_loading.infrastructure.proxy import LazyUserProfileProxy
from lazy_loading.infrastructure.real_subject import PostgresUserProfileService

_pool: asyncpg.Pool | None = None
_proxy: LazyUserProfileProxy | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _pool, _proxy
    database_url = os.environ.get(
        "DATABASE_URL", "postgresql://app:secret@localhost:5432/lazyloading"
    )
    _pool = await asyncpg.create_pool(database_url)
    real_service = PostgresUserProfileService(pool=_pool)
    _proxy = LazyUserProfileProxy(real_service=real_service)
    yield
    await _pool.close()


app = FastAPI(
    title="Lazy DB Proxy — Virtual Proxy Pattern",
    description=(
        "UserProfileService Proxy defers expensive Postgres queries until "
        "the data is actually requested, caching results per user."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


def get_proxy() -> LazyUserProfileProxy:
    if _proxy is None:
        raise RuntimeError("Proxy not initialized — app lifespan has not started.")
    return _proxy


@app.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_profile(
    user_id: int, proxy: LazyUserProfileProxy = Depends(get_proxy)
) -> UserProfile:
    use_case = GetUserProfileUseCase(service=proxy)
    try:
        return await use_case.execute(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@app.get("/users/{user_id}/avatar", response_model=UserAvatar)
async def get_avatar(
    user_id: int, proxy: LazyUserProfileProxy = Depends(get_proxy)
) -> UserAvatar:
    use_case = GetUserAvatarUseCase(service=proxy)
    try:
        return await use_case.execute(user_id)
    except AvatarNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@app.get("/users/{user_id}/documents", response_model=list[UserDocument])
async def get_documents(
    user_id: int, proxy: LazyUserProfileProxy = Depends(get_proxy)
) -> list[UserDocument]:
    use_case = GetUserDocumentsUseCase(service=proxy)
    return await use_case.execute(user_id)


@app.get("/users/{user_id}/analytics", response_model=UserAnalytics)
async def get_analytics(
    user_id: int, proxy: LazyUserProfileProxy = Depends(get_proxy)
) -> UserAnalytics:
    use_case = GetUserAnalyticsUseCase(service=proxy)
    try:
        return await use_case.execute(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@app.get("/profile/load-stats", response_model=LoadStats)
async def load_stats(proxy: LazyUserProfileProxy = Depends(get_proxy)) -> LoadStats:
    use_case = GetLoadStatsUseCase(proxy=proxy)
    return use_case.execute()
