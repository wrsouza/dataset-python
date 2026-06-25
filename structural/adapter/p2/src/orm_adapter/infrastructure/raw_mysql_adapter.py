"""Adapter 2 — Raw pymysql wrapped to implement UserRepository (Target).

Adaptee: pymysql connection with manual SQL queries.
Adapter: RawMySQLUserAdapter translates UserRepository calls into SQL strings.

LSP: same contract as SQLAlchemyUserAdapter — both implement UserRepository.
"""

from __future__ import annotations

from typing import Any

import pymysql
import pymysql.cursors

from orm_adapter.domain.entities import User, UserNotFoundError


class RawMySQLUserAdapter:
    """Adapter: bridges raw pymysql (Adaptee) to UserRepository (Target).

    Demonstrates that the Adapter pattern is about interface translation,
    not about the sophistication of the underlying technology.
    """

    def __init__(self, connection: pymysql.connections.Connection) -> None:
        self._conn = connection

    def find_by_id(self, user_id: int) -> User | None:
        with self._conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT id, name, email, is_active FROM users WHERE id = %s",
                (user_id,),
            )
            row: dict[str, Any] | None = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def find_all(self) -> list[User]:
        with self._conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT id, name, email, is_active FROM users")
            rows: list[dict[str, Any]] = cursor.fetchall()
        return [self._row_to_entity(r) for r in rows]

    def save(self, user: User) -> User:
        with self._conn.cursor() as cursor:
            if user.id:
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s, is_active=%s WHERE id=%s",
                    (user.name, user.email, user.is_active, user.id),
                )
                if cursor.rowcount == 0:
                    raise UserNotFoundError(user.id)
                self._conn.commit()
                return User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    is_active=user.is_active,
                )
            else:
                cursor.execute(
                    "INSERT INTO users (name, email, is_active) VALUES (%s, %s, %s)",
                    (user.name, user.email, user.is_active),
                )
                new_id: int = cursor.lastrowid
                self._conn.commit()
                return User(
                    id=new_id,
                    name=user.name,
                    email=user.email,
                    is_active=user.is_active,
                )

    def delete(self, user_id: int) -> None:
        with self._conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            if cursor.rowcount == 0:
                raise UserNotFoundError(user_id)
        self._conn.commit()

    @staticmethod
    def _row_to_entity(row: dict[str, Any]) -> User:
        return User(
            id=int(row["id"]),
            name=str(row["name"]),
            email=str(row["email"]),
            is_active=bool(row["is_active"]),
        )
