"""Domain-level errors raised when a command is invalid against current state."""

from __future__ import annotations


class AccountAlreadyOpenError(ValueError):
    """Raised when trying to open an account that is already open."""


class AccountNotOpenError(ValueError):
    """Raised when trying to deposit/withdraw on an account that isn't open."""


class InsufficientFundsError(ValueError):
    """Raised when a withdrawal would take the balance below zero."""


class InvalidAmountError(ValueError):
    """Raised when a deposit/withdrawal amount is not strictly positive."""
