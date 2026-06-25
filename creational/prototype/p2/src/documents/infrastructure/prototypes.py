"""Concrete Document Prototype implementations.

Each ConcretePrototype knows its structure and how to clone itself
with placeholder substitutions applied to content and metadata.
"""
from __future__ import annotations

import copy
import re
from typing import Any


class BaseDocument:
    """Base implementation for all document prototypes.

    Demonstrates substitution-aware cloning:
    copy.deepcopy creates a structural copy, then substitutions are applied
    to the cloned content — original template content remains unchanged.
    """

    def __init__(
        self,
        doc_type: str,
        title: str,
        content: str,
        metadata: dict[str, str],
    ) -> None:
        self._doc_type = doc_type
        self._title = title
        self._content = content
        self._metadata = dict(metadata)

    @property
    def doc_type(self) -> str:
        return self._doc_type

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content

    @property
    def metadata(self) -> dict[str, str]:
        return dict(self._metadata)

    def clone(self, substitutions: dict[str, str]) -> BaseDocument:
        """Clone this document and apply substitutions.

        Uses copy.deepcopy to ensure the clone is fully independent,
        then applies placeholder substitutions to content and title.
        The original template is never modified.
        """
        cloned = copy.deepcopy(self)
        cloned._apply_substitutions(substitutions)
        return cloned

    def _apply_substitutions(self, substitutions: dict[str, str]) -> None:
        """Replace {{key}} placeholders with provided values in-place."""
        for placeholder, value in substitutions.items():
            # Normalize: accept both "key" and "{{key}}" format
            key = placeholder if placeholder.startswith("{{") else f"{{{{{placeholder}}}}}"
            self._content = self._content.replace(key, value)
            self._title = self._title.replace(key, value)
            self._metadata = {
                k: v.replace(key, value) for k, v in self._metadata.items()
            }

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for MongoDB storage."""
        return {
            "doc_type": self._doc_type,
            "title": self._title,
            "content": self._content,
            "metadata": self._metadata,
        }

    def get_placeholders(self) -> list[str]:
        """Extract all {{placeholder}} keys from content for discovery."""
        return re.findall(r"\{\{(\w+)\}\}", self._content)


class ContractDocument(BaseDocument):
    """ConcretePrototype for contract documents.

    Contracts have legal clauses with client/party placeholders.
    """

    def __init__(self) -> None:
        super().__init__(
            doc_type="contract",
            title="Service Contract — {{client_name}}",
            content=(
                "CONTRACT AGREEMENT\n\n"
                "This agreement is entered into between {{company_name}} "
                "(hereinafter 'Provider') and {{client_name}} "
                "(hereinafter 'Client') on {{contract_date}}.\n\n"
                "SERVICES:\n{{services_description}}\n\n"
                "PAYMENT TERMS:\n"
                "The Client agrees to pay {{payment_amount}} due on {{payment_due_date}}.\n\n"
                "DURATION:\nThis contract is valid from {{start_date}} to {{end_date}}.\n\n"
                "Signed by: {{signer_name}}\nDate: {{signed_date}}"
            ),
            metadata={
                "document_version": "1.0",
                "jurisdiction": "{{jurisdiction}}",
                "currency": "{{currency}}",
            },
        )

    def clone(self, substitutions: dict[str, str]) -> ContractDocument:
        """Clone contract with deep copy, preserving legal structure."""
        cloned = copy.deepcopy(self)
        cloned._apply_substitutions(substitutions)
        return cloned


class ReportDocument(BaseDocument):
    """ConcretePrototype for analytical report documents."""

    def __init__(self) -> None:
        super().__init__(
            doc_type="report",
            title="{{report_title}} — {{period}}",
            content=(
                "EXECUTIVE REPORT\n\n"
                "Report: {{report_title}}\n"
                "Period: {{period}}\n"
                "Prepared by: {{author}}\n"
                "Department: {{department}}\n\n"
                "EXECUTIVE SUMMARY:\n{{summary}}\n\n"
                "KEY FINDINGS:\n{{findings}}\n\n"
                "RECOMMENDATIONS:\n{{recommendations}}\n\n"
                "Data Source: {{data_source}}\n"
                "Generated: {{generated_date}}"
            ),
            metadata={
                "confidentiality": "{{confidentiality_level}}",
                "distribution": "{{distribution_list}}",
            },
        )

    def clone(self, substitutions: dict[str, str]) -> ReportDocument:
        """Clone report with independent content block."""
        cloned = copy.deepcopy(self)
        cloned._apply_substitutions(substitutions)
        return cloned


class FormDocument(BaseDocument):
    """ConcretePrototype for fillable form documents."""

    def __init__(self) -> None:
        super().__init__(
            doc_type="form",
            title="{{form_title}} Form",
            content=(
                "FORM: {{form_title}}\n\n"
                "Applicant Name: {{applicant_name}}\n"
                "Date of Birth: {{date_of_birth}}\n"
                "Email: {{email}}\n"
                "Phone: {{phone}}\n\n"
                "Request Details:\n{{request_details}}\n\n"
                "Submission Date: {{submission_date}}\n"
                "Reference Number: {{reference_number}}\n\n"
                "Authorized by: {{authorizer_name}}"
            ),
            metadata={
                "form_version": "{{form_version}}",
                "department": "{{department}}",
            },
        )

    def clone(self, substitutions: dict[str, str]) -> FormDocument:
        """Clone form, ensuring each instance has independent field values."""
        cloned = copy.deepcopy(self)
        cloned._apply_substitutions(substitutions)
        return cloned


def get_template_by_type(doc_type: str) -> BaseDocument:
    """Factory function: return the prototype for a given document type.

    OCP: adding a new type means adding a new class and a mapping entry,
    not modifying existing code.
    """
    templates: dict[str, BaseDocument] = {
        "contract": ContractDocument(),
        "report": ReportDocument(),
        "form": FormDocument(),
    }
    if doc_type not in templates:
        raise ValueError(f"Unknown document type: '{doc_type}'")
    return templates[doc_type]
