# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Root-level conftest.py — sys.path bootstrap only.

pytest loads this before any test module is imported, making it the only
safe place to set up sys.path.

Layout
------
HISTMessagesGenerator/        ← project root (this file lives here)
    src/
        hist_messages_generator/   ← importable package
    tests/
        fixtures.py               ← shared XML helpers
        conftest.py               ← pytest fixtures
        test_*.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.resolve()
_SRC = _ROOT / "src"
_TESTS = _ROOT / "tests"

for _p in (_SRC, _TESTS, _ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
