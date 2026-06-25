"""FastAPI application for the Event Sourcing account service.

Composition root: the only place that wires the concrete PostgreSQL
event store and Kafka publisher into the use cases.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from event_sourcing.application.use_cases import (
    DispatchCommandUseCase,
    GetAccountStateUseCase,
    GetEventHistoryUseCase,
)
from event_sourcing.domain.exceptions import (
    AccountAlreadyOpenError,
    AccountNotOpenError,
    InsufficientFundsError,
    InvalidAmountError,
)
from event_sourcing.domain.interfaces import EventPublisher, EventStore
from event_sourcing.infrastructure.commands import (
    DepositCommand,
    OpenAccountCommand,
    WithdrawCommand,
)
from event_sourcing.infrastructure.factory import build_event_store, build_publisher

app = FastAPI(
    title="Event Sourcing — Account Service",
    description=(
        "Command pattern: AccountCommand=open/deposit/withdraw, "
        "events persisted in PostgreSQL and published to Kafka, "
        "current state rebuilt by replaying the event log."
    ),
    version="1.0.0",
)

_event_store: EventStore | None = None
_publisher: EventPublisher | None = None


def get_event_store() -> EventStore:
    global _event_store
    if _event_store is None:
        _event_store = build_event_store()
    return _event_store


def get_publisher() -> EventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = build_publisher()
    return _publisher


class AmountRequest(BaseModel):
    amount: float


def _domain_error_to_http(exc: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@app.post("/accounts/{account_id}/open", status_code=201)
def open_account(
    account_id: str,
    event_store: Annotated[EventStore, Depends(get_event_store)],
    publisher: Annotated[EventPublisher, Depends(get_publisher)],
) -> dict[str, object]:
    use_case = DispatchCommandUseCase(event_store, publisher)
    try:
        event = use_case.execute(account_id, OpenAccountCommand())
    except AccountAlreadyOpenError as exc:
        raise _domain_error_to_http(exc) from exc
    return {"event_id": event.event_id, "event_type": event.event_type.value}


@app.post("/accounts/{account_id}/deposit", status_code=201)
def deposit(
    account_id: str,
    request: AmountRequest,
    event_store: Annotated[EventStore, Depends(get_event_store)],
    publisher: Annotated[EventPublisher, Depends(get_publisher)],
) -> dict[str, object]:
    use_case = DispatchCommandUseCase(event_store, publisher)
    try:
        event = use_case.execute(account_id, DepositCommand(request.amount))
    except (AccountNotOpenError, InvalidAmountError) as exc:
        raise _domain_error_to_http(exc) from exc
    return {"event_id": event.event_id, "event_type": event.event_type.value}


@app.post("/accounts/{account_id}/withdraw", status_code=201)
def withdraw(
    account_id: str,
    request: AmountRequest,
    event_store: Annotated[EventStore, Depends(get_event_store)],
    publisher: Annotated[EventPublisher, Depends(get_publisher)],
) -> dict[str, object]:
    use_case = DispatchCommandUseCase(event_store, publisher)
    try:
        event = use_case.execute(account_id, WithdrawCommand(request.amount))
    except (AccountNotOpenError, InvalidAmountError, InsufficientFundsError) as exc:
        raise _domain_error_to_http(exc) from exc
    return {"event_id": event.event_id, "event_type": event.event_type.value}


@app.get("/accounts/{account_id}")
def get_account_state(
    account_id: str,
    event_store: Annotated[EventStore, Depends(get_event_store)],
) -> dict[str, object]:
    use_case = GetAccountStateUseCase(event_store)
    state = use_case.execute(account_id)
    return {
        "account_id": state.account_id,
        "balance": state.balance,
        "is_open": state.is_open,
    }


@app.get("/accounts/{account_id}/events")
def get_account_events(
    account_id: str,
    event_store: Annotated[EventStore, Depends(get_event_store)],
) -> list[dict[str, object]]:
    use_case = GetEventHistoryUseCase(event_store)
    events = use_case.execute(account_id)
    return [
        {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "payload": event.payload,
            "occurred_at": event.occurred_at.isoformat(),
        }
        for event in events
    ]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
