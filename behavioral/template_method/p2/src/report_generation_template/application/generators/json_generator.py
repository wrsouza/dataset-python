"""JSONReportGenerator — ConcreteClass rendering one JSON object per line."""

from __future__ import annotations

import json
from typing import Any

from report_generation_template.domain.interfaces import ReportGenerator


class JSONReportGenerator(ReportGenerator):
    def format_header(self, title: str) -> str:
        return json.dumps({"title": title})

    def format_row(self, row: dict[str, Any]) -> str:
        return json.dumps(row)

    def get_format_name(self) -> str:
        return "json"

    # ── Hook override ────────────────────────────────────────────────────────────

    def include_summary(self) -> bool:
        # JSON Lines output stays valid line-per-record without a trailing
        # human-readable summary line.
        return False
