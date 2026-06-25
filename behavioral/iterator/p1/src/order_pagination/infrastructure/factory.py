"""Composition helpers for wiring the repository to a real PostgreSQL database."""

from __future__ import annotations

import os
from typing import cast

import psycopg2

from order_pagination.infrastructure.postgres_repository import (
    DBConnection,
    PostgresOrderRepository,
)


def build_connection() -> DBConnection:
    """Open a PostgreSQL connection from environment variables."""
    connection = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        dbname=os.environ.get("POSTGRES_DB", "order_pagination"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    )
    return cast(DBConnection, connection)


def build_repository() -> PostgresOrderRepository:
    """Build the order repository on top of a fresh PostgreSQL connection."""
    return PostgresOrderRepository(build_connection())
