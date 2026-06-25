"""Root conftest — ensures `src/` is importable before test collection."""

from __future__ import annotations

import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
