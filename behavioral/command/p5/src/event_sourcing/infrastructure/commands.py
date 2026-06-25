"""Concrete commands: open account, deposit, withdraw."""

from __future__ import annotations

from event_sourcing.domain.entities import AccountState, DomainEvent, EventType
from event_sourcing.domain.exceptions import (
    AccountAlreadyOpenError,
    AccountNotOpenError,
    InsufficientFundsError,
    InvalidAmountError,
)
from event_sourcing.domain.interfaces import AccountCommand


class OpenAccountCommand(AccountCommand):
    """Encapsulates opening a new account."""

    def execute(self, state: AccountState) -> DomainEvent:
        if state.is_open:
            raise AccountAlreadyOpenError(f"Account {state.account_id} is already open")
        return DomainEvent.new(state.account_id, EventType.ACCOUNT_OPENED, {})


class DepositCommand(AccountCommand):
    """Encapsulates depositing funds into an open account."""

    def __init__(self, amount: float) -> None:
        self._amount = amount

    def execute(self, state: AccountState) -> DomainEvent:
        if not state.is_open:
            raise AccountNotOpenError(f"Account {state.account_id} is not open")
        if self._amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        return DomainEvent.new(
            state.account_id, EventType.FUNDS_DEPOSITED, {"amount": self._amount}
        )


class WithdrawCommand(AccountCommand):
    """Encapsulates withdrawing funds from an open account."""

    def __init__(self, amount: float) -> None:
        self._amount = amount

    def execute(self, state: AccountState) -> DomainEvent:
        if not state.is_open:
            raise AccountNotOpenError(f"Account {state.account_id} is not open")
        if self._amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if self._amount > state.balance:
            raise InsufficientFundsError(
                f"Cannot withdraw {self._amount}, balance is {state.balance}"
            )
        return DomainEvent.new(
            state.account_id, EventType.FUNDS_WITHDRAWN, {"amount": self._amount}
        )
