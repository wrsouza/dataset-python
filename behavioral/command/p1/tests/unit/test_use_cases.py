"""Unit tests for HistoryInvoker using mocked DocumentCommand objects."""

from __future__ import annotations

from unittest.mock import MagicMock

from document_editor.application.use_cases import HistoryInvoker
from document_editor.domain.entities import CommandResult
from document_editor.domain.interfaces import DocumentCommand


def _make_mock_command(description: str = "mock command") -> MagicMock:
    command = MagicMock(spec=DocumentCommand)
    command.execute.return_value = CommandResult(
        success=True, message="executed", content_snapshot="snapshot"
    )
    command.undo.return_value = CommandResult(
        success=True, message="undone", content_snapshot="snapshot"
    )
    command.get_description.return_value = description
    command.is_reversible.return_value = True
    return command


class TestHistoryInvoker:
    def test_execute_runs_command_and_records_history(self) -> None:
        invoker = HistoryInvoker()
        command = _make_mock_command("insert x")

        result = invoker.execute(command)

        command.execute.assert_called_once()
        assert result.message == "executed"
        history = invoker.get_history()
        assert len(history) == 1
        assert history[0].description == "insert x"

    def test_undo_calls_command_undo_and_moves_to_redo_stack(self) -> None:
        invoker = HistoryInvoker()
        command = _make_mock_command()
        invoker.execute(command)

        result = invoker.undo()

        command.undo.assert_called_once()
        assert result is not None
        assert result.message == "undone"
        assert invoker.get_history() == []

    def test_undo_on_empty_history_returns_none(self) -> None:
        invoker = HistoryInvoker()

        assert invoker.undo() is None

    def test_redo_reexecutes_undone_command(self) -> None:
        invoker = HistoryInvoker()
        command = _make_mock_command()
        invoker.execute(command)
        invoker.undo()

        result = invoker.redo()

        assert command.execute.call_count == 2
        assert result is not None
        assert len(invoker.get_history()) == 1

    def test_redo_on_empty_redo_stack_returns_none(self) -> None:
        invoker = HistoryInvoker()

        assert invoker.redo() is None

    def test_new_execute_after_undo_clears_redo_stack(self) -> None:
        invoker = HistoryInvoker()
        first = _make_mock_command("first")
        second = _make_mock_command("second")
        invoker.execute(first)
        invoker.undo()

        invoker.execute(second)

        assert invoker.redo() is None

    def test_clear_empties_both_stacks(self) -> None:
        invoker = HistoryInvoker()
        invoker.execute(_make_mock_command())

        invoker.clear()

        assert invoker.get_history() == []
        assert invoker.undo() is None
