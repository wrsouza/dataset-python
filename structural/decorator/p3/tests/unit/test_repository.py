"""Unit tests for InMemoryResourceRepository."""

from __future__ import annotations

from permission_layers.domain.entities import Resource
from permission_layers.infrastructure.repository import InMemoryResourceRepository


def test_find_by_id_returns_none_when_missing() -> None:
    repo = InMemoryResourceRepository()
    assert repo.find_by_id("missing") is None


def test_find_by_id_returns_resource_when_present() -> None:
    resource = Resource(resource_id="r1", owner_id="u1", title="Doc")
    repo = InMemoryResourceRepository({"r1": resource})
    assert repo.find_by_id("r1") == resource


def test_add_registers_new_resource() -> None:
    repo = InMemoryResourceRepository()
    resource = Resource(resource_id="r2", owner_id="u2", title="Other")
    repo.add(resource)
    assert repo.find_by_id("r2") == resource
