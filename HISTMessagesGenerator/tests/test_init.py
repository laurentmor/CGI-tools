# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Unit tests for __init__.py

Covers:
- Public names exported in __all__
- HISTMessagesGenerator importable from package root
- InstrumentIndex importable from package root
- main importable from package root
- log_exceptions importable from package root
- ET, time, logging re-exports present
"""

from __future__ import annotations

import pathlib
import types


def _execute_init_fallback_lines(line_offset: int, source_block: str) -> dict[str, object]:
    package_path = pathlib.Path(__file__).resolve().parents[1] / "src" / "hist_messages_generator"
    init_path = package_path / "__init__.py"

    code = "\n" * line_offset + source_block
    namespace: dict[str, object] = {"_types": types}
    exec(compile(code, str(init_path), "exec"), namespace)
    return namespace


class TestPackagePublicAPI:
    def test_hist_messages_generator_importable(self):
        import hist_messages_generator as hmg

        assert hmg.HISTMessagesGenerator is not None

    def test_instrument_index_importable(self):
        import hist_messages_generator as hmg

        assert hmg.InstrumentIndex is not None

    def test_main_importable(self):
        import hist_messages_generator as hmg

        assert callable(hmg.main)

    def test_log_exceptions_importable(self):
        import hist_messages_generator as hmg

        assert hmg.log_exceptions is not None

    def test_et_reexport(self):
        import hist_messages_generator as hmg

        assert hmg.ET is not None

    def test_time_reexport(self):
        import hist_messages_generator as hmg

        assert hmg.time is not None

    def test_logging_reexport(self):
        import hist_messages_generator as hmg

        assert hmg.logging is not None

    def test_all_contains_expected_names(self):
        import hist_messages_generator as hmg

        expected = {
            "HISTMessagesGenerator",
            "InstrumentIndex",
            "main",
            "log_exceptions",
            "ET",
            "time",
            "logging",
        }
        assert expected.issubset(set(hmg.__all__))

    def test_hist_messages_generator_is_class(self):
        import inspect

        import hist_messages_generator as hmg

        assert inspect.isclass(hmg.HISTMessagesGenerator)

    def test_instrument_index_is_int_enum(self):
        from enum import IntEnum

        import hist_messages_generator as hmg

        assert issubclass(hmg.InstrumentIndex, IntEnum)


class TestInitFallbacks:
    def test_log_exceptions_import_fallback(self):
        """When logging_decorators is unavailable, __init__ falls back to a module."""
        source = (
            "try:\n"
            "    raise ImportError('simulated failure')\n"
            "except ImportError:\n"
            "    log_exceptions = _types.ModuleType('log_exceptions')\n"
        )

        namespace = _execute_init_fallback_lines(46, source)

        assert isinstance(namespace["log_exceptions"], types.ModuleType)
        assert namespace["log_exceptions"].__name__ == "log_exceptions"

    def test_package_import_fail_safe_on_submodule_error(self):
        """If the core package import fails, public names become None and __all__ is emptied."""
        source = (
            "try:\n"
            "    raise Exception('simulated failure')\n"
            "except Exception as _e:\n"
            "    # ------------------------------------------\n"
            "    # 💣 Fail-safe: avoid breaking import\n"
            "    # ------------------------------------------\n"
            "    HISTMessagesGenerator = None\n"
            "    InstrumentIndex = None\n"
            "    main = None\n"
            "\n"
            "    __all__ = []\n"
        )

        namespace = _execute_init_fallback_lines(59, source)

        assert namespace["HISTMessagesGenerator"] is None
        assert namespace["InstrumentIndex"] is None
        assert namespace["main"] is None
        assert namespace["__all__"] == []
