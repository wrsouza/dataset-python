"""Composition helpers for wiring the escalation chain to a database."""

from __future__ import annotations

import os
from typing import cast

import psycopg2

from ticket_escalation.infrastructure.postgres_repository import (
    DBConnection,
    PostgresTicketRepository,
)


def build_connection() -> DBConnection:
    """Open a PostgreSQL connection from environment variables."""
    connection = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        dbname=os.environ.get("POSTGRES_DB", "ticket_escalation"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    )
    return cast(DBConnection, connection)


def build_repository(connection: DBConnection) -> PostgresTicketRepository:
    """Build the ticket repository on top of an existing connection."""
    return PostgresTicketRepository(connection)
