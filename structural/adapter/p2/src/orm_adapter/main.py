"""Flask application — composition root.

The ?adapter=sqlalchemy|raw query parameter chooses which Adapter to inject,
demonstrating that both implement UserRepository interchangeably (LSP).
"""

from __future__ import annotations

import os
from dataclasses import asdict

import pymysql
from flask import Flask, Response, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from orm_adapter.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from orm_adapter.domain.entities import User, UserNotFoundError
from orm_adapter.domain.interfaces import UserRepository
from orm_adapter.infrastructure.raw_mysql_adapter import RawMySQLUserAdapter
from orm_adapter.infrastructure.sqlalchemy_adapter import (
    SQLAlchemyUserAdapter,
    create_tables,
)

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://app:secret@db:3306/appdb",
)

_engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


def _init_db() -> None:
    """Create tables and ensure raw MySQL table exists."""
    create_tables(_engine)


# ---------------------------------------------------------------------------
# Adapter factory — selects which Adapter to inject based on request param
# ---------------------------------------------------------------------------


def _get_repository() -> UserRepository:
    adapter_name = request.args.get("adapter", "sqlalchemy").lower()

    if adapter_name == "raw":
        # Adaptee 2: raw pymysql connection
        db_host = os.environ.get("MYSQL_HOST", "db")
        db_port = int(os.environ.get("MYSQL_PORT", "3306"))
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=os.environ.get("MYSQL_USER", "app"),
            password=os.environ.get("MYSQL_PASSWORD", "secret"),
            database=os.environ.get("MYSQL_DATABASE", "appdb"),
            autocommit=False,
        )
        return RawMySQLUserAdapter(connection=conn)

    # Adaptee 1: SQLAlchemy session
    session = Session(_engine)
    return SQLAlchemyUserAdapter(session=session)


def _user_dict(user: User) -> dict[str, object]:
    return asdict(user)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/users")
def list_users() -> Response:
    repo = _get_repository()
    users = ListUsersUseCase(repository=repo).execute()
    return jsonify([_user_dict(u) for u in users])


@app.get("/users/<int:user_id>")
def get_user(user_id: int) -> Response | tuple[Response, int]:
    repo = _get_repository()
    try:
        user = GetUserUseCase(repository=repo).execute(user_id)
        return jsonify(_user_dict(user))
    except UserNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404


@app.post("/users")
def create_user() -> tuple[Response, int]:
    body = request.get_json(force=True) or {}
    repo = _get_repository()
    user = CreateUserUseCase(repository=repo).execute(
        name=body.get("name", ""),
        email=body.get("email", ""),
    )
    return jsonify(_user_dict(user)), 201


@app.put("/users/<int:user_id>")
def update_user(user_id: int) -> Response | tuple[Response, int]:
    body = request.get_json(force=True) or {}
    repo = _get_repository()
    try:
        user = UpdateUserUseCase(repository=repo).execute(
            user_id=user_id,
            name=body.get("name", ""),
            email=body.get("email", ""),
        )
        return jsonify(_user_dict(user))
    except UserNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404


@app.delete("/users/<int:user_id>")
def delete_user(user_id: int) -> Response | tuple[Response, int]:
    repo = _get_repository()
    try:
        DeleteUserUseCase(repository=repo).execute(user_id)
        return jsonify({"deleted": user_id})
    except UserNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404


@app.get("/health")
def health() -> Response:
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    with app.app_context():
        _init_db()
    app.run(host="0.0.0.0", port=5001, debug=False)
