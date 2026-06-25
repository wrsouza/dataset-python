"""Django ORM Caretaker — persists and retrieves ProductSnapshots.

OCP: this is the concrete implementation. Swap with a different backend
(e.g. a separate audit database, S3, Kafka) by creating another class
implementing AuditTrailCaretaker ABC.
"""

from __future__ import annotations

from datetime import UTC

from audit_trail_records.django_app.models import AuditRecordModel
from audit_trail_records.domain.entities import NoHistoryError, ProductSnapshot
from audit_trail_records.domain.interfaces import AuditTrailCaretaker


class DjangoAuditTrailCaretaker(AuditTrailCaretaker):
    """Stores product snapshots (mementos) in the audit_record table.

    SRP: only manages snapshot persistence — does not modify ProductModel.
    """

    def save(self, product_id: str, snapshot: ProductSnapshot) -> None:
        AuditRecordModel.objects.update_or_create(
            product_id=product_id,
            version=snapshot.version,
            defaults={
                "name": snapshot.name,
                "price": snapshot.price,
                "stock": snapshot.stock,
                "changed_by": snapshot.changed_by,
                "created_at": snapshot.created_at,
            },
        )

    def undo(self, product_id: str) -> ProductSnapshot:
        rows = list(
            AuditRecordModel.objects.filter(product_id=product_id).order_by("-version")[
                :2
            ]
        )
        if len(rows) < 2:
            raise NoHistoryError(product_id)
        # rows[0] is current, rows[1] is the previous one
        return self._row_to_snapshot(rows[1])

    def history(self, product_id: str) -> list[ProductSnapshot]:
        rows = AuditRecordModel.objects.filter(product_id=product_id).order_by(
            "version"
        )
        return [self._row_to_snapshot(row) for row in rows]

    @staticmethod
    def _row_to_snapshot(row: AuditRecordModel) -> ProductSnapshot:
        created_at = row.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return ProductSnapshot(
            name=row.name,
            price=row.price,
            stock=row.stock,
            version=row.version,
            changed_by=row.changed_by,
            created_at=created_at,
        )
