"""Unit tests for DjangoAuditLogger — real ORM, SQLite in-memory."""

from __future__ import annotations

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from django.test import TestCase  # noqa: E402

from access_control.infrastructure.audit_logger import DjangoAuditLogger  # noqa: E402
from access_control.infrastructure.models import AuditLogModel  # noqa: E402


class DjangoAuditLoggerTests(TestCase):
    def test_log_persists_an_audit_entry(self) -> None:
        logger = DjangoAuditLogger()

        logger.log("u1", "read", "doc-1", True, "")

        assert AuditLogModel.objects.count() == 1
        entry = AuditLogModel.objects.first()
        assert entry is not None
        assert entry.user_id == "u1"
        assert entry.granted is True

    def test_log_records_denial_reason(self) -> None:
        logger = DjangoAuditLogger()

        logger.log("u1", "delete", "doc-1", False, "role VIEWER lacks 'delete'")

        entry = AuditLogModel.objects.first()
        assert entry is not None
        assert entry.granted is False
        assert "lacks" in entry.reason
