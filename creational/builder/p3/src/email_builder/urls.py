"""URL routing for the email_builder app."""

from __future__ import annotations

from django.urls import path

from email_builder.views import EmailLogListView, SendEmailView

urlpatterns = [
    path("emails/logs", EmailLogListView.as_view(), name="email-logs"),
    path("emails/<str:template_type>", SendEmailView.as_view(), name="send-email"),
]
