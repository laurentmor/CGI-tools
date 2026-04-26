# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
HISTMessagesGenerator package

Re-export public API so users can do:

    import hist_messages_generator as hmg
    hmg.HISTMessagesGenerator(...)

Also prevents RuntimeWarning when running:
    python -m hist_messages_generator.hist_messages_generator
"""

from __future__ import annotations

import pathlib as _pl
import sys as _sys
import types as _types

# --------------------------------------------------
# 🧠 runpy guard (CRUCIAL)
# --------------------------------------------------
_argv0_stem = _pl.Path(_sys.argv[0]).stem if _sys.argv else ""
_is_script = _argv0_stem in {
    "hist_messages_generator",
    "HISTMessagesGenerator",
}

# --------------------------------------------------
# 📦 Safe import (skip when run as script)
# --------------------------------------------------
if not _is_script:
    try:
        from .hist_messages_generator import (
            ET,
            HISTMessagesGenerator,
            InstrumentIndex,
            logging,
            main,
            time,
        )

        # optional internal imports (if needed externally)
        try:
            from .logging_decorators import log_exceptions
        except ImportError:
            log_exceptions = _types.ModuleType("log_exceptions")

        __all__ = [
            "HISTMessagesGenerator",
            "InstrumentIndex",
            "main",
            "log_exceptions",
            # exposed modules (useful for tests / patching)
            "ET",
            "time",
            "logging",
        ]

    except Exception as _e:
        # ------------------------------------------
        # 💣 Fail-safe: avoid breaking import
        # ------------------------------------------
        HISTMessagesGenerator = None  # type: ignore
        InstrumentIndex = None  # type: ignore
        main = None  # type: ignore

        __all__ = []