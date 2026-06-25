"""Shared pytest fixtures for the UI Component Factory test suite."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ui_factory.domain.entities import ComponentUsageLog
from ui_factory.infrastructure.factories import (
    LinuxUIFactory,
    MacUIFactory,
    WindowsUIFactory,
)


@pytest.fixture
def windows_factory() -> WindowsUIFactory:
    return WindowsUIFactory()


@pytest.fixture
def linux_factory() -> LinuxUIFactory:
    return LinuxUIFactory()


@pytest.fixture
def mac_factory() -> MacUIFactory:
    return MacUIFactory()


@pytest.fixture
def mock_log_repository() -> MagicMock:
    """Mock of the UsageLogRepository — isolates use cases from PostgreSQL."""
    repo = MagicMock()
    repo.save.side_effect = lambda log: log
    repo.find_all.return_value = [
        ComponentUsageLog(
            id=1,
            platform="windows",
            component_family=["button", "input", "modal"],
        )
    ]
    return repo
