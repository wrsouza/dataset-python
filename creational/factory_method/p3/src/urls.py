"""URL configuration for the Auth Provider Factory Django project."""

from __future__ import annotations

from django.urls import path

from auth.views.api import login, logout, validate

urlpatterns = [
    path("auth/<str:scheme>/login", login, name="login"),
    path("auth/<str:scheme>/validate", validate, name="validate"),
    path("auth/<str:scheme>/logout", logout, name="logout"),
]
