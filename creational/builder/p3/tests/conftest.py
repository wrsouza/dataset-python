"""Shared pytest fixtures for the Email Template Builder (Django)."""

from __future__ import annotations

import pytest
from django.test import Client


@pytest.fixture
def api_client() -> Client:
    return Client()
