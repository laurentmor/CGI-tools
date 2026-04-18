# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for load_replace_map_from_json()."""

import json
import unittest
from unittest.mock import mock_open, patch

import xml_extractor as xe


class TestLoadReplaceMapFromJson(unittest.TestCase):
    """Validate JSON replace-map loading and error handling."""

    def test_loads_valid_json(self):
        """Verify that valid JSON is loaded correctly."""
        data = {"*": "-", "\x02": ""}
        m = mock_open(read_data=json.dumps(data))
        with patch("builtins.open", m):
            result = xe.load_replace_map_from_json("replacements.json")
        self.assertEqual(result, data)

    def test_file_not_found(self):
        """Verify that missing file logs a warning and returns default map."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            result = xe.load_replace_map_from_json("missing.json")
        self.assertEqual(result, {"*": "-", "\x02": "", "\x1a": ""})

    def test_bad_json(self):
        """Verify that invalid JSON logs a warning and returns default map."""
        m = mock_open(read_data="not a json")
        with patch("builtins.open", m):
            result = xe.load_replace_map_from_json("bad.json")
        self.assertEqual(result, {"*": "-", "\x02": "", "\x1a": ""})
