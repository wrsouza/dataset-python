"""Django views for feature flag API endpoints.

SRP: each view function handles exactly one HTTP endpoint.
All views are thin adapters — they delegate to use cases.
"""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from feature_flags.application.use_cases import (
    CheckFlagRequest,
    CheckFlagUseCase,
    GetRegistryStatsUseCase,
    ListAllFlagsUseCase,
    ReloadFlagsUseCase,
)
from feature_flags.infrastructure.singleton import FeatureFlagManager
from feature_flags.middleware.decorators import feature_required


def _manager() -> FeatureFlagManager:
    """Return the singleton manager — same object every call."""
    return FeatureFlagManager()


@require_GET
def list_flags(request: HttpRequest) -> JsonResponse:
    """GET /flags/ — list all feature flags and their configurations."""
    flags = ListAllFlagsUseCase(_manager()).execute()
    stats = GetRegistryStatsUseCase(_manager()).execute()
    return JsonResponse(
        {
            "flags": {
                name: {
                    "enabled": cfg.enabled,
                    "flag_type": cfg.flag_type.value,
                    "rollout_percentage": cfg.rollout_percentage,
                    "allowlist": cfg.allowlist,
                }
                for name, cfg in flags.items()
            },
            "stats": {
                "total_flags": stats.total_flags,
                "enabled_flags": stats.enabled_flags,
                "reload_count": stats.reload_count,
                "override_count": stats.override_count,
            },
            "singleton_id": id(_manager()),
        }
    )


@csrf_exempt
@require_POST
def reload_flags(request: HttpRequest) -> JsonResponse:
    """POST /flags/reload — reload flags from the JSON source file."""
    stats = ReloadFlagsUseCase(_manager()).execute()
    return JsonResponse(
        {
            "message": "flags reloaded",
            "stats": {
                "total_flags": stats.total_flags,
                "enabled_flags": stats.enabled_flags,
                "reload_count": stats.reload_count,
            },
        }
    )


@require_GET
def check_flag(request: HttpRequest, flag_name: str) -> JsonResponse:
    """GET /flags/<name>/check?user_id=... — evaluate a flag for a user."""
    user_id: str | None = request.GET.get("user_id") or None
    result = CheckFlagUseCase(_manager()).execute(
        CheckFlagRequest(flag_name=flag_name, user_id=user_id)
    )
    return JsonResponse(
        {
            "flag": result.flag_name,
            "is_enabled": result.is_enabled,
            "user_id": result.user_id,
            "reason": result.reason,
            "singleton_id": id(_manager()),
        }
    )


@require_GET
@feature_required("experimental_dashboard")
def experimental_dashboard(request: HttpRequest) -> JsonResponse:
    """GET /flags/experimental-dashboard/ — gated by @feature_required decorator."""
    return JsonResponse(
        {"message": "Welcome to the experimental dashboard!", "status": "active"}
    )
