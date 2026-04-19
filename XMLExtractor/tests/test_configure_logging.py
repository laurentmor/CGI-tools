# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for configure_logging().
These tests verify logger creation and correct log filename selection across normal and test mode."""

import logging
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
            m.level = logging.NOTSET  # required: logging internals access handler.level
            return m

        log = logging.getLogger("xml_extractor.xml_extractor")
        original_handlers = log.handlers[:]
        try:
            with (
                patch("os.getcwd", return_value="/home/user"),
                patch("logging.FileHandler", side_effect=fake_fh),
            ):
                log.handlers.clear()
                xe.configure_logging()
        finally:
            log.handlers[:] = original_handlers

        self.assertIn("script.log", captured.get("name", ""))