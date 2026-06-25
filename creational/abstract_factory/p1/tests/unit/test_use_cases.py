"""Unit tests for the UI Component Factory use cases.

All external dependencies (PostgreSQL) are mocked.
Tests verify the pattern structure and SOLID principles are upheld.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ui_factory.application.use_cases import ListUsageLogsUseCase, RenderUIFamilyUseCase
from ui_factory.domain.entities import ComponentFamilyResponse, ComponentUsageLog
from ui_factory.infrastructure.factories import (
    LinuxUIFactory,
    MacUIFactory,
    WindowsUIFactory,
    get_factory_for_platform,
)


class TestWindowsUIFactory:
    """Tests for the WindowsUIFactory concrete factory."""

    def test_create_button_returns_fluent_design(
        self, windows_factory: WindowsUIFactory
    ) -> None:
        button = windows_factory.create_button()
        rendered = button.render()
        assert rendered["platform"] == "windows"
        assert rendered["style"] == "fluent-design"
        assert "accent_color" in rendered

    def test_create_input_returns_inline_error_validation(
        self, windows_factory: WindowsUIFactory
    ) -> None:
        input_field = windows_factory.create_input()
        assert input_field.get_validation_mode() == "inline-error"

    def test_create_modal_returns_slide_down_animation(
        self, windows_factory: WindowsUIFactory
    ) -> None:
        modal = windows_factory.create_modal()
        assert modal.get_animation() == "slide-down"

    def test_get_platform_name(self, windows_factory: WindowsUIFactory) -> None:
        assert windows_factory.get_platform_name() == "windows"

    def test_all_components_have_correct_platform_tag(
        self, windows_factory: WindowsUIFactory
    ) -> None:
        for component in [
            windows_factory.create_button(),
            windows_factory.create_input(),
            windows_factory.create_modal(),
        ]:
            assert component.render()["platform"] == "windows"


class TestLinuxUIFactory:
    """Tests for the LinuxUIFactory concrete factory."""

    def test_create_button_returns_gtk_adwaita(
        self, linux_factory: LinuxUIFactory
    ) -> None:
        button = linux_factory.create_button()
        rendered = button.render()
        assert rendered["platform"] == "linux"
        assert rendered["style"] == "gtk-adwaita"

    def test_create_input_returns_tooltip_validation(
        self, linux_factory: LinuxUIFactory
    ) -> None:
        assert linux_factory.create_input().get_validation_mode() == "tooltip"

    def test_create_modal_returns_fade_in_animation(
        self, linux_factory: LinuxUIFactory
    ) -> None:
        assert linux_factory.create_modal().get_animation() == "fade-in"

    def test_get_platform_name(self, linux_factory: LinuxUIFactory) -> None:
        assert linux_factory.get_platform_name() == "linux"


class TestMacUIFactory:
    """Tests for the MacUIFactory concrete factory."""

    def test_create_button_returns_aqua_style(
        self, mac_factory: MacUIFactory
    ) -> None:
        button = mac_factory.create_button()
        assert button.render()["style"] == "aqua"

    def test_create_input_returns_popover_validation(
        self, mac_factory: MacUIFactory
    ) -> None:
        assert mac_factory.create_input().get_validation_mode() == "popover"

    def test_create_modal_returns_sheet_drop_animation(
        self, mac_factory: MacUIFactory
    ) -> None:
        assert mac_factory.create_modal().get_animation() == "sheet-drop"

    def test_get_platform_name(self, mac_factory: MacUIFactory) -> None:
        assert mac_factory.get_platform_name() == "mac"


class TestRenderUIFamilyUseCase:
    """Tests for the Client (use case) that orchestrates the abstract factory."""

    def test_execute_returns_component_family_response(
        self,
        windows_factory: WindowsUIFactory,
        mock_log_repository: MagicMock,
    ) -> None:
        use_case = RenderUIFamilyUseCase(
            factory=windows_factory,
            log_repository=mock_log_repository,
        )
        result = use_case.execute()
        assert isinstance(result, ComponentFamilyResponse)

    def test_execute_saves_usage_log(
        self,
        linux_factory: LinuxUIFactory,
        mock_log_repository: MagicMock,
    ) -> None:
        use_case = RenderUIFamilyUseCase(
            factory=linux_factory,
            log_repository=mock_log_repository,
        )
        use_case.execute()
        mock_log_repository.save.assert_called_once()
        saved_log = mock_log_repository.save.call_args[0][0]
        assert saved_log.platform == "linux"
        assert "button" in saved_log.component_family

    def test_execute_produces_correct_platform_in_response(
        self,
        mac_factory: MacUIFactory,
        mock_log_repository: MagicMock,
    ) -> None:
        use_case = RenderUIFamilyUseCase(
            factory=mac_factory,
            log_repository=mock_log_repository,
        )
        result = use_case.execute()
        assert result.platform == "mac"
        assert result.button["platform"] == "mac"
        assert result.input["platform"] == "mac"
        assert result.modal["platform"] == "mac"

    def test_to_dict_has_all_component_keys(
        self,
        windows_factory: WindowsUIFactory,
        mock_log_repository: MagicMock,
    ) -> None:
        use_case = RenderUIFamilyUseCase(
            factory=windows_factory,
            log_repository=mock_log_repository,
        )
        result = use_case.execute().to_dict()
        assert "components" in result
        assert "button" in result["components"]
        assert "input" in result["components"]
        assert "modal" in result["components"]

    def test_use_case_works_with_any_factory_demonstrating_dip(
        self,
        mock_log_repository: MagicMock,
    ) -> None:
        """DIP: the use case works unchanged with any concrete factory."""
        for factory in [WindowsUIFactory(), LinuxUIFactory(), MacUIFactory()]:
            use_case = RenderUIFamilyUseCase(
                factory=factory,
                log_repository=mock_log_repository,
            )
            result = use_case.execute()
            assert result.platform == factory.get_platform_name()


class TestListUsageLogsUseCase:
    """Tests for the log listing use case."""

    def test_execute_returns_list_of_dicts(
        self, mock_log_repository: MagicMock
    ) -> None:
        use_case = ListUsageLogsUseCase(log_repository=mock_log_repository)
        result = use_case.execute()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["platform"] == "windows"

    def test_execute_calls_find_all(
        self, mock_log_repository: MagicMock
    ) -> None:
        use_case = ListUsageLogsUseCase(log_repository=mock_log_repository)
        use_case.execute()
        mock_log_repository.find_all.assert_called_once()


class TestGetFactoryForPlatform:
    """Tests for the factory registry / lookup function."""

    @pytest.mark.parametrize("platform", ["windows", "linux", "mac"])
    def test_returns_correct_factory_type(self, platform: str) -> None:
        factory = get_factory_for_platform(platform)
        assert factory.get_platform_name() == platform

    def test_case_insensitive_lookup(self) -> None:
        factory = get_factory_for_platform("WINDOWS")
        assert factory.get_platform_name() == "windows"

    def test_unsupported_platform_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unsupported platform"):
            get_factory_for_platform("dos")

    def test_ocp_factories_are_independent(self) -> None:
        """OCP: each factory is independent and does not affect the others."""
        win = get_factory_for_platform("windows")
        lnx = get_factory_for_platform("linux")
        assert win.create_button().render()["style"] != lnx.create_button().render()["style"]
