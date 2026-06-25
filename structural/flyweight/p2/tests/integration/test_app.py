"""Integration tests for the Flask app (main.py) using the test client.

main.py wires a real S3ImageStorage at import time, so AWS must be mocked
*before* the module is imported — fixture uses importlib to control ordering.
"""

from __future__ import annotations

import importlib
import io
from collections.abc import Iterator

import pytest
from flask.testing import FlaskClient
from moto import mock_aws
from PIL import Image


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    with mock_aws():
        import main as main_module

        importlib.reload(main_module)
        main_module.app.testing = True
        with main_module.app.test_client() as test_client:
            yield test_client


def _upload_sample_image(client: FlaskClient, key: str) -> None:
    import main as main_module

    buf = io.BytesIO()
    Image.new("RGB", (400, 400), color=(50, 60, 70)).save(buf, format="JPEG")
    main_module._storage.upload(key, buf.getvalue(), content_type="image/jpeg")


def test_list_specs_returns_named_flyweights(client: FlaskClient) -> None:
    response = client.get("/specs")

    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] >= 6
    assert "thumb_sm" in body["specs"]


def test_generate_thumbnail_missing_fields_returns_400(client: FlaskClient) -> None:
    response = client.post("/thumbnails/generate", json={})

    assert response.status_code == 400


def test_generate_thumbnail_unknown_spec_returns_404(client: FlaskClient) -> None:
    _upload_sample_image(client, "photo.jpg")

    response = client.post(
        "/thumbnails/generate",
        json={"image_key": "photo.jpg", "spec_name": "does_not_exist"},
    )

    assert response.status_code == 404


def test_generate_thumbnail_missing_image_returns_404(client: FlaskClient) -> None:
    response = client.post(
        "/thumbnails/generate",
        json={"image_key": "never_uploaded.jpg", "spec_name": "thumb_sm"},
    )

    assert response.status_code == 404


def test_generate_then_get_thumbnail_full_flow(client: FlaskClient) -> None:
    _upload_sample_image(client, "flow.jpg")

    generate_response = client.post(
        "/thumbnails/generate",
        json={"image_key": "flow.jpg", "spec_name": "avatar"},
    )
    assert generate_response.status_code == 201
    generated = generate_response.get_json()
    assert generated["image_key"] == "flow.jpg"

    get_response = client.get("/thumbnails/flow.jpg/avatar")
    assert get_response.status_code == 200
    fetched = get_response.get_json()
    assert fetched["flyweight_id"] == generated["flyweight_id"]


def test_get_thumbnail_unknown_spec_returns_404(client: FlaskClient) -> None:
    response = client.get("/thumbnails/flow.jpg/does_not_exist")

    assert response.status_code == 404


def test_get_thumbnail_not_generated_returns_404(client: FlaskClient) -> None:
    response = client.get("/thumbnails/never_generated.jpg/thumb_sm")

    assert response.status_code == 404


def test_factory_stats_reports_sharing_ratio(client: FlaskClient) -> None:
    _upload_sample_image(client, "stats_a.jpg")
    _upload_sample_image(client, "stats_b.jpg")
    client.post(
        "/thumbnails/generate",
        json={"image_key": "stats_a.jpg", "spec_name": "thumb_sm"},
    )
    client.post(
        "/thumbnails/generate",
        json={"image_key": "stats_b.jpg", "spec_name": "thumb_sm"},
    )

    response = client.get("/factory/stats")

    assert response.status_code == 200
    body = response.get_json()
    assert body["total_thumbnails"] >= 2
    assert "key_insight" in body
    assert "memory" in body
