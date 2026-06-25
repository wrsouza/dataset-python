"""Redis Caretaker — persists and retrieves FormSnapshots.

Each session's history is stored as a Redis list of JSON-encoded
snapshots (`form:history:<session_id>`), appended on every save. A
Redis list gives us O(1) append and natural ordering for free, which
is exactly the access pattern the Caretaker needs (latest, undo, full
history).

OCP: this is the concrete implementation. Swap with a different backend
by creating another class implementing FormCaretaker ABC.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from redis import Redis

from form_state_memento.domain.entities import FormSnapshot, NoHistoryError
from form_state_memento.domain.interfaces import FormCaretaker

_HISTORY_TTL_SECONDS = 60 * 60 * 24  # 24h — autosave history is short-lived


class RedisFormCaretaker(FormCaretaker):
    """Stores form snapshots (mementos) in a Redis list per session.

    SRP: only manages snapshot persistence — does not interpret field
    contents.
    """

    def __init__(self, client: Redis) -> None:
        self._client = client

    def save(self, session_id: str, snapshot: FormSnapshot) -> None:
        key = self._key(session_id)
        self._client.rpush(key, self._encode(snapshot))
        self._client.expire(key, _HISTORY_TTL_SECONDS)

    def undo(self, session_id: str) -> FormSnapshot:
        key = self._key(session_id)
        if self._client.llen(key) < 2:
            raise NoHistoryError(session_id)
        self._client.rpop(key)
        raw = self._client.lindex(key, -1)
        assert raw is not None
        return self._decode(raw)

    def latest(self, session_id: str) -> FormSnapshot:
        key = self._key(session_id)
        raw = self._client.lindex(key, -1)
        if raw is None:
            raise NoHistoryError(session_id)
        return self._decode(raw)

    def history(self, session_id: str) -> list[FormSnapshot]:
        key = self._key(session_id)
        raw_items = self._client.lrange(key, 0, -1)
        return [self._decode(item) for item in raw_items]

    @staticmethod
    def _key(session_id: str) -> str:
        return f"form:history:{session_id}"

    @staticmethod
    def _encode(snapshot: FormSnapshot) -> str:
        return json.dumps(
            {
                "fields": snapshot.fields,
                "step": snapshot.step,
                "label": snapshot.label,
                "created_at": snapshot.created_at.isoformat(),
            }
        )

    @staticmethod
    def _decode(raw: str | bytes) -> FormSnapshot:
        payload = json.loads(raw)
        created_at = datetime.fromisoformat(payload["created_at"])
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return FormSnapshot(
            fields=payload["fields"],
            step=payload["step"],
            label=payload["label"],
            created_at=created_at,
        )
