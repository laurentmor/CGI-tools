# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for validate_column_exists().
These tests ensure the required XML column tag exists and that missing values are handled correctly."""

import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

import xml_extractor as xe  # type: ignore
from tests.fixtures import SINGLE_ROW_XML


class TestValidateColumnExists(unittest.TestCase):
    """Verify XML column existence checks and error handling for missing tags."""

    def test_column_found_in_file(self):
        """Verify that Column found in file."""
        with (
            patch("os.path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.ET.parse") as mock_parse,
        ):
            ET.ElementTree(ET.fromstring(SINGLE_ROW_XML))
            root = ET.fromstring("<RESULTS><COLUMN NAME='RICH_TEXT_NCLOB'/></RESULTS>")
            mock_parse.return_value.getroot = lambda: root
            result = xe.validate_column_exists("input.xml", "RICH_TEXT_NCLOB")
        self.assertTrue(result)

    def test_column_not_found_raises(self):
        """Verify that Column not found raises."""
        with (
            patch("os.path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.ET.parse") as mock_parse,
        ):
            root = ET.fromstring("<RESULTS><COLUMN NAME='OTHER'/></RESULTS>")
            mock_parse.return_value.getroot = lambda: root
            with self.assertRaises((ValueError, Exception)):
                xe.validate_column_exists("input.xml", "RICH_TEXT_NCLOB")

    def test_xml_string_input(self):
        """Verify that Xml string input."""
        xml_str = "<RESULTS><COLUMN NAME='RICH_TEXT_NCLOB'/></RESULTS>"
        result = xe.validate_column_exists(xml_str, "RICH_TEXT_NCLOB")
        self.assertTrue(result)

    def test_file_not_found_raises(self):
        """Verify that File not found raises."""
        with patch("os.path.exists", return_value=False), self.assertRaises((ValueError, Exception)):
            xe.validate_column_exists("missing.xml", "COL")
