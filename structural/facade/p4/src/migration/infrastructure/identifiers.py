"""Shared SQL-identifier validation — prevents injection via table names.

Table names reach this code from trusted CLI args, not untrusted web input,
but every subsystem still validates before interpolating into SQL: defense
in depth costs one regex check and avoids a whole class of bugs.
"""

from __future__ import annotations

import re

_VALID_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class InvalidTableNameError(ValueError):
    def __init__(self, table: str) -> None:
        super().__init__(f"Invalid table name: {table!r}")


def validate_table_name(table: str) -> str:
    """Return `table` unchanged if it is a safe SQL identifier, else raise."""
    if not _VALID_IDENTIFIER.match(table):
        raise InvalidTableNameError(table)
    return table
