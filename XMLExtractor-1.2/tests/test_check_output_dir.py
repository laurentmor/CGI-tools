import logging
import unittest
from unittest.mock import patch
import xml_extractor as xe
from tests.fixtures import make_extractor


class TestCheckOutputDir(unittest.TestCase):

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_creates_dir_when_absent(self):
        ext = make_extractor()
        with patch("os.path.exists", return_value=False), \
             patch("os.makedirs") as mock_mkdirs:
            ext.check_output_dir()
        mock_mkdirs.assert_called_once_with("output", exist_ok=True)

    def test_dry_run_skips_all(self):
        ext = make_extractor(dry_run=True)
        with patch("os.path.exists") as mock_exists, \
             patch("os.makedirs") as mock_mkdirs:
            ext.check_output_dir()
        mock_exists.assert_not_called()
        mock_mkdirs.assert_not_called()

    def test_test_mode_auto_deletes(self):
        ext = make_extractor(test_mode="Y")
        with patch("os.path.exists", return_value=True), \
             patch.object(ext, "delete_output_dir") as mock_del, \
             patch("os.makedirs"):
            ext.check_output_dir()
        mock_del.assert_called_once()

    def test_dir_exists_user_says_no_appends(self):
        ext = make_extractor()
        with patch("os.path.exists", return_value=True), \
             patch("builtins.input", return_value="N"), \
             patch.object(ext, "delete_output_dir") as mock_del:
            ext.check_output_dir()
        mock_del.assert_not_called()
