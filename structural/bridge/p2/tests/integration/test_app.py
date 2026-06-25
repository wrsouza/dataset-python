"""Integration tests for the Flask API — full request/response cycle."""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_endpoint(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_get_product_default_json(client: FlaskClient) -> None:
    response = client.get("/products/p-100")
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    body = response.get_json()
    assert body["data"]["name"] == "Mechanical Keyboard"


def test_get_product_html_format(client: FlaskClient) -> None:
    response = client.get("/products/p-100?format=html")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"Mechanical Keyboard" in response.data


def test_get_product_xml_format(client: FlaskClient) -> None:
    response = client.get("/products/p-100?format=xml")
    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert b"<title>Mechanical Keyboard</title>" in response.data


def test_get_product_not_found(client: FlaskClient) -> None:
    response = client.get("/products/does-not-exist")
    assert response.status_code == 404


def test_get_product_invalid_format(client: FlaskClient) -> None:
    response = client.get("/products/p-100?format=yaml")
    assert response.status_code == 400


def test_get_blog_post(client: FlaskClient) -> None:
    response = client.get("/blog/bridge-pattern-explained?format=html")
    assert response.status_code == 200
    assert b"The Bridge Pattern Explained" in response.data


def test_get_blog_post_not_found(client: FlaskClient) -> None:
    response = client.get("/blog/missing-slug")
    assert response.status_code == 404


def test_get_user_profile(client: FlaskClient) -> None:
    response = client.get("/users/u-1?format=html")
    assert response.status_code == 200
    assert b"janedoe" in response.data


def test_get_user_profile_not_found(client: FlaskClient) -> None:
    response = client.get("/users/missing-user")
    assert response.status_code == 404
