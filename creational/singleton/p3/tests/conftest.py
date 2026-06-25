"""Shared pytest configuration for P3 feature_flags tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add src to path so imports work without installing the package.
src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
