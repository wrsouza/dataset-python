"""Unit tests for document prototypes."""
from __future__ import annotations

import copy

import pytest

from documents.infrastructure.prototypes import (
    ContractDocument,
    FormDocument,
    ReportDocument,
    get_template_by_type,
)


class TestContractDocument:
    def test_clone_replaces_placeholders(self) -> None:
        contract = ContractDocument()
        cloned = contract.clone({"client_name": "Acme Corp", "contract_date": "2024-01-01"})
        assert "Acme Corp" in cloned.content
        assert "{{client_name}}" not in cloned.content

    def test_clone_does_not_modify_original(self) -> None:
        contract = ContractDocument()
        original_content = contract.content
        contract.clone({"client_name": "Modified"})
        assert contract.content == original_content

    def test_clone_is_independent(self) -> None:
        contract = ContractDocument()
        clone1 = contract.clone({"client_name": "Client A"})
        clone2 = contract.clone({"client_name": "Client B"})
        assert "Client A" in clone1.content
        assert "Client B" in clone2.content
        assert "Client A" not in clone2.content

    def test_doc_type_is_contract(self) -> None:
        assert ContractDocument().doc_type == "contract"

    def test_title_substitution(self) -> None:
        contract = ContractDocument()
        cloned = contract.clone({"client_name": "TechCorp"})
        assert "TechCorp" in cloned.title


class TestReportDocument:
    def test_clone_replaces_author(self) -> None:
        report = ReportDocument()
        cloned = report.clone({"author": "John Doe", "report_title": "Q4 Report"})
        assert "John Doe" in cloned.content
        assert "Q4 Report" in cloned.title

    def test_doc_type_is_report(self) -> None:
        assert ReportDocument().doc_type == "report"


class TestFormDocument:
    def test_clone_replaces_applicant(self) -> None:
        form = FormDocument()
        cloned = form.clone({"applicant_name": "Jane Doe", "form_title": "Registration"})
        assert "Jane Doe" in cloned.content

    def test_empty_substitutions_preserves_placeholders(self) -> None:
        form = FormDocument()
        cloned = form.clone({})
        assert "{{applicant_name}}" in cloned.content


class TestGetTemplateByType:
    def test_returns_contract_prototype(self) -> None:
        proto = get_template_by_type("contract")
        assert proto.doc_type == "contract"

    def test_returns_report_prototype(self) -> None:
        proto = get_template_by_type("report")
        assert proto.doc_type == "report"

    def test_returns_form_prototype(self) -> None:
        proto = get_template_by_type("form")
        assert proto.doc_type == "form"

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown document type"):
            get_template_by_type("invoice")


class TestDeepCopyVsClone:
    def test_deepcopy_creates_independent_metadata(self) -> None:
        """Demonstrates why deepcopy is required for nested dicts."""
        contract = ContractDocument()
        # deepcopy: metadata dict is independent
        deep = copy.deepcopy(contract)
        deep._metadata["jurisdiction"] = "Brazil"
        # Original metadata must remain unchanged
        assert "{{jurisdiction}}" in contract.metadata.get("jurisdiction", "")

    def test_clone_returns_correct_type(self) -> None:
        contract = ContractDocument()
        cloned = contract.clone({})
        assert isinstance(cloned, ContractDocument)
