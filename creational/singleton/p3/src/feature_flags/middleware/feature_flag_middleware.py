"""Django middleware that injects `request.flags` on every request.

SRP: the middleware has exactly one job — attach the singleton manager
to the request object so views receive it without importing it directly.

Usage in views:
    def my_view(request):
        if request.flags.is_enabled("dark_mode", user_id=str(request.user.id)):
            ...
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse

from feature_flags.infrastructure.singleton import FeatureFlagManager


class FeatureFlagMiddleware:
    """Attach the FeatureFlagManager singleton to every Django request.

    The singleton is already loaded — this middleware is zero-cost after
    the first request (no I/O on subsequent calls).
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self._get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Attach singleton; views read it via request.flags.
        # Using type: ignore because Django's HttpRequest doesn't declare .flags.
        request.flags = FeatureFlagManager()  # type: ignore[attr-defined]
        return self._get_response(request)
