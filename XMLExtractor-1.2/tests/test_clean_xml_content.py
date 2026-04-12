"""Unit tests for clean_xml_content().
These tests ensure invalid XML characters are removed and replacement rules are applied correctly."""
import unittest
import xml_extractor as xe
from tests.fixtures import REPLACE_MAP


class TestCleanXmlContent(unittest.TestCase):

    """Verify XML content cleaning removes control characters and applies replacement rules correctly."""
    def test_empty_string_passthrough(self):
        """Verify that Empty string passthrough."""
        self.assertEqual(xe.clean_xml_content("", REPLACE_MAP), "")

    def test_none_passthrough(self):
        """Verify that None passthrough."""
        self.assertIsNone(xe.clean_xml_content(None, REPLACE_MAP))

    def test_control_chars_removed(self):
        """Verify that Control chars removed."""
        result = xe.clean_xml_content("A\x02B\x1AC", REPLACE_MAP)
        self.assertNotIn("\x02", result)
        self.assertNotIn("\x1A", result)

    def test_asterisk_replaced(self):
        """Verify that Asterisk replaced."""
        result = xe.clean_xml_content("A*B", REPLACE_MAP)
        self.assertIn("-", result)
        self.assertNotIn("*", result)

    def test_tab_and_newline_preserved(self):
        """Verify that Tab and newline preserved."""
        result = xe.clean_xml_content("\t\n\rtext", REPLACE_MAP)
        self.assertIn("\t", result)
        self.assertIn("\n", result)

    def test_plain_ascii_unchanged(self):
        """Verify that Plain ascii unchanged."""
        plain = "Hello World 123"
        self.assertEqual(xe.clean_xml_content(plain, {}), plain)

    def test_no_replace_map(self):
        """Verify that No replace map."""
        result = xe.clean_xml_content("A\x02B", None)
        self.assertNotIn("\x02", result)

    def test_multiple_replacements(self):
        """Verify that Multiple replacements."""
        result = xe.clean_xml_content("A*B*C", {"*": "-"})
        self.assertEqual(result, "A-B-C")
