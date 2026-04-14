"""Unit tests for running_in_test_runner_context().
These tests verify whether the current working directory indicates a test-mode execution."""
import os
import unittest
from unittest.mock import patch
import xml_extractor as xe


class TestRunningInTestMode(unittest.TestCase):
    def test_running_in_test_mode_true(self):
        with patch.dict(os.environ, {"XML_EXTRACTOR_TEST_MODE": "true"}):
            self.assertTrue(xe.running_in_test_runner_context())

    def test_running_in_test_mode_false(self):
        with patch.dict(os.environ, {"XML_EXTRACTOR_TEST_MODE": ""}):
            self.assertFalse(xe.running_in_test_runner_context())