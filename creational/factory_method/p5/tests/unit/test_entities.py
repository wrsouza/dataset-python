"""Unit tests for domain entities and exceptions."""

from __future__ import annotations

import pytest

from serializer.domain.entities import (
    DeserializationError,
    SerializationError,
    SerializationFormat,
    UnsupportedFormatError,
)


class TestSerializationFormat:
    def test_has_expected_members(self) -> None:
        assert {f.value for f in SerializationFormat} == {
            "json",
            "xml",
            "yaml",
            "csv",
        }

    def test_member_is_str_enum(self) -> None:
        assert SerializationFormat.JSON == "json"


class TestUnsupportedFormatError:
    def test_message_lists_available_formats(self) -> None:
        error = UnsupportedFormatError("toml")

        message = str(error)

        assert "toml" in message
        assert "json" in message
        assert "yaml" in message

    def test_is_exception_subclass(self) -> None:
        assert issubclass(UnsupportedFormatError, Exception)


class TestDomainExceptions:
    def test_serialization_error_can_be_raised(self) -> None:
        with pytest.raises(SerializationError, match="boom"):
            raise SerializationError("boom")

    def test_deserialization_error_can_be_raised(self) -> None:
        with pytest.raises(DeserializationError, match="bad data"):
            raise DeserializationError("bad data")
