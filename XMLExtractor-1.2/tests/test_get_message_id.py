"""Unit tests for get_message_id().
These tests cover extracting a message ID from XML, handling missing tags, custom tags, and nested XML content."""
import unittest
from tests.fixtures import make_extractor


class TestGetMessageId(unittest.TestCase):

    """Test get_message_id() extraction logic for standard IDs, missing IDs, custom tags, and nested content."""
    def setUp(self):
        self.extractor = make_extractor()

    def test_extracts_standard_id(self):
        """Verify that Extracts standard id."""
        content = "<Proponix><Header><MessageID>MSG001</MessageID></Header></Proponix>"
        self.assertEqual(self.extractor.get_message_id(content), "MSG001")

    def test_returns_empty_when_tag_missing(self):
        """Verify that Returns empty when tag missing."""
        self.assertEqual(self.extractor.get_message_id("<Root/>"), "")

    def test_custom_tag(self):
        """Verify that Custom tag."""
        ext = make_extractor(file_id_tag="InvoiceID")
        content = "<Root><InvoiceID>INV42</InvoiceID></Root>"
        self.assertEqual(ext.get_message_id(content), "INV42")

    def test_empty_string_content(self):
        """Verify that Empty string content."""
        self.assertEqual(self.extractor.get_message_id(""), "")

    def test_nested_id(self):
        """Verify that Nested id."""
        content = "<a><b><MessageID>NESTED</MessageID></b></a>"
        self.assertEqual(self.extractor.get_message_id(content), "NESTED")
