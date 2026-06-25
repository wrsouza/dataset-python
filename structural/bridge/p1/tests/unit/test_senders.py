"""Unit tests for concrete sender implementations (non-SES ones)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from notifications.domain.entities import Channel, DeliveryStatus
from notifications.infrastructure.implementations import (
    EmailSender,
    PushSender,
    SMSSender,
)


class TestSMSSender:
    def test_deliver_returns_sent_status(self) -> None:
        sender = SMSSender()
        result = sender.deliver(
            to="+5511999990000",
            subject="Alert",
            body="Disk is full",
        )
        assert result.status == DeliveryStatus.SENT
        assert result.channel == Channel.SMS
        assert result.message_id.startswith("sms-")

    def test_each_delivery_has_unique_message_id(self) -> None:
        sender = SMSSender()
        r1 = sender.deliver(to="+1", subject="s", body="b")
        r2 = sender.deliver(to="+2", subject="s", body="b")
        assert r1.message_id != r2.message_id


class TestPushSender:
    def test_deliver_returns_sent_status(self) -> None:
        sender = PushSender()
        result = sender.deliver(
            to="device-token-abc",
            subject="New Report",
            body="Your Q1 report is ready",
        )
        assert result.status == DeliveryStatus.SENT
        assert result.channel == Channel.PUSH
        assert result.message_id.startswith("push-")

    def test_each_delivery_has_unique_message_id(self) -> None:
        sender = PushSender()
        r1 = sender.deliver(to="t1", subject="s", body="b")
        r2 = sender.deliver(to="t2", subject="s", body="b")
        assert r1.message_id != r2.message_id


class TestEmailSender:
    def _make_mock_ses(self, message_id: str = "ses-test-123") -> MagicMock:
        mock = MagicMock()
        mock.send_email.return_value = {"MessageId": message_id}
        return mock

    def test_deliver_returns_sent_status(self) -> None:
        mock_ses = self._make_mock_ses()
        sender = EmailSender(
            sender_address="noreply@example.com",
            ses_client=mock_ses,
        )
        result = sender.deliver(
            to="user@example.com",
            subject="Hello",
            body="Body text",
        )
        assert result.status == DeliveryStatus.SENT
        assert result.message_id == "ses-test-123"
        assert result.channel == Channel.EMAIL

    def test_ses_send_email_called_with_correct_params(self) -> None:
        mock_ses = self._make_mock_ses()
        sender = EmailSender(
            sender_address="from@example.com",
            ses_client=mock_ses,
        )
        sender.deliver(to="to@example.com", subject="Sub", body="Body")

        mock_ses.send_email.assert_called_once()
        call_kwargs = mock_ses.send_email.call_args[1]
        assert call_kwargs["Source"] == "from@example.com"
        assert "to@example.com" in call_kwargs["Destination"]["ToAddresses"]

    def test_ses_client_error_returns_failed(self) -> None:
        from botocore.exceptions import ClientError

        mock_ses = MagicMock()
        mock_ses.send_email.side_effect = ClientError(
            {"Error": {"Code": "MessageRejected", "Message": "Email rejected"}},
            "SendEmail",
        )
        sender = EmailSender(sender_address="from@example.com", ses_client=mock_ses)
        result = sender.deliver(to="bad@example.com", subject="S", body="B")

        assert result.status == DeliveryStatus.FAILED
        assert result.error is not None
        assert not result.is_successful
