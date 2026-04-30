# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for validate_xml_structure().
These tests verify XML parsing success, malformed XML errors, and missing file behavior."""

import unittest
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET

import xml_extractor as xe


class TestValidateXmlStructure(unittest.TestCase):
    """Verify XML structure validation handles parse errors and missing files."""

    def test_valid_xml_file(self):
        """Verify that Valid xml file."""
        with patch("xml_extractor.ET.parse", return_value=MagicMock()):
            result = xe.validate_xml_structure("any_file.xml")
        self.assertTrue(result)

    def test_invalid_xml_raises_parse_error(self):
        """Verify that Invalid xml raises parse error."""
        with (
            patch("xml_extractor.ET.parse", side_effect=ET.ParseError("bad xml")),
            self.assertRaises(ET.ParseError),
        ):
            xe.validate_xml_structure("bad.xml")

    def test_missing_file_raises(self):
        """Verify that Missing file raises."""
        with (
            patch("xml_extractor.ET.parse", side_effect=FileNotFoundError),
            self.assertRaises(FileNotFoundError),
        ):
            xe.validate_xml_structure("missing.xml")
