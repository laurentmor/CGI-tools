import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
import xml_extractor as xe
from tests.fixtures import SINGLE_ROW_XML


class TestValidateColumnExists(unittest.TestCase):

    def test_column_found_in_file(self):
        with patch("os.path.exists", return_value=True), \
             patch("xml_extractor.ET.parse") as mock_parse:
            ET.ElementTree(ET.fromstring(SINGLE_ROW_XML))
            root = ET.fromstring("<RESULTS><COLUMN NAME='RICH_TEXT_NCLOB'/></RESULTS>")
            mock_parse.return_value.getroot = lambda: root
            result = xe.validate_column_exists("input.xml", "RICH_TEXT_NCLOB")
        self.assertTrue(result)

    def test_column_not_found_raises(self):
        with patch("os.path.exists", return_value=True), \
             patch("xml_extractor.ET.parse") as mock_parse:
            root = ET.fromstring("<RESULTS><COLUMN NAME='OTHER'/></RESULTS>")
            mock_parse.return_value.getroot = lambda: root
            with self.assertRaises((ValueError, Exception)):
                xe.validate_column_exists("input.xml", "RICH_TEXT_NCLOB")

    def test_xml_string_input(self):
        xml_str = "<RESULTS><COLUMN NAME='RICH_TEXT_NCLOB'/></RESULTS>"
        result = xe.validate_column_exists(xml_str, "RICH_TEXT_NCLOB")
        self.assertTrue(result)

    def test_file_not_found_raises(self):
        with patch("os.path.exists", return_value=False):
            with self.assertRaises((ValueError, Exception)):
                xe.validate_column_exists("missing.xml", "COL")
