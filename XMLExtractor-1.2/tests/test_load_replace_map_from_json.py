"""Unit tests for load_replace_map_from_json().
These tests exercise real JSON parsing and exception handling via the real decorator wrapper."""
import json
import unittest
from unittest.mock import mock_open, patch
import xml_extractor as xe
from tests.fixtures import load_real_log_exceptions


class TestLoadReplaceMapFromJson(unittest.TestCase):
    """Validate JSON replace-map loading and real decorator-based exception handling."""

    def setUp(self):
        real_log_exc = load_real_log_exceptions()
        bare = xe.load_replace_map_from_json
        self._wrapped = real_log_exc(
            {FileNotFoundError: "JSON file not found",
             json.JSONDecodeError: "JSON decoding failed"},
            log_level="warning",
            raise_exception=False,
            logger=None,
        )(bare)

    def test_loads_valid_json(self):
        """Verify that Loads valid json."""
        data = {"*": "-", "\x02": ""}
        m = mock_open(read_data=json.dumps(data))
        with patch("builtins.open", m):
            result = self._wrapped("replacements.json")
        self.assertEqual(result, data)

    def test_file_not_found_returns_none(self):
        """Verify that File not found returns none."""
        with patch("builtins.open", side_effect=FileNotFoundError("no file")):
            result = self._wrapped("missing.json")
        self.assertIsNone(result)

    def test_bad_json_returns_none(self):
        """Verify that Bad json returns none."""
        m = mock_open(read_data="{bad json}")
        with patch("builtins.open", m):
            result = self._wrapped("bad.json")
        self.assertIsNone(result)
