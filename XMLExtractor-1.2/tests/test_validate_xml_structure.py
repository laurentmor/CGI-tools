import unittest
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET
import xml_extractor as xe


class TestValidateXmlStructure(unittest.TestCase):

    def test_valid_xml_file(self):
        with patch("xml_extractor.ET.parse", return_value=MagicMock()):
            result = xe.validate_xml_structure("any_file.xml")
        self.assertTrue(result)

    def test_invalid_xml_raises_parse_error(self):
        with patch("xml_extractor.ET.parse", side_effect=ET.ParseError("bad xml")):
            with self.assertRaises(ET.ParseError):
                xe.validate_xml_structure("bad.xml")

    def test_missing_file_raises(self):
        with patch("xml_extractor.ET.parse", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                xe.validate_xml_structure("missing.xml")
