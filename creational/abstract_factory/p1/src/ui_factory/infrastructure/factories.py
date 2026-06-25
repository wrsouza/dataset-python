"""Concrete Factories and Concrete Products for the UI Component Factory pattern.

Each platform (Windows, Linux, Mac) has its own factory that creates
components with platform-appropriate styles and behaviours.

OCP: adding a new platform requires only a new factory class in this file
     (or a new file) — no existing code is modified.
"""
from __future__ import annotations

import os

import psycopg2
from psycopg2.extras import RealDictCursor

from ui_factory.domain.entities import ComponentUsageLog
from ui_factory.domain.interfaces import UIComponentFactory


# ── Windows Concrete Products ──────────────────────────────────────────────────

class WindowsButton:
    """ConcreteProduct: Windows-style Button using Fluent Design language."""

    def render(self) -> dict[str, str]:
        return {
            "type": "button",
            "platform": "windows",
            "style": self.get_style(),
            "border_radius": "2px",
            "font_family": "Segoe UI",
            "accent_color": "#0078D4",
            "hover_effect": "color_shift",
        }

    def get_style(self) -> str:
        return "fluent-design"


class WindowsInput:
    """ConcreteProduct: Windows-style Input using Fluent Design language."""

    def render(self) -> dict[str, str]:
        return {
            "type": "input",
            "platform": "windows",
            "style": "fluent-design",
            "border_bottom_only": "true",
            "font_family": "Segoe UI",
            "validation_mode": self.get_validation_mode(),
        }

    def get_validation_mode(self) -> str:
        return "inline-error"


class WindowsModal:
    """ConcreteProduct: Windows-style Modal dialog."""

    def render(self) -> dict[str, str]:
        return {
            "type": "modal",
            "platform": "windows",
            "style": "fluent-design",
            "animation": self.get_animation(),
            "backdrop": "blur",
            "border_radius": "4px",
            "shadow": "depth-64",
        }

    def get_animation(self) -> str:
        return "slide-down"


# ── Linux Concrete Products ────────────────────────────────────────────────────

class LinuxButton:
    """ConcreteProduct: Linux GTK-style Button."""

    def render(self) -> dict[str, str]:
        return {
            "type": "button",
            "platform": "linux",
            "style": self.get_style(),
            "border_radius": "6px",
            "font_family": "Ubuntu, sans-serif",
            "accent_color": "#E95420",
            "hover_effect": "opacity",
        }

    def get_style(self) -> str:
        return "gtk-adwaita"


class LinuxInput:
    """ConcreteProduct: Linux GTK-style Input."""

    def render(self) -> dict[str, str]:
        return {
            "type": "input",
            "platform": "linux",
            "style": "gtk-adwaita",
            "border": "1px solid #ccc",
            "font_family": "Ubuntu, sans-serif",
            "validation_mode": self.get_validation_mode(),
        }

    def get_validation_mode(self) -> str:
        return "tooltip"


class LinuxModal:
    """ConcreteProduct: Linux GTK-style Modal dialog."""

    def render(self) -> dict[str, str]:
        return {
            "type": "modal",
            "platform": "linux",
            "style": "gtk-adwaita",
            "animation": self.get_animation(),
            "backdrop": "dim",
            "border_radius": "8px",
            "shadow": "box-shadow-md",
        }

    def get_animation(self) -> str:
        return "fade-in"


# ── Mac Concrete Products ──────────────────────────────────────────────────────

class MacButton:
    """ConcreteProduct: macOS Aqua-style Button."""

    def render(self) -> dict[str, str]:
        return {
            "type": "button",
            "platform": "mac",
            "style": self.get_style(),
            "border_radius": "6px",
            "font_family": "SF Pro Display",
            "accent_color": "#007AFF",
            "hover_effect": "brightness",
        }

    def get_style(self) -> str:
        return "aqua"


class MacInput:
    """ConcreteProduct: macOS Aqua-style Input."""

    def render(self) -> dict[str, str]:
        return {
            "type": "input",
            "platform": "mac",
            "style": "aqua",
            "border": "1px solid #d1d1d6",
            "font_family": "SF Pro Text",
            "validation_mode": self.get_validation_mode(),
        }

    def get_validation_mode(self) -> str:
        return "popover"


class MacModal:
    """ConcreteProduct: macOS sheet-style Modal dialog."""

    def render(self) -> dict[str, str]:
        return {
            "type": "modal",
            "platform": "mac",
            "style": "aqua",
            "animation": self.get_animation(),
            "backdrop": "vibrancy",
            "border_radius": "10px",
            "shadow": "mac-shadow",
        }

    def get_animation(self) -> str:
        return "sheet-drop"


# ── Concrete Factories ─────────────────────────────────────────────────────────

class WindowsUIFactory(UIComponentFactory):
    """ConcreteFactory: creates the Windows (Fluent Design) component family."""

    def create_button(self) -> WindowsButton:
        return WindowsButton()

    def create_input(self) -> WindowsInput:
        return WindowsInput()

    def create_modal(self) -> WindowsModal:
        return WindowsModal()

    def get_platform_name(self) -> str:
        return "windows"


class LinuxUIFactory(UIComponentFactory):
    """ConcreteFactory: creates the Linux (GTK/Adwaita) component family."""

    def create_button(self) -> LinuxButton:
        return LinuxButton()

    def create_input(self) -> LinuxInput:
        return LinuxInput()

    def create_modal(self) -> LinuxModal:
        return LinuxModal()

    def get_platform_name(self) -> str:
        return "linux"


class MacUIFactory(UIComponentFactory):
    """ConcreteFactory: creates the macOS (Aqua) component family."""

    def create_button(self) -> MacButton:
        return MacButton()

    def create_input(self) -> MacInput:
        return MacInput()

    def create_modal(self) -> MacModal:
        return MacModal()

    def get_platform_name(self) -> str:
        return "mac"


# ── Factory Registry ───────────────────────────────────────────────────────────

PLATFORM_FACTORIES: dict[str, UIComponentFactory] = {
    "windows": WindowsUIFactory(),
    "linux": LinuxUIFactory(),
    "mac": MacUIFactory(),
}


def get_factory_for_platform(platform: str) -> UIComponentFactory:
    """Return the appropriate UIComponentFactory for the given platform name.

    OCP: to support a new platform, register it in PLATFORM_FACTORIES.
    No conditional logic is scattered across the codebase.
    """
    factory = PLATFORM_FACTORIES.get(platform.lower())
    if factory is None:
        supported = ", ".join(PLATFORM_FACTORIES.keys())
        raise ValueError(f"Unsupported platform '{platform}'. Supported: {supported}")
    return factory


# ── PostgreSQL Repository ──────────────────────────────────────────────────────

class PostgreSQLUsageLogRepository:
    """Infrastructure: persists ComponentUsageLogs in PostgreSQL.

    SRP: only handles persistence — no business logic.
    DIP: the use case depends on UsageLogRepository (Protocol), not this class.
    """

    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS component_usage_logs (
            id SERIAL PRIMARY KEY,
            platform VARCHAR(50) NOT NULL,
            component_family TEXT[] NOT NULL,
            requested_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """

    INSERT_SQL = """
        INSERT INTO component_usage_logs (platform, component_family, requested_at)
        VALUES (%s, %s, %s)
        RETURNING id
    """

    SELECT_ALL_SQL = """
        SELECT id, platform, component_family, requested_at
        FROM component_usage_logs
        ORDER BY requested_at DESC
    """

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._ensure_table_exists()

    def _get_connection(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(self._database_url)

    def _ensure_table_exists(self) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(self.CREATE_TABLE_SQL)

    def save(self, log: ComponentUsageLog) -> ComponentUsageLog:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    self.INSERT_SQL,
                    (log.platform, log.component_family, log.requested_at),
                )
                row = cur.fetchone()
                log.id = row[0]
        return log

    def find_all(self) -> list[ComponentUsageLog]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(self.SELECT_ALL_SQL)
                rows = cur.fetchall()

        return [
            ComponentUsageLog(
                id=row["id"],
                platform=row["platform"],
                component_family=list(row["component_family"]),
                requested_at=row["requested_at"],
            )
            for row in rows
        ]
