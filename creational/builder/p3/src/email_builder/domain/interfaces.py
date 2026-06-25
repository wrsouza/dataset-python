"""Abstract interfaces for the Email Builder pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, Self

from email_builder.domain.entities import Attachment, Email, SendResult


class EmailBuilder(ABC):
    """Builder interface for constructing transactional emails.

    OCP: new email types (PromoEmailBuilder, etc.) extend this ABC.
    """

    @abstractmethod
    def set_subject(self, subject: str) -> Self: ...

    @abstractmethod
    def set_from(self, address: str) -> Self: ...

    @abstractmethod
    def set_to(self, *addresses: str) -> Self: ...

    @abstractmethod
    def set_html_body(self, html: str) -> Self: ...

    @abstractmethod
    def set_text_body(self, text: str) -> Self: ...

    @abstractmethod
    def add_attachment(self, attachment: Attachment) -> Self: ...

    @abstractmethod
    def build(self) -> Email: ...


class EmailSender(Protocol):
    """Port — infrastructure implements this, use cases depend on it (DIP)."""

    def send(self, email: Email) -> SendResult: ...
