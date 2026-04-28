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
