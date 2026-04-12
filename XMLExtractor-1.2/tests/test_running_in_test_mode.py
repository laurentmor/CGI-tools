"""Unit tests for running_in_test_mode().
These tests verify whether the current working directory indicates a test-mode execution."""
import unittest
from unittest.mock import patch
import xml_extractor as xe


class TestRunningInTestMode(unittest.TestCase):

    """Verify test-mode detection based on the current working directory."""
    def test_returns_true_when_test_in_cwd(self):
        """Verify that Returns true when test in cwd."""
        with patch("os.getcwd", return_value="/home/user/tests/run"):
            self.assertTrue(xe.running_in_test_mode())

    def test_returns_false_when_test_not_in_cwd(self):
        """Verify that Returns false when test not in cwd."""
        with patch("os.getcwd", return_value="/home/user/project"):
            self.assertFalse(xe.running_in_test_mode())
