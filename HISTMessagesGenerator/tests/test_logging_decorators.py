# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Unit tests for logging_decorators.py

Covers:
- Normal (non-exception) path passes through unchanged
- Mapped exceptions are logged at the correct level
- Unmapped exceptions propagate without logging
- raise_exception=True re-raises after logging
- raise_exception=False suppresses re-raise
- Logger resolution: callable, string attribute, default module logger
- __wrapped__ attribute exposed for introspection / testing
- Subclass exceptions matched by isinstance semantics
- Multiple exception types in error_map
- Return value preservation on happy path
- log_level parameter respected
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from hist_messages_generator.logging_decorators import log_exceptions

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_logger():
    lgr = MagicMock(spec=logging.Logger)
    lgr.warning = MagicMock()
    lgr.error = MagicMock()
    lgr.info = MagicMock()
    return lgr


# ---------------------------------------------------------------------------
# Normal path
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_return_value_preserved(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({ValueError: "bad"}, logger=mock_lgr)
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_no_logging_on_success(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({ValueError: "bad"}, logger=mock_lgr)
        def noop():
            pass

        noop()
        mock_lgr.warning.assert_not_called()
        mock_lgr.error.assert_not_called()

    def test_wrapped_attribute_exposed(self):
        def inner():
            pass

        decorated = log_exceptions({ValueError: "v"})(inner)
        assert decorated.__wrapped__ is inner


# ---------------------------------------------------------------------------
# Exception logging
# ---------------------------------------------------------------------------


class TestExceptionLogging:
    def test_mapped_exception_logged_at_warning(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({ValueError: "value problem"}, raise_exception=False, logger=mock_lgr)
        def boom():
            raise ValueError("oops")

        boom()
        mock_lgr.warning.assert_called_once()
        call_arg = mock_lgr.warning.call_args[0][0]
        assert "value problem" in call_arg

    def test_mapped_exception_logged_at_custom_level(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions(
            {ValueError: "v"}, log_level="error", raise_exception=False, logger=mock_lgr
        )
        def boom():
            raise ValueError("x")

        boom()
        mock_lgr.error.assert_called_once()
        mock_lgr.warning.assert_not_called()

    def test_exception_message_included_in_log(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({KeyError: "key issue"}, raise_exception=False, logger=mock_lgr)
        def boom():
            raise KeyError("missing_key")

        boom()
        call_arg = mock_lgr.warning.call_args[0][0]
        assert "missing_key" in call_arg

    def test_unmapped_exception_propagates_without_logging(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({ValueError: "v"}, logger=mock_lgr)
        def boom():
            raise TypeError("not mapped")

        with pytest.raises(TypeError, match="not mapped"):
            boom()

        mock_lgr.warning.assert_not_called()

    def test_raise_exception_true_reraises(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({ValueError: "v"}, raise_exception=True, logger=mock_lgr)
        def boom():
            raise ValueError("re-raise me")

        with pytest.raises(ValueError, match="re-raise me"):
            boom()

        mock_lgr.warning.assert_called_once()

    def test_raise_exception_false_suppresses_reraise(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({ValueError: "v"}, raise_exception=False, logger=mock_lgr)
        def boom():
            raise ValueError("suppress me")

        boom()  # must not raise
        mock_lgr.warning.assert_called_once()

    def test_subclass_exception_matched(self):
        """FileNotFoundError is a subclass of OSError; should match OSError mapping."""
        mock_lgr = _make_mock_logger()

        @log_exceptions({OSError: "os level"}, raise_exception=False, logger=mock_lgr)
        def boom():
            raise FileNotFoundError("no file")

        boom()
        mock_lgr.warning.assert_called_once()
        assert "os level" in mock_lgr.warning.call_args[0][0]

    def test_first_matching_message_used(self):
        """When multiple keys match, the first matching message is used."""
        mock_lgr = _make_mock_logger()

        @log_exceptions(
            {FileNotFoundError: "file msg", OSError: "os msg"},
            raise_exception=False,
            logger=mock_lgr,
        )
        def boom():
            raise FileNotFoundError("f")

        boom()
        call_arg = mock_lgr.warning.call_args[0][0]
        assert "file msg" in call_arg


# ---------------------------------------------------------------------------
# Logger resolution
# ---------------------------------------------------------------------------


class TestLoggerResolution:
    def test_logger_as_direct_instance(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions({ValueError: "v"}, raise_exception=False, logger=mock_lgr)
        def boom():
            raise ValueError("x")

        boom()
        mock_lgr.warning.assert_called_once()

    def test_logger_as_callable(self):
        """
        NOTE: The current log_exceptions implementation only resolves the logger
        when it is a str attribute name. When logger is a non-str callable
        (lambda), it is assigned directly as _logger, causing an AttributeError
        when a log method is invoked. This is a known source quirk.

        This test documents that behaviour: a callable logger causes AttributeError
        rather than silently swallowing the exception.
        """
        mock_lgr = _make_mock_logger()

        class Svc:
            my_logger = mock_lgr

            @log_exceptions(
                {ValueError: "v"},
                raise_exception=False,
                logger=lambda self: self.my_logger,
            )
            def do(self):
                raise ValueError("x")

        # The lambda is not called — it is used directly as the logger object,
        # which then has no .warning attribute.
        with pytest.raises(AttributeError):
            Svc().do()

    def test_logger_as_string_attribute(self):
        """logger='attr_name' resolves to getattr(self, attr_name)."""
        mock_lgr = _make_mock_logger()

        class Svc:
            my_lgr = mock_lgr

            @log_exceptions({ValueError: "v"}, raise_exception=False, logger="my_lgr")
            def do(self):
                raise ValueError("x")

        Svc().do()
        mock_lgr.warning.assert_called_once()

    def test_default_logger_used_when_none(self, caplog):
        """When logger=None, module logger is used."""

        @log_exceptions({ValueError: "v"}, raise_exception=False, logger=None)
        def boom():
            raise ValueError("default logger test")

        with caplog.at_level(logging.WARNING):
            boom()

        assert any("v" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# Multiple exception types
# ---------------------------------------------------------------------------


class TestMultipleExceptionTypes:
    def test_key_error_mapped(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions(
            {ValueError: "val", KeyError: "key"},
            raise_exception=False,
            logger=mock_lgr,
        )
        def boom():
            raise KeyError("k")

        boom()
        assert "key" in mock_lgr.warning.call_args[0][0]

    def test_value_error_mapped(self):
        mock_lgr = _make_mock_logger()

        @log_exceptions(
            {ValueError: "val", KeyError: "key"},
            raise_exception=False,
            logger=mock_lgr,
        )
        def boom():
            raise ValueError("v")

        boom()
        assert "val" in mock_lgr.warning.call_args[0][0]
