"""Unit tests for configure_logging().
These tests verify logger creation and correct log filename selection across normal and test mode."""
import logging
import os
import unittest
from unittest.mock import MagicMock, patch
import xml_extractor as xe


class TestConfigureLogging(unittest.TestCase):

    
    def test_log_file_name_in_normal_mode(self):
        """Verify that Log file name in normal mode."""
        captured = {}
        original_fh = logging.FileHandler

        def fake_fh(name, *a, **kw):
            captured["name"] = name
            m = MagicMock(spec=original_fh)
            m.setFormatter = MagicMock()
            m.setLevel = MagicMock()
            return m

        with patch("os.getcwd", return_value="/home/user"), \
             patch("logging.FileHandler", side_effect=fake_fh):
            log = logging.getLogger("xml_extractor")
            log.handlers.clear()
            xe.configure_logging()

        self.assertIn("script.log", captured.get("name", ""))
