"""URL configuration for the Database Connector Factory Django project."""

from __future__ import annotations

from django.urls import path

from db_factory.views.db_views import health_check, run_query

urlpatterns = [
    # GET /db/health/<db_type>/  → health check for the requested engine
    path("db/health/<str:db_type>/", health_check, name="db-health"),
    # POST /db/query/<db_type>/  → execute a basic query on the requested engine
    path("db/query/<str:db_type>/", run_query, name="db-query"),
]
