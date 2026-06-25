"""Unit tests for the `filesystem.app` module's lazy `app` attribute (PEP 562)."""

from __future__ import annotations

import pytest
from moto import mock_aws

import filesystem.app as app_module
from filesystem.infrastructure import s3_client as s3_client_module


class TestLazyAppAttribute:
    def test_accessing_app_builds_flask_instance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # moto's mock_aws() intercepts boto3's real AWS endpoints, not a
        # custom LocalStack URL. Point the module's AWS_ENDPOINT constant
        # at the standard AWS endpoint so the default S3StorageClient()
        # built lazily by `app` is caught by the moto mock.
        monkeypatch.setattr(s3_client_module, "AWS_ENDPOINT", None)

        with mock_aws():
            built_app = app_module.app

        assert built_app is not None
        assert built_app.name == "filesystem.app"

    def test_accessing_unknown_attribute_raises_attribute_error(self) -> None:
        with pytest.raises(AttributeError, match="no attribute 'missing_thing'"):
            app_module.__getattr__("missing_thing")
