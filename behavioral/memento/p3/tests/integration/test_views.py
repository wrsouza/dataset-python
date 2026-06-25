"""Integration tests for the audit_trail_records Django views."""

from __future__ import annotations

import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_create_product_returns_201(client: Client) -> None:
    response = client.post(
        "/products/",
        data=json.dumps(
            {"product_id": "p1", "name": "Widget", "price": 9.99, "stock": 10}
        ),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 201
    assert body["current_version"] == 1


def test_update_product_increments_version(client: Client) -> None:
    client.post(
        "/products/",
        data=json.dumps(
            {"product_id": "p1", "name": "Widget", "price": 9.99, "stock": 10}
        ),
        content_type="application/json",
    )

    response = client.put(
        "/products/p1/",
        data=json.dumps(
            {"name": "Widget v2", "price": 12.0, "stock": 5, "changed_by": "bob"}
        ),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 200
    assert body["current_version"] == 2
    assert body["name"] == "Widget v2"


def test_update_unknown_product_returns_404(client: Client) -> None:
    response = client.put(
        "/products/does-not-exist/",
        data=json.dumps({"name": "x", "price": 1.0, "stock": 1}),
        content_type="application/json",
    )

    assert response.status_code == 404


def test_undo_product_reverts_to_previous_version(client: Client) -> None:
    client.post(
        "/products/",
        data=json.dumps(
            {"product_id": "p1", "name": "Widget", "price": 9.99, "stock": 10}
        ),
        content_type="application/json",
    )
    client.put(
        "/products/p1/",
        data=json.dumps({"name": "Widget v2", "price": 12.0, "stock": 5}),
        content_type="application/json",
    )

    response = client.post("/products/p1/undo/")

    body = response.json()
    assert response.status_code == 200
    assert body["name"] == "Widget"
    assert body["current_version"] == 1


def test_undo_unknown_product_returns_404(client: Client) -> None:
    response = client.post("/products/does-not-exist/undo/")

    assert response.status_code == 404


def test_undo_without_history_returns_404(client: Client) -> None:
    client.post(
        "/products/",
        data=json.dumps(
            {"product_id": "p1", "name": "Widget", "price": 9.99, "stock": 10}
        ),
        content_type="application/json",
    )

    response = client.post("/products/p1/undo/")

    assert response.status_code == 404


def test_product_history_lists_all_snapshots(client: Client) -> None:
    client.post(
        "/products/",
        data=json.dumps(
            {"product_id": "p1", "name": "Widget", "price": 9.99, "stock": 10}
        ),
        content_type="application/json",
    )
    client.put(
        "/products/p1/",
        data=json.dumps({"name": "Widget v2", "price": 12.0, "stock": 5}),
        content_type="application/json",
    )

    response = client.get("/products/p1/history/")

    body = response.json()
    assert response.status_code == 200
    assert [item["version"] for item in body] == [1, 2]
