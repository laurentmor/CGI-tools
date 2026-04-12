import types
import unittest
from unittest.mock import MagicMock
from tests.fixtures import load_real_log_exceptions

log_exceptions = load_real_log_exceptions()


class TestLogExceptionsDecorator(unittest.TestCase):
    """
    Tests for the real log_exceptions decorator loaded directly from
    decorators.py.

    Key gotcha: MagicMock() is callable, so the decorator's
        `if callable(logger): log_instance = logger(*args, **kwargs)`
    branch fires and calls the mock as a factory, returning a *child* mock
    rather than using the mock we passed.  Fix: use a non-callable
    types.SimpleNamespace that exposes only the needed log methods.
    """

    @staticmethod
    def _spy():
        return types.SimpleNamespace(
            debug=MagicMock(),
            info=MagicMock(),
            warning=MagicMock(),
            error=MagicMock(),
        )

    def test_no_exception_returns_value(self):
        @log_exceptions({ValueError: "bad value"})
        def good():
            return 42

        self.assertEqual(good(), 42)

    def test_mapped_exception_logged_returns_none(self):
        spy = self._spy()

        @log_exceptions({ValueError: "bad value"}, logger=spy)
        def bad():
            raise ValueError("oops")

        self.assertIsNone(bad())
        spy.warning.assert_called_once()

    def test_raise_exception_true_re_raises(self):
        spy = self._spy()

        @log_exceptions({ValueError: "bad"}, raise_exception=True, logger=spy)
        def bad():
            raise ValueError("boom")

        with self.assertRaises(ValueError):
            bad()

    def test_log_level_error(self):
        spy = self._spy()

        @log_exceptions({KeyError: "missing key"}, log_level="error", logger=spy)
        def bad():
            raise KeyError("k")

        bad()
        spy.error.assert_called_once()

    def test_unmapped_exception_propagates(self):
        @log_exceptions({ValueError: "val"})
        def bad():
            raise RuntimeError("unhandled")

        with self.assertRaises(RuntimeError):
            bad()

    def test_wraps_preserves_function_name(self):
        @log_exceptions({ValueError: "v"})
        def my_function():
            pass

        self.assertEqual(my_function.__name__, "my_function")

    def test_instance_logger_resolved(self):
        """logger='logger' string resolved from args[0].logger attribute."""

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
