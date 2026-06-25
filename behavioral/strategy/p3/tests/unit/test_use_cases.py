"""Unit tests for the Authentication Strategy use cases."""

from __future__ import annotations

import pytest
from django.contrib.auth.hashers import make_password

from auth_strategy.application.use_cases import (
    AuthenticateInput,
    AuthenticateUseCase,
    GetAuthAttemptsUseCase,
)
from auth_strategy.django_app.models import UserCredentialModel
from auth_strategy.domain.exceptions import InvalidStrategyError
from auth_strategy.infrastructure.repository import DjangoAuthAttemptLogRepository

pytestmark = pytest.mark.django_db


def test_authenticate_use_case_logs_successful_attempt() -> None:
    UserCredentialModel.objects.create(
        username="ana", password_hash=make_password("s3cret"), user_id="u1"
    )
    repository = DjangoAuthAttemptLogRepository()
    use_case = AuthenticateUseCase(repository)

    result = use_case.execute(
        AuthenticateInput(
            strategy_name="password",
            credentials={"username": "ana", "password": "s3cret"},
        )
    )

    assert result.success is True
    assert len(repository.list_all()) == 1


def test_authenticate_use_case_raises_for_unknown_strategy() -> None:
    use_case = AuthenticateUseCase(DjangoAuthAttemptLogRepository())

    with pytest.raises(InvalidStrategyError):
        use_case.execute(AuthenticateInput(strategy_name="unknown", credentials={}))


def test_get_auth_attempts_use_case_returns_all_logged_attempts() -> None:
    repository = DjangoAuthAttemptLogRepository()
    AuthenticateUseCase(repository).execute(
        AuthenticateInput(strategy_name="token", credentials={"token": "x"})
    )

    history = GetAuthAttemptsUseCase(repository).execute()

    assert len(history) == 1
