import unittest
from unittest.mock import patch
import xml_extractor as xe


class TestRunningInTestMode(unittest.TestCase):

    def test_returns_true_when_test_in_cwd(self):
        with patch("os.getcwd", return_value="/home/user/tests/run"):
            self.assertTrue(xe.running_in_test_mode())

    def test_returns_false_when_test_not_in_cwd(self):
        with patch("os.getcwd", return_value="/home/user/project"):
            self.assertFalse(xe.running_in_test_mode())
