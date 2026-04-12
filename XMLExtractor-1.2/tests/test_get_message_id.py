import unittest
from tests.fixtures import make_extractor


class TestGetMessageId(unittest.TestCase):

    def setUp(self):
        self.extractor = make_extractor()

    def test_extracts_standard_id(self):
        content = "<Proponix><Header><MessageID>MSG001</MessageID></Header></Proponix>"
        self.assertEqual(self.extractor.get_message_id(content), "MSG001")

    def test_returns_empty_when_tag_missing(self):
        self.assertEqual(self.extractor.get_message_id("<Root/>"), "")

    def test_custom_tag(self):
        ext = make_extractor(file_id_tag="InvoiceID")
        content = "<Root><InvoiceID>INV42</InvoiceID></Root>"
        self.assertEqual(ext.get_message_id(content), "INV42")

    def test_empty_string_content(self):
        self.assertEqual(self.extractor.get_message_id(""), "")

    def test_nested_id(self):
        content = "<a><b><MessageID>NESTED</MessageID></b></a>"
        self.assertEqual(self.extractor.get_message_id(content), "NESTED")
