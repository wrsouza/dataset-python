"""Decorators for feature-flag-gated Django views.

OCP: new gate behaviours (redirect, return 402, etc.) are added as new
decorators without modifying existing ones.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse, JsonResponse


def feature_required(
    flag_name: str,
    user_id_attr: str = "user_id",
) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    """Return 403 JSON if the named flag is disabled for this request.

    Reads user_id from request.GET.get(user_id_attr) so it works with
    anonymous and authenticated requests alike.

    Args:
        flag_name:     The feature flag to check.
        user_id_attr:  Query-string parameter name for the user identifier.

    Example:
        @feature_required("new_checkout")
        def checkout_view(request):
            ...
    """

    def decorator(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            user_id: str | None = request.GET.get(user_id_attr)
            manager = getattr(request, "flags", None)

            if manager is None or not manager.is_enabled(flag_name, user_id=user_id):
                return JsonResponse(
                    {"error": f"Feature '{flag_name}' is not enabled", "flag": flag_name},
                    status=403,
                )
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
