"""URL configuration for the feature_flags Django project."""

from __future__ import annotations

from django.urls import path

from feature_flags.views.api import (
    check_flag,
    experimental_dashboard,
    list_flags,
    reload_flags,
)

urlpatterns = [
    path("flags/", list_flags, name="list_flags"),
    path("flags/reload", reload_flags, name="reload_flags"),
    path("flags/experimental-dashboard/", experimental_dashboard, name="experimental_dashboard"),
    path("flags/<str:flag_name>/check", check_flag, name="check_flag"),
]
