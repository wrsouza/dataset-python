"""Resource repository abstraction and its in-memory/Django implementations.

The application/domain layers depend only on `ResourceRepository` (a
`Protocol`), never on Django's ORM directly — keeping persistence concerns
out of the business rules (Dependency Inversion).
"""

from __future__ import annotations

from typing import Protocol

from permission_layers.domain.entities import Resource


class ResourceRepository(Protocol):
    """Read access to resources, independent of the storage technology."""

    def find_by_id(self, resource_id: str) -> Resource | None:
        """Return the resource with `resource_id`, or None if it does not exist."""
        ...


class InMemoryResourceRepository:
    """Simple dict-backed repository — used in tests and as a lightweight default."""

    def __init__(self, resources: dict[str, Resource] | None = None) -> None:
        self._resources: dict[str, Resource] = dict(resources or {})

    def find_by_id(self, resource_id: str) -> Resource | None:
        return self._resources.get(resource_id)

    def add(self, resource: Resource) -> None:
        """Register a resource (test/demo helper)."""
        self._resources[resource.resource_id] = resource


class DjangoResourceRepository:
    """Adapter that fetches resources from the Django ORM (PostgreSQL)."""

    def find_by_id(self, resource_id: str) -> Resource | None:
        from permission_layers.models import DocumentModel

        try:
            model = DocumentModel.objects.get(resource_id=resource_id)
        except DocumentModel.DoesNotExist:
            return None
        return Resource(
            resource_id=model.resource_id,
            owner_id=model.owner_id,
            title=model.title,
        )
