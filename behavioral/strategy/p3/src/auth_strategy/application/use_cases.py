"""Application use cases for the Authentication Strategy system.

Each use case has a single responsibility and depends only on
abstractions (DIP): the Authenticator context and the attempt-log
repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from auth_strategy.application.context import Authenticator
from auth_strategy.domain.entities import AuthResult
from auth_strategy.infrastructure.repository import DjangoAuthAttemptLogRepository
from auth_strategy.infrastructure.strategies.registry import get_strategy


@dataclass
class AuthenticateInput:
    strategy_name: str
    credentials: dict[str, Any]


class AuthenticateUseCase:
    def __init__(self, repository: DjangoAuthAttemptLogRepository) -> None:
        self._repository = repository

    def execute(self, data: AuthenticateInput) -> AuthResult:
        strategy = get_strategy(data.strategy_name)
        authenticator = Authenticator(strategy)
        result = authenticator.authenticate(data.credentials)
        self._repository.append(result)
        return result


class GetAuthAttemptsUseCase:
    def __init__(self, repository: DjangoAuthAttemptLogRepository) -> None:
        self._repository = repository

    def execute(self) -> list[AuthResult]:
        return self._repository.list_all()
