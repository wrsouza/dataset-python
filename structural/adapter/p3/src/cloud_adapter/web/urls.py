"""URL routing for the cloud_adapter web layer."""

from __future__ import annotations

from django.urls import path

from cloud_adapter.web import views

urlpatterns = [
    path("files/upload", views.upload_file, name="upload_file"),
    path("files/", views.list_files, name="list_files"),
    path("files/<int:file_id>/download", views.download_file, name="download_file"),
    path("files/<int:file_id>", views.delete_file, name="delete_file"),
]
