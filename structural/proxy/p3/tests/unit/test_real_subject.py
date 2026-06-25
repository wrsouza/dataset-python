"""Unit tests for DjangoDocumentService (RealSubject) — real ORM, SQLite in-memory."""

from __future__ import annotations

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

import pytest  # noqa: E402
from django.test import TestCase  # noqa: E402

from access_control.domain.exceptions import DocumentNotFoundError  # noqa: E402
from access_control.infrastructure import real_subject  # noqa: E402

DjangoDocumentService = real_subject.DjangoDocumentService


class DjangoDocumentServiceTests(TestCase):
    def setUp(self) -> None:
        self.service = DjangoDocumentService()

    def test_create_and_get_round_trip(self) -> None:
        created = self.service.create(
            {
                "doc_id": "doc-1",
                "title": "Title",
                "content": "Content",
                "owner_id": "u1",
            }
        )

        fetched = self.service.get("doc-1")

        assert fetched.doc_id == created.doc_id
        assert fetched.title == "Title"

    def test_get_raises_for_missing_document(self) -> None:
        with pytest.raises(DocumentNotFoundError):
            self.service.get("does-not-exist")

    def test_update_changes_title_and_content(self) -> None:
        self.service.create(
            {"doc_id": "doc-1", "title": "Old", "content": "Old", "owner_id": "u1"}
        )

        updated = self.service.update("doc-1", {"title": "New"})

        assert updated.title == "New"
        assert updated.content == "Old"

    def test_delete_is_soft_delete(self) -> None:
        self.service.create(
            {"doc_id": "doc-1", "title": "T", "content": "C", "owner_id": "u1"}
        )

        self.service.delete("doc-1")

        with pytest.raises(DocumentNotFoundError):
            self.service.get("doc-1")

    def test_list_filters_by_owner(self) -> None:
        self.service.create(
            {"doc_id": "doc-1", "title": "T1", "content": "C", "owner_id": "u1"}
        )
        self.service.create(
            {"doc_id": "doc-2", "title": "T2", "content": "C", "owner_id": "u2"}
        )

        results = self.service.list({"owner_id": "u1"})

        assert len(results) == 1
        assert results[0].doc_id == "doc-1"

    def test_list_without_filter_returns_all(self) -> None:
        self.service.create(
            {"doc_id": "doc-1", "title": "T1", "content": "C", "owner_id": "u1"}
        )
        self.service.create(
            {"doc_id": "doc-2", "title": "T2", "content": "C", "owner_id": "u2"}
        )

        results = self.service.list({})

        assert len(results) == 2
