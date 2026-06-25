"""Unit tests for application use cases, with a mocked PriceMonitor (DIP)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from price_alerts.application.use_cases import (
    ListPriceAlertsUseCase,
    ProcessPriceUpdateUseCase,
    RegisterPriceAlertUseCase,
    RemovePriceAlertUseCase,
)
from price_alerts.domain.entities import Subscription
from price_alerts.infrastructure.notification_observers import EmailAlertObserver


def test_register_use_case_rejects_empty_product_id() -> None:
    use_case = RegisterPriceAlertUseCase(monitor=MagicMock())
    observer = EmailAlertObserver(recipient_email="a@example.com")

    with pytest.raises(ValueError, match="product_id"):
        use_case.execute(observer, product_id="", threshold=5.0)


def test_register_use_case_rejects_non_positive_threshold() -> None:
    use_case = RegisterPriceAlertUseCase(monitor=MagicMock())
    observer = EmailAlertObserver(recipient_email="a@example.com")

    with pytest.raises(ValueError, match="threshold"):
        use_case.execute(observer, product_id="SKU-1", threshold=0.0)


def test_register_use_case_delegates_to_monitor() -> None:
    mock_monitor = MagicMock()
    mock_monitor.subscribe.return_value = "sub-123"
    use_case = RegisterPriceAlertUseCase(monitor=mock_monitor)
    observer = EmailAlertObserver(recipient_email="a@example.com")

    result = use_case.execute(observer, product_id="SKU-1", threshold=5.0)

    assert result == "sub-123"
    mock_monitor.subscribe.assert_called_once_with(observer, "SKU-1", 5.0)


def test_remove_use_case_delegates_to_monitor() -> None:
    mock_monitor = MagicMock()
    use_case = RemovePriceAlertUseCase(monitor=mock_monitor)

    use_case.execute("sub-123")

    mock_monitor.unsubscribe.assert_called_once_with("sub-123")


def test_list_use_case_returns_subscriptions() -> None:
    mock_monitor = MagicMock()
    sub = Subscription(
        subscription_id="sub-1",
        observer_id="email:a@example.com",
        product_id="SKU-1",
        threshold=5.0,
    )
    mock_monitor.subscriptions = {"sub-1": sub}
    use_case = ListPriceAlertsUseCase(monitor=mock_monitor)

    result = use_case.execute()

    assert result == [sub]


def test_process_price_update_delegates_to_monitor() -> None:
    mock_monitor = MagicMock()
    use_case = ProcessPriceUpdateUseCase(monitor=mock_monitor)

    use_case.execute(product_id="SKU-1", old_price=100.0, new_price=110.0)

    mock_monitor.notify_price_change.assert_called_once_with("SKU-1", 100.0, 110.0)
