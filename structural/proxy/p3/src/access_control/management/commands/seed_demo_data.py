"""Management command: seed_demo_data

Creates one demo user per Role and a couple of documents, so the API can be
exercised immediately with `X-User-Id` headers (owner, editor, viewer, guest).
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from access_control.domain.entities import Role
from access_control.infrastructure.models import DocumentModel, UserModel

_DEMO_USERS = [
    ("owner-1", "alice", "alice@example.com", Role.OWNER),
    ("editor-1", "bob", "bob@example.com", Role.EDITOR),
    ("viewer-1", "carol", "carol@example.com", Role.VIEWER),
    ("guest-1", "dave", "dave@example.com", Role.GUEST),
]


class Command(BaseCommand):
    help = "Seed demo users (one per role) and sample documents."

    def handle(self, *args: object, **options: object) -> None:
        for user_id, username, email, role in _DEMO_USERS:
            UserModel.objects.get_or_create(
                user_id=user_id,
                defaults={"username": username, "email": email, "role": role.value},
            )

        DocumentModel.objects.get_or_create(
            doc_id="doc-1",
            defaults={
                "title": "Quarterly Report",
                "content": "Lorem ipsum dolor sit amet.",
                "owner_id": "owner-1",
            },
        )
        DocumentModel.objects.get_or_create(
            doc_id="doc-2",
            defaults={
                "title": "Onboarding Guide",
                "content": "Welcome to the team!",
                "owner_id": "editor-1",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(_DEMO_USERS)} users and 2 documents. "
                "Use header 'X-User-Id: owner-1' (or editor-1/viewer-1/guest-1)."
            )
        )
