# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for the log_exceptions decorator.
These tests verify exception mapping, logger resolution, and wrapper metadata preservation."""

import types
import unittest
from unittest.mock import MagicMock

from tests.fixtures import load_real_log_exceptions

log_exceptions = load_real_log_exceptions()


class TestLogExceptionsDecorator(unittest.TestCase):
    """Validate decorator behavior for mapping exceptions to log messages and preserving wrapped functions."""

    @staticmethod
    def _spy():
        return types.SimpleNamespace(
            debug=MagicMock(),
            info=MagicMock(),
            warning=MagicMock(),
            error=MagicMock(),
        )

    def test_no_exception_returns_value(self):
        """Verify that No exception returns value."""

        @log_exceptions({ValueError: "bad value"})
        def good():
            return 42

        self.assertEqual(good(), 42)

    def test_mapped_exception_logged_returns_none(self):
        """Verify that Mapped exception logged returns none."""
        spy = self._spy()

        @log_exceptions({ValueError: "bad value"}, logger=spy)
        def bad():
            raise ValueError("oops")

        self.assertIsNone(bad())
        spy.warning.assert_called_once()

    def test_raise_exception_true_re_raises(self):
        """Verify that Raise exception true re raises."""
        spy = self._spy()

        @log_exceptions({ValueError: "bad"}, raise_exception=True, logger=spy)
        def bad():
            raise ValueError("boom")

        with self.assertRaises(ValueError):
            bad()

    def test_log_level_error(self):
        """Verify that Log level error."""
        spy = self._spy()

        @log_exceptions({KeyError: "missing key"}, log_level="error", logger=spy)
        def bad():
            raise KeyError("k")

        bad()
        spy.error.assert_called_once()

    def test_unmapped_exception_propagates(self):
        """Verify that Unmapped exception propagates."""

        @log_exceptions({ValueError: "val"})
        def bad():
            raise RuntimeError("unhandled")

        with self.assertRaises(RuntimeError):
            bad()

    def test_wraps_preserves_function_name(self):
        """Verify that Wraps preserves function name."""

        @log_exceptions({ValueError: "v"})
        def my_function():
            pass

        self.assertEqual(my_function.__name__, "my_function")

    def test_instance_logger_resolved(self):
        """Verify that Instance logger resolved."""

        class MyClass:
            def __init__(self):
                self.logger = types.SimpleNamespace(
                    warning=MagicMock(), error=MagicMock(), info=MagicMock()
                )

            @log_exceptions({ValueError: "bad"}, log_level="warning", logger="logger")
            def method(self):
                raise ValueError("err")

        obj = MyClass()
        obj.method()
        obj.logger.warning.assert_called_once()
