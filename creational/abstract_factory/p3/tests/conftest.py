"""Shared pytest fixtures for the Message Broker Factory test suite."""

from __future__ import annotations

import pytest

from broker_factory.infrastructure.factories import InMemoryBrokerFactory


@pytest.fixture
def in_memory_factory() -> InMemoryBrokerFactory:
    """A fresh in-memory broker factory — no external dependencies."""
    return InMemoryBrokerFactory(broker_name="in-memory")
