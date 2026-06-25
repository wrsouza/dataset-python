"""Integration tests for the auth_strategy Django views."""

from __future__ import annotations

import json

import pytest
from django.contrib.auth.hashers import make_password
from django.test import Client

from auth_strategy.django_app.models import ApiTokenModel, UserCredentialModel

pytestmark = pytest.mark.django_db


def test_authenticate_with_password_strategy_succeeds(client: Client) -> None:
    UserCredentialModel.objects.create(
        username="ana", password_hash=make_password("s3cret"), user_id="u1"
    )

    response = client.post(
        "/auth/password/",
        data=json.dumps({"username": "ana", "password": "s3cret"}),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["user_id"] == "u1"


def test_authenticate_with_wrong_password_returns_401(client: Client) -> None:
    UserCredentialModel.objects.create(
        username="ana", password_hash=make_password("s3cret"), user_id="u1"
    )

    response = client.post(
        "/auth/password/",
        data=json.dumps({"username": "ana", "password": "wrong"}),
        content_type="application/json",
    )

    assert response.status_code == 401


def test_authenticate_with_token_strategy(client: Client) -> None:
    ApiTokenModel.objects.create(token="abc123", user_id="u1", is_active=True)

    response = client.post(
        "/auth/token/",
        data=json.dumps({"token": "abc123"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == "u1"


def test_authenticate_with_unknown_strategy_returns_400(client: Client) -> None:
    response = client.post(
        "/auth/unknown/",
        data=json.dumps({}),
        content_type="application/json",
    )

    assert response.status_code == 400


def test_attempts_lists_every_authentication_call(client: Client) -> None:
    ApiTokenModel.objects.create(token="abc123", user_id="u1", is_active=True)
    client.post(
        "/auth/token/",
        data=json.dumps({"token": "abc123"}),
        content_type="application/json",
    )
    client.post(
        "/auth/token/",
        data=json.dumps({"token": "wrong"}),
        content_type="application/json",
    )

    response = client.get("/auth/attempts/")

    body = response.json()
    assert response.status_code == 200
    assert len(body) == 2
