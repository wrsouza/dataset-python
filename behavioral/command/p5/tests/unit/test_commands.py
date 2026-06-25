"""Unit tests for the concrete commands."""

from __future__ import annotations

import pytest

from event_sourcing.domain.entities import AccountState, EventType
from event_sourcing.domain.exceptions import (
    AccountAlreadyOpenError,
    AccountNotOpenError,
    InsufficientFundsError,
    InvalidAmountError,
)
from event_sourcing.infrastructure.commands import (
    DepositCommand,
    OpenAccountCommand,
    WithdrawCommand,
)


def test_open_account_command_succeeds_when_closed() -> None:
    state = AccountState(account_id="acc-1")

    event = OpenAccountCommand().execute(state)

    assert event.event_type == EventType.ACCOUNT_OPENED
    assert event.account_id == "acc-1"


def test_open_account_command_raises_when_already_open() -> None:
    state = AccountState(account_id="acc-1", is_open=True)

    with pytest.raises(AccountAlreadyOpenError):
        OpenAccountCommand().execute(state)


def test_deposit_command_succeeds_on_open_account() -> None:
    state = AccountState(account_id="acc-1", is_open=True, balance=10.0)

    event = DepositCommand(5.0).execute(state)

    assert event.event_type == EventType.FUNDS_DEPOSITED
    assert event.payload == {"amount": 5.0}


def test_deposit_command_raises_when_account_closed() -> None:
    state = AccountState(account_id="acc-1", is_open=False)

    with pytest.raises(AccountNotOpenError):
        DepositCommand(5.0).execute(state)


def test_deposit_command_raises_for_non_positive_amount() -> None:
    state = AccountState(account_id="acc-1", is_open=True)

    with pytest.raises(InvalidAmountError):
        DepositCommand(0.0).execute(state)


def test_withdraw_command_succeeds_when_funds_available() -> None:
    state = AccountState(account_id="acc-1", is_open=True, balance=10.0)

    event = WithdrawCommand(4.0).execute(state)

    assert event.event_type == EventType.FUNDS_WITHDRAWN
    assert event.payload == {"amount": 4.0}


def test_withdraw_command_raises_when_account_closed() -> None:
    state = AccountState(account_id="acc-1", is_open=False)

    with pytest.raises(AccountNotOpenError):
        WithdrawCommand(4.0).execute(state)


def test_withdraw_command_raises_for_non_positive_amount() -> None:
    state = AccountState(account_id="acc-1", is_open=True, balance=10.0)

    with pytest.raises(InvalidAmountError):
        WithdrawCommand(-1.0).execute(state)


def test_withdraw_command_raises_when_insufficient_funds() -> None:
    state = AccountState(account_id="acc-1", is_open=True, balance=3.0)

    with pytest.raises(InsufficientFundsError):
        WithdrawCommand(4.0).execute(state)
