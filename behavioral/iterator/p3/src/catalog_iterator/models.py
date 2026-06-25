"""Django app models module — re-exports from the infrastructure layer.

Models live in infrastructure/models.py (persistence is an infrastructure
concern); this shim exists only because Django's app loading expects
`<app_label>.models` to be importable.
"""

from __future__ import annotations

from catalog_iterator.infrastructure.models import ProductModel

__all__ = ["ProductModel"]
