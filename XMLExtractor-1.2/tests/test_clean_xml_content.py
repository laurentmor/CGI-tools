import unittest
import xml_extractor as xe
from tests.fixtures import REPLACE_MAP


class TestCleanXmlContent(unittest.TestCase):

    def test_empty_string_passthrough(self):
        self.assertEqual(xe.clean_xml_content("", REPLACE_MAP), "")

    def test_none_passthrough(self):
        self.assertIsNone(xe.clean_xml_content(None, REPLACE_MAP))

    def test_control_chars_removed(self):
        result = xe.clean_xml_content("A\x02B\x1AC", REPLACE_MAP)
        self.assertNotIn("\x02", result)
        self.assertNotIn("\x1A", result)

    def test_asterisk_replaced(self):
        result = xe.clean_xml_content("A*B", REPLACE_MAP)
        self.assertIn("-", result)
        self.assertNotIn("*", result)

    def test_tab_and_newline_preserved(self):
        result = xe.clean_xml_content("\t\n\rtext", REPLACE_MAP)
        self.assertIn("\t", result)
        self.assertIn("\n", result)

    def test_plain_ascii_unchanged(self):
        plain = "Hello World 123"
        self.assertEqual(xe.clean_xml_content(plain, {}), plain)

    def test_no_replace_map(self):
        result = xe.clean_xml_content("A\x02B", None)
        self.assertNotIn("\x02", result)

    def test_multiple_replacements(self):
        result = xe.clean_xml_content("A*B*C", {"*": "-"})
        self.assertEqual(result, "A-B-C")
