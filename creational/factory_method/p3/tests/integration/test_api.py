"""Integration tests for Django Auth Provider Factory API endpoints.

Uses Django's test client — no real HTTP server needed. Each ConcreteCreator
in SCHEME_REGISTRY is exercised through the full HTTP -> view -> use case ->
factory method -> provider stack.
"""

from __future__ import annotations

import json
import os

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django
from django.test import Client

django.setup()


@pytest.fixture()
def client() -> Client:
    return Client()


# ── /auth/email_password/* ───────────────────────────────────────────────────


def test_email_password_login_success(client: Client) -> None:
    response = client.post(
        "/auth/email_password/login",
        data=json.dumps({"username": "alice", "password": "password123"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["user_id"] == "alice"
    assert data["scheme"] == "EmailPassword"
    assert "token" in data


def test_email_password_login_invalid_credentials(client: Client) -> None:
    response = client.post(
        "/auth/email_password/login",
        data=json.dumps({"username": "alice", "password": "wrong"}),
        content_type="application/json",
    )
    assert response.status_code == 401


def test_email_password_login_get_not_allowed(client: Client) -> None:
    response = client.get("/auth/email_password/login")
    assert response.status_code == 405


def test_login_validate_logout_full_cycle(client: Client) -> None:
    login_response = client.post(
        "/auth/email_password/login",
        data=json.dumps({"username": "bob", "password": "password123"}),
        content_type="application/json",
    )
    token = json.loads(login_response.content)["token"]

    validate_response = client.post(
        "/auth/email_password/validate",
        data=json.dumps({"token": token}),
        content_type="application/json",
    )
    assert validate_response.status_code == 200
    assert json.loads(validate_response.content)["user_id"] == "bob"

    logout_response = client.post(
        "/auth/email_password/logout",
        data=json.dumps({"token": token}),
        content_type="application/json",
    )
    assert logout_response.status_code == 200

    revalidate_response = client.post(
        "/auth/email_password/validate",
        data=json.dumps({"token": token}),
        content_type="application/json",
    )
    assert revalidate_response.status_code == 401


# ── /auth/oauth_google/* (simulated OAuth) ───────────────────────────────────


def test_oauth_google_login_success(client: Client) -> None:
    response = client.post(
        "/auth/oauth_google/login",
        data=json.dumps({"auth_code": "google-oauth-code-alice"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["scheme"] == "OAuthGoogle"
    assert data["user_id"] == "alice@gmail.com"


def test_oauth_google_login_invalid_code(client: Client) -> None:
    response = client.post(
        "/auth/oauth_google/login",
        data=json.dumps({"auth_code": "bad-code"}),
        content_type="application/json",
    )
    assert response.status_code == 401


# ── /auth/oauth_github/* (simulated OAuth) ───────────────────────────────────


def test_oauth_github_login_success(client: Client) -> None:
    response = client.post(
        "/auth/oauth_github/login",
        data=json.dumps({"auth_code": "github-oauth-code-bob"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["scheme"] == "OAuthGithub"
    assert data["user_id"] == "bob-gh"


def test_oauth_github_login_invalid_code(client: Client) -> None:
    response = client.post(
        "/auth/oauth_github/login",
        data=json.dumps({"auth_code": "bad-code"}),
        content_type="application/json",
    )
    assert response.status_code == 401


# ── /auth/api_key/* ───────────────────────────────────────────────────────────


def test_api_key_login_success(client: Client) -> None:
    response = client.post(
        "/auth/api_key/login",
        data=json.dumps({"api_key": "ak_alice_test_key_001"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["scheme"] == "APIKey"
    assert data["user_id"] == "alice"


def test_api_key_login_invalid_key(client: Client) -> None:
    response = client.post(
        "/auth/api_key/login",
        data=json.dumps({"api_key": "not-a-real-key"}),
        content_type="application/json",
    )
    assert response.status_code == 401


# ── Unsupported scheme ─────────────────────────────────────────────────────────


def test_unsupported_scheme_returns_404(client: Client) -> None:
    response = client.post(
        "/auth/unknown_scheme/login",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_unsupported_scheme_validate_returns_404(client: Client) -> None:
    response = client.post(
        "/auth/unknown_scheme/validate",
        data=json.dumps({"token": "x"}),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_unsupported_scheme_logout_returns_404(client: Client) -> None:
    response = client.post(
        "/auth/unknown_scheme/logout",
        data=json.dumps({"token": "x"}),
        content_type="application/json",
    )
    assert response.status_code == 404
