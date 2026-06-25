"""Abstractions for the Mediator pattern: Mediator and Colleague (Participant)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from chat_room.domain.entities import ChatMessage


class ChatParticipant(ABC):
    """A Colleague: a single client connected to the chat room.

    Never talks to other participants directly — only ever sends through
    the mediator and receives messages the mediator routes to it.
    """

    @abstractmethod
    def get_participant_id(self) -> str:
        """Return this participant's stable identifier."""

    @abstractmethod
    async def receive(self, message: ChatMessage) -> None:
        """Deliver a message routed by the mediator to this participant."""


class ChatMediator(ABC):
    """The Mediator: coordinates message delivery between participants.

    Participants register/unregister with the mediator and never hold a
    reference to each other — all communication is routed here.
    """

    @abstractmethod
    def register(self, participant: ChatParticipant) -> None:
        """Add a participant to the room."""

    @abstractmethod
    def unregister(self, participant: ChatParticipant) -> None:
        """Remove a participant from the room."""

    @abstractmethod
    async def send(self, sender_id: str, text: str) -> None:
        """Route a message from `sender_id` to every other registered participant."""

    @abstractmethod
    async def start_listening(self) -> None:
        """Start dispatching incoming messages to locally registered participants."""

    @abstractmethod
    async def stop_listening(self) -> None:
        """Stop dispatching incoming messages."""
