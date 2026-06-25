"""Receivers: the objects that know how to perform the actual work."""

from __future__ import annotations


class EmailReceiver:
    """Knows how to send an email. Stands in for a real SMTP/SES client."""

    def send(self, to: str, subject: str, body: str) -> str:
        return f"Email sent to {to} with subject '{subject}' ({len(body)} chars)"


class ReportReceiver:
    """Knows how to generate a report. Stands in for a real reporting engine."""

    def generate(self, report_type: str, parameters: dict[str, object]) -> str:
        return f"Report '{report_type}' generated with parameters {parameters}"
