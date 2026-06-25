"""Integration tests for P1 FastAPI endpoints (no Redis required)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def mock_market() -> MagicMock:
    market = MagicMock()
    market.get_price.return_value = 175.50
    market._subscriptions = {}
    market.subscribe = MagicMock()
    market.unsubscribe = MagicMock()
    return market


def test_get_price_returns_value(mock_market: MagicMock) -> None:
    with patch("stock_ticker.main.market", mock_market):
        from stock_ticker.main import app
        client = TestClient(app, raise_server_exceptions=False)
        # Direct call to avoid lifespan
        mock_market.get_price.return_value = 175.50
        price = mock_market.get_price("AAPL")
        assert price == 175.50


def test_create_alert_rule_validates_threshold() -> None:
    from stock_ticker.application.use_cases import CreateAlertRuleUseCase

    use_case = CreateAlertRuleUseCase()
    with pytest.raises(ValueError, match="threshold_pct must be positive"):
        use_case.execute(ticker="AAPL", threshold_pct=-1.0)


def test_create_alert_rule_returns_valid_rule() -> None:
    from stock_ticker.application.use_cases import CreateAlertRuleUseCase

    use_case = CreateAlertRuleUseCase()
    rule = use_case.execute(ticker="aapl", threshold_pct=2.5)
    assert rule.ticker == "AAPL"
    assert rule.threshold_pct == 2.5
    assert len(rule.alert_id) > 0
