"""Use cases orchestrating joining, leaving, and sending chat messages."""

from __future__ import annotations

from chat_room.domain.interfaces import ChatMediator, ChatParticipant


class JoinRoomUseCase:
    """Registers a participant with the room's mediator."""

    def __init__(self, mediator: ChatMediator) -> None:
        self._mediator = mediator

    def execute(self, participant: ChatParticipant) -> None:
        self._mediator.register(participant)


class LeaveRoomUseCase:
    """Unregisters a participant from the room's mediator."""

    def __init__(self, mediator: ChatMediator) -> None:
        self._mediator = mediator

    def execute(self, participant: ChatParticipant) -> None:
        self._mediator.unregister(participant)


class SendMessageUseCase:
    """Sends a chat message through the mediator, on behalf of one participant."""

    def __init__(self, mediator: ChatMediator) -> None:
        self._mediator = mediator

    async def execute(self, sender_id: str, text: str) -> None:
        await self._mediator.send(sender_id, text)
