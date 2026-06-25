"""PostgreSQL-backed implementation of EventStore."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Protocol

from event_sourcing.domain.entities import DomainEvent, EventType
from event_sourcing.domain.interfaces import EventStore

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS account_events (
    event_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL
)
"""

INSERT_SQL = """
INSERT INTO account_events (event_id, account_id, event_type, payload, occurred_at)
VALUES (%s, %s, %s, %s, %s)
"""

SELECT_SQL = """
SELECT event_id, account_id, event_type, payload, occurred_at
FROM account_events
WHERE account_id = %s
ORDER BY occurred_at ASC, event_id ASC
"""


class DBConnection(Protocol):
    """Minimal DB-API connection contract this event store relies on."""

    def cursor(self) -> Any: ...

    def commit(self) -> None: ...


class PostgresEventStore(EventStore):
    """Stores account events in an append-only `account_events` table."""

    def __init__(self, connection: DBConnection) -> None:
        self._connection = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        self._connection.commit()

    def append(self, event: DomainEvent) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            INSERT_SQL,
            (
                event.event_id,
                event.account_id,
                event.event_type.value,
                json.dumps(event.payload),
                event.occurred_at.isoformat(),
            ),
        )
        self._connection.commit()

    def get_events(self, account_id: str) -> list[DomainEvent]:
        cursor = self._connection.cursor()
        cursor.execute(SELECT_SQL, (account_id,))
        rows = cursor.fetchall()
        return [self._row_to_event(row) for row in rows]

    @staticmethod
    def _row_to_event(row: tuple[Any, ...]) -> DomainEvent:
        event_id, account_id, event_type, payload, occurred_at = row
        return DomainEvent(
            event_id=event_id,
            account_id=account_id,
            event_type=EventType(event_type),
            payload=json.loads(payload) if isinstance(payload, str) else payload,
            occurred_at=(
                occurred_at
                if isinstance(occurred_at, datetime)
                else datetime.fromisoformat(occurred_at)
            ),
        )
