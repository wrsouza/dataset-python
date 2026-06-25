"""Application use cases for the UI Component Factory.

The Client role in the Abstract Factory pattern lives here.
Use cases depend on UIComponentFactory (abstraction) — never on concrete factories.
This demonstrates the Dependency Inversion Principle.
"""
from __future__ import annotations

from typing import Protocol

from ui_factory.domain.entities import ComponentFamilyResponse, ComponentUsageLog
from ui_factory.domain.interfaces import UIComponentFactory


class UsageLogRepository(Protocol):
    """Port (interface) for persisting component usage logs.

    Decouples use cases from the database implementation.
    """

    def save(self, log: ComponentUsageLog) -> ComponentUsageLog:
        """Persist a usage log and return it with the assigned id."""
        ...

    def find_all(self) -> list[ComponentUsageLog]:
        """Return all persisted usage logs ordered by requested_at desc."""
        ...


class RenderUIFamilyUseCase:
    """Client that uses UIComponentFactory to render a full component family.

    DIP: receives factory via constructor — does not import any concrete class.
    SRP: single responsibility — render components and log usage.
    """

    def __init__(
        self,
        factory: UIComponentFactory,
        log_repository: UsageLogRepository,
    ) -> None:
        self._factory = factory
        self._log_repository = log_repository

    def execute(self) -> ComponentFamilyResponse:
        """Render all three components and persist the usage log.

        Returns a ComponentFamilyResponse with rendered component data.
        """
        button = self._factory.create_button()
        input_field = self._factory.create_input()
        modal = self._factory.create_modal()

        platform = self._factory.get_platform_name()
        log = ComponentUsageLog(
            platform=platform,
            component_family=["button", "input", "modal"],
        )
        self._log_repository.save(log)

        return ComponentFamilyResponse(
            platform=platform,
            button=button.render(),
            input=input_field.render(),
            modal=modal.render(),
        )


class ListUsageLogsUseCase:
    """Retrieve all component usage logs from the repository.

    SRP: only retrieves logs — no rendering logic here.
    """

    def __init__(self, log_repository: UsageLogRepository) -> None:
        self._log_repository = log_repository

    def execute(self) -> list[dict[str, object]]:
        """Return serialized usage logs for all past requests."""
        logs = self._log_repository.find_all()
        return [log.to_dict() for log in logs]
