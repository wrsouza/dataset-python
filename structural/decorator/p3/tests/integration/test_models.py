"""Integration tests for Django ORM models and DjangoResourceRepository."""

from __future__ import annotations

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_test")
django.setup()

import pytest

from permission_layers.infrastructure.repository import DjangoResourceRepository
from permission_layers.models import DocumentModel

pytestmark = pytest.mark.django_db


def test_django_repository_returns_resource_for_existing_document() -> None:
    DocumentModel.objects.create(
        resource_id="doc-99", owner_id="owner-99", title="Spec"
    )
    repository = DjangoResourceRepository()
    resource = repository.find_by_id("doc-99")
    assert resource is not None
    assert resource.owner_id == "owner-99"
    assert resource.title == "Spec"


def test_django_repository_returns_none_for_missing_document() -> None:
    repository = DjangoResourceRepository()
    assert repository.find_by_id("does-not-exist") is None
